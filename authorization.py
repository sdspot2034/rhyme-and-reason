from flask import Flask, redirect, request
import urllib.parse as urlparse
import base64
import requests
import json
import os
import time
from functools import wraps


# Mini web app to procure authorization
class FlaskWrapper():
    def __init__(self, client_id, redirect_url, scopes):
        self.client_id = client_id
        self.redirect_url = redirect_url
        self.scopes = scopes
        self.auth_code = None
        self.app = Flask(__name__)
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route("/")
        def index():
            user_auth_url = 'https://accounts.spotify.com/authorize?' + urlparse.urlencode({
                'client_id': self.client_id,
                'response_type': 'code',
                'scope': self.scopes,
                'redirect_uri': self.redirect_url,
            })
            return redirect(user_auth_url)

        @self.app.route("/callback")
        def callback():
            self.auth_code = request.args.get('code')
            if self.auth_code is None:
                err = request.args.get('error')
                self.shutdown_server()
                return f"Authorization failed with the following error: {err}"
            else:
                self.shutdown_server()
                return "<h1> Authorization successful. Please close this window. </h1>"
            
            
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def run(self):
        self.app.run(host="localhost", port=5050)

    def get_auth_code(self):
        return self.auth_code
    
    def __del__():
        # Ensure auth_code is removed from flask app object to prevent misuse
        self.auth_code = None
        print("Flask authorization micro-app destructed.")


class SpotifyAuth:
    def __init__(self, client_id, client_secret, redirect_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.auth_code = None
        self.token = None
        self.scopes = " ".join([
            "user-read-playback-state",
            "user-read-currently-playing",
            "playlist-read-private",
            "playlist-read-collaborative",
            "user-read-playback-position",
            "user-top-read",
            "user-read-recently-played",
            "user-library-read",
            "user-read-email",
            "user-read-private"
        ])

    def first_authorization(self):
        flask_app = FlaskWrapper(self.client_id, self.redirect_url, self.scopes)
        flask_app.run()
        self.auth_code = flask_app.get_auth_code()
        del flask_app         # Destroy app object
        

    def get_auth_code(self):
        return self.auth_code
    
    def set_auth_code_from_file(self, auth_file):
        with open(auth_file, 'r') as file:
            code = file.read(auth_file)
        self.auth_code = code

    def authorize_app(self, auth_file = None):
        if not auth_file:
            self.first_authorization()
        else:
            self.set_auth_code_from_file(auth_file)

    def set_access_tokens(self, auth_file = None):
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")

        self.authorize_app(auth_file)

        token_endpoint = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "redirect_uri": self.redirect_url,
        }
        headers = {
            "Authorization": "Basic " + auth_encoded,
            "Content-type": "application/x-www-form-urlencoded"
        }
        result = requests.post(token_endpoint, headers=headers, data=data)
        json_results = json.loads(result.content)

        if 'error' in json_results.keys():
            if json_results['error_description'] == 'Authorization code expired':
                print('Authorization code expired. Please reauthorize application.')
                self.first_authorization()
            else:
                raise Exception(json_results['error_description'])

        json_results['expires_at'] = int(time.time()) + json_results['expires_in']

        self.token = json_results

    
    def set_access_token_from_file(self, token_file):
        with open(token_file) as file:
            token_details = json.load(file)
        self.token = token_details
        
    
    def get_access_token(self, token_file = None, auth_file = None, update_file=False):
        if not self.token and not token_file:
            self.set_access_token(auth_file)
        elif not self.token:
            self.set_access_token_from_file(token_file)

        if int(time.time()) >= self.token['expires_at']:
            self.token = self.refresh_access_tokens(self.token['refresh_token'])
            if update_file and not token_file:
                print("Token file location not provided. Proceeding without updating file, please use method save_access_token_to_file for updating file.")
            elif update_file:
                with open(token_file, 'w+') as file:
                    json.dump(self.token, file, indent=4)

        return self.token['access_token']

    def refresh_access_tokens(self, refresh_token):
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")

        refresh_endpoint = 'https://accounts.spotify.com/api/token'
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        headers = {
            "Authorization": "Basic " + auth_encoded,
            "Content-type": "application/x-www-form-urlencoded"
        }

        result = requests.post(refresh_endpoint, headers=headers, data=data)
        json_results = json.loads(result.content)
        json_results['expires_at'] = int(time.time()) + json_results['expires_in']

        return json_results

    def refresh_token_decorator(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            access_token = self.get_access_token()
            return func(access_token, *args, **kwargs)
        return wrapper

    def save_auth_code_to_file(self, auth_file):
        with open(auth_file, 'w+') as file:
            file.write(json.dumps(self.auth_code, indent=4))
            
    def save_access_token_to_file(self, token_file):
        with open(token_file, 'w+') as file:
            file.write(json.dumps(self.token, indent=4))
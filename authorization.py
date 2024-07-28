import flask
import urllib.parse as urlparse
import base64
import requests
import json
import os
import time
from functools import wraps

class SpotifyAuth:
    def __init__(self, client_id, client_secret, redirect_url, auth_file='auth_code.txt', token_file='access_token.json'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.auth_file = auth_file
        self.token_file = token_file

    def first_authorization(self):
        code = None
        app = flask.Flask(__name__)
        scopes = " ".join([
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
        print("scopes defined")

        @app.route("/")
        def index():
            user_auth_url = 'https://accounts.spotify.com/authorize?' + urlparse.urlencode({
                'client_id': self.client_id,
                'response_type': 'code',
                'scope': scopes,
                'redirect_uri': self.redirect_url,
            })
            return flask.redirect(user_auth_url)

        @app.route("/callback")
        def callback():
            code = flask.request.args.get('code')
            if code is None:
                err = flask.request.args.get('error')
                self.shutdown_server()
                return f"Authorization failed with the following error: {err}"
            else:
                with open(self.auth_file, 'w+') as file:
                    file.write(code)
                self.shutdown_server()
                return "<h1> Authorization successful. Please close this window. </h1>"

        def shutdown_server():
            func = flask.request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()

        app.run(host="localhost", port=5050)

    def peek_file(self, file_path):
        return os.path.isfile(file_path)

    def get_auth_code(self):
        with open(self.auth_file, 'r') as file:
            auth_code = file.read()
        return auth_code

    def authorize_app(self):
        authorized = self.peek_file(self.auth_file)
        if not authorized:
            self.first_authorization()
        return self.get_auth_code()

    def get_auth_tokens(self):
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")

        auth_code = self.authorize_app()

        token_endpoint = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
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

        return json_results

    def get_access_token(self):
        access_token_exists = self.peek_file(self.token_file)

        if access_token_exists:
            with open(self.token_file) as file:
                token_details = json.load(file)
        else:
            token_details = self.get_auth_tokens()
            with open(self.token_file, 'w+') as file:
                json.dump(token_details, file, indent=4)

            if os.path.isfile(self.auth_file):
                os.remove(self.auth_file)

        if int(time.time()) >= token_details['expires_at']:
            token_details = self.refresh_access_tokens(token_details['refresh_token'])
            with open(self.token_file, 'w+') as file:
                json.dump(token_details, file, indent=4)

        return token_details['access_token']

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

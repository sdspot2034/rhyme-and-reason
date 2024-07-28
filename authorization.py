import flask
import urllib.parse as urlparse
import base64
import requests
import json
import os
    
def first_authorization(client_id, redirect_url, auth_file):
    code = None
    app = flask.Flask(__name__)

    scopes = " ".join([
        "user-read-playback-state"
        ,"user-read-currently-playing"
        ,"playlist-read-private"
        ,"playlist-read-collaborative"
        ,"user-read-playback-position"
        ,"user-top-read"
        ,"user-read-recently-played"
        ,"user-library-read"
        ,"user-read-email"
        ,"user-read-private"])
    print("scopes defined")

    @app.route("/")
    def index():
        user_auth_url = 'https://accounts.spotify.com/authorize?' + urlparse.urlencode({
            'client_id': client_id,
            'response_type': 'code',
            'scope': scopes,
            'redirect_uri': redirect_url,
        })
        return flask.redirect(user_auth_url)

    @app.route("/callback")
    def callback():
        code = flask.request.args.get('code')
        if code is None:
            err = flask.request.args.get('error')
            shutdown_server()
            return f"Authorization failed with the following error: {err}"
        else:
            with open(auth_file, 'w+') as file: file.write(code)
            shutdown_server()
            return "<h1> Authorization successful. Please close this window. </h1>"

    def shutdown_server():
        func = flask.request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
    
    app.run(host="localhost", port=5050)

    
    
def peek_file(file_path):
    return os.path.isfile(file_path)


def get_auth_code(auth_file):
    with open(auth_file, 'r') as file:
        auth_code = file.read()
    return auth_code

    
def authorize_app(auth_file = 'auth_code.txt', client_id = None, redirect_url = None):
    authorized = peek_file(auth_file)

    if not authorized:
        if not client_id or not redirect_url: 
            raise ValueError("Following arguments are required:  client_id, redirect_url, auth_file.")
        first_authorization(client_id, redirect_url, auth_file)

    return get_auth_code(auth_file)


def get_auth_tokens(client_id, client_secret, redirect_url, auth_file):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")
    
    auth_code = authorize_app(auth_file, client_id, redirect_url)
    
    token_endpoint = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type":"authorization_code",
        "code":auth_code,
        "redirect_uri":redirect_url,
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
            if not client_id or not redirect_url or not auth_file:
                raise ValueError("Following arguments are required: client_id, redirect_url, auth_file.")
            first_authorization(client_id, redirect_url, auth_file)
        
        else: raise Exception(json_results['error_description'])
    
    return json_results



def get_access_token (
    token_file = 'access_token.json',
    client_id = None,
    client_secret = None,
    redirect_url = None,
    auth_file = None,
):
    
    access_token_exists = peek_file(token_file)
    
    if access_token_exists:
        with open(token_file) as file:
            token_details = json.load(file)
    
    else:
        if not client_id or not client_secret or not redirect_url or not auth_file: 
            raise ValueError("Following arguments are required:  client_id, client_secret, redirect_url, auth_file.")
        
        
        token_details = get_auth_tokens(client_id, client_secret, redirect_url, auth_file)
        with open(token_file, 'w+') as file:
            file.write(json.dumps(token_details, indent=4))
        
        # Delete auth_file as the authorization has been used and cannot be reused
        if os.path.isfile(auth_file): os.remove(auth_file)
        
    return token_details['access_token']


def refresh_access_tokens(client_id, client_secret, refresh_token):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")
    
    refresh_endpoint = 'https://accounts.spotify.com/api/token'
    data = {
        "grant_type":"refresh_token",
        "refresh_token":refresh_token
    }
    headers = {
        "Authorization": "Basic " + auth_encoded,
        "Content-type": "application/x-www-form-urlencoded"
    }
    
    result = requests.post(refresh_endpoint, headers=headers, data=data)
    json_results = json.loads(result.content)
    return json_results
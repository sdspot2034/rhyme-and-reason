import flask
import urllib.parse as urlparse
import base64
import requests
import json
    
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

    
    
def peek_file(file_path, read_mode='r'):
    try:
        file = open(file_path, read_mode)
        return True
    except FileNotFoundError: return False



def get_auth_code(auth_file):
    with open(auth_file, 'r') as file:
        auth_code = file.read()
    return auth_code

    
def authorize_app(client_id, redirect_url, auth_file = 'auth_code.txt'):
    authorized = peek_file(auth_file)

    if not authorized:
        first_authorization(client_id, redirect_url, auth_file)

    return get_auth_code(auth_file)


def get_access_token(client_id, client_secret):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")
    
    auth_api_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_encoded,
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(auth_api_url, headers=headers, data=data)
    json_results = json.loads(result.content)
    token = json_results["access_token"]
    return(token)


def refresh_access_tokens(refresh_token):
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


def get_auth_tokens(client_id, client_secret, redirect_url, auth_file):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_encoded = str(base64.b64encode(auth_bytes), "utf-8")
    
    with open(auth_file,'r+') as file:
        auth_code = file.read()
    
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
    return json_results
from dw_etl_scripts import * 
from authorization import SpotifyAuth
import json

# STEP - 1: GET SECRETS
with open('client-secrets-rnr.json','r+') as secrets_file:
    secrets = json.load(secrets_file)

client_id = secrets["client_id"]
client_secret = secrets["client_secret"]
redirect_url = secrets["redirect_url"]

# STEP - 2: AUTHORISE SPOTIFY
spotify_authorisation = SpotifyAuth(client_id=client_id, client_secret=client_secret, redirect_url=redirect_url)
spotify_authorisation.set_access_token_from_file('access_token.json')

print(spotify_authorisation.get_access_token())
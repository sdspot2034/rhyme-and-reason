from dw_etl_scripts import * 
from authorization import SpotifyAuth
from sql_functions import *
import spotify_functions as spotify
import json
from helpers.helpers import to_datetime

from time import strftime, localtime

# STEP - 1: GET SECRETS
with open('client-secrets-rnr.json','r+') as secrets_file:
    secrets = json.load(secrets_file)

client_id = secrets["client_id"]
client_secret = secrets["client_secret"]
redirect_url = secrets["redirect_url"]

# STEP - 2: AUTHORISE SPOTIFY
spotify_authorisation = SpotifyAuth(client_id=client_id, client_secret=client_secret, redirect_url=redirect_url)
spotify_authorisation.set_access_token_from_file('access_token.json')
access_token = spotify_authorisation.get_access_token()

# STEP - 3: GET LAST LOADED DATE
query = "SELECT MAX(played_at) FROM FACT_PLAY"
last_date = to_datetime(read_from_sql(query).values[0][0])
# print(last_date)
cdc_time = int(last_date.timestamp()*1e3)
# print(cdc_time)
next = cdc_time

i=1
while next:
    print("\nIteration",i,":",strftime('%Y-%m-%d %H:%M:%S', localtime(cdc_time/1000)))
    results = spotify.get_listening_history(access_token, cdc_time)
    if len(results['items']) == 0: break

    print(len(results['items']))
    print(results['next'])
    print(results['cursors'])

    next = results['next']
    cdc_time = int(results['cursors']['after'])
    i=i+1

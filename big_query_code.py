from google.cloud import bigquery
import os, json
import pandas as pd
from helpers.helpers import get_url

from authorization import SpotifyAuth
import spotify_functions as spotify

with open('client-secrets-rnr.json','r+') as secrets_file:
    secrets = json.load(secrets_file)

client_id = secrets["client_id"]
client_secret = secrets["client_secret"]
redirect_url = secrets["redirect_url"]

spotify_authorisation = SpotifyAuth(client_id=client_id, client_secret=client_secret, redirect_url=redirect_url)
spotify_authorisation.set_access_token_from_file('access_token.json')

user = [spotify.get_user_details(spotify_authorisation.get_access_token())]
df_user = pd.DataFrame(user)
df_user['spotify_url'] = df_user['external_urls'].apply(lambda x:x['spotify'])
df_user['profile_pic'] = df_user['images'].apply(get_url, args=[300])
df_user['user_wid'] = 1
df_user = df_user[['user_wid','display_name','type','country','product','spotify_url','profile_pic']]

# print(df_user)

credentials_path = 'bigquery_pk.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

client = bigquery.Client()

user_table_id = "rhyme-and-reason.Spotify_db.DIM_USER"
user_table = bigquery.Table(user_table_id)

client.load_table_from_dataframe(
    destination = user_table
    , dataframe = df_user
)

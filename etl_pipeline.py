#!/usr/bin/env python
# coding: utf-8


import json
from authorization import SpotifyAuth
import spotify_functions as spotify



import datetime
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
# print(yesterday.timestamp()*1e3)
cdc_time = int(yesterday.timestamp()*1e3)



with open('client-secrets-rnr.json','r+') as secrets_file:
    secrets = json.load(secrets_file)

client_id = secrets["client_id"]
client_secret = secrets["client_secret"]
redirect_url = secrets["redirect_url"]



spotify_authorisation = SpotifyAuth(client_id=client_id, client_secret=client_secret, redirect_url=redirect_url)
spotify_authorisation.set_access_token_from_file('access_token.json')


# # Extract, Transform, Load (ETL)


from dw_etl_scripts import *


# ## Dimensions

# ### DIM_USER

# #### Load (Type 0 SCD)


# dim_user_load(spotify, spotify_authorisation.get_access_token())


# ### DIM_ARTIST

# #### Load (Type 1 SCD)


dim_artist_load(spotify, spotify_authorisation.get_access_token(), cdc_time)


# ### DIM_ALBUM

# #### Load (Type 1 SCD)


dim_album_load(spotify, spotify_authorisation.get_access_token(), cdc_time)


# ### BRIDGE_ALBUM_ARTIST

# #### Load (Type 1 SCD)


bridge_album_artist_load(spotify, spotify_authorisation.get_access_token(), cdc_time)


# ### DIM_SONG

# #### Load (Type 1 SCD)


dim_song_load(spotify, spotify_authorisation.get_access_token(), cdc_time)


# ### FACT_PLAY


fact_play_load(spotify, spotify_authorisation.get_access_token(), cdc_time)


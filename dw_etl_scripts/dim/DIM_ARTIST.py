import pandas as pd
from sqlalchemy import Table, MetaData, Column, Integer, String
import sql_functions

def dim_artist_load(spotify, access_token, cdc_time):
    history = spotify.get_listening_history(access_token, cdc_time)['items']
    
    # stacked list-comprehension
    artist_list = [artist for artists in [play['track']['artists'] for play in history] for artist in artists]
    
    df_artists = pd.DataFrame(artist_list)
    df_artists = df_artists.drop(columns=['href','uri','external_urls'])
    df_artists = df_artists.rename(columns={'id':'spotify_id','name':'artist_name','type':'artist_type'})
    df_artists.drop_duplicates(inplace=True)
    
    metadata = MetaData()

    # Define the dimension table schema
    dim_table = Table('DIM_ARTIST', metadata,
        Column('artist_wid', Integer, primary_key=True, autoincrement=True),
        Column('spotify_id', String(255), nullable=False, unique=True),
        Column('artist_name', String(255)),
        Column('artist_type', String(255))
    )
    
    sql_functions.save_to_sql(df_artists, dim_table, key_cols=['spotify_id'], wid=['artist_wid'], mode='upsert')
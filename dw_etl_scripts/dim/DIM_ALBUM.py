import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Date
import sql_functions
from helpers.helpers import get_url

def dim_album_load(spotify, access_token, cdc_time):
    history = spotify.get_listening_history(access_token, cdc_time)['items']
    album_list = [play['track']['album'] for play in history]
    
    df_album = pd.DataFrame(album_list)
    df_album['cover_image_url'] = df_album['images'].apply(get_url)
    df_album = df_album.drop(columns=['href','uri','external_urls', 'images','artists','type'])
    df_album = df_album.drop_duplicates()
    df_album = df_album.rename(columns={'id':'album_id','name':'album_name'})
    
    metadata = MetaData()

    dim_album = Table(
        'DIM_ALBUM', metadata,
        Column('album_wid', Integer, primary_key=True, autoincrement=True),
        Column('album_id', String(62), nullable=False, unique=True),
        Column('album_type', String(20), nullable=False),
        Column('album_name', Text, nullable=False),
        Column('release_date', Date),
        Column('release_date_precision', String(20)),
        Column('total_tracks', Integer),
        Column('cover_image_url', Text)
    )
    
    sql_functions.save_to_sql(df_album, dim_album, key_cols = ['album_id'], wid = ['album_wid'], mode = 'upsert')
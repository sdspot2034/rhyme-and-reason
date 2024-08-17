import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer
import sql_functions

def bridge_album_artist_load(spotify, access_token, cdc_time):
    history = spotify.get_listening_history(access_token, cdc_time)['items']
    album_list = [play['track']['album'] for play in history]

    df_album = pd.DataFrame(album_list)
    df_album_map = df_album[['id','artists']]
    df_album_map = df_album_map.explode('artists')
    df_album_map['artist_id'] = df_album_map['artists'].apply(lambda x:x['id'])
    df_album_map = df_album_map.drop(columns=['artists'])
    
    dim_artist = sql_functions.read_from_sql('DIM_ARTIST')
    dim_album = sql_functions.read_from_sql('DIM_ALBUM')
    
    # Join with DIM_ARTIST, DIM_ALBUM to get ARTIST_WID, ALBUM_WID
    df_bridge_album_artist = df_album_map.merge(dim_artist, left_on='artist_id', right_on='spotify_id')
    df_bridge_album_artist = df_bridge_album_artist.merge(dim_album, left_on='id', right_on='album_id')
    df_bridge_album_artist = df_bridge_album_artist[['album_wid','artist_wid']]
    df_bridge_album_artist = df_bridge_album_artist.drop_duplicates()
    
    metadata = MetaData()

    bridge_album_artist = Table(
        'BRIDGE_ALBUM_ARTIST', metadata,
        Column('album_artist_map_wid', Integer, primary_key=True, autoincrement=True),
        Column('album_wid', Integer, nullable=False),
        Column('artist_wid', Integer, nullable=False)
    )
    
    sql_functions.save_to_sql(
        df_bridge_album_artist
        , bridge_album_artist
        , key_cols = ['album_wid', 'artist_wid']
        , wid = ['album_artist_map_wid']
        , mode = 'ignore'
    )
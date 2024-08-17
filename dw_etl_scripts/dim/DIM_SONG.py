import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer, String, BigInteger, Boolean, Text
import sql_functions

def dim_song_load(spotify, access_token, cdc_time):
    history = spotify.get_listening_history(access_token, cdc_time)['items']
    track_list = [play['track'] for play in history]
    
    dim_album = sql_functions.read_from_sql('DIM_ALBUM')
    
    df_songs = pd.DataFrame(track_list)
    df_songs = df_songs.explode('artists')
    df_songs['artist_id'] = df_songs['artists'].apply(lambda x: x['id'])
    df_songs['isrc_id'] = df_songs['external_ids'].apply(lambda x: x['isrc'])
    df_songs = df_songs.drop(columns=['href','uri','external_urls','artists','external_ids', 'artist_id', 'popularity'])
    df_songs['album_id'] = df_songs['album'].apply(lambda x:x['id'])
    df_songs = df_songs.merge(dim_album[['album_wid','album_id']], left_on='album_id', right_on='album_id')
    df_songs = df_songs.drop(columns=['album','album_id'])
    df_songs = df_songs.rename(columns={'id':'song_id'})
    df_songs = df_songs.drop_duplicates()
    
    metadata = MetaData()

    dim_song = Table(
        'DIM_SONG', metadata,
        Column('song_wid', Integer, primary_key=True, autoincrement=True),
        Column('song_id', String(62), nullable=False, unique=True),
        Column('album_wid', Integer),
        Column('disc_number', Integer),
        Column('duration_ms', BigInteger, nullable=False),
        Column('explicit', Boolean),
        Column('is_local', Boolean),
        Column('name', Text, nullable=False),
        Column('preview_url', Text),
        Column('track_number', Integer),
        Column('type', String(50)),
        Column('isrc_id', String(100))
    )
    
    sql_functions.save_to_sql(df_songs, dim_song, key_cols = ['song_id'], wid = ['song_wid'], mode = 'upsert')
    
    
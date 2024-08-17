import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime
import sql_functions

def fact_play_load(spotify, access_token, cdc_time):
    history = spotify.get_listening_history(access_token, cdc_time)['items']
    
    dim_song = sql_functions.read_from_sql('DIM_SONG')
    
    df_play = pd.DataFrame(history)
    df_play['song_id'] = df_play['track'].apply(lambda x:x['id'])
    df_play = df_play.merge(dim_song, 'left', on = 'song_id')
    df_play['context_playlist'] = df_play['context'].apply(lambda x:x['href'] if x and 'href' in x.keys() else None)
    df_play = df_play[['song_wid','played_at','context_playlist']]
    df_play['played_at'] = pd.to_datetime(df_play['played_at'])
    df_play['played_at'] = df_play['played_at'] + pd.Timedelta(hours=5, minutes=30)
    df_play['played_at'] = df_play['played_at'].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S.%f'))
    
    metadata = MetaData()

    # Define the FACT_PLAY table
    fact_play = Table(
        'FACT_PLAY', metadata,
        Column('play_wid', Integer, primary_key=True, autoincrement=True),
        Column('song_wid', Integer, nullable=False),
        Column('played_at', DateTime, nullable=False),
        Column('context_playlist', Text, nullable=False)
    )
    
    sql_functions.save_to_sql(
        df_play
        , fact_play
        , key_cols = ['song_wid','played_at']
        , wid = ['play_wid']
        , mode = 'append'
    )
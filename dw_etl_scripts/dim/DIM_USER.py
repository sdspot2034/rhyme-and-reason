import pandas as pd
from sqlalchemy import Table, MetaData, Column, Integer, String
import sql_functions
from helpers.helpers import get_url

def dim_user_load(spotify, access_token):
    user = [spotify.get_user_details(access_token)]
    
    df_user = pd.DataFrame(user)
    df_user['spotify_url'] = df_user['external_urls'].apply(lambda x:x['spotify'])
    df_user['profile_pic'] = df_user['images'].apply(get_url, args=[300])
    df_user = df_user[['display_name','type','country','product','spotify_url','profile_pic']]
    
    metadata = MetaData()

    # Define the dimension table schema
    dim_table = Table('DIM_USER', metadata,
        Column('user_wid', Integer, primary_key=True, autoincrement=True),
        Column('display_name', String(255), nullable=False, unique=True),
        Column('type', String(255)),
        Column('country', String(255)),
        Column('product', String(255)),
        Column('spotify_url', String(255)),
        Column('profile_pic', String(255))
    )
    
    sql_functions.save_to_sql(df_user, dim_table, key_cols=['spotify_url'], wid=['user_wid'], mode='upsert')
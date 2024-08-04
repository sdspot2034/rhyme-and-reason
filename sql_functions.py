import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
import json


with open('SQL_CREDENTIALS.json', 'r') as file:
    cred = json.loads(file.read())
    
user = cred['user']
pswd = cred['pass']
host = cred['host']
target_engine = create_engine(f'mysql+mysqlconnector://{user}:{pswd}@{host}:3306/spotify_db')


def save_to_sql(df, table, key_cols, mode, wid=None, other_cols=None):
    
    list_of_records = df.to_dict(orient='records')
    all_columns = table.columns
    
    if mode == 'upsert':
        insert_stmt = insert(table).values(list_of_records)
        update_columns = {c_name: insert_stmt.inserted[c_name] for c_name in all_columns if c_name not in key_cols}
        upsert_stmt = insert_stmt.on_duplicate_key_update(update_columns)
        
        with target_engine.connect() as connection:
            connection.execute(upsert_stmt)

    
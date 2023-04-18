import os
import json
import sqlite3
import pandas

def dir_to_json(path, exclude_folders=[]):
    data = {'name': os.path.basename(path), 'type': 'directory', 'children': []}
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and item not in exclude_folders:
            data['children'].append({'name': item, 'type': 'directory', 'children': dir_to_json(item_path, exclude_folders)})
        else:
            data['children'].append({'name': item, 'type': 'file'})
    return data['children']

def current_dir_to_json(exclude_folders=[]):
    current_dir = os.getcwd()
    return json.dumps(dir_to_json(current_dir, exclude_folders))

def open_database(db_name):
    """opens the master table and prints as a pandas dataframe"""
    with sqlite3.connect(db_name) as conn:
        df = pandas.read_sql_query("SELECT * FROM sqlite_master", conn)
    print(df)

if __name__ == '__main__':
    open_database('testing.db')
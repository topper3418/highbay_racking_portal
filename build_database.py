import pandas
from py_lib.sqlite_tools import Database
import os

with Database('test.db') as db:
    sql_path = os.path.join('sql', 'create_requests_table.sql')
    db.run_sql(sql_path)

# Sample data as a Pandas DataFrame
data = pandas.DataFrame({
    'type': ['Type A', 'Type B', 'Type C'],
    'submitter': ['John Doe', 'Jane Smith', 'Bob Johnson'],
    'submitted': ['2022-01-01 10:00:00', '2022-01-02 11:00:00', '2022-01-03 12:00:00'],
    'due_date': ['2022-02-01', '2022-02-02', '2022-02-03'],
    'due_date_reason': ['Reason A', 'Reason B', 'Reason C']
})

# Insert the data into the requests table
with Database('test.db') as db:
    db.insert_df('requests', data)
    

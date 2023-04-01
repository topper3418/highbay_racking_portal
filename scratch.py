from py_lib.sqlite_tools import Database

with Database('test.db') as db:
    new_row = {'type': 'Type F', 
               'submitter': 'ga4 douche',
               'submitted': '2022-04-02 14:00:00', 
               'due_date': '2023-04-02', 
               'due_date_reason': 'fuck you again'}
    db.insert_row('requests', new_row)

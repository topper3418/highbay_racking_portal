# ok we are going to create a brand new database  file
from data.db import database
db = database('testing.db')
# then we add data to the lookup tables
def zip_org_dict(org, description):
    org_headers = ['org', 'description']
    return dict(zip(org_headers, [org, description]))
org_lines = [('Production Control')]
# then we access data in the lookup tables
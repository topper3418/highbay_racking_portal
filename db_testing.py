import sys
import os
sys.path.append("..") 
import data.db
# define the database name
db_name = 'testing.db'
# remove the database if it exists so we start fresh
if os.path.exists(db_name):
    os.remove(db_name)
# create the database object
db = data.db.database(db_name)
# create database file and tables
db.build_db()
# then we add data to the org table
db.default_insert('orgs', ['my org', 'the organization that the portal is for'])
db.default_insert('orgs', ['internal org 1', 'an organization we frequently work with'])
db.default_insert('orgs', ['internal org 2', 'another organization we frequently work with'])
db.default_insert('orgs', ['internal org 3', 'yet another organization we frequently work with'])
db.default_insert('orgs', ['vendor 1', 'a vendor we work with'])
db.default_insert('orgs', ['vendor 2', 'another vendor we work with'])
db.default_insert('orgs', ['vendor 3', 'yet another vendor we work with'])
# now we add some people
db.default_insert('people', ['Me', 1])
db.default_insert('people', ['My wife', 1])
db.default_insert('people', ['My intern', 1])
db.default_insert('people', ['My boss', 1])
db.default_insert('people', ['My coworker', 2])
db.default_insert('people', ['Another coworker', 2])
db.default_insert('people', ['A bad coworker', 3])
db.default_insert('people', ['The worst coworker', 4])
db.default_insert('people', ['A vendor owner', 5])
db.default_insert('people', ['A vendor AM', 5])
db.default_insert('people', ['A vendor contact', 5])
db.default_insert('people', ['A vendor engineer', 6])
db.default_insert('people', ['A vendor salesman', 6])
# now we add some roles
db.default_insert('roles', ['owner', 'the owner of the portal'])
db.default_insert('roles', ['admin', 'an administrator of the portal'])
db.default_insert('roles', ['user', 'a user of the portal'])
db.default_insert('roles', ['guest', 'a guest of the portal'])
# now we add some permissions
db.default_insert('role_permissions', ['read', 'read access to the portal'])
db.default_insert('role_permissions', ['make_ticket', 'create a ticket in the portal'])
db.default_insert('role_permissions', ['edit_ticket', 'edit a ticket in the portal'])
db.default_insert('role_permissions', ['delete_ticket', 'delete a ticket in the portal'])
db.default_insert('role_permissions', ['comment', 'create a comment in the portal'])
# then we access data in the lookup tables
print(db.show_tables())
print()
print(db.read_table('orgs'))
print()
print(db.read_table('people'))
print()
print(db.read_table('roles'))
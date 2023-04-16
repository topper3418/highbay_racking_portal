# normally import * is a bad idea, but in this case this is mostly an extension of sqlite_tools
from sqlite_tools import *

orgs = LookupTable('orgs')
# TODO: add data to the table for a default org
people = SQLiteTable('people',
                     [PrimaryKeyColumn(),
                      NameColumn('name'),
                      TextColumn('email'),
                      TextColumn('phone'),
                      IntColumn('org_id', foreign_key=orgs.link, is_not_null=True)])
# TODO: add data to the table for a default user SuperUser
roles = LookupTable('roles')
# TODO: add data to the table for a default database admin role
user_groups = LookupTable('user_groups')
# TODO: add data to the table for a default database admin role
user_roles = SQLiteTable('user_roles',
                         [IntColumn('user_group_id', foreign_key=user_groups.link, is_not_null=True),
                          IntColumn('role_id', foreign_key=roles.link, is_not_null=True)])
# TODO: add data to the table for a default user SuperUser with role database admin
users = SQLiteTable('users',
                    [PrimaryKeyColumn(),
                     NameColumn('username'),
                     TextColumn('password', is_not_null=True),
                     IntColumn('role_id', foreign_key=roles.link),
                     IntColumn('person_id', foreign_key=people.link, is_unique=True, is_not_null=True),
                     IntColumn('user_type_id', foreign_key=user_groups.link, is_not_null=True)])
# TODO: add a default admin user, make a superuser
equipment_types = LookupTable('equipment_types')
# TODO: add a default equipment type, call it a doodad
# TODO: link the doodad to the ticket link, thats the minimum requirement for a doodad
equipment = SQLiteTable('equipment',
                        [PrimaryKeyColumn(),
                         NameColumn('equipment_name'),
                         TextColumn('description', is_not_null=True),
                         DateColumn('created', is_not_null=True),
                         IntColumn('creator', foreign_key=users.link, is_not_null=True),
                         IntColumn('owner', foreign_key=users.link, is_not_null=True),
                         IntColumn('equipment_type_id', foreign_key=equipment_types.link, is_not_null=True)])
equipment_history = SQLiteTable('equipment_history',
                                [PrimaryKeyColumn(),
                                 TextColumn('field_name', is_not_null=True),
                                 TextColumn('old_value', is_not_null=True),
                                 TextColumn('new_value', is_not_null=True)])
# TODO: create a trigger to add a row to equipment_history when a row in equipment is updated (thatll be a whole class)
equipment_change_types = LookupTable('equipment_change_types')
# TODO: create a default equipment change type, call it add
equipment_change_statuses = LookupTable('equipment_change_statuses')
# TODO: create a default equipment change status, call it pending
equipment_change_requirements = LookupTable('equipment_change_requirements')
# TODO: add a default requirement, call it a ticket_link
equipment_requirements = SQLiteTable('equipment_change_requirements',
                                     [IntColumn('equipment_type_id', foreign_key=equipment_types.link, is_not_null=True),
                                      IntColumn('requirement_id', foreign_key=equipment_change_requirements.link, is_not_null=True)])
equipment_changes = SQLiteTable('equipment_changes',
                                [PrimaryKeyColumn(),
                                 TextColumn('description', is_not_null=True),
                                 IntColumn('equipment_id', foreign_key=equipment.link, is_not_null=True),
                                 IntColumn('change_type_id', foreign_key=equipment_change_types.link, is_not_null=True),
                                 IntColumn('change_status_id', foreign_key=equipment_change_statuses.link, is_not_null=True)])
attachment_types = LookupTable('attachment_types')
equipment_change_comments = SQLiteTable('equipment_change_attachments',
                                        [PrimaryKeyColumn(),
                                         IntColumn('equipment_change_id', foreign_key=equipment_changes.link, is_not_null=True),
                                         IntColumn('attachment_type_id', foreign_key=attachment_types.link, is_not_null=True),
                                         TextColumn('attachment_value', is_not_null=True),
                                         TextColumn('comment', is_not_null=True)])
ticket_types = LookupTable('ticket_types')
# TODO: add a default ticket type, call it a new doodad
ticket_status =  LookupTable('ticket_status')
# TODO: add a default ticket status, call it new
tickets = SQLiteTable('tickets',
                        [PrimaryKeyColumn(),
                        NameColumn('ticket_name'),
                        TextColumn('description', is_not_null=True),
                        IntColumn('ticket_type_id', foreign_key=ticket_types.link, is_not_null=True),
                        DateColumn('created', is_not_null=True),
                        IntColumn('created_by', foreign_key=people.link, is_not_null=True),
                        IntColumn('status_id', foreign_key=ticket_status.link, is_not_null=True),
                        IntColumn('owner_id', foreign_key=users.link)])
attachments = SQLiteTable('attachments',
                            [PrimaryKeyColumn(),
                            NameColumn('attachment_name'),
                            IntColumn('ticket_id', foreign_key=tickets.link, is_not_null=True),
                            IntColumn('created_by', foreign_key=users.link, is_not_null=True),
                            NameColumn('file_name'),
                            DateColumn('created', is_not_null=True)])

tables = [orgs, 
          people, 
          roles, 
          user_roles, 
          users, 
          equipment_types, 
          requirements, 
          equipment_requirements, 
          equipment, 
          equipment_history, 
          equipment_change_types, 
          equipment_change_statuses, 
          equipment_changes, 
          equipment_change_comments, 
          ticket_types, 
          ticket_status, 
          tickets, 
          attachments]

def database(filepath):
    db = SQLiteDatabase(filepath, tables)
    return db
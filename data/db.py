# normally import * is a bad idea, but in this case this is mostly an extension of sqlite_tools
from data.sqlite_tools import *
import sys
sys.path.append("..")

orgs = LookupTable('orgs')
people = SQLiteTable('people',
                     [PrimaryKeyColumn(),
                      NameColumn('name'),
                      TextColumn('email'),
                      TextColumn('phone'),
                      IntColumn('org_id', foreign_key=orgs.link, is_not_null=True)])
roles = LookupTable('roles')
role_permissions = LookupTable('role_permissions')
role_permission_lookup = SQLiteTable('role_permission_lookup',
                         [IntColumn('permission_id', foreign_key=role_permissions.link, is_not_null=True),
                          IntColumn('role_id', foreign_key=roles.link, is_not_null=True)])
users = SQLiteTable('users',
                    [PrimaryKeyColumn(),
                     NameColumn('username'),
                     TextColumn('password', is_not_null=True),
                     IntColumn('person_id', foreign_key=people.link,
                               is_unique=True, is_not_null=True),
                     IntColumn('role_id', foreign_key=roles.link, is_not_null=True)])
equipment_types = LookupTable('equipment_types')
equipment = SQLiteTable('equipment',
                        [PrimaryKeyColumn(),
                         NameColumn('equipment_name'),
                         TextColumn('description', is_not_null=True),
                         DateColumn('created', is_not_null=True),
                         IntColumn('creator', foreign_key=users.link,
                                   is_not_null=True),
                         IntColumn('owner', foreign_key=users.link,
                                   is_not_null=True),
                         IntColumn('equipment_type_id', foreign_key=equipment_types.link, is_not_null=True)])
equipment_history = SQLiteTable('equipment_history',
                                [PrimaryKeyColumn(),
                                 TextColumn('field_name', is_not_null=True),
                                 TextColumn('old_value', is_not_null=True),
                                 TextColumn('new_value', is_not_null=True)])
equipment_change_types = LookupTable('equipment_change_types')
equipment_change_statuses = LookupTable('equipment_change_statuses')
equipment_change_requirements = LookupTable('equipment_change_requirements')
equipment_requirements = SQLiteTable('equipment_change_requirements',
                                     [IntColumn('equipment_type_id', foreign_key=equipment_types.link, is_not_null=True),
                                      IntColumn('requirement_id', foreign_key=equipment_change_requirements.link, is_not_null=True)])
equipment_changes = SQLiteTable('equipment_changes',
                                [PrimaryKeyColumn(),
                                 TextColumn('description', is_not_null=True),
                                 IntColumn(
                                     'equipment_id', foreign_key=equipment.link, is_not_null=True),
                                 IntColumn(
                                     'change_type_id', foreign_key=equipment_change_types.link, is_not_null=True),
                                 IntColumn('change_status_id', foreign_key=equipment_change_statuses.link, is_not_null=True)])
attachment_types = LookupTable('attachment_types')
equipment_change_comments = SQLiteTable('equipment_change_attachments',
                                        [PrimaryKeyColumn(),
                                         IntColumn(
                                             'equipment_change_id', foreign_key=equipment_changes.link, is_not_null=True),
                                         IntColumn(
                                             'attachment_type_id', foreign_key=attachment_types.link, is_not_null=True),
                                         TextColumn(
                                             'attachment_value', is_not_null=True),
                                         TextColumn('comment', is_not_null=True)])
ticket_types = LookupTable('ticket_types')
ticket_status = LookupTable('ticket_status')
tickets = SQLiteTable('tickets',
                      [PrimaryKeyColumn(),
                       NameColumn('ticket_name'),
                       TextColumn('description', is_not_null=True),
                       IntColumn(
                           'ticket_type_id', foreign_key=ticket_types.link, is_not_null=True),
                       DateColumn('created', is_not_null=True),
                       IntColumn('created_by', foreign_key=people.link,
                                 is_not_null=True),
                       IntColumn(
                           'status_id', foreign_key=ticket_status.link, is_not_null=True),
                       IntColumn('owner_id', foreign_key=users.link)])
attachments = SQLiteTable('attachments',
                          [PrimaryKeyColumn(),
                           TextColumn('attachment_name', is_not_null=True),
                           IntColumn(
                               'ticket_id', foreign_key=tickets.link, is_not_null=True),
                           IntColumn('created_by',
                                     foreign_key=users.link, is_not_null=True),
                           NameColumn('file_name'),
                           DateColumn('created', is_not_null=True)])

tables = [orgs,
          people,
          roles,
          role_permissions,
          users,
          equipment_types,
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

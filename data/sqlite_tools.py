from __future__ import annotations
import sqlite3
import pandas
import os
from datetime import datetime
from dataclasses import dataclass, field

from typing import Any, Optional, List

def script_path(script_name, folder=None):
    if folder is None:
        return os.path.join(os.path.dirname(__file__), 'sql', script_name)
    else:
        return os.path.join(os.path.dirname(__file__), 'sql', folder, script_name)


class SqlConnectionBase:
    
    def __init__(self, db_path):
        self.db_path = db_path
        # raise exception if the directory does not exist
        if not os.path.isdir(os.path.dirname(self.db_path)):
            raise ValueError(f"{self.db_path} is not a valid path")
        self.conn = None
        self.cursor = None
        return os.path.isfile(self.db_path)
        
    # dunder methods for using context manager to connect to the database
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            
    # general method for writing to the database
    def run_cmd(self, sql_query: str):
        with self as db:
            db.cursor.execute(sql_query)
            
    # run a command with params
    def run_cmd_params(self, sql_query: str, params: dict):
        with self as db:
            db.cursor.execute(sql_query, params)
            
    # general method for reading from the database
    def get_data(self, sql_query: str):
        with self as db:
            return pandas.read_sql_query(sql_query, db.conn)
    
    # getter method to get the tables in the database
    def get_tables(self) -> pandas.DataFrame:
        sql = "SELECT * FROM sqlite_master WHERE type='table' ORDER BY name;"
        return self.get_data(sql)
        
    # getter method to get the views in the database
    def get_views(self) -> pandas.DataFrame:
        sql = "SELECT * FROM sqlite_master WHERE type='view' ORDER BY name;"
        return self.get_data(sql)
    
    # method for running sql scripts
    def run_sql_script(self, sql_file: str):
        with open(sql_file) as f:
            sql = f.read()
        self.run_cmd(sql)
    
    # method for running sql scripts with multiple commands
    def run_sql_script_multi(self, sql_file: str):
        with open(sql_file) as f:
            sql = f.read()
        for cmd in sql.split(';'):
            self.run_cmd(cmd)
        
    # getter method to get the description of a table or view
    def get_description(self, table_name: str) -> pandas.DataFrame:
        sql = f"PRAGMA table_info({table_name})"
        return self.get_data(sql)

class AppData(SqlConnectionBase):
    """Class for managing the sqlite connection to the app database
    """
    # when initialized, it will connect to the database, get values from it
    def __init__(self, db_path):
        super().__init__(db_path)
        if not os.path.isfile(self.db_path):
            self.build_database()
    
    def build_database(self):
        # create the database
        tables = [
            'roles',
            'users',
            'ticket_types', 
            'ticket_status',
            'equipment_status',
            'due_date_reasons',
            'orgs', 
            'contacts',
            'tickets',
            'ticket_comments',
            'ticket_attachments',
            'ticket_history',
            'equipment',
            'equipment_history'
        ]
        triggers = [
            'equipment_history_insert',
            'equipment_history_update_status',
            'equipment_history_update_pc_owner',
            'equipment_history_update_external_owner',
            'equipment_history_update_location',
            'tickets_history_insert',
            'tickets_history_update_type_id',
            'tickets_history_update_due_date',
            'tickets_history_update_due_date_reason_id',
            'tickets_history_update_status_id',
            'tickets_history_update_owner_id'
        ]
        views = [
            'all_tickets_view'
        ]
        for table in tables:
            print(f'Creating table {table}...')
            self.run_sql_script(script_path(f'{table}.sql', 'table_ddls'))
        for trigger in triggers:
            print(f'Creating trigger {trigger}...')
            self.run_sql_script(script_path(f'{trigger}.sql', 'trigger_ddls'))
        for view in views:
            print(f'Creating view {view}...')
            self.run_sql_script(script_path(f'{view}.sql', 'view_ddls'))

class DbTableBase(SqlConnectionBase):
    """Base class for all database tables
    """
    def __init__(self, db_path, table_name: str):
        super().__init__(db_path)
        self.table_name = table_name
        self.description = self.get_description()   
    
    def get_description(self) -> pandas.DataFrame:
        return super().get_description(self.table_name) 
    
    def default_insert(self, params: dict) -> None:
        """inserts a row into the table with the given params

        Args:
            params (dict): _description_
        """
        headers = params.keys()
        sql = f"""INSERT INTO {self.table_name} 
                    ({', '.join(headers)}) 
                  VALUES 
                    ({', '.join([f':{header}' for header in headers])})"""
        print(f'Running SQL: {sql} with params: {params}')
        self.run_cmd_params(sql, params)
    
    def fetch_100(self, sql=None) -> pandas.DataFrame:
        """returns the first 100 rows from the requests table where the endtime is less than the given endtime

        Args:
            endtime (datetime): _description_

        Returns:
            pandas.DataFrame: _description_
        """
        if sql is None:
            sql = f"SELECT * FROM {self.table_name} LIMIT 100"
        
        return self.get_data(sql)

class Tickets(DbTableBase):
    """represents the requests table in the database
    """
    # takes in the app data object to do all db transactions
    # this will be the only class that interacts with the requests table.
    # if other classes need to interact with the requests table, they will
    # do so through this class
    def __init__(self, db_path):
        super().__init__(db_path, 'tickets')
        self.view_name = 'all_tickets_view'
        
    def fetch_100(self, endtime: datetime = datetime.now()) -> pandas.DataFrame:
        sql = f"""SELECT * FROM {self.view_name}
                  WHERE submitted < {endtime.timestamp()}
                  LIMIT 100"""
        return super().fetch_100(sql)
    
class Roles(DbTableBase):
    """represents the roles table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'roles')
        
    def insert(self, new_role: str, new_description) -> None:
        params = {
            'role': new_role,
            'description': new_description
        }
        super().default_insert(params)
    
    def dropdown(self) -> pandas.DataFrame:
        return self.get_data(f"SELECT id, role as text FROM {self.table_name}")
    
class Users(DbTableBase):
    """represents the users table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'users')
    
    def insert(self, new_username: str, new_password: str, new_role: int) -> None:
        params = {
            'username': new_username,
            'password': new_password,
            'role': new_role
        }
        super().default_insert(params)
        
class TicketTypes(DbTableBase):
    """represents the ticket_types table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'ticket_types')
    
    def insert(self, new_type: str, new_description) -> None:
        params = {
            'type': new_type,
            'description': new_description
        }
        super().default_insert(params)
        
    def dropdown(self) -> pandas.DataFrame:
        return self.get_data(f"SELECT id, type as text FROM {self.table_name}")
    
class TicketStatus(DbTableBase):
    """represents the ticket_status table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'ticket_status')
    
    def insert(self, new_status: str, new_description) -> None:
        params = {
            'status': new_status,
            'description': new_description
        }
        super().default_insert(params)
        
    def dropdown(self) -> pandas.DataFrame:
        return self.get_data(f"SELECT id, status as text FROM {self.table_name}")
    
class EquipmentStatus(DbTableBase):
    """represents the equipment_status table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'equipment_status')
    
    def insert(self, new_status: str, new_description) -> None:
        params = {
            'status': new_status,
            'description': new_description
        }
        super().default_insert(params)
        
    def dropdown(self) -> pandas.DataFrame:
        return self.get_data(f"SELECT id, status as text FROM {self.table_name}")
    
class DueDateReason(DbTableBase):
    """represents the due_date_reason table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'due_date_reasons')
        
    def insert(self, new_reason: str, new_description) -> None:
        params = {
            'reason': new_reason,
            'description': new_description
        }
        super().default_insert(params)
        
    def dropdown(self) -> pandas.DataFrame:
        return self.get_data(f"SELECT id, reason as text FROM {self.table_name}")
    
class Orgs(DbTableBase):
    """represents the vendors table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'orgs')
        
    def insert(self, new_vendor_name, new_vendor_description, internal: bool):
        """inserts a new vendor into the vendors table"""
        params = {
            'name': new_vendor_name,
            'description': new_vendor_description,
            'internal': int(internal)
        }
        super().default_insert(params)
        
    def dropdown(self, internal: bool) -> pandas.DataFrame:
        return self.get_data(f"SELECT id, name as text FROM {self.table_name} WHERE internal = {int(internal)}")

class Contacts(DbTableBase):
    """represents the contacts table in the database
    """
    def __init__(self, db_path):
        super().__init__(db_path, 'contacts')
        
    def insert(self, new_contact_name, new_contact_phone, new_contact_email, new_contact_department):
        """inserts a new contact into the contacts table"""
        params = {
            'name': new_contact_name,
            'phone': new_contact_phone,
            'email': new_contact_email,
            'org_id': new_contact_department,
        }
        super().default_insert(params)
        
    def dropdown(self) -> pandas.DataFrame:
        sql = f"SELECT id, c.name || ' - ' || o.name as text FROM contacts c JOIN orgs o ON c.org_id = o.id"
        return self.get_data(sql)
    




# I am now going to experiment with an object oriented way to interface with sqlite. 
# the idea is to make a dataclass for each type of variable, and then make objects I can 
# assemble into a table. The tables then get fed into a database object that can build
# the database and tables. During runtime the same object can be used to interact with
# the database. This should make changine the database more intuitive 

@dataclass
class SQLiteColumn:
    name: str
    data_type: str
    is_primary_key: bool = False
    is_autoincrement: bool = False
    is_not_null: bool = False
    default_value: Optional[Any] = None
    is_unique: bool = False
    check_constraint: Optional[str] = None
    foreign_key: Optional[ForeignKey] = field(default=None, repr=False, compare=False)
    table: Optional['SQLiteTable'] = field(default=None, repr=False, compare=False)

    def __str__(self) -> str:
        return f"{self.name} ({self.data_type})"

    def render_read_sql(self) -> str:
        if self.data_type.upper() == "INTEGER" and "unixtime" in self.name.lower():
            return f"strftime('%Y-%m-%d %H:%M:%S', {self.name}, 'unixepoch') AS {self.name}"
        return self.name

    def get_python_type(self) -> type:
        data_type_mapping = {
            "INTEGER": int,
            "REAL": float,
            "TEXT": str,
            "BLOB": bytes
        }
        return data_type_mapping.get(self.data_type.upper(), None)

@dataclass
class ForeignKey:
    target_column: SQLiteColumn
    on_delete: Optional[str] = None
    on_update: Optional[str] = None

class SQLiteTable:
    def __init__(self, name: str, 
                       columns: List[SQLiteColumn], 
                       primary_key: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.primary_key = primary_key
        self.foreign_keys = self._gather_foreign_keys()

    def __str__(self) -> str:
        return f"Table: {self.name} ({', '.join(str(col) for col in self.columns)})"

    def _gather_foreign_keys(self) -> List[str]:
        foreign_keys = []
        for column in self.columns:
            if column.foreign_key is not None:
                foreign_keys.append(str(column.foreign_key))
        return foreign_keys

    def render_ddl(self) -> str:
        column_definitions = []

        for column in self.columns:
            column_parts = [column.name, column.data_type]

            if column.is_primary_key:
                column_parts.append("PRIMARY KEY")
                if column.is_autoincrement:
                    column_parts.append("AUTOINCREMENT")

            if column.is_not_null:
                column_parts.append("NOT NULL")

            if column.default_value is not None:
                default_value_str = f"DEFAULT {column.default_value}"
                if isinstance(column.default_value, str):
                    default_value_str = f"DEFAULT '{column.default_value}'"
                column_parts.append(default_value_str)

            if column.is_unique:
                column_parts.append("UNIQUE")

            if column.check_constraint is not None:
                column_parts.append(f"CHECK({column.check_constraint})")

            column_definitions.append(" ".join(column_parts))

        if self.primary_key is not None:
            primary_key_constraint = f"PRIMARY KEY({self.primary_key})"
            column_definitions.append(primary_key_constraint)

        # Add foreign key constraints
        for fk in self.foreign_keys:
            constraint_parts = [f"FOREIGN KEY({fk.source_column}) REFERENCES {fk.target_column.table.name}({fk.target_column.name})"]

            if fk.on_delete is not None:
                constraint_parts.append(f"ON DELETE {fk.on_delete}")

            if fk.on_update is not None:
                constraint_parts.append(f"ON UPDATE {fk.on_update}")

            column_definitions.append(" ".join(constraint_parts))

        columns_ddl = ", ".join(column_definitions)
        return f"CREATE TABLE {self.name} ({columns_ddl});"

@dataclass
class PrimaryKeyColumn(SQLiteColumn):
    def __init__(self):
        super().__init__(
            name="id",
            data_type="INTEGER",
            is_primary_key=True,
            is_autoincrement=True,
            is_not_null=True,
        )   

@dataclass
class DateColumn(SQLiteColumn):
    def __init__(self, name: str, 
                       is_not_null: bool = False, 
                       default_value: Optional[Any] = None, 
                       check_constraint: Optional[str] = None):
        super().__init__(
            name=name,
            data_type="INTEGER",
            is_not_null=is_not_null,
            default_value=default_value,
            check_constraint=check_constraint,
        )

    def render_read_sql(self) -> str:
        return f"strftime('%Y-%m-%d %H:%M:%S', {self.name}, 'unixepoch') AS {self.name}"

    def get_python_type(self) -> type:
        return datetime.datetime
    
@dataclass
class NameColumn(SQLiteColumn):
    def __init__(self, name: str, 
                       check_constraint: Optional[str] = None):
        super().__init__(
            name=name,
            data_type="TEXT",
            is_autoincrement=False,
            is_not_null=True,
            is_unique=True,
            check_constraint=check_constraint,
        )

    def get_python_type(self) -> type:
        return str
        
if __name__ == '__main__':
    table = SQLiteTable('dope_ass_table', 
                        [PrimaryKeyColumn(),
                         NameColumn('name'),
                         DateColumn('created_time'),
                         SQLiteColumn('random_value', 'TEXT')],
                        primary_key='id')
    print(table.render_ddl())
    
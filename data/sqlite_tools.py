from __future__ import annotations
from ast import Dict
import pandas
import sqlite3
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
    foreign_key: Optional[ForeignKey] = field(
        default=None, repr=False, compare=False)
    table: Optional['SQLiteTable'] = field(
        default=None, repr=False, compare=False)
    # this is not a sqlite clumn, but a convenience for the table object
    is_name_column: bool = False

    def __str__(self) -> str:
        return f"{self.name} ({self.data_type})"

    def render_read_sql(self) -> str:
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
    """I will only ever have foreign keys be referencing primary keys, therefore these can point at 
    tables. """
    referenced_table: SQLiteTable
    on_delete: Optional[str] = None
    on_update: Optional[str] = None


class SQLiteTable:
    def __init__(self, name: str,
                 columns: List[SQLiteColumn]):
        self.name = name
        self.columns = columns
        self.colnames = [col.name for col in self.columns]
        self.primary_keys = [
            col.name for col in self.columns if col.is_primary_key]
        self.foreign_keys = [(col.name, col.foreign_key)
                             for col in self.columns 
                             if col.foreign_key is not None]
        self.validate()

    def validate(self) -> None:
        """checks all inputs and raises errors if something is wrong"""
        # first make sure there's only one name column
        name_columns = [col.name for col in self.columns if col.is_name_column]
        if len(name_columns) > 1:
            raise ValueError(
                f"Table {self.name} has more than one name column: {', '.join(name_columns)}")

    def __str__(self) -> str:
        return f"Table: {self.name} ({', '.join(str(col) for col in self.columns)})"

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

        # Add primary key constraints
        for pk in self.primary_keys:
            column_definitions.append(f"PRIMARY KEY({pk})")

        # Add foreign key constraints
        for colname, foreign_key in self.foreign_keys:
            # again, all primary keys are id in this db
            constraint_parts = [
                f"FOREIGN KEY({colname}) REFERENCES {foreign_key.referenced_table.name}(id)"]

            if foreign_key.on_delete is not None:
                constraint_parts.append(f"ON DELETE {foreign_key.on_delete}")

            if foreign_key.on_update is not None:
                constraint_parts.append(f"ON UPDATE {foreign_key.on_update}")

            column_definitions.append(" ".join(constraint_parts))

        columns_ddl = ", ".join(column_definitions)
        return f"CREATE TABLE {self.name} ({columns_ddl});"

    def render_insert_sql(self, data: Dict[str, Any]) -> str:
        """data is a dictionary of column names and values"""
        columns = []
        values = []
        for column in self.columns:
            if column.name in data:
                columns.append(column.name)
                value = data[column.name]
                if isinstance(value, str):
                    value = f"'{value}'"
                values.append(str(value))

        columns_ddl = ", ".join(columns)
        values_ddl = ", ".join(values)
        return f"INSERT INTO {self.name} ({columns_ddl}) VALUES ({values_ddl});"

    def render_read_sql(self, col_list: Optional[List[str]]=None, max_rows=100) -> str:
        if col_list is None:
            col_list = self.colnames
        columns_ddl = ", ".join(col.render_read_sql() for col in self.columns if col.name in col_list)
        return f"SELECT {columns_ddl} FROM {self.name} LIMIT {max_rows};"

    @property
    def link(self) -> ForeignKey:
        return ForeignKey(referenced_table=self)


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
class TextColumn(SQLiteColumn):
    def __init__(self, name: str,
                 is_not_null: bool = False,
                 is_unique: bool = False,
                 check_constraint: Optional[str] = None):
        super().__init__(
            name=name,
            data_type="TEXT",
            is_not_null=is_not_null,
            is_unique=is_unique,
            is_autoincrement=False,
            check_constraint=check_constraint,
        )

    def get_python_type(self) -> type:
        return str


@dataclass
class NameColumn(TextColumn):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            is_not_null=True,
            is_unique=True,
            check_constraint="length(name) > 0"
        )


@dataclass
class IntColumn(SQLiteColumn):
    def __init__(self, name: str,
                 is_not_null: bool = False,
                 is_unique: bool = False,
                 default_value: Optional[Any] = None,
                 foreign_key: Optional[ForeignKey] = None,
                 check_constraint: Optional[str] = None):
        super().__init__(
            name=name,
            data_type="INTEGER",
            is_not_null=is_not_null,
            is_unique=is_unique,
            foreign_key=foreign_key,
            default_value=default_value,
            check_constraint=check_constraint,
        )


@dataclass
class BoolColumn(SQLiteColumn):
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

    def get_python_type(self) -> type:
        return bool


class SQLiteDatabase:
    def __init__(self, filename: str, tables: List[SQLiteTable]):
        self.filename = filename
        self.tables = tables
        self.table_dict = {table.name: table for table in self.tables}
        
    def __getitem__(self, table_name: str) -> SQLiteTable:
        return self.table_dict[table_name]
        
    def build_db(self):
        with sqlite3.connect(self.filename) as conn:
            for table in self.tables:
                conn.execute(table.render_ddl())
        
    def run_sql_query(self, sql_query):
        with sqlite3.connect(self.filename) as conn:
            return pandas.read_sql(sql_query, conn)
        
    def run_sql_command(self, sql_command):
        with sqlite3.connect(self.filename) as conn:
            conn.execute(sql_command)
    
    def read_table(self, table_name, max_rows=100):
        if not table_name in self.table_dict:
            raise ValueError(f"Table {table_name} does not exist")
        return self.run_sql_query(self[table_name].render_read_sql(max_rows=max_rows))
    
    def insert_into(self, table_name: str, values: Dict[str, Any]):
        if not table_name in self.table_dict:
            raise ValueError(f"Table {table_name} does not exist")
        return self.run_sql_command(self[table_name].render_insert_sql(values)) 


class LookupTable(SQLiteTable):
    def __init__(self, name: str,
                 columns: Optional[List[SQLiteColumn]] = None):
        
        self.name = name
        self.columns = [PrimaryKeyColumn(),
                        NameColumn(name[:-1]),
                        TextColumn('description')]
        if columns is not None:
            self.columns.extend(columns)
        self.colnames = [col.name for col in self.columns]
        self.primary_keys = [col.name for col in self.columns if col.is_primary_key]
        self.foreign_keys = [(col.name, col.foreign_key) 
                             for col in self.columns 
                             if col.foreign_key is not None]
    

if __name__ == '__main__':
    pass
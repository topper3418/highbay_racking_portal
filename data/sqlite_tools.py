from __future__ import annotations
from ast import Dict, Tuple
import pandas
import sqlite3
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional, List, Tuple
import logging

sql_logger = logging.getLogger("sql_logs")
# this logger will log to a file, date and then message
file_handler = logging.FileHandler('sql_logs.log')
formatter = logging.Formatter('%(asctime)s:%(message)s')
file_handler.setFormatter(formatter)
sql_logger.addHandler(file_handler)
sql_logger.setLevel(logging.DEBUG)

def script_path(script_name, folder=None):
    if folder is None:
        return os.path.join(os.path.dirname(__file__), 'sql', script_name)
    else:
        return os.path.join(os.path.dirname(__file__), 'sql', folder, script_name)


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

    # this method will be called by the table object. Use case: can automatically render a datetime
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
    
    def render_value(self, value: Any) -> str:
        """returns a string that can be used in an insert statement"""
        if self.data_type.upper() == "TEXT":
            return f"'{value}'"
        else:
            return str(value)


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
        name_column_name = [col.name for col in self.columns if col.is_name_column]
        self.name_column_name = name_column_name[0] if name_column_name else None
        self.validate_self()

    def validate_self(self) -> None:
        """checks all inputs and raises errors if something is wrong"""
        # first make sure there's only one name column
        name_columns = [col.name for col in self.columns if col.is_name_column]
        if len(name_columns) > 1:
            raise ValueError(
                f"Table {self.name} has more than one name column: {', '.join(name_columns)}")
        # then make sure all column names are unique
        if len(self.colnames) != len(set(self.colnames)):
            raise ValueError(
                f"Table {self.name} has duplicate column names: {', '.join(self.colnames)}")

    def validate_colname(self, colname: str) -> None:
        if colname not in self.colnames:
            raise ValueError(
                f"Column {colname} not found in table {self.name}.")

    def validate_insert_dict(self, insert_dict: Dict[str, Any]) -> None:
        """checks that all keys in the insert dict are valid column names"""
        for key, value in insert_dict.items():
            self.validate_colname(key)
            data_type = self[key].get_python_type()
            if not isinstance(value, data_type):
                raise ValueError(f"Value {value} is not of type {data_type}")
            
    def __getitem__(self, key: str) -> SQLiteColumn:
        ii = self.colnames.index(key)
        return self.columns[ii]

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
        # first make sure all columns are in the data
        self.validate_insert_dict(data) 
        # dictionary keys are the column  names
        columns = [colname for colname in data.keys()]
        values = []
        for column in columns:
            value = self[column].render_value(data[column])
            values.append(value)

        columns_ddl = ", ".join(columns)
        values_ddl = ", ".join(values)
        return f"INSERT INTO {self.name} ({columns_ddl}) VALUES ({values_ddl});"

    def render_default_insert(self, values: List[Any]) -> str:
        """calls the render_insert_sql with the not_null columns, 
        not including the primary key"""
        colnames = [col.name for col in self.columns if col.is_not_null and not col.is_primary_key]
        # first make sure the default values match the number of default values
        if len(colnames) != len(values):
            raise ValueError(f"Number of values {len(values)} does not match number of columns {len(colnames)}")
        insert_dict = dict(zip(colnames, values))
        # then render the insert statement
        return self.render_insert_sql(insert_dict) 

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
                 check_constraint: Optional[str] = None,
                 is_name_column: bool = False):
        super().__init__(
            name=name,
            data_type="TEXT",
            is_not_null=is_not_null,
            is_unique=is_unique,
            is_autoincrement=False,
            check_constraint=check_constraint,
            is_name_column=is_name_column,
        )


@dataclass
class NameColumn(TextColumn):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            is_not_null=True,
            is_unique=True,
            is_name_column=True
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
                 default_value: Optional[bool] = None,
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
                table_ddl = table.render_ddl()
                sql_logger.debug(f"running sql command: {table_ddl}")
                conn.execute(table_ddl)
        
    def run_sql_query(self, sql_query):
        sql_logger.debug(f"running sql query: {sql_query}")
        with sqlite3.connect(self.filename) as conn:
            return pandas.read_sql(sql_query, conn)
        
    def run_sql_command(self, sql_command):
        sql_logger.debug(f"running sql command: {sql_command}")
        with sqlite3.connect(self.filename) as conn:
            conn.execute(sql_command)
    
    def read_table(self, table_name, max_rows=100):
        self.validate_table_name(table_name)
        return self.run_sql_query(self[table_name].render_read_sql(max_rows=max_rows))
    
    def read_master(self):
        return self.run_sql_query("SELECT * FROM sqlite_master")
    
    def show_tables(self):
        return self.run_sql_query("SELECT * FROM sqlite_master WHERE type='table';")
    
    def insert_into(self, table_name: str, values: Dict[str, Any]):
        """runs an insert into the table with the given values. 
        The values must be a dictionary"""
        self.validate_table_name(table_name)
        return self.run_sql_command(self[table_name].render_insert_sql(values)) 
    
    def default_insert(self, table_name: str, values: Tuple(Any)):
        """runs a simple insert into the table with the given values. 
        The values must be a list, matching the default values"""
        self.validate_table_name(table_name)
        return self.run_sql_command(self[table_name].render_default_insert(values))

    def validate_table_name(self, table_name: str) -> None:
        if not table_name in self.table_dict:
            raise ValueError(f"Table {table_name} does not exist")


class LookupTable(SQLiteTable):
    """A table that has a name and a description. Neither of these values can be null. 
    any subsequent columns have to be optional. This doesn't have to just be a lookup table,
    it can be any type of table that fits this description."""
    
    def __init__(self, name: str | Tuple[str, str], 
                       columns: Optional[List[SQLiteColumn]]=None):
        if isinstance(name, tuple):
            name, name_column_name = name
        else:
            name_column_name = name[:-1]
        default_columns = [PrimaryKeyColumn(),
                           NameColumn(name_column_name),
                           TextColumn('description', is_not_null=True)]
        if columns is not None:
            default_columns.extend(columns)
        super().__init__(name, default_columns)
        
    # overwrite validate method to enforce name and description
    def validate_self(self) -> None:
        name_columns = [col.name for col in self.columns if isinstance(col, NameColumn)]
        if len(name_columns) > 1:
            raise ValueError("Only one column can be a name column")
        if len(name_columns) == 0:
            raise ValueError("Must have a name column")
        not_null_colums = [col.name for col in self.columns if col.is_not_null]
        if len(not_null_colums) > 3:
            raise ValueError("Only the name and description columns can be 'not null'")
        
    
    def add_row(self, name: str, description: str):
        # enforce
        return self.render_insert_sql({'name': name, 'description': description})
    

if __name__ == '__main__':
    pass
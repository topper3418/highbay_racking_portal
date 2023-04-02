import sqlite3
import pandas
import os
from datetime import datetime

def script_path(script_name):
    """gets the path to a sql script

    Args:
        script_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    return os.path.join(os.path.dirname(__file__), 'sql', script_name)

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        
    @property
    def tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        cursor = self.conn.cursor()
        cursor.execute(query)
        table_names = [table[0] for table in cursor.fetchall()]
        return table_names

    @property
    def views(self):
        query = "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;"
        cursor = self.conn.cursor()
        cursor.execute(query)
        view_names = [view[0] for view in cursor.fetchall()]
        return view_names
    
    def get_table_headers(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"{table_name} is not a valid table name.")
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
        return [description[0] for description in cursor.description]
    
    def insert_row(self, table_name, row_data: dict):
        headers = self.get_table_headers(table_name)
        if not all([k in headers for k in row_data.keys()]):
            raise ValueError(f"{row_data.keys()} is not a valid column name for {table_name}.")
        headers_in = row_data.keys()
        columns = ', '.join(headers_in)
        values = ', '.join([f"'{row_data[header]}'" for header in headers_in])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self.conn.execute(query)
        self.conn.commit()
        
    def verify_connection(self):
        if not self.conn:
            raise sqlite3.Error("No active connection found")
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def run_sql(self, sql_file) -> sqlite3.Cursor:
        self.verify_connection()
        
        with open(sql_file) as f:
            sql = f.read()
        return self.conn.executescript(sql)
    
    def insert_df(self, table_name, df):
        with self.conn:
            df.to_sql(table_name, self.conn, if_exists='append', index=False)

    def get_table_data(self, table_name):
        self.verify_connection()
        # Verify that the table exists
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"Table '{table_name}' does not exist in the database")

        # Get the table data as a pandas DataFrame
        query = f"SELECT * FROM {table_name}"
        df = pandas.read_sql_query(query, self.conn)

        return df

class SqlConnectionBase:
    
    def __init__(self, db_path):
        self.db_path = db_path
        # raise exception if the directory does not exist
        if not os.path.isdir(os.path.dirname(self.db_path)):
            raise ValueError(f"{self.db_path} is not a valid path")
        self.conn = None
        self.cursor = None
    
    @property
    def valid_filename(self) -> bool:
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
        if not self.valid_filename:
            self.build_database()
        self.tables: pandas.DataFrame = self.get_tables()
        self.views: pandas.DataFrame = self.get_views()
    
    def build_database(self):
        # create the database
        self.run_sql_script(script_path("create_tickets_table.sql"))

class DbTableBase(SqlConnectionBase):
    """Base class for all database tables
    """
    def __init__(self, db_path, table_name: str):
        super().__init__(db_path)
        self.table_name = table_name
        self.description = self.get_description()   
    
    def get_description(self) -> pandas.DataFrame:
        return super().get_description(self.table_name) 
    
    def fetch_100(self, endtime: datetime = datetime.now(), sql=None) -> pandas.DataFrame:
        """returns the first 100 rows from the requests table where the endtime is less than the given endtime

        Args:
            endtime (datetime): _description_

        Returns:
            pandas.DataFrame: _description_
        """
        if sql is None:
            sql = f"SELECT * FROM {self.table_name} WHERE submitted < '{endtime.timestamp()}' LIMIT 100"
        
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
        
    def fetch_100(self, endtime: datetime = datetime.now()) -> pandas.DataFrame:
        sql = f"""SELECT 
                    id,
                    submitter,
                    strftime('%Y-%m-%d %H:%M:%S', submitted, 'unixepoch') as submitted,
                    strftime('%Y-%m-%d', due_date, 'unixepoch') as due_date,
                    due_date_reason
                  FROM tickets 
                  WHERE submitted < {endtime.timestamp()}
                  ORDER BY submitted DESC
                  LIMIT 100"""
        return super().fetch_100(endtime, sql)
    

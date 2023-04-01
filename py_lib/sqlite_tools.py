import sqlite3
import pandas

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

if __name__ == '__main__':
    db_path = 'requests.db'

    with Database(db_path) as db:
        db.run_sql('create_table.sql')

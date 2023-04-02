import configparser
import os
from config.logging import logger
from data.sqlite_tools import AppData, Tickets, DbTableBase
from flask import Flask, render_template, request, jsonify

# Load configuration from file
config_path = os.path.join('config', 'app.conf')
config = configparser.ConfigParser()
config.read(config_path)

# Create Flask app
app = Flask(__name__)
# initialize data
database_name = config.get('Database', 'name')
app_data_path = os.path.join('data', database_name)
app_data = AppData(app_data_path)
all_tables = app_data.get_tables()
all_views = app_data.get_views()

# get the configuration values from the config file
host_addr = config.get('Server', 'host')
host_port = config.get('Server', 'port')
            
# Example usage
@app.route('/')
def serve_main():
    # log the ip address of the request
    logger.info(f'serving / request from {request.remote_addr}')
    return render_template('index.html')

@app.route('/get_tickets', methods=['GET'])
def fetch_ticket_data():
    """Return the requests table data as JSON"""
    # log the ip address of the request
    logger.info(f'serving /table_data request from {request.remote_addr}')
    # use the table name to get the data from the database
    df = Tickets(app_data_path).fetch_100()
    # convert the DataFrame to JSON
    return jsonify(df.to_dict(orient='records'))
    
@app.route('/dev_page', methods=['GET'])
def serve_dev_page():
    return render_template('dev_page.html')

@app.route('/get_table', methods=['GET'])
def get_table():
    """Return the requests table data as JSON"""
    # first make sure the query is a valid table or view
    query = request.args.get('query')
    if query not in all_tables['name'].values and query not in all_views['name'].values:
        return jsonify({'error': 'invalid query'})
    # log the ip address of the request
    logger.info(f'serving /table_data request from {request.remote_addr}')
    # get and return the data
    if query == 'all_tables':
        df = all_tables
    elif query == 'all_views':
        df = all_views
    elif query not in all_tables['name'].values and query not in all_views['name'].values:
        return jsonify({'error': 'invalid query'})
    else:
        df = DbTableBase(app_data_path, query).fetch_100()
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host=host_addr, port=host_port, debug=True)


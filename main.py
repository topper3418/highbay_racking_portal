import configparser
import datetime
import os
from config.logging import logger
from data.sqlite_tools import Database, AppData, Tickets
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

# get the configuration values from the config file
host_addr = config.get('Server', 'host')
host_port = config.get('Server', 'port')
            
# Example usage
@app.route('/')
def hello():
    # log the ip address of the request
    logger.info(f'serving / request from {request.remote_addr}')
    return render_template('index.html')

@app.route('/get_requests', methods=['GET'])
def fetch_table_data():
    """Return the requests table data as JSON"""
    # log the ip address of the request
    logger.info(f'serving /table_data request from {request.remote_addr}')
    # use the table name to get the data from the database
    df = Tickets(app_data_path).fetch_100()
    # convert the DataFrame to JSON
    return jsonify(df.to_dict(orient='records'))
    

if __name__ == '__main__':
    app.run(host=host_addr, port=host_port, debug=True)


import configparser
import datetime
import os
from config.logging import logger
from py_lib.sqlite_tools import Database
from flask import Flask, render_template, request, jsonify

# Load configuration from file
config_path = os.path.join('config', 'app.conf')
config = configparser.ConfigParser()
config.read(config_path)

# Create Flask app
app = Flask(__name__)

# get the configuration values from the config file
host_addr = config.get('Server', 'host')
host_port = config.get('Server', 'port')
# Example usage
@app.route('/')
def hello():
    # log the ip address of the request
    logger.info(f'serving / request from {request.remote_addr}')
    return render_template('index.html')

@app.route('/table_data', methods=['GET'])
def fetch_table_data():
    """Return the table data as JSON"""
    # log the ip address of the request
    logger.info(f'serving /table_data request from {request.remote_addr}')
    # get the table name from the request
    table_name = request.args.get('table_name')
    # use the table name to get the data from the database
    with Database('test.db') as db:
        df = db.get_table_data(table_name)
    # convert the DataFrame to JSON
    return jsonify(df.to_dict(orient='records'))
    

if __name__ == '__main__':
    app.run(host=host_addr, port=host_port, debug=True)

import logging
import logging.handlers
import configparser
import datetime
import os
from flask import Flask, render_template, request, jsonify

# Load configuration from file
config_path = os.path.join('config', 'app.conf')
config = configparser.ConfigParser()
config.read(config_path)

# Set up logging, first the filehandler
log_level = config.get('Logging', 'log_level')
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'app.log')
handler = logging.handlers.TimedRotatingFileHandler(
    log_path,
    when='midnight',
    backupCount=7
)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
handler.setLevel(log_level)
# then the console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
console_handler.setLevel(log_level)
# get the logger and add the handlers and set the level
app_logger = logging.getLogger('werkzeug')
app_logger.addHandler(console_handler)
app_logger.addHandler(handler)
app_logger.setLevel(log_level)

# Create Flask app
app = Flask(__name__)

# get the configuration values from the config file
host_addr = config.get('Server', 'host')
host_port = config.get('Server', 'port')
# Example usage
@app.route('/')
def hello():
    # log the ip address of the request
    app_logger.info(f'serving request from {request.remote_addr}')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=host_addr, port=host_port, debug=True)

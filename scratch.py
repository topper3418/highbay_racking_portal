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

print(all_tables)
import logging
import logging.handlers
import os
import configparser

# Load configuration from file
config_path = os.path.join('config', 'app.conf')
config = configparser.ConfigParser()
config.read(config_path)

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
logger = logging.getLogger('werkzeug')
logger.addHandler(console_handler)
logger.addHandler(handler)
logger.setLevel(log_level)
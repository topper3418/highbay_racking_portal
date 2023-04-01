import logging
import logging.handlers
import configparser
import datetime

# Load configuration from file
config = configparser.ConfigParser()
config.read('config/app.conf')

# Set up logging
log_level = config.get('Logging', 'log_level')
log_path = config.get('Logging', 'log_path')
handler = logging.handlers.TimedRotatingFileHandler(
    log_path,
    when='midnight',
    backupCount=7
)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
handler.setLevel(log_level)
logging.root.addHandler(handler)

# Example usage
logging.info('Hello, world!')

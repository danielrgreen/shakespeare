import os
import configparser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'configuration.conf')

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

DB_DIR = os.path.join(ROOT_DIR, config['DEFAULT']['db_dir'])
DB_PATH = os.path.join(DB_DIR, config['DEFAULT']['db_name'])
DB_SCHEMA_PATH = os.path.join(DB_DIR, config['DEFAULT']['db_schema_name'])

import os

# Generate API keys: https://my.telegram.org/apps
TELEGRAM_ID = os.environ.get('TELEGRAM_ID', '')
TELEGRAM_HASH = os.environ.get('TELEGRAM_HASH', '')

APP_VERSION = 0.1
CONFIG_DIR = os.path.expanduser('~') + '/.termgram/'
SESSION_FILE = CONFIG_DIR + 'auth'
IGNORE_FILE = CONFIG_DIR + 'ignore.txt'
TIMESTAMP_FORMAT = '%H:%M'

# Init
os.makedirs(CONFIG_DIR, exist_ok=True)
open(IGNORE_FILE, 'a').close()  # create empty file

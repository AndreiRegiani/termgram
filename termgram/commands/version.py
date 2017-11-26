import platform

from termgram import app
from termgram import config


def run(args):
    message = "Termgram {}, Python {}".format(config.APP_VERSION, platform.python_version())
    app.display_message(message)

import platform

from termgram import config


def run(args, current_chat, display_message):
    message = "Termgram {}, Python {}".format(config.APP_VERSION, platform.python_version())
    display_message(message)

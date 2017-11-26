import os

from termgram import app


def run(args):
    app.display_message("Available commands: \n")

    for command_name in os.listdir('./termgram/commands'):
        # skip :help and other files
        if command_name in ('help.py', '__init__.py', '__pycache__'):
            continue
        command_name = command_name.replace('.py', '')
        command_module = 'termgram.commands.' + command_name
        command = __import__(command_module, fromlist=[''])
        message = ':' + command_name
        try:
            message += ' ' + command.help
        except AttributeError:
            pass
        app.display_message(message)

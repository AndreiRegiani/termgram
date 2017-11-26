class CommandHandler:
    """Use prefix : to run commands

    Available commands are dynamically loaded from termgram/commands module
    Use :help to list them all.
    """

    def run(self, message: str) -> bool:
        if not message[0] == ':':
            return False
        cmd, *args = message.split()
        try:
            command_name = 'termgram.commands.' + cmd[1:]  # without':'
            command = __import__(command_name, fromlist=[''])
            command.run(args)
            return True
        except ImportError:
            return False

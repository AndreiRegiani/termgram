from typing import Callable

from telethon.tl import types


class CommandHandler:
    """Use prefix : to run commands

    Available commands are dynamically loaded from termgram/commands/ module
    Use :help to list them all.
    """

    def run(self, message: str, current_chat: types.User, display_message: Callable) -> bool:
        if not message[0] == ':':
            return False
        cmd, *args = message.split()
        try:
            mod_name = 'termgram.commands.' + cmd[1:]  # without':'
            mod = __import__(mod_name, fromlist=[''])
            mod.run(args, current_chat, display_message)
            return True
        except ImportError:
            return False

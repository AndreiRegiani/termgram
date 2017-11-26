import datetime
import sys

import urwid
import telethon
from telethon.tl import types
from telethon.utils import get_display_name

from termgram import config
from termgram.command import CommandHandler
from termgram.ignore import IgnoreHandler


# Telegram (Telethon)
client = None  # type: telethon.TelegramClient
current_chat = None  # type: telethon.types.User|Channel

# UI (Urwid)
mainloop = None  # type: urwid.MainLoop
mainframe = None  # type: urwid.Frame
columns = None  # type: urwid.Columns
message_log = None  # type: urwid.ListBox
header_text = None  # type: urwid.Text
input_field = None  # type: urwid.Edit

# Handlers
command_handler = CommandHandler()
ignore_handler = IgnoreHandler()


def run():
    """Entry point"""

    init()
    login()
    live_chatroom()
    exit_program()


def init():
    """Initialize components"""

    # Telegram
    if not any([config.TELEGRAM_ID, config.TELEGRAM_HASH]):
        print("Missing Telegram API keys at termgram/config.py")
        sys.exit(1)
    global client
    client = telethon.TelegramClient(config.SESSION_FILE, config.TELEGRAM_ID, config.TELEGRAM_HASH, update_workers=1)
    client.add_update_handler(event_polling)

    # UI
    global header_text
    header_text = urwid.Text('Termgram')
    header_text.set_align_mode('center')

    global input_field
    input_field = urwid.Edit('>>> ')


def login():
    """First time login"""

    client.connect()
    while not client.is_user_authorized():
        try:
            phone = input("Phone number: ")
            client.sign_in(phone=phone)
            code = input("Activation code: ")
            client.sign_in(code=code)
            if not client.is_user_authorized():
                print("Failed to authenticate. Try again.\n")
        except KeyboardInterrupt:
            exit_program()


def event_polling(update):
    """Telegram event updates"""

    if isinstance(update, (types.UpdateNewMessage, types.UpdateNewChannelMessage)):
        if update.message.from_id == current_chat.id or update.message.to_id.channel_id == current_chat.id:
            display_message(update.message.message, update.message.from_id)

    elif isinstance(update, types.UpdateShortMessage):
        if update.user_id == current_chat.id:
            display_message(update.message, update.user_id)

    elif isinstance(update, types.UpdateShortChatMessage):
        if update.chat_id == current_chat.id:
            display_message(update.message, update.from_id)


def input_handler(key):
    """Handle UI key events accordingly to current focused widget"""

    # Left Column
    if columns.focus_col == 0:
        # Input field
        if mainframe.focus_part == 'footer':
            message_input_handler(key)
        # Message logs
        else:
            logs_input_handler(key)

    # Right Column
    elif columns.focus_col == 1:
        # Chat list
        chatlist_input_handler(key)


def message_input_handler(key):
    """Handles key events while writing a message"""

    global current_chat

    # Send message
    if key == 'enter':
        my_message = input_field.get_edit_text().strip()
        if my_message and current_chat:
            input_field.set_edit_text('')  # clear input
            # Command Handler
            if command_handler.run(my_message):
                return
            # Regular Message
            client.send_message(current_chat, my_message)
            display_message(my_message, client.get_me())

    # @TODO: scroll logs up
    elif key == 'up':
        pass

    # @TODO: scroll logs down
    elif key == 'down':
        pass


def logs_input_handler(key):
    """Handles key events while message logs are in focus"""
    pass


def chatlist_input_handler(key):
    """Handles key events while contact list is in focus"""
    pass


def live_chatroom():
    """Main loop"""

    global message_log
    message_log = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Divider()]))
    body = urwid.LineBox(message_log)

    global mainframe
    mainframe = urwid.Frame(header=header_text, body=body, footer=input_field)
    mainframe.focus_part = 'footer'

    global columns
    contact_list_width = 25
    columns = urwid.Columns([mainframe, (contact_list_width, build_contact_list())])
    columns.set_focus_column(1)  # Focus on contact list

    global mainloop
    mainloop = urwid.MainLoop(columns, unhandled_input=input_handler)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        exit_program()


def build_contact_list():
    """Returns widget of contact list"""

    body = []
    _, entities = client.get_dialogs(50)

    for entity in reversed(entities):
        label = get_display_name(entity)
        label_max_chars = 18
        if len(label) > label_max_chars:
            label = label[:label_max_chars] + '…'
        button = urwid.Button(label)
        urwid.connect_signal(button, 'click', on_selected_chatroom, entity)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))

    list_conversations = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    widget = urwid.Padding(list_conversations, left=1, right=1)
    return widget


def on_selected_chatroom(event, entity):
    """Chat is selected"""

    global current_chat
    current_chat = entity
    global header_text
    header_text.set_text(get_display_name(entity))
    columns.set_focus_column(0)  # change focus to Left Column (input message)

    # retrieve recent chat (history)
    total, messages, senders = client.get_message_history(entity)
    for message in reversed(messages):
        # normal message
        if isinstance(message, types.Message):
            display_message(message.message, client.get_entity(message.from_id))

        # notification messages
        elif isinstance(message, types.MessageService):
            if isinstance(message.action, types.MessageActionChatAddUser):
                pass
            elif isinstance(message.action, types.MessageActionChatDeleteUser):
                pass
            elif isinstance(message.action, types.MessageActionPinMessage):
                pass
            elif isinstance(message.action, types.MessageActionChatEditTitle):
                pass
            elif isinstance(message.action, types.MessageActionChatJoinedByLink):
                pass
            elif isinstance(message.action, types.MessageActionPhoneCall):
                pass


def display_message(message: str, sender_id=None, date=None):
    """Appends new message to message logs"""

    if ignore_handler.check(message):
        return

    if sender_id:
        if not date:
            date = datetime.datetime.now()
        if not message:
            message = '{multimedia ¯\_(ツ)_/¯}'
        date = date.strftime(config.TIMESTAMP_FORMAT)
        sender_name = get_display_name(sender_id) + ': '
        message = " {} | {}{}".format(date, sender_name, message)

    message_log.body.insert(-1, urwid.Text(message))
    message_log.set_focus(len(message_log.body)-1)
    mainloop.draw_screen()


def exit_program():
    """Gracefully exits"""

    client.disconnect()
    sys.exit(0)

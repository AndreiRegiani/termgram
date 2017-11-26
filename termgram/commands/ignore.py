from termgram import app
from termgram import config


help = "</regex/ or sentence> Don't show messages that matches <regex>, adds to ~/.termgram/ignore.txt"

def run(args):
    if not args:
        app.display_message("Missing <regex> parameter")
        return
    with open(config.IGNORE_FILE, 'a') as fout:
        entry = ' '.join(args)
        fout.write(entry + '\n')
        app.display_message("Added '{}' to {}".format(entry, config.IGNORE_FILE))
    app.ignore_handler.refresh()

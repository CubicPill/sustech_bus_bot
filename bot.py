from telegram.ext import Updater
import json

config = dict()


def main():
    global config
    with open('config.json') as f:
        config = json.load(f)
    updater = Updater(config['token'])
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

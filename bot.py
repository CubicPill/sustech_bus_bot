from telegram.ext import Updater, CommandHandler
import json
from utils import BusSchedule

config = dict()
sched = None


def next_bus(bot, update):
    pass


def lines(bot, update):
    pass


def detail(bot, update):
    pass


def show_help(bot, update):
    pass


def main():
    global config
    with open('config.json') as f:
        config = json.load(f)
    updater = Updater(config['token'])
    global sched
    sched = BusSchedule(config['line_folder'], override=config['data_file'])
    updater.dispatcher.add_handler(CommandHandler('next', next_bus))
    updater.dispatcher.add_handler(CommandHandler('lines', lines))
    updater.dispatcher.add_handler(CommandHandler('detail', detail))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

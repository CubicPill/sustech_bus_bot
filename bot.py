from telegram.ext import Updater, CommandHandler
import json
from utils import BusSchedule, QueryStatus

config = dict()
sched: BusSchedule = None


def next_bus(bot, update):
    result = sched.get_all_lines_next()
    text = ''
    for group_id, (t, line_id) in result.items():
        if t == QueryStatus.MISS_LAST:
            r_str = '末班车已开出'
        elif t == QueryStatus.NOT_TODAY:
            r_str = '今日不运行'
        else:
            t = list(str((t)))
            t.insert(-2, ':')
            r_str = ''.join(t)


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
    sched = BusSchedule()
    updater.dispatcher.add_handler(CommandHandler('next', next_bus))
    updater.dispatcher.add_handler(CommandHandler('lines', lines))
    updater.dispatcher.add_handler(CommandHandler('detail', detail))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    # updater.start_polling()
    # updater.idle()


if __name__ == '__main__':
    main()

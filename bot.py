from telegram.ext import Updater, CommandHandler
from telegram import Message, Bot, Update
import json
from utils import BusSchedule, QueryStatus, BusLine

config = dict()
sched: BusSchedule = None


def next_bus(bot: Bot, update: Update):
    result = sched.get_all_lines_next()
    text = list()
    for group_id, (int_t, line_id) in result.items():
        text.append(sched.get_group_def(group_id) + ':')

        if int_t == QueryStatus.MISS_LAST:
            text.append(sched.get_line(line_id).name)
            r_str = '末班车已开出'
        elif int_t == QueryStatus.NOT_TODAY:
            r_str = '今日不运行'
        else:
            text.append(sched.get_line(line_id).name)

            r_str = BusLine.time_to_string(int_t)
        text.append(r_str)
    update.message.reply_text('\n'.join(text))


def lines(bot: Bot, update: Update):
    update.message.reply_text(sched.get_all_lines_brief())


def detail(bot: Bot, update: Update, args: list):
    if not args:
        # TODO: show buttons
        update.message.reply_text('请输入线路 id!')
        return
    line = sched.get_line(args[0])
    if line:
        update.message.reply_text(line.to_string())
    else:
        update.message.reply_text('线路 "{}" 不存在!')


def show_help(bot, update):
    text = [
        '一个用来查询校巴发车时间的 bot',
        '源代码详见 https://github.com/CubicPill/sustech_bus_bot',
        '欢迎 PR',
        '',
        '详细命令:',
        '/next              查询下一班校巴发车时间',
        '/lines             查看当前所有线路',
        '/detail <line_id>  查看线路详情',
        '/help              显示此帮助',
        ''
    ]
    update.message.reply_text('\n'.join(text))


def main():
    global config
    with open('config.json') as f:
        config = json.load(f)
    updater = Updater(config['token'])
    global sched
    sched = BusSchedule()
    updater.dispatcher.add_handler(CommandHandler('start', show_help))
    updater.dispatcher.add_handler(CommandHandler('next', next_bus))
    updater.dispatcher.add_handler(CommandHandler('lines', lines))
    updater.dispatcher.add_handler(CommandHandler('detail', detail, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

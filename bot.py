import time

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler

from globals import get_config, get_logger
from utils import BusSchedule, QueryStatus, BusLine

sched = None
config = get_config()
logger = get_logger()


def bus_info(bot, update, type):
    ts = time.time()
    logger.info('Incoming request by user @{}'.format(update.message.from_user.username))
    if type == 1:
        result = sched.get_all_lines_next(ts)
        text = ['下一班车']

    else:
        result = sched.get_all_lines_current(ts)
        text = ['上一班车']
    text.append('')
    for group_id, (int_t, line_id) in sorted(result.items(), key=lambda x: x[0]):
        text.append('<b>{}</b>'.format(sched.get_group_def(group_id) + ':'))
        if int_t == QueryStatus.MISS_LAST:
            text.append(sched.get_line(line_id).name)
            r_str = '末班车已开出'
        elif int_t == QueryStatus.NOT_TODAY:
            r_str = '今日不运行'
        else:
            text.append(sched.get_line(line_id).name)
            r_str = '<code>{}</code>'.format(BusLine.time_to_string(int_t))
        text.append(r_str)
        text.append('')
    update.message.reply_text('\n'.join(text), parse_mode='HTML')


def next_bus(bot: Bot, update: Update, args: list):
    bus_info(bot, update, 1)


def current_bus(bot: Bot, update: Update, args: list):
    bus_info(bot, update, 0)


def lines(bot: Bot, update: Update):
    all_lines = sched.get_all_lines_brief()
    update.message.reply_text('\n'.join([': '.join([k, v]) for k, v in all_lines.items()]))


def detail(bot: Bot, update: Update, args: list):
    if not args:
        update.message.reply_text('请输入线路 id! 向机器人发送 /lines 获取全部线路信息')
        return
    line = sched.get_line(args[0])
    if line:
        update.message.reply_text(line.to_string())
    else:
        update.message.reply_text('线路 "{}" 不存在!'.format(line))


def show_help(bot, update):
    text = [
        '一个用来查询校巴发车时间的 bot',
        '源代码详见 https://github.com/CubicPill/sustech_bus_bot',
        '欢迎 PR',
        '',
        '详细命令:',
        '/next              查询下一班校巴发车时间',
        '/current           查询当前已发出的校巴',
        '/lines             查看当前所有线路',
        '/detail <line_id>  查看线路详情',
        '/help              显示此帮助',
        ''
    ]
    update.message.reply_text('\n'.join(text))


def main():
    updater = Updater(config['token'])
    global sched
    sched = BusSchedule()
    updater.dispatcher.add_handler(CommandHandler('start', show_help))
    updater.dispatcher.add_handler(CommandHandler('next', next_bus, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('current', current_bus, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('lines', lines))
    updater.dispatcher.add_handler(CommandHandler('detail', detail, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

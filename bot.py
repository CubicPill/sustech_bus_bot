import os
import pickle
import time

from telegram import Bot, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from globals import get_config, get_logger
from utils import BusSchedule, QueryStatus, BusLine

sched: BusSchedule = None
config = get_config()
logger = get_logger()
users = dict()


def disable_in_group(func):
    def wrapper(*args, **kwargs):
        update = args[1]
        if update.message.from_user.id != update.message.chat_id:
            update.message.reply_text('请私聊机器人')
            return
        return func(*args, **kwargs)

    return wrapper


def bus_info(bot: Bot, update: Update, type):
    ts = time.time()
    logger.info('[Incoming request] @{usn},{uid}'.format(usn=update.message.from_user.username,
                                                         uid=update.message.from_user.id))
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
            text.append(sched.get_line_detail(line_id).name)
            r_str = '末班车已开出'
        elif int_t == QueryStatus.BEFORE_FIRST:
            text.append(sched.get_line_detail(line_id).name)
            r_str = '第一班车尚未发出'
        elif int_t == QueryStatus.NOT_TODAY:
            r_str = '今日不运行'
        else:
            text.append(sched.get_line_detail(line_id).name)
            r_str = '<code>{}</code>'.format(BusLine.time_to_string(int_t))
        text.append(r_str)
        text.append('')
    update.message.reply_text('\n'.join(text), parse_mode='HTML')


@disable_in_group
def next_bus(bot: Bot, update: Update):
    bus_info(bot, update, 1)


@disable_in_group
def current_bus(bot: Bot, update: Update):
    bus_info(bot, update, 0)


@disable_in_group
def lines(bot: Bot, update: Update):
    all_lines = sched.get_all_lines_brief()
    update.message.reply_text('\n'.join([': '.join([k, v]) for k, v in all_lines.items()]))


@disable_in_group
def detail(bot: Bot, update: Update, args: list):
    if args:

        line = sched.get_line_detail(args[0])
        if line:
            update.message.reply_text(line.to_string())
        else:
            update.message.reply_text('线路 "{}" 不存在! 请用 /lines 查询线路列表或直接发送 /detail 获取当前运行线路信息'.format(args[0]))
    else:  # no args, send buttons
        available_lines = sched.get_all_lines_brief(timestamp=time.time())
        if not available_lines:  # no line running, poor guy
            available_lines = sched.get_all_lines_brief()  # send all
            reply_text = '今日无运行线路, 所有线路列表如下:'
        else:
            reply_text = '当前运行线路列表:'
        button_list = list()
        for id, name in sorted(list(available_lines.items()), key=lambda l: l[0]):
            button_list.append([InlineKeyboardButton(name, callback_data=id)])
        reply_markup = InlineKeyboardMarkup(button_list)
        if not available_lines:
            update.message.reply_text(reply_text, reply_markup=reply_markup)
        else:
            update.message.reply_text(reply_text, reply_markup=reply_markup)


def detail_callback(bot, update):
    query = update.callback_query
    line_id = query.data
    line = sched.get_line_detail(line_id)
    if line:
        bot.editMessageText(text=line.to_string(),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
    else:
        bot.editMessageText(text='线路 "{}" 不存在!'.format(line_id),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)


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
        '/version           查看线路配置版本(日期)',
        '注意: 智园线等班次较少的线路尚未加入, 但其他线路时刻表已经为最新.'
        ''
    ]
    update.message.reply_text('\n'.join(text), disable_web_page_preview=True)


def record_user(bot, update):
    global users
    with open('users.pickle', 'rb') as f:
        users = pickle.load(f)
    users[update.message.from_user.id] = [update.message.from_user.username, update.message.from_user.first_name,
                                          update.message.from_user.last_name]
    with open('users.pickle', 'wb') as f:
        pickle.dump(users, f)


def version(bot, update):
    update.message.reply_text(sched.version)


def main():
    if os.path.isfile('users.pickle'):
        global users
        with open('users.pickle', 'rb') as f:
            users = pickle.load(f)
    updater = Updater(config['token'])
    global sched
    sched = BusSchedule()
    updater.dispatcher.add_handler(MessageHandler(Filters.all, record_user), group=2)
    updater.dispatcher.add_handler(CallbackQueryHandler(detail_callback))
    updater.dispatcher.add_handler(CommandHandler('start', show_help))
    updater.dispatcher.add_handler(CommandHandler('next', next_bus))
    updater.dispatcher.add_handler(CommandHandler('current', current_bus))
    updater.dispatcher.add_handler(CommandHandler('lines', lines))
    updater.dispatcher.add_handler(CommandHandler('detail', detail, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.dispatcher.add_handler(CommandHandler('version', version))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

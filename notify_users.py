import json
import pickle
import time
from queue import Queue
from threading import Thread

from telegram import Bot
from telegram.error import RetryAfter, BadRequest, Unauthorized

user_with_err = list()


class TelegramSender(Thread):
    def __init__(self, bot, queue):
        Thread.__init__(self, name='TelegramSender')
        self._bot = bot
        self._queue = queue

    def run(self):
        while not self._queue.empty():
            message, user_id, usn, fn, ln = self._queue.get_nowait()
            message = message.format(uid=user_id, usn=usn, fn=fn, ln=ln)
            try:
                self._bot.send_message(user_id, message, parse_mode='HTML', disable_web_page_preview=True)
                print('Sent! {}'.format(user_id))
            except BadRequest as e:
                print('Bad request, message will not be delivered:', e.message)
                continue
            except Unauthorized:
                print('User {} {} ({}) unauthorized'.format(user_id, fn, ln))
                continue
            except RetryAfter as e:
                print('Limit hit, retry after {} second(s)'.format(e.retry_after))
                self._queue.put((message, user_id, usn, fn, ln))
                time.sleep(e.retry_after)
                continue
            user_with_err.remove(user_id)


def main():
    with open('message.txt') as f:
        message = f.read()
    with open('users.pickle', 'rb') as f:
        users: dict = pickle.load(f)
    with open('config.json') as f:
        bot_token = json.load(f)['token']
    q = Queue()
    global user_with_err
    user_with_err = list(users.keys())
    for user_id, (usn, fn, ln) in users.items():
        q.put((message, user_id, usn, fn, ln))

    bot = Bot(bot_token)
    t = TelegramSender(bot, q)
    t.start()
    t.join()
    for u in user_with_err:
        del users[u]
    with open('users.pickle', 'wb') as f:
        pickle.dump(users, f)


if __name__ == '__main__':
    main()

from config import DB_PATH
from modules.bot import bot, dispatcher
from modules.video_uploading.repeats_search import check_repeated_videos_after_start
from modules.logger import get_logger
from db import db_session
from time import sleep
from aiogram import executor
import threading
import requests
import urllib3
import sys
import traceback
import tracemalloc

logger = get_logger("main")
logger.info("БОТ ЗАПУЩЕН")
tracemalloc.start()
bot.delete_webhook()

import modules.callback
import modules.search
import modules.commands.help_and_start
import modules.commands.users
import modules.commands.videos
import modules.commands.admin.help_admin
import modules.commands.admin.info
import modules.commands.admin.users
import modules.commands.admin.videos
import modules.commands.admin.codes.pr_codes
import modules.commands.admin.codes.admin_codes
import modules.video_uploading.new_video_handler
import modules.video_uploading.title
import modules.video_uploading.description
import modules.video_uploading.actors
import modules.video_uploading.tags


def start_bot():
    bot.logger = logger
    last_e = None
    while True:
        try:
            executor.start_polling(dispatcher)
        except requests.exceptions.ConnectionError as e:
            if e != last_e:
                last_e = e
                logger.error(e)
                sleep(2)
        except urllib3.exceptions.ProtocolError as e:
            if e != last_e:
                last_e = e
                logger.error(e)
                sleep(2)
        except ConnectionResetError as e:
            if e != last_e:
                last_e = e
                logger.error(e)
                sleep(2)
        except Exception as e:
            if e != last_e:
                last_e = e
                traceback.print_exception(*sys.exc_info())
                logger.error(e, exc_info=True)
                sleep(2)


db_session.global_init(DB_PATH)

t1 = threading.Thread(target=check_repeated_videos_after_start)
t2 = threading.Thread(target=start_bot)
t1.start()
t2.start()
for thread in [t1, t2]:
    thread.join()

tracemalloc.stop()
logger.critical(f"Программа завершилась, т.к. вышла из цикла!!!")

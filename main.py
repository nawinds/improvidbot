from config import DB_PATH
from modules.bot import dp
from modules.logger import get_logger
from db import db_session
from aiogram import executor
import asyncio

logger = get_logger("main")
logger.info("БОТ ЗАПУЩЕН")

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


if __name__ == '__main__':
    db_session.global_init(DB_PATH)
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop)

    logger.critical(f"Программа завершилась, т.к. вышла из цикла!!!")

from config import ADMIN_ID
import config
from modules.bot import bot
from modules.logger import get_logger
from modules.decorators import main_admin
from db import db_session
from db.users import User
from db.videos import Video
from db.stats import Stats
import os
import tracemalloc

admin_info = get_logger("admin_info_commands")


@bot.message_handler(commands=["memory"], func=lambda m: main_admin(m))
def memory(message):
    current, peak = tracemalloc.get_traced_memory()
    bot.send_message(ADMIN_ID, f"Current memory usage is "
                               f"{current / 10 ** 3}KB; "
                               f"Peak was {peak / 10 ** 3}KB; "
                               f"Diff = {(peak - current) / 10 ** 3}KB")


@bot.message_handler(commands=["stats"], func=lambda m: main_admin(m))
def stats(message):
    session = db_session.create_session()
    len_users = session.query(User).count()
    len_videos = session.query(Video).count()
    len_active_videos = session.query(Video).filter(Video.active == True).count()
    len_uploaders = session.query(Video).filter(Video.active == True).\
        distinct(Video.author_id).group_by(Video.author_id).count()
    len_admins = session.query(User).filter(User.is_admin == True).count()
    all_queries = session.query(Stats).filter(Stats.title == "all_queries").first().value
    chosen_queries = session.query(Stats).filter(Stats.title == "chosen_queries").first().value
    no_res_queries = session.query(Stats).filter(Stats.title == "no_res_queries").first().value
    average_q_res = session.query(Stats).filter(Stats.title == "average_q_res").first().value
    bot.send_message(ADMIN_ID, f"Пользователей: {len_users}\n"
                               f"Всего видео: {len_videos}\n"
                               f"Активных видео: {len_active_videos}\n"
                               f"Загружавших видео: {len_uploaders}\n"
                               f"Админов: {len_admins}\n"
                               f"Всего поисковых запросов: {all_queries}\n"
                               f"Выбранных в поиске видео: {chosen_queries}\n"
                               f"Запросов без результатов: {no_res_queries}\n"
                               f"Средний номер выбранного видео: {average_q_res}")


@bot.message_handler(commands=['logs'], func=lambda message: main_admin(message))
def logs(message):
    bot.reply_to(message, "Готовлю файл с логами...")
    args = message.text.split()
    filename = f"{args[1]}.log" if len(args) > 1 else "main.log"
    first = int(args[2]) if len(args) > 2 else 0
    last = int(args[3]) if len(args) > 3 else None
    if not os.path.exists(f"{config.LOCAL_PATH}//temp"):
        os.mkdir(f"{config.LOCAL_PATH}//temp")
    with open(f"{config.LOCAL_PATH}/logs/{filename}", "r") as data:
        with open(f"{config.LOCAL_PATH}/temp/{filename}.txt", "w") as temp_file:
            temp_file.write("".join(data.readlines()[first:last]))
    with open(f"{config.LOCAL_PATH}/temp/{filename}.txt", "rb") as file:
        bot.send_document(ADMIN_ID,
                          data=file)
    os.remove(f"{config.LOCAL_PATH}/temp/{filename}.txt")
    admin_info.info("LOGS EXPORTED")


@bot.message_handler(commands=['db'], func=lambda message: main_admin(message))
def get_db(message):
    bot.send_message(ADMIN_ID, "Готовлю файл с БД...")
    filename = f"{config.LOCAL_PATH}//db/main.db"
    with open(filename, "rb") as file:
        bot.send_document(ADMIN_ID,
                          data=file)
    admin_info.info("DB EXPORTED")

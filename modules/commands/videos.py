from modules.bot import bot
from modules.logger import get_logger
from modules.decorators import main_admin
from modules.search import search
from db import db_session
from db.videos import Video
from telebot import types
from sqlalchemy.sql.expression import func

videos_logger = get_logger("videos_commands")


@bot.message_handler(commands=["random"])
def random_video(message):
    session = db_session.create_session()
    video = session.query(Video).filter(Video.active == True).order_by(func.random()).first()
    if not video:
        videos_logger.critical(f"Рандомное видео не найдено!!!")
    bot.send_video(message.from_user.id, video.url,
                   caption=f"<b>{video.title}</b>\n"
                           f"{video.description}\n\n"
                           f"<i>{video.actors}</i>",
                   parse_mode="html")


@bot.message_handler(commands=['id'])
def vid_id(message):
    send_by_id(message, True)


@bot.message_handler(commands=['only_media'])
def only_media(message):
    send_by_id(message, False)


def send_by_id(message, full):
    session = db_session.create_session()
    command = "id" if full else "only_media"
    try:
        video = session.query(Video).filter(Video.id == message.text.split()[1],
                                            Video.active == True).first()
    except IndexError:
        bot.send_message(message.from_user.id, f"Неверный формат ввода! Введите в формате: /{command} n, "
                                               f"где n — id видео")
        videos_logger.info(f"Неверный формат ввода для команды {command}!")
        return
    if not video:
        bot.send_message(message.from_user.id, "Видео с таким id не найдено")
        videos_logger.info(f"Видео с таким id не найдено для команды {command}")
        return
    text = f"<b>{video.title}</b>\n{video.description}\n\n<i>{video.actors}" \
           f"<b>{video.tags if main_admin(message) else ''}</b></i>" if full else None
    bot.send_video(message.from_user.id, video.url,
                   caption=text,
                   parse_mode="html")


@bot.message_handler(commands=["search"])
def search_cmd(message):
    q = " ".join(message.text.split()[1:])
    session = db_session.create_session()
    rev_res, ratings = search(q)
    out = []
    count = 1
    for rating in ratings:
        for res in rev_res[rating]:
            video = session.query(Video).filter(Video.id == res).first()
            if video:
                out.append(f"{video.id}. {video.title}\n"
                           f"<i>{video.description}\n"
                           f"{video.actors}</i>\n\n")
            else:
                videos_logger.error(f"Видео {res} не найдено при выполнении поиска")
            count += 1
            if count == 45:
                break
        if count == 45:
            break
    bot.send_message(message.from_user.id, f"ПОИСК ПО ЗАПРОСУ \"{q}\":\n{''.join(out)}", parse_mode="html")


@bot.message_handler(commands=['all_full'])
def all_full(message):
    get_videos_page(message.text, message.from_user.id, True)


@bot.message_handler(commands=['all'])
def all_vid(message):
    get_videos_page(message.text, message.from_user.id, False)


def get_videos_page(message, chat, full):
    limit = 10 if full else 20
    session = db_session.create_session()
    try:
        page = int(message.split()[1])
    except ValueError:
        bot.send_message(chat, f"Неверный формат ввода! Введите в формате: {message.split()[0]} n, "
                               f"где n — id видео")
        videos_logger.info(f"Неверный формат ввода для команды {message.split()[0]}")
        return
    except IndexError:
        page = 1
    if page < 1:
        bot.send_message(chat, f"Такой страницы не существует! Нумерация страниц начинается с 1")
        videos_logger.info(f"Неверная страница для команды {message.split()[0]}")
        return
    videos = session.query(Video).filter(Video.id > (page - 1) * limit, Video.id <= page * limit).all()
    if not videos:
        bot.send_message(chat, "На этой странице видео нет. "
                               "Попробуйте страницу с меньшим номером")
        videos_logger.info("На этой странице видео нет. "
                           "Попробуйте страницу с меньшим номером")
        return
    if full:
        data = '\n\n'.join([f"<b>{video.id}. {video.title}</b>\n{video.description}\n"
                            f"<i>{video.actors}</i>" for video in videos])
    else:
        data = '\n'.join([f"<b>{video.id}</b>. {video.title}" for video in videos])
    key = types.InlineKeyboardMarkup()
    if full:
        prefix = "full"
    else:
        prefix = ""
    prev_btn = types.InlineKeyboardButton(text="Предыдущая страница", callback_data=f"{prefix}page-{page - 1}")
    next_btn = types.InlineKeyboardButton(text="Следующая страница", callback_data=f"{prefix}page-{page + 1}")
    if page > 1:
        key.add(prev_btn)
    key.add(next_btn)
    bot.send_message(chat, f"Страница {page}:\n"
                           f"{data}",
                     parse_mode="html", reply_markup=key)

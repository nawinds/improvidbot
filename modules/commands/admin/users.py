from config import ADMIN_ID
from modules.bot import bot
from modules.logger import get_logger
from modules.decorators import main_admin
from modules.scores import add_score
from db import db_session
from db.users import User

admin_users_logger = get_logger("admin_users_commands")


@bot.message_handler(commands=["all_admins"], func=lambda message: main_admin(message))
def all_admins(message):
    session = db_session.create_session()
    admins = session.query(User).filter(User.is_admin == True).all()
    data = '\n\n'.join([f'@{bot.get_chat(admin.tg_id).username}\n'
                        f'id: {admin.tg_id}\n'
                        f'name: {bot.get_chat(admin.tg_id).first_name}\n'
                        f'surname: {bot.get_chat(admin.tg_id).last_name}\n'
                        f'bio: {bot.get_chat(admin.tg_id).bio}\n'
                        f'Счёт: {admin.score}\n'
                        f'Регистрация: {admin.joined_date}' for admin in admins])
    text = f"Список админов:\n\n{data}"
    bot.send_message(ADMIN_ID, text)


@bot.message_handler(commands=["ban_admin"], func=lambda message: main_admin(message))
def ban_admin(message):
    try:
        admin_id = str(int(message.text.split()[1]))
    except (IndexError, ValueError):
        bot.send_message(ADMIN_ID, "Неверный формат! Напишите так: /ban_admin admin_id")
        admin_users_logger.info("Неверный формат! Напишите так: /ban_admin admin_id")
        return
    session = db_session.create_session()
    admin_db = session.query(User).filter(User.tg_id == admin_id).first()
    if not admin_db:
        bot.send_message("Админ не найден в БД")
        admin_users_logger.info("Админ не найден в БД")
        return
    admin_db.is_admin = False
    session.commit()
    bot.send_message(admin_id, "Вы больше не админ...")
    bot.send_message(ADMIN_ID, "Админ больше не админ...")


@bot.message_handler(commands=['find_user'], func=lambda message: main_admin(message))
def find_user(message):
    try:
        user = message.text.split()[1]
    except IndexError:
        bot.send_message(ADMIN_ID, "Пожалуйста, укажите получателя в формате: /find_user @username или "
                                   "/find_user tg_id")
        admin_users_logger.info("Пожалуйста, укажите получателя в формате: /find_user @username или "
                                "/find_user tg_id")
        return
    session = db_session.create_session()
    if user[0] == "@":
        user_db = session.query(User).filter(User.username == user[1:]).first()
    else:
        user_db = session.query(User).filter(User.tg_id == user).first()
    if not user_db:
        bot.send_message(ADMIN_ID, "Пользователь не найден в базе!")
        admin_users_logger.info("Пользователь не найден в базе! Команда /find_user")
        return
    bot.send_message(ADMIN_ID, f"Пользователь найден! <b>@{bot.get_chat(user_db.tg_id).username} "
                               f"({user_db.tg_id})</b>\n"
                               f"name: {bot.get_chat(user_db.tg_id).first_name}\n"
                               f"surname: {bot.get_chat(user_db.tg_id).last_name}\n"
                               f"bio: {bot.get_chat(user_db.tg_id).bio}\n"
                               f"is admin: <b>{user_db.is_admin}</b>\n"
                               f"code id: <b>{user_db.code_id}</b>\n"
                               f"score: <b>{user_db.score}</b>\n"
                               f"joined: <b>{user_db.joined_date}</b>", parse_mode="html")
    bot.send_message(ADMIN_ID, bot.get_chat(user_db.tg_id))


@bot.message_handler(commands=['send'], func=lambda message: main_admin(message))
def send(message):
    try:
        receiver = str(int(message.text.split()[1]))
        message = " ".join(message.text.split()[2:])
    except (IndexError, ValueError):
        bot.send_message(ADMIN_ID, "Неверный формат! Напишите так: /send receiver_tg_id message")
        admin_users_logger.info("Неверный формат! Напишите так: /send receiver_tg_id message")
        return
    session = db_session.create_session()
    user_db = session.query(User).filter(User.tg_id == receiver).first()
    if not user_db:
        bot.send_message(ADMIN_ID, "Пользователь не найден в базе!")
        admin_users_logger.info("Пользователь не найден в базе!")
        return
    try:
        bot.send_message(receiver, message)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Не удалось отправить сообщение адресату. {e}")
        admin_users_logger.error(f"Не удалось отправить сообщение адресату. {e}")
        return
    bot.send_message(ADMIN_ID, "Сообщение успешно отправлено!")
    admin_users_logger.info(f"Сообщение успешно отправлено {receiver}! msg: {message}")


@bot.message_handler(commands=['add_score'], func=lambda message: main_admin(message))
def add_score_cmd(message):
    try:
        user_id, value = message.text.split()[1], int(message.text.split()[2])
    except (IndexError, ValueError):
        bot.send_message(f"Неверный формат! /add_score user_id value")
        return
    add_score(user_id, value)

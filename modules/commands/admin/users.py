from config import ADMIN_ID
from modules.bot import bot, dp, Filter
from modules.logger import get_logger
from modules.decorators import main_admin
from modules.scores import add_score
from db import db_session
from db.users import User

admin_users_logger = get_logger("admin_users_commands")


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=["all_users"])
async def all_users(message):
    try:
        page = int(message.split()[1])
    except IndexError:
        page = 1
    except ValueError:
        message.reply("Неверный формат! Введите так: /all_users <page>")
        return
    if page < 1:
        await bot.send_message(message.from_user.id, f"Такой страницы не существует!"
                                                     f" Нумерация страниц начинается с 1")
        return
    session = db_session.create_session()
    users = session.query(User).all()
    data = '\n\n'.join([f'@{(await bot.get_chat(user.tg_id)).username}\n'
                        f'id: <code>{user.tg_id}</code>\n'
                        f'is_admin: {user.is_admin}\n'
                        f'name: {(await bot.get_chat(user.tg_id)).first_name}\n'
                        f'surname: {(await bot.get_chat(user.tg_id)).last_name}\n'
                        f'bio: {(await bot.get_chat(user.tg_id)).bio}\n'
                        f'Счёт: {user.score}\n'
                        f'Регистрация: {user.joined_date}' for user in users])
    data = data[(page - 1) * 10:page * 10]
    if not data:
        await bot.send_message(message.from_user.id, f"На этой странице нет пользователей. "
                                                     f"Попробуйте страницу с меньшим номером.", parse_mode="html")
        return
    text = f"Список пользователей (Страница {page}):\n\n{data}"
    await bot.send_message(ADMIN_ID, text, parse_mode="html")


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=["all_admins"])
async def all_admins(message):
    try:
        page = int(message.split()[1])
    except IndexError:
        page = 1
    except ValueError:
        message.reply("Неверный формат! Введите так: /all_admins <page>")
        return
    if page < 1:
        await bot.send_message(message.from_user.id, f"Такой страницы не существует!"
                                                     f" Нумерация страниц начинается с 1")
        return
    session = db_session.create_session()
    admins = session.query(User).filter(User.is_admin == True).all()
    data = '\n\n'.join([f'@{(await bot.get_chat(admin.tg_id)).username}\n'
                        f'id: <code>{admin.tg_id}</code>\n'
                        f'name: {(await bot.get_chat(admin.tg_id)).first_name}\n'
                        f'surname: {(await bot.get_chat(admin.tg_id)).last_name}\n'
                        f'bio: {(await bot.get_chat(admin.tg_id)).bio}\n'
                        f'Счёт: {admin.score}\n'
                        f'Регистрация: {admin.joined_date}' for admin in admins])
    data = data[(page - 1) * 10:page * 10]
    if not data:
        await bot.send_message(message.from_user.id, f"На этой странице нет пользователей. "
                                                     f"Попробуйте страницу с меньшим номером.", parse_mode="html")
        return
    text = f"Список админов (Страница {page}):\n\n{data}"
    await bot.send_message(ADMIN_ID, text, parse_mode="html")


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=["ban_admin"])
async def ban_admin(message):
    try:
        admin_id = str(int(message.text.split()[1]))
    except (IndexError, ValueError):
        await bot.send_message(ADMIN_ID, "Неверный формат! Напишите так: /ban_admin admin_id")
        admin_users_logger.info("Неверный формат! Напишите так: /ban_admin admin_id")
        return
    session = db_session.create_session()
    admin_db = session.query(User).filter(User.tg_id == admin_id).first()
    if not admin_db:
        await message.reply("Админ не найден в БД")
        admin_users_logger.info("Админ не найден в БД")
        return
    admin_db.is_admin = False
    session.commit()
    await bot.send_message(admin_id, "Вы больше не админ...")
    await bot.send_message(ADMIN_ID, "Админ больше не админ...")


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=['find_user'])
async def find_user(message):
    try:
        user = message.text.split()[1]
    except IndexError:
        await bot.send_message(ADMIN_ID,
                               "Пожалуйста, укажите пользователя в формате: /find_user @username или "
                               "/find_user tg_id")
        admin_users_logger.info("Пожалуйста, укажите пользователя в формате: /find_user @username или "
                                "/find_user tg_id")
        return
    session = db_session.create_session()
    if user[0] == "@":
        user_db = session.query(User).filter(User.username == user[1:]).first()
    else:
        user_db = session.query(User).filter(User.tg_id == user).first()
    if not user_db:
        await bot.send_message(ADMIN_ID, "Пользователь не найден в базе!")
        admin_users_logger.info("Пользователь не найден в базе! Команда /find_user")
        return
    await bot.send_message(ADMIN_ID,
                           f"Пользователь найден! <b>@{(await bot.get_chat(user_db.tg_id)).username} "
                           f"(<code>{user_db.tg_id}</code>)</b>\n"
                           f"name: {(await bot.get_chat(user_db.tg_id)).first_name}\n"
                           f"surname: {(await bot.get_chat(user_db.tg_id)).last_name}\n"
                           f"bio: {(await bot.get_chat(user_db.tg_id)).bio}\n"
                           f"is_admin: <b>{user_db.is_admin}</b>\n"
                           f"code_id: <b>{user_db.code_id}</b>\n"
                           f"score: <b>{user_db.score}</b>\n"
                           f"joined: <b>{user_db.joined_date}</b>", parse_mode="html")
    await bot.send_message(ADMIN_ID, await bot.get_chat(user_db.tg_id))


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=['send'])
async def send(message):
    try:
        receiver = message.text.split()[1]
        message = " ".join(message.text.split()[2:])
    except (IndexError, ValueError):
        await bot.send_message(ADMIN_ID, "Неверный формат! Напишите так: /send receiver_tg_id message")
        admin_users_logger.debug("Неверный формат! Напишите так: /send receiver_tg_id message")
        return
    session = db_session.create_session()
    if receiver == "all":
        receivers = session.query(User).all()
    elif receiver == "admins":
        receivers = session.query(User).filter(User.is_admin == True).all()
    else:
        try:
            receiver = str(int(receiver))
        except ValueError:
            await bot.send_message(ADMIN_ID, "Неверный формат! Напишите так: /send receiver_tg_id message")
            admin_users_logger.debug("Неверный формат! Напишите так: /send receiver_tg_id message")
            return
        receivers = [session.query(User).filter(User.tg_id == receiver).first()]
    if not receivers:
        await bot.send_message(ADMIN_ID, "Пользователь не найден в базе!")
        admin_users_logger.debug("Пользователь не найден в базе!")
        return
    for receiver in receivers:
        try:
            await bot.send_message(receiver.tg_id, message)
        except Exception as e:
            await bot.send_message(ADMIN_ID, f"Не удалось отправить сообщение адресату. {e}")
            admin_users_logger.error(f"Не удалось отправить сообщение адресату. {e}")
            return
    await bot.send_message(ADMIN_ID, "Сообщения успешно отправлены!")
    admin_users_logger.info(f"Сообщения успешно отправлены {str(receivers)}! msg: {message}")


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=['add_score'])
async def add_score_cmd(message):
    try:
        user_id, value = message.text.split()[1], int(message.text.split()[2])
    except (IndexError, ValueError):
        await bot.send_message(f"Неверный формат! /add_score user_id value")
        return
    add_score(user_id, value)

from config import ADMIN_ID,  ADMIN_USERNAME
from modules.bot import bot, dp, Filter
from modules.logger import get_logger
from modules.commands.admin.help_admin import help_admin
from modules.decorators import main_admin
from db import db_session
from db.users import User
from db.codes import Code

help_and_start_logger = get_logger("help_and_start_commands")


@dp.message_handler(Filter(lambda message: not main_admin(message)), commands=["help"])
async def help_all(message):
    text = f"Привет, {message.from_user.first_name}!\n" \
           f"Это бот, который умеет находить небольшие видео из выпусков и выступлений шоу \"Импровизация\".\n\n" \
           f"<u><b>ИНЛАЙН-РЕЖИМ</b></u>\n" \
           f"Бот работает также в <b>инлайн-режиме</b>, благодаря которому удобно использовать видео из базы " \
           f"вместо стикеров, отправляя их в других чатах. " \
           f"<a href=\"https://telegra.ph/Kak-rabotaet-inlajn-rezhim-06-19\">Подробнее про инлайн-режим</a>\n\n" \
           f"<u><b>ПОИСК ПО БАЗЕ</b></u>\n" \
           f"<b>/search q</b> — Поиск видео, где q — поисковый запрос\n\n" \
           f"<u><b>ЗАГРУЗКА СВОИХ ВИДЕО В БАЗУ</b></u>\n" \
           f"<a href=\"https://telegra.ph/Zachem-voobshche-zagruzhat-svoi-video-v-bazu-06-25\">Зачем " \
           f"загружать свои видео</a>\n" \
           f"Для загрузки видео в базу этого нужно всего лишь отправить нужное " \
           f"<b>видео</b> и следовать инструкциям. Видео появляются в поиске только после модерации. \n" \
           f"Вы также можете стать админом этого бота и выкладывать " \
           f"свои видео без проверки. Прочитайте, " \
           f"<a href=\"https://telegra.ph/Kak-stat-adminom-i-zagruzhat-svoi-video-bez-moderacii-07-03\">" \
           f"как стать админом</a> и напишите @{ADMIN_USERNAME}.\n" \
           f"<b>/my_videos</b> — Список загруженных Вами видео\n\n" \
           f"<u><b>ПРОСМОТР ВИДЕО В БАЗЕ</b></u>\n" \
           f"<b>/all n</b> — Список названий всех видео базы страницами по 20 видео, где n — " \
           f"номер страницы\n" \
           f"<b>/all_full n</b> — Список названий и описаний всех видео базы страницами по 10 видео, где n " \
           f"— номер страницы\n""" \
           f"<b>/random</b> — Случайное видео из базы и полная информация по нему\n" \
           f"<b>/id n</b> — Видео из базы и полная информация по нему, где n — id видео\n" \
           f"<b>/only_media n</b> — Видео из базы без дополнительной информации, где n — id видео.\n\n" \
           f"<u><b>РЕЙТИНГ И СТАТИСТИКА</b></u>\n" \
           f"В боте ведётся рейтинг самых активных пользователей. Чтобы попасть в ТОП нужно " \
           f"накопить баллы одним из следующих способов:\n" \
           f"<i>1. Приглашайте друзей\n" \
           f"<b>/my_referal</b> — Получение Вашей реферальной ссылки\n" \
           f"2. Отпраляйте видео через инлайн-режим\n" \
           f"3. Загружайте свои видео</i>\n" \
           f"<b><a href=\"https://telegra.ph/Kak-popast-v-TOP--rejting-polzovatelej-v-bote-07-03\">" \
           f"Читайте подробнее, как попасть в ТОП здесь.</a></b>\n" \
           f"<b>/top</b> — ТОП самых активных пользователей и Ваш рейтинг\n\n" \
           f"<b>/articles</b> — Список статей о боте. Там можно узнать лайфхаки, " \
           f"о которых знают пока немногие\n" \
           f"<b>/help</b> — Эта страница.\n" \
           f"\n" \
           f"<i>Бот пока работает в тестовом режиме. " \
           f"Если что-то не работает — не пугайтесь, пишите мне!</i>\n\n" \
           f"По любым вопросам можете писать @{ADMIN_USERNAME}. С удовольствием отвечу =)"
    await bot.send_message(message.from_user.id, text, parse_mode="html")


@dp.message_handler(commands=["start"])
async def start(message):
    params = message.text[7:].split("-")
    command = params[0]
    session = db_session.create_session()
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    if not user:
        if command == "pr":
            try:
                code = params[1]
            except IndexError:
                code = "a"
                await bot.send_message(ADMIN_ID, f"pr-код не указан! Сообщение: {message.text}")
                help_and_start_logger.warn(f"pr-код не указан! Сообщение: {message.text}")
            code_db = session.query(Code).filter(Code.code == code, Code.type == 2).first()
            if code_db:
                if code.isnumeric():
                    user_db = session.query(User).filter(User.tg_id == int(code)).first()
                    if user_db:
                        await bot.send_message(user_db.tg_id,
                                               f"@{message.from_user.username} ({message.from_user.id}) "
                                               f"воспользовался "
                                               f"Вашим реферальным кодом "
                                               f"и присоединился.", disable_notification=True)
                        user_db.score += 100
                    else:
                        help_and_start_logger.warn(f"Пользователь, чей существующий в базе реферальный код был "
                                                   f"использован, не зарегистрирован! Сообщение: {message.text}")
                new_user = User(tg_id=message.from_user.id, username=message.from_user.username,
                                code_id=code_db.id)
                session.add(new_user)
                session.commit()
                help_and_start_logger.info(f"Зарегистрирован новый пользователь по pr-коду {code_db.title}! "
                                           f"{new_user.username} ({new_user.tg_id})")
                await bot.send_message(ADMIN_ID,
                                       f"@{message.from_user.username} ({message.from_user.id}) "
                                       f"воспользовался кодом "
                                       f"{code_db.title} и присоединился.", disable_notification=True)
            elif code.isnumeric():
                user_db = session.query(User).filter(User.tg_id == int(code)).first()
                if user_db:
                    session.add(Code(code=code, title=f"Реферальный код @{user_db.username} "
                                                      f"({user_db.tg_id})", type=2))
                    session.commit()
                    code_db = session.query(Code).filter(Code.code == code, Code.type == 2).first()
                    help_and_start_logger.info(f"Добавлен новый реферальный код пользователя @{user_db.username} "
                                               f"({user_db.tg_id})")
                    user_db.score += 100
                    new_code = session.query(Code).filter(Code.code == code, Code.type == 2).first()
                    new_user = User(tg_id=message.from_user.id, username=message.from_user.username,
                                    code_id=new_code.id)
                    session.add(new_user)
                    session.commit()
                    await bot.send_message(user_db.tg_id,
                                           f"@{message.from_user.username} ({message.from_user.id}) "
                                           f"воспользовался Вашим "
                                           f"реферальным кодом "
                                           f"и присоединился.", disable_notification=True)
                    await bot.send_message(ADMIN_ID,
                                           f"@{message.from_user.username} ({message.from_user.id}) ВПЕРВЫЕ "
                                           f"воспользовался реферальным "
                                           f"кодом @{user_db.username} ({user_db.tg_id}) и присоединился.",
                                           disable_notification=True)
                    help_and_start_logger.info(f"@{message.from_user.username} ({message.from_user.id}) ВПЕРВЫЕ "
                                               f"воспользовался кодом "
                                               f"{code_db.title} и присоединился.")
                else:
                    help_and_start_logger.warn(f"Пользователь, чей несохраненный в базе реферальный код попытались "
                                               f"использовать не зарегистрирован! Сообщение: {message.text}")
            else:
                await bot.send_message(ADMIN_ID, f"pr-код не найден! Сообщение: {message.text}")
                help_and_start_logger.warn(f"pr-код не найден! Сообщение: {message.text}")
        else:
            user = User(tg_id=message.from_user.id, username=message.from_user.username)
            session.add(user)
            help_and_start_logger.info(f"Зарегистрирован новый пользователь, присоединившийся без pr-кода")
        session.commit()
    else:
        user.username = message.from_user.username
        session.commit()
    if command == "admininvite" and user.is_admin == False:
        try:
            code = params[1]
        except IndexError:
            await bot.send_message(message.from_user.id,
                                   f"Ссылка для получения прав админа устарела. Пожалуйста, "
                                   f"обратитесь к @{ADMIN_USERNAME}")
            help_and_start_logger.warn(f"Ссылка для получения прав админа устарела. Сообщение: {message.text}")
            return
        code_db = session.query(Code).filter(Code.code == code, Code.type == 1).first()
        if code_db:
            user.is_admin = True
            await bot.send_message(message.from_user.id,
                                   "Здравствуйте! Теперь Вы админ и можете загружать видео в базу "
                                   "бота без дополнительной проверки!) Чтобы узнать подробнее про бота "
                                   "и посмотреть список всех команд и возможностей, отправьте команду /help.")
            await bot.send_message(ADMIN_ID,
                                   f"Теперь @{message.from_user.username} ({message.from_user.id}) "
                                   f"админ. Была использована "
                                   f"пригласительная ссылка {code_db.title}")
            help_and_start_logger.info(f"Теперь @{message.from_user.username} ({message.from_user.id}) "
                                       f"админ. Была использована "
                                       f"пригласительная ссылка {code_db.title}")
            session.delete(code_db)
            session.commit()
        else:
            await bot.send_message(message.from_user.id,
                                   f"Ссылка для получения прав админа устарела. Пожалуйста, "
                                   f"обратитесь к @{ADMIN_USERNAME}")
            help_and_start_logger.warn(f"Ссылка для получения прав админа устарела. Сообщение: {message.text}")
        return
    if not main_admin(message):
        await help_all(message)
    else:
        await help_admin(message)


@dp.message_handler(commands=["articles"])
async def articles(message):
    text = "СПИСОК СТАТЕЙ О БОТЕ:\n" \
           "1. <a href=\"https://telegra.ph/Kak-rabotaet-inlajn-rezhim-06-19\">" \
           "Как работает инлайн-режим?</a>\n\n" \
           "2. <a href=\"https://telegra.ph/Zachem-voobshche-zagruzhat-svoi-video-v-bazu-06-25\">" \
           "Зачем вообще загружать свои видео в базу? 🤷‍♀️</a>\n\n" \
           "3. <a href=\"https://telegra.ph/Kak-popast-v-TOP--rejting-polzovatelej-v-bote-07-03\">" \
           "Как попасть в ТОП — рейтинг пользователей в боте</a>\n\n" \
           "4. <a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-i-uvelichivat-ih-prosmotry-07-03\">" \
           "Как загружать видео в базу бота и увеличивать их просмотры</a>\n\n" \
           "5. <a href=\"https://telegra.ph/Kak-stat-adminom-i-zagruzhat-svoi-video-bez-moderacii-07-03\">" \
           "Как стать админом и загружать свои видео без модерации</a>"
    await bot.send_message(message.from_user.id, text, parse_mode="html", disable_web_page_preview=True)

from config import BOT_USERNAME
from modules.bot import bot, dp
from db import db_session
from db.users import User
from db.videos import Video


@dp.message_handler(commands=["my_referal"])
async def get_referal_link(message):
    await bot.send_message(message.from_user.id, f"https://t.me/{BOT_USERNAME}?start=pr-{message.from_user.id}")


@dp.message_handler(commands=["top"])
async def top(message):
    session = db_session.create_session()
    all_users = session.query(User).order_by(User.score.desc()).all()
    top_users = all_users[:10]
    data = [f"{user + 1}. <b>{top_users[user].score}</b> "
            f"<a href=\"https://t.me/{(await bot.get_chat(top_users[user].tg_id)).username}\">"
            f"{(await bot.get_chat(top_users[user].tg_id)).first_name} "
            f"{(await bot.get_chat(top_users[user].tg_id)).last_name if (await bot.get_chat(top_users[user].tg_id)).last_name else ''}"
            f"</a>" if (await bot.get_chat(top_users[user].tg_id)).username else

            f"{user + 1}. <b>{top_users[user].score}</b> "
            f"{(await bot.get_chat(top_users[user].tg_id)).first_name} "
            f"{(await bot.get_chat(top_users[user].tg_id)).last_name if (await bot.get_chat(top_users[user].tg_id)).last_name else ''}"
            for user in range(len(top_users))]
    places_emojis = ["🥇", "🥈", "🥉"]
    for i in range(3):
        try:
            data[i] = places_emojis[i] + data[i][2:]
        except IndexError:
            break
    me = session.query(User).filter(message.from_user.id == User.tg_id).first()
    if me not in top_users and me in all_users:
        data.append("...")
        data.append(f"{all_users.index(me) + 1}. <b>{me.score}</b> Вы")
    await bot.send_message(message.from_user.id,
                           "Рейтинг самых активных пользователей и их очки:\n\n" + "\n".join(data),
                           parse_mode="html", disable_web_page_preview=True)


@dp.message_handler(commands=["my_videos"])
async def my_videos(message):
    try:
        page = int(message.text.split()[1])
    except IndexError:
        page = 1
    except ValueError:
        await message.reply("Неверный формат команды! Введите: /my_videos <номер страницы>")
        return
    if page < 1:
        await bot.send_message(message.from_user.id, f"Такой страницы не существует! Нумерация страниц начинается с 1")
        return
    session = db_session.create_session()
    videos = session.query(Video).filter(Video.author_id == message.from_user.id). \
        order_by(Video.used.desc()).all()[(page - 1) * 10:page * 10]
    if not videos:
        await bot.send_message(message.from_user.id, f"На этой странице нет видео. "
                                                     f"Попробуйте страницу с меньшим номером.", parse_mode="html")
        return
    data = str()
    for video in videos:
        data += f"<b>{video.id}. {video.title}</b> (использовалось {video.used} раз)," \
                f" {'активно' if video.active else 'неактивно'}, " \
                f"{len(video.actors)} актёров, {len(video.tags)} тегов, " \
                f"загружено {video.created_date}.\n\n"
    await bot.send_message(message.from_user.id, f"Ваши загруженные видео (Страница {page}):\n\n"
                                                 f"{data}", parse_mode="html")

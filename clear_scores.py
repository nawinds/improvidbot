#!/home/pi/venvs/improvidbot/bin/python3
import asyncio
import config
from db.db_session import global_init, create_session
from db.users import User
from modules.bot import bot


async def notify(tg_id):
    print(tg_id)
    await bot.send_message(tg_id, "Рейтинг пользователей обнулён. "
                                  "Загружайте видео, чтобы снова попасть в ТОП!")


global_init(config.DB_PATH)
s = create_session()
users = s.query(User).all()
for u in users:
    u.score = 0
s.commit()
loop = asyncio.get_event_loop()
for u in users:
    loop.run_until_complete(future=notify(u.tg_id))

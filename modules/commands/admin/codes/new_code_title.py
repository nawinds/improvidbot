from config import ADMIN_ID, BOT_USERNAME
from modules.bot import bot
from modules.logger import get_logger
from modules.states import change_state
from db import db_session
from db.codes import Code

codes_logger = get_logger("codes")


async def new_code_title(message, text, prefix):
    try:
        title = text.split(". ")[1]
    except IndexError:
        await bot.send_message(ADMIN_ID, "Вы ввели название в неверном формате! Повторите попытку")
        codes_logger.info(f"Название {prefix}-кода в неверном формате!")
        return
    session = db_session.create_session()
    code = session.query(Code).filter(Code.id == text.split(". ")[0]).first()
    try:
        code.title = title
    except AttributeError:
        await bot.send_message(ADMIN_ID, "Ошибка! Код не найден!")
        codes_logger.info(f"{prefix}-код не найден!")
        change_state(message)
        return
    session.commit()
    await bot.send_message(ADMIN_ID, f"{code.title}\nhttps://t.me/{BOT_USERNAME}?start={prefix}-{code.code}")
    codes_logger.info(f"Изменено название {prefix}-кода! {code.title}: {code.code}")
    change_state(message)

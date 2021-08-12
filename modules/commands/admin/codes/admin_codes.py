from config import ADMIN_ID
from modules.bot import bot, dp, Filter
from modules.logger import get_logger
from modules.states import change_state, get_state
from modules.commands.admin.codes.new_code_title import new_code_title
from modules.decorators import main_admin
from db import db_session
from db.states import NEW_ADMIN_CODE_TITLE_STATE
from db.codes import Code
import random
import string

admin_codes_logger = get_logger("admin_codes_commands")


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=["new_admin_code"])
async def new_admin_code(message):
    letters = string.ascii_lowercase
    session = db_session.create_session()
    code_db = True
    while code_db:
        code = ''.join(random.choice(letters) for _ in range(25))
        code_db = session.query(Code).filter(Code.code == code, Code.type == 1).first()
    session.add(Code(code=code, type=1))
    session.commit()
    code_db = session.query(Code).filter(Code.code == code, Code.type == 1).first()
    await bot.send_message(ADMIN_ID, f"Новый админ-код с id: {code_db.id}. Придумайте ему "
                                     f"название: {code_db.id}. Название")
    admin_codes_logger.info(f"Новый админ-код с id: {code_db.id}")
    change_state(message, NEW_ADMIN_CODE_TITLE_STATE)


@dp.message_handler(Filter(lambda m: main_admin(m)), commands=["edit_admin_title"])
async def edit_admin_title(message):
    await new_code_title(message, " ".join(message.text.split()[1:]), 'admininvite')


@dp.message_handler(Filter(lambda m: get_state(m) == NEW_ADMIN_CODE_TITLE_STATE), content_types=["text"])
async def new_admin_code_title(message):
    await new_code_title(message, message.text, 'admininvite')


@dp.message_handler(Filter(lambda message: main_admin(message)), commands=["all_admin_codes"])
async def all_admin_codes(message):
    session = db_session.create_session()
    codes = session.query(Code).filter(Code.type == 1).all()
    data = '\n\n'.join([f'{code.id}. {code.title}' for code in codes])
    text = f"Список пригласительных кодов админов:\n{data}"
    await bot.send_message(ADMIN_ID, text)

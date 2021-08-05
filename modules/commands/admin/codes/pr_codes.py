from config import ADMIN_ID
from modules.bot import bot
from modules.logger import get_logger
from modules.states import change_state, get_state
from modules.commands.admin.codes.new_code_title import new_code_title
from modules.decorators import main_admin
from db import db_session
from db.users import User
from db.codes import Code
from db.states import NEW_PR_CODE_TITLE_STATE
import random
import string


pr_codes_logger = get_logger("admin_pr_codes_commands")


@bot.message_handler(commands=["new_pr_code"], func=lambda message: main_admin(message))
def new_pr_code(message):
    code_db = True
    letters = string.ascii_lowercase
    session = db_session.create_session()
    while code_db:
        code = ''.join(random.choice(letters) for _ in range(20))
        code_db = session.query(Code).filter(Code.code == code, Code.type == 2).first()
    session.add(Code(code=code, type=2))
    session.commit()
    code_db = session.query(Code).filter(Code.code == code, Code.type == 2).first()
    bot.send_message(ADMIN_ID, f"Новый пригласительный код с id: {code_db.id}. "
                               f"Придумайте ему название: {code_db.id}. Название")
    pr_codes_logger.info(f"Новый pr-код с id: {code_db.id}")
    change_state(message, NEW_PR_CODE_TITLE_STATE)


@bot.message_handler(commands=["edit_pr_title"], func=lambda m: main_admin(m))
def edit_pr_title(message):
    new_code_title(message, " ".join(message.text.split()[1:]), 'pr')


@bot.message_handler(content_types=["text"], func=lambda m: get_state(m) == NEW_PR_CODE_TITLE_STATE)
def new_pr_code_title(message):
    new_code_title(message, message.text, 'pr')


@bot.message_handler(commands=["all_pr_codes"], func=lambda message: main_admin(message))
def all_pr_codes(message):
    session = db_session.create_session()
    codes = session.query(Code).filter(Code.type == 2).all()
    text = "Список pr-кодов:\n"
    data = {}
    used_data = []
    for code in codes:
        used = len(session.query(User).filter(User.code_id == code.id).all())
        used_data.append(used)
        if used in data.keys():
            data[used].append(f'{code.id}. {code.title} ({used})\n\n')
        else:
            data[used] = [f'{code.id}. {code.title} ({used})\n\n']
    used_data.sort(reverse=True)
    for i in used_data:
        for u in data[i]:
            text += u
    bot.send_message(ADMIN_ID, text)

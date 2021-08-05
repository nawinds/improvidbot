from config import ADMIN_ID
from db.db_session import create_session
from db.users import User


def admin(message):
    session = create_session()
    check = session.query(User).filter(User.is_admin == True, User.tg_id == message.from_user.id).first()
    return True if check else False


def main_admin(message):
    return True if message.from_user.id == ADMIN_ID else False

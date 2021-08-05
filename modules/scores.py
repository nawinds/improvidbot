from modules.logger import get_logger
from db import db_session
from db.users import User
from db.codes import Code

scores_logger = get_logger("scores")


def add_score(user_id, value):
    session = db_session.create_session()
    user_db = session.query(User).filter(User.tg_id == user_id).first()
    if not user_db:
        scores_logger.error(f"При начислении баллов пользователю {user_id}, он не был найден в БД")
        return
    user_db.score += value
    session.commit()
    if value > 0:
        code = session.query(Code).filter(Code.id == user_db.code_id).first()
        if not code:
            scores_logger.info(f"При начислении баллов пользователю {user_id}, указанный код не был найден в БД")
            return
        if code.code.isnumeric():
            inviter = session.query(User).filter(User.tg_id == int(code.code)).first()
            if not inviter:
                scores_logger.error(f"При начислении баллов пользователю {user_id}, пригласивший его "
                                    f"человек {code.code} не был найден в БД")
                return
            inviter.score += value / 20
            session.commit()

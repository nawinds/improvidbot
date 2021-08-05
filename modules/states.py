from modules.logger import get_logger
from db import db_session
from db.states import State

logger = get_logger("states")


def change_state(message, new_state=None):
    session = db_session.create_session()
    state = session.query(State).filter(State.user_id == message.from_user.id).first()
    if state:
        session.delete(state)
        session.commit()
    if new_state:
        session.add(State(state=new_state, user_id=message.from_user.id))
        session.commit()


def get_state(message):
    session = db_session.create_session()
    state_db = session.query(State).filter(State.user_id == message.from_user.id).first()
    if state_db:
        return state_db.state

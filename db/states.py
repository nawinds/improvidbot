import sqlalchemy
from db.db_session import SqlAlchemyBase

NEW_VIDEO_TITLE_STATE = 1
NEW_VIDEO_DESCRIPTION_STATE = 2
NEW_VIDEO_ACTORS_STATE = 3
NEW_VIDEO_TAGS_STATE = 4

NEW_PR_CODE_TITLE_STATE = 5
NEW_ADMIN_CODE_TITLE_STATE = 6


class State(SqlAlchemyBase):
    __tablename__ = 'states'

    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, index=True)
    state = sqlalchemy.Column(sqlalchemy.Integer)

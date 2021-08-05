import datetime
import sqlalchemy
from db.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    username = sqlalchemy.Column(sqlalchemy.String, index=True)
    code_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("codes.id"), default=None)
    score = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    joined_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)


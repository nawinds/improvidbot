import sqlalchemy
from db.db_session import SqlAlchemyBase


class Alias(SqlAlchemyBase):
    __tablename__ = 'aliases'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    alias = sqlalchemy.Column(sqlalchemy.String)
    word = sqlalchemy.Column(sqlalchemy.String)

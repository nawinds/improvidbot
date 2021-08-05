import sqlalchemy
from db.db_session import SqlAlchemyBase


class Stats(SqlAlchemyBase):
    __tablename__ = 'stats'

    title = sqlalchemy.Column(sqlalchemy.String, primary_key=True, index=True)
    value = sqlalchemy.Column(sqlalchemy.String)

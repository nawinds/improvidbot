import sqlalchemy
from db.db_session import SqlAlchemyBase


class Code(SqlAlchemyBase):
    __tablename__ = 'codes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    code = sqlalchemy.Column(sqlalchemy.String, index=True)

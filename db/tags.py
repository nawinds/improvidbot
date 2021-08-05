import datetime
import sqlalchemy
from db.db_session import SqlAlchemyBase


class Tag(SqlAlchemyBase):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    tag = sqlalchemy.Column(sqlalchemy.String, index=True)
    coef = sqlalchemy.Column(sqlalchemy.Integer)
    video_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("videos.id"), index=True)
    added_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.tg_id"), nullable=True, index=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    def __repr__(self):
        return self.tag

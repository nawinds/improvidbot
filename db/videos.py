import datetime
import sqlalchemy
from db.db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Video(SqlAlchemyBase):
    __tablename__ = 'videos'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    url = sqlalchemy.Column(sqlalchemy.String)
    thumb_url = sqlalchemy.Column(sqlalchemy.String)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    used = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    last_edited = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    active = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    actors = orm.relation("Actor",
                          secondary="video_actors",
                          backref="videos")
    tags = orm.relation("Tag",
                        backref="videos")

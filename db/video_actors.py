import datetime
import sqlalchemy
from db.db_session import SqlAlchemyBase


class Actor(SqlAlchemyBase):
    __tablename__ = 'actors'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, index=True)
    added_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.tg_id"), nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    association_table = sqlalchemy.Table(
        'video_actors',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('videos', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('videos.id')),
        sqlalchemy.Column('actors', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('actors.id'))
    )

    def __repr__(self):
        return self.name

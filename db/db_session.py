import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

import config
from modules.logger import get_logger


db_logger = get_logger("db_global_init")

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    import db.__all_models
    from db.users import User
    from db.video_actors import Actor
    from db.aliases import Alias
    from db.stats import Stats

    SqlAlchemyBase.metadata.create_all(engine)
    session = create_session()
    if not session.query(User).filter(User.tg_id == config.ADMIN_ID).first():
        session.add(User(tg_id=config.ADMIN_ID, username="VoneskA_N", is_admin=True))
        session.commit()
        db_logger.info("Главный админ добавлен в базу")
    for actor in config.ACTORS:
        if not session.query(Actor).filter(Actor.name == actor).first():
            session.add(Actor(name=actor, added_id=None))
            db_logger.info(f"Актер {actor} добавлен в базу")
    for actor, v in config.ALIASES.items():
        for al in v:
            if not session.query(Alias).filter(Alias.alias == al.lower()).first():
                session.add(Alias(alias=al.lower(), word=actor.lower()))
                db_logger.info(f"Алиас {al.lower()} -> {actor} добавлен в базу")
    session.commit()
    if not session.query(Stats).filter(Stats.title == "all_queries").first():
        session.add(Stats(title="all_queries", value=0))
        session.commit()
        db_logger.info("all_queries добавлен в базу")
    if not session.query(Stats).filter(Stats.title == "chosen_queries").first():
        session.add(Stats(title="chosen_queries", value=0))
        session.commit()
        db_logger.info("chosen_queries добавлен в базу")
    if not session.query(Stats).filter(Stats.title == "no_res_queries").first():
        session.add(Stats(title="no_res_queries", value=0))
        session.commit()
        db_logger.info("no_res_queries добавлен в базу")
    if not session.query(Stats).filter(Stats.title == "average_q_res").first():
        session.add(Stats(title="average_q_res", value=0))
        session.commit()
        db_logger.info("average_q_res добавлен в базу")


def create_session() -> Session:
    global __factory
    return __factory()

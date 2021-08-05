from config import ADMIN_ID
from modules.bot import bot
from modules.decorators import main_admin
from modules.logger import get_logger
from modules.text_func import normalize, get_text_variants
from db import db_session
from db.videos import Video
from db.tags import Tag
from db.video_actors import Actor

admin_videos_logger = get_logger("admin_videos_commands")


@bot.message_handler(commands=['get_user_videos'], func=lambda message: main_admin(message))
def get_user_videos(message):
    try:
        user_id = message.text.split()[1]
    except (IndexError, ValueError):
        bot.send_message(f"Неверный формат! /get_user_videos user_id")
        return
    session = db_session.create_session()
    videos = session.query(Video).filter(Video.author_id == user_id). \
        order_by(Video.used.desc()).all()
    data = str()
    for video in videos:
        data += f"<b>{video.id}. {video.title}</b> (использовалось {video.used} раз)," \
                f" {'активно' if video.active else 'неактивно'}, " \
                f"{len(video.actors)} актёров, {len(video.tags)} тегов, " \
                f"загружено {video.created_date}.\n\n"
    bot.send_message(message.from_user.id, f"Загруженные этим пользователем видео:\n\n"
                                           f"{data}", parse_mode="html")


@bot.message_handler(commands=["edit_title"], func=lambda message: main_admin(message))
def edit_title_cmd(message):
    vid_id, title = message.text.split()[1], " ".join(message.text.split()[2:])
    edit_title(vid_id, title)


def edit_title(vid_id, title):
    s = db_session.create_session()
    video = s.query(Video).filter(Video.id == vid_id).first()
    if not video:
        bot.send_message(ADMIN_ID, "Видео не найдено!")
        admin_videos_logger.info("Видео для изменения названия не найдено")
        return
    old = video.title
    video.title = title
    s.commit()
    variants, short = get_text_variants(title)
    tags = variants + short
    for tag in tags:
        tag_db = s.query(Tag).filter(Tag.video_id == video.id, Tag.tag == tag).first()
        if not tag_db:
            s.add(Tag(tag=tag, added_id=ADMIN_ID, video_id=video.id,
                      coef=len(tag.split()) * 4))
            s.commit()
    bot.send_message(ADMIN_ID, "Название успешно сменено!")
    admin_videos_logger.info(f"Название видео {video.id} сменено с {old} на {title}.")


@bot.message_handler(commands=["edit_description"], func=lambda message: main_admin(message))
def edit_description_cmd(message):
    vid_id, description = message.text.split()[1], " ".join(message.text.split()[2:])
    edit_description(vid_id, description)


def edit_description(vid_id, description):
    s = db_session.create_session()
    video = s.query(Video).filter(Video.id == vid_id).first()
    if not video:
        bot.send_message(ADMIN_ID, "Видео не найдено!")
        admin_videos_logger.info("Видео для изменения описания не найдено")
        return
    old = video.description
    video.description = description
    s.commit()
    variants, short = get_text_variants(description)
    tags = variants + short
    for tag in tags:
        tag_db = s.query(Tag).filter(Tag.video_id == video.id, Tag.tag == tag).first()
        if not tag_db:
            s.add(Tag(tag=tag, added_id=ADMIN_ID, video_id=video.id,
                      coef=len(tag.split()) * 4))
            s.commit()
    bot.send_message(ADMIN_ID, "Описание успешно сменено!")
    admin_videos_logger.info(f"Описание видео {video.id} сменено с {old} на {description}.")


@bot.message_handler(commands=["edit_actors"], func=lambda message: main_admin(message))
def edit_actors_cmd(message):
    vid_id, actors = message.text.split()[1], " ".join(message.text.split()[2:]).split(", ")
    edit_actors(vid_id, actors)


def edit_actors(vid_id, actors):
    s = db_session.create_session()
    video = s.query(Video).filter(Video.id == vid_id).first()
    if not video:
        bot.send_message(ADMIN_ID, "Видео не найдено!")
        admin_videos_logger.info(f"Видео {vid_id} для изменения состава актеров не найдено")
        return
    old = video.actors
    for actor in video.actors:
        video.actors.remove(actor)
        admin_videos_logger.info(f"Актёр {actor.name} видео {vid_id} удалён")
        s.commit()
    for actor in actors:
        if not s.query(Actor).filter(Actor.name == actor).first():
            s.add(Actor(name=actor, added_id=ADMIN_ID))
            s.commit()
            admin_videos_logger.info(f"Актёр {actor} добавлен")
        db_actor = s.query(Actor).filter(Actor.name == actor).first()
        video.actors.append(db_actor)
        s.commit()
        admin_videos_logger.info(f"Актёр {actor} добавлен к видео {vid_id}")
        tag = " ".join(normalize(actor))
        tag_db = s.query(Tag).filter(Tag.video_id == video.id, Tag.tag == tag).first()
        if not tag_db:
            s.add(Tag(tag=tag, added_id=ADMIN_ID, video_id=video.id,
                      coef=4 * 2))
            s.commit()

    bot.send_message(ADMIN_ID, "Актёры успешно обновлены!")
    admin_videos_logger.info(f"Актеры видео {video.id} обновлены с {old} на {actors}.")


@bot.message_handler(commands=["delete_tag"], func=lambda message: main_admin(message))
def del_tag_cmd(message):
    vid_id, tag = message.text.split()[1], " ".join(message.text.split()[2:])
    del_tag(vid_id, tag)


@bot.message_handler(commands=["delete_all_tags"], func=lambda message: main_admin(message))
def del_all_tags_cmd(message):
    vid_id = message.text.split()[1]
    del_all_tags(vid_id)


def del_all_tags(vid_id):
    s = db_session.create_session()
    tags = s.query(Tag).filter(Tag.video_id == vid_id).all()
    for tag in tags:
        del_tag(vid_id, tag.tag, True)
    bot.send_message(ADMIN_ID, "Все теги удалены!")
    admin_videos_logger.info(f"Все теги видео {vid_id} удалены")


def del_tag(vid_id, tag, del_all=False):
    s = db_session.create_session()
    video = s.query(Video).filter(Video.id == vid_id).first()
    if not video:
        bot.send_message(ADMIN_ID, "Видео не найдено!")
        admin_videos_logger.info(f"Видео {vid_id} не найдено")
        return
    tag = " ".join(normalize(tag))
    db_tag = s.query(Tag).filter(Tag.tag == tag, Tag.video_id == vid_id).first()
    if not db_tag:
        bot.send_message(ADMIN_ID, f"Тег {tag} не найден!")
        admin_videos_logger.info(f"Тег {tag} видео {vid_id} не найден")
        return
    s.delete(db_tag)
    s.commit()
    if not del_all:
        bot.send_message(ADMIN_ID, "Тег успешно удалён!")
        admin_videos_logger.info(f"Тег {tag} видео {video.id} удалён")


@bot.message_handler(commands=["add_tag"], func=lambda message: main_admin(message))
def add_tag_cmd(message):
    vid_id, tag = message.text.split()[1], " ".join(message.text.split()[2:])
    add_tag(vid_id, tag)


def add_tag(vid_id, tag):
    s = db_session.create_session()
    video = s.query(Video).filter(Video.id == vid_id).first()
    if not video:
        bot.send_message(ADMIN_ID, "Видео не найдено!")
        return
    tag = " ".join(normalize(tag))
    db_tag = s.query(Tag).filter(Tag.tag == tag, Tag.video_id == vid_id).first()
    if db_tag:
        bot.send_message(ADMIN_ID, "Тег уже существует")
        admin_videos_logger.info(f"Тег {tag} уже существует в видео {vid_id}")
        return
    s.add(Tag(tag=tag, added_id=ADMIN_ID, video_id=video.id,
              coef=len(tag.split()) * 3))
    s.commit()
    db_tag = s.query(Tag).filter(Tag.tag == tag, Tag.video_id == vid_id).first()
    video.tags.append(db_tag)
    s.commit()
    bot.send_message(ADMIN_ID, "Тег успешно добавлен!")
    admin_videos_logger.info(f"Тег {tag} успешно добавлен к видео {vid_id}")

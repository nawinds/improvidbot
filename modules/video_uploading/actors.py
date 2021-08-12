from config import ADMIN_USERNAME, WHITE_SYMBOLS
from modules.bot import bot, dp, Filter
from modules.text_func import normalize
from modules.states import get_state, change_state
from modules.logger import get_logger
from db import db_session
from db.videos import Video
from db.video_actors import Actor
from db.tags import Tag
from db.states import NEW_VIDEO_ACTORS_STATE, NEW_VIDEO_TAGS_STATE
from aiogram.types import ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove

logger = get_logger("new_video_actors")
text_field = ForceReply(selective=False)


@dp.message_handler(Filter(lambda message: get_state(message) == NEW_VIDEO_ACTORS_STATE))
async def new_video_actors(message):
    actor = message.text
    if actor == "Всё":
        markup = ReplyKeyboardRemove(selective=False)
        session = db_session.create_session()
        video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                            Video.last_edited == True).first()
        actors = [i.name for i in video.actors]
        await bot.send_message(message.from_user.id, "Отлично! Выбранные актёры: " + ", ".join(actors),
                         reply_markup=markup)
        markup = ReplyKeyboardMarkup()
        markup.add("Всё")
        await bot.send_message(message.from_user.id, "<b>Теперь нужно добавить к видео теги</b>. Здесь хорошо будет "
                                               "указать <b>фразы, часто использующиеся в диалогах</b> "
                                               "(например, \"Как дела?\"), которые это видео может собой "
                                               "заменить. Тогда это видео можно будет использовать вместо "
                                               "стикера. Здесь также можно указать другие ключевые слова, "
                                               "по которым это видео могут искать. Чтобы ввести теги, "
                                               "присылайте по одному тегу в одном сообщении. Если "
                                               "закончите с тегами, напишите <b>\"Всё\"</b>. Обратите "
                                               "внимание, что слово \"Всё\" не может быть одним из тегов. "
                                               "<b>После каждого сообщения дожидайтесь ответа, "
                                               "чтобы всё сохранилось!</b>\n\n"
                                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         parse_mode="html", reply_markup=markup, disable_web_page_preview=True)
        change_state(message, NEW_VIDEO_TAGS_STATE)
    elif len(actor.split()) != 2:
        await bot.send_message(message.from_user.id, f"Пожалуйста, напишите только имя и фамилию двумя словами. "
                                               f"Если что-то не так, пишите @{ADMIN_USERNAME}\n\n"
                                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         parse_mode="html", disable_web_page_preview=True)
        logger.info("Некорректное кол-во слов в имени актера")
        return
    elif any([i not in WHITE_SYMBOLS for i in actor]):
        await bot.send_message(message.from_user.id, f"Пожалуйста, напишите только имя и фамилию двумя словами. "
                                               f"Вы использовали дополнительные символы. Пожалуйста, "
                                               f"обойдитесь без них. "
                                               f"Если что-то не так, пишите @{ADMIN_USERNAME}\n\n"
                                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         parse_mode="html", disable_web_page_preview=True)
        logger.info("Недопустимые символы в имени актера")
        return
    elif len(actor) > 30:
        await bot.send_message(message.from_user.id, f"Слишком длинное имя (более 30 символов). "
                                               f"Пожалуйста, удостоверьтесь, что Вы написали имя и фамилию. "
                                               f"Если всё правильно, пишите @{ADMIN_USERNAME}\n\n"
                                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         parse_mode="html", disable_web_page_preview=True)
        logger.info("Слишком длинное имя актера (более 30 символов)")
        return
    if actor != "Всё":
        session = db_session.create_session()
        video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                            Video.last_edited == True).first()
        if not session.query(Actor).filter(Actor.name == actor).first():
            session.add(Actor(name=actor, added_id=message.from_user.id))
            session.commit()
        db_actor = session.query(Actor).filter(Actor.name == actor).first()
        video.actors.append(db_actor)
        session.commit()
        tag = " ".join(normalize(actor))
        tag_db = session.query(Tag).filter(Tag.video_id == video.id, Tag.tag == tag).first()
        if tag_db:
            tag_db.coef += 4 * 2
            session.commit()
        else:
            session.add(Tag(tag=tag, added_id=message.from_user.id, video_id=video.id,
                            coef=4 * 2))
            session.commit()
        await bot.send_message(message.from_user.id, f"{actor}, отлично. Кто-то ещё?\n\n"
                                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         parse_mode="html", disable_web_page_preview=True)

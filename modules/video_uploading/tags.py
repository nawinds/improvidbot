from config import ADMIN_USERNAME
from modules.bot import bot, dp, Filter
from modules.decorators import main_admin, admin
from modules.logger import get_logger
from modules.text_func import normalize
from modules.states import get_state, change_state
from modules.video_uploading.new_video_handler import new_video_notify
from modules.scores import add_score
from db import db_session
from db.videos import Video
from db.tags import Tag
from db.states import NEW_VIDEO_TAGS_STATE
from aiogram.types import ForceReply, ReplyKeyboardRemove

logger = get_logger("new_video_tags")
text_field = ForceReply(selective=False)


@dp.message_handler(Filter(lambda message: get_state(message) == NEW_VIDEO_TAGS_STATE))
async def new_video_tags(message):
    tag = message.text
    if not tag:
        await bot.send_message(message.from_user.id,
                               f"Пожалуйста, введите тег текстом\n"
                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                               "i-uvelichivat-ih-prosmotry-07-03\">"
                               "Советы по оформлению ролика</a>\n"
                               "/cancel для отмены загрузки и удаления ролика</i>",
                               parse_mode="html", disable_web_page_preview=True)
        logger.info("Тег не указан")
        return
    elif len(tag) >= 50:
        await bot.send_message(message.from_user.id,
                               f"Тег слишком длинный (больше 50 символов). Пожалуйста, "
                               f"разбейте его на более короткие. "
                               f"Если что-то не так, пишите @{ADMIN_USERNAME}\n\n"
                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                               "i-uvelichivat-ih-prosmotry-07-03\">"
                               "Советы по оформлению ролика</a>\n"
                               "/cancel для отмены загрузки и удаления ролика</i>",
                               parse_mode="html", disable_web_page_preview=True)
        logger.info("Тег слишком длинный (больше 50 символов)")
        return
    if tag != "Всё":
        processed_tag = " ".join(normalize(tag))
        session = db_session.create_session()
        video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                            Video.last_edited == True).first()
        tag_db = session.query(Tag).filter(Tag.video_id == video.id, Tag.tag == processed_tag).first()
        if not tag_db:
            session.add(Tag(tag=processed_tag, added_id=message.from_user.id, video_id=video.id,
                            coef=len(processed_tag.split()) * 3))
            session.commit()
        await bot.send_message(message.from_user.id,
                               f"{tag}, отлично. Что-то ещё?\n"
                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                               "i-uvelichivat-ih-prosmotry-07-03\">"
                               "Советы по оформлению ролика</a>\n"
                               "/cancel для отмены загрузки и удаления ролика</i>",
                               parse_mode="html", disable_web_page_preview=True)
    else:
        markup = ReplyKeyboardRemove(selective=False)
        session = db_session.create_session()
        video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                            Video.last_edited == True).first()
        video_id = video.id
        await bot.send_message(message.from_user.id, "Отлично! Видео сохранено под id: " + str(video_id),
                               reply_markup=markup)
        change_state(message)
        if admin(message):
            video.active = True
            add_score(message.from_user.id, 200)
            if not main_admin(message):
                await new_video_notify(video_id, False)
            session.commit()
        else:
            await new_video_notify(video_id, True)

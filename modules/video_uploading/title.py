from modules.bot import bot, dp, Filter
from modules.logger import get_logger
from modules.text_func import get_text_variants
from modules.states import get_state, change_state
from db import db_session
from db.videos import Video
from db.tags import Tag
from db.states import NEW_VIDEO_TITLE_STATE, NEW_VIDEO_DESCRIPTION_STATE
from aiogram.types import ForceReply

logger = get_logger("new_video_title")
text_field = ForceReply(selective=False)


@dp.message_handler(Filter(lambda message: get_state(message) == NEW_VIDEO_TITLE_STATE))
async def new_video_title(message):
    title = message.text
    if title and len(title) <= 100:
        session = db_session.create_session()
        video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                            Video.last_edited == True).first()
        video.title = title
        session.commit()
        variants, short = get_text_variants(title)
        tags = variants + short
        for tag in tags:
            tag_db = session.query(Tag).filter(Tag.video_id == video.id, Tag.tag == tag).first()
            if tag_db:
                tag_db.coef += len(tag.split()) * 6
                session.commit()
            else:
                session.add(Tag(tag=tag, added_id=message.from_user.id, video_id=video.id,
                                coef=len(tag.split()) * 6))
                session.commit()
        await bot.send_message(message.from_user.id,
                               "Придумайте <b>описание</b>\n\n"
                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                               "i-uvelichivat-ih-prosmotry-07-03\">"
                               "Советы по оформлению ролика</a>\n"
                               "/cancel для отмены загрузки и удаления ролика</i>",
                               reply_markup=text_field, parse_mode="html",
                               disable_web_page_preview=True)
        change_state(message, NEW_VIDEO_DESCRIPTION_STATE)
    elif title:
        await bot.send_message(message.from_user.id,
                               "Слишком длинное название (более 100 символов). "
                               "Пожалуйста, попробуйте что-то покороче. Так видео "
                               "будет легче искать.\n\n"
                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                               "i-uvelichivat-ih-prosmotry-07-03\">"
                               "Советы по оформлению ролика</a>\n"
                               "/cancel для отмены загрузки и удаления ролика</i>",
                               reply_markup=text_field, parse_mode="html", disable_web_page_preview=True)
        logger.info("Слишком длинное название")
        return
    else:
        await bot.send_message(message.from_user.id,
                               "Вы ничего не написали. Пожалуйста, выберите, "
                               "как назвать видео\n\n"
                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                               "i-uvelichivat-ih-prosmotry-07-03\">"
                               "Советы по оформлению ролика</a>\n"
                               "/cancel для отмены загрузки и удаления ролика</i>",
                               reply_markup=text_field, parse_mode="html",
                               disable_web_page_preview=True)
        logger.info("Название не указано")

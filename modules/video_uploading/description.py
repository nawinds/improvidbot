from config import ACTORS
from modules.bot import bot
from modules.logger import get_logger
from modules.text_func import get_text_variants
from modules.states import get_state, change_state
from db.states import NEW_VIDEO_DESCRIPTION_STATE, NEW_VIDEO_ACTORS_STATE
from db import db_session
from db.videos import Video
from db.tags import Tag
from telebot.types import ForceReply, ReplyKeyboardMarkup

logger = get_logger("new_video_description")
text_field = ForceReply(selective=False)


@bot.message_handler(func=lambda message: get_state(message) == NEW_VIDEO_DESCRIPTION_STATE)
def new_video_description(message):
    description = message.text
    if description != "" and len(description) <= 5000:
        session = db_session.create_session()
        video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                            Video.last_edited == True).first()
        video.description = description
        session.commit()
        variants, short = get_text_variants(description)
        tags = variants + short
        for tag in tags:
            tag_db = session.query(Tag).filter(Tag.video_id == video.id, Tag.tag == tag).first()
            if tag_db:
                tag_db.coef += len(tag.split()) * 4
                session.commit()
            else:
                session.add(Tag(tag=tag, added_id=message.from_user.id, video_id=video.id,
                                coef=len(tag.split()) * 4))
                session.commit()
        markup = ReplyKeyboardMarkup()
        markup.add(*ACTORS + ["Всё"])
        bot.send_message(message.from_user.id, "Если в видео фигурируют <b>конкретные личности, актёры</b>, "
                                               "нажимайте на <b>кнопки с их именами</b>.\n"
                                               "Если их нет на кнопках, введите полное имя и фамилию. "
                                               "<b>Один человек — одно сообщение</b>.\n\n"
                                               "Как только Вы захотите завершить ввод, нажмите <b>\"Всё\"</b>. "
                                               "<b>Пожалуйста, после каждого сообщения дожидайтесь ответа, "
                                               "иначе что-то может не сохраниться.</b>\n\n"
                                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         reply_markup=markup, parse_mode="html", disable_web_page_preview=True)
        change_state(message, NEW_VIDEO_ACTORS_STATE)
    elif description != "":
        bot.send_message(message.from_user.id, "Слишком длинное описание (более 5000 символов). "
                                               "Пожалуйста, попробуйте что-то покороче.\n\n"
                                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         reply_markup=text_field, parse_mode="html", disable_web_page_preview=True)
        logger.info("Слишком длинное описание")
        return
    else:
        bot.send_message(message.from_user.id, "Вы ничего не написали. Пожалуйста, придумайте описание\n\n"
                                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         reply_markup=text_field, parse_mode="html", disable_web_page_preview=True)
        logger.info("Описание не указано")

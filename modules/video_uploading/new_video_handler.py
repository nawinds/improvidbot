from config import ADMIN_USERNAME
from config import ADMIN_ID
from modules.bot import bot, dp, Filter
from modules.states import get_state, change_state
from modules.decorators import main_admin
from modules.logger import get_logger
from db import db_session
from db.videos import Video
from db.users import User
from db.states import NEW_VIDEO_TITLE_STATE, NEW_VIDEO_DESCRIPTION_STATE,\
    NEW_VIDEO_ACTORS_STATE, NEW_VIDEO_TAGS_STATE
from aiogram.types import ForceReply, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

logger = get_logger("new_video_handler")
text_field = ForceReply(selective=False)


@dp.message_handler(Filter(lambda m: get_state(m) is None), content_types=["video"])
async def new_video(message):
    if message.video.duration > 60 and not main_admin(message):
        await bot.send_message(message.from_user.id, f"Длина видео превышает 1 минуту! Обычно видео такой длины "
                                               f"не подходят под формат, для которого создан этот бот. "
                                               f"Обрежьте его или обратитесь к @{ADMIN_USERNAME}\n"
                                               f"<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a></i>", disable_web_page_preview=True)
        logger.info("Длина видео превышает 1 минуту!")
        change_state(message)
        return
    session = db_session.create_session()
    pre_edited = session.query(Video).filter(Video.author_id == message.from_user.id,
                                             Video.last_edited == True).all()
    for i in pre_edited:
        i.last_edited = False
    session.commit()
    video = Video(
        url=message.video.file_id,
        thumb_url=message.video.thumb.file_id,
        author_id=message.from_user.id
    )
    session.add(video)
    session.commit()
    logger.info(f"Загружен новый видеофайл! author: {message.from_user.id},"
                f" url: {message.video.thumb.file_id}")
    user_videos = session.query(Video).filter(Video.author_id == message.from_user.id).all()
    if len(user_videos) < 2:
        await bot.send_message(message.from_user.id, "О! Кажется, это первое видео, которое Вы загрузили. "
                                               "Пожалуйста, не забывайте, что <b>все видео модерируются</b>, "
                                               "а создатель бота в любой момент может удалить или изменить "
                                               "данные какого-то видео. Это может лишить Вас преимуществ "
                                               "загрузки. Чтобы Ваш ролик никто не трогал "
                                               "и он приносил Вам много-много баллов, <b>рекомендуем прочитать "
                                               "<a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "наши несложные советы по загрузке видео</a> =)</b>. А когда вернётесь, "
                                               "придумайте <b>название</b> своего видео и напишите его мне. Обычно "
                                               "здорово, когда названием является <b>самая главная цитата из "
                                               "видео без кавычек и авторства.</b>\n\n"
                                               "<i> Отправьте /cancel, если решите отменить загрузку "
                                               "и удалить ролик</i>", parse_mode="html")
        change_state(message, NEW_VIDEO_TITLE_STATE)
    else:
        await bot.send_message(message.from_user.id, "Как <b>назовём</b> видео?\n\n"
                                               "<i><a href=\"https://telegra.ph/Kak-zagruzhat-video-v-bazu-bota-"
                                               "i-uvelichivat-ih-prosmotry-07-03\">"
                                               "Советы по оформлению ролика</a>\n"
                                               "/cancel для отмены загрузки и удаления ролика</i>",
                         reply_markup=text_field, parse_mode="html", disable_web_page_preview=True)
        change_state(message, NEW_VIDEO_TITLE_STATE)


@dp.message_handler(Filter(lambda message: get_state(message) in [NEW_VIDEO_TITLE_STATE,
                    NEW_VIDEO_DESCRIPTION_STATE, NEW_VIDEO_TAGS_STATE, NEW_VIDEO_ACTORS_STATE]), commands=["cancel"])
async def cancel_uploading(message):
    session = db_session.create_session()
    video = session.query(Video).filter(Video.author_id == message.from_user.id,
                                        Video.last_edited == True).first()
    if not video:
        await bot.send_message(message.from_user.id, "Произошла ошибка. Последнее редактируемое видео не найдено")
        logger.error("Произошла ошибка. Последнее редактируемое видео не найдено")
    session.delete(video)
    session.commit()
    change_state(message)
    await bot.send_message(message.from_user.id, "Загрузка видео успешно отменена. Видео удалено",
                     reply_markup=ReplyKeyboardRemove(selective=False))


async def new_video_notify(video_id, needs_confirmation):
    session = db_session.create_session()
    video = session.query(Video).filter(Video.id == video_id).first()
    if not video:
        logger.error(f"Видео {video_id} не найдено")
    author = session.query(User).filter(User.tg_id == video.author_id).first()
    if not author:
        logger.error(f"Автор {video.author_id} видео {video_id} не найден!")
    key = None
    if needs_confirmation:
        key = InlineKeyboardMarkup()
        but_1 = InlineKeyboardButton(text="Принять", callback_data=f"accept-{video_id}")
        but_2 = InlineKeyboardButton(text="Отклонить", callback_data=f"cancel-{video_id}")
        key.add(but_1, but_2)
    await bot.send_message(ADMIN_ID, f"<b>Загружено новое видео!</b>\n"
                               f"<i>id</i>: <b>{video_id}</b>\n"
                               f"<i>Название</i>: <b>{video.title}</b>\n"
                               f"<i>Описание</i>: <b>{video.description}</b>\n"
                               f"<i>Теги</i>: <b>{video.tags}</b>\n"
                               f"<i>Актеры</i>: <b>{video.actors}</b>\n\n"
                               f"Загрузил @{author.username}", reply_markup=key,
                     parse_mode="html")
    await bot.send_video(ADMIN_ID, video.url)

from modules.bot import bot, dp
from modules.commands.videos import get_videos_page
from modules.logger import get_logger
from modules.scores import add_score
from db import db_session
from db.videos import Video

logger = get_logger("callback")


@dp.callback_query_handler(function=lambda c: c.data.split("-")[0] in ("accept", "cancel", "title",
                                                                       "description", "tags", "actors"))
async def inline_buttons(c):
    command, video_id = c.data.split("-")
    session = db_session.create_session()
    video = session.query(Video).filter(Video.id == video_id).first()
    if not video:
        await bot.answer_callback_query(c.id, text='Ошибка! Возможно, видео удалено', show_alert=True)
        logger.warn('Ошибка! Возможно, видео удалено')
        return
    author = video.author_id
    title = video.title
    if command == "accept":
        video.active = True
        session.commit()
        add_score(author, 200)
        await bot.send_message(author, f"Ваше видео \"{title}\" принято")
        await bot.answer_callback_query(c.id, text="Видео принято", show_alert=True)
        logger.info(f"Видео {video_id} принято")
    elif command == "cancel":
        session.delete(video)
        session.commit()
        await bot.send_message(author, f"Ваше видео \"{title}\" отклонено")
        await bot.answer_callback_query(c.id, text="Видео отклонено", show_alert=True)
        logger.info(f"Видео {video_id} отклонено")


@dp.callback_query_handler(function=lambda c: c.data.split("-")[0] in ("fullpage", "page"))
async def inline_buttons(c):
    command, page = c.data.split("-")
    if command == "fullpage":
        get_videos_page(f"callback {page}", c.from_user.id, True)
    elif command == "page":
        get_videos_page(f"callback {page}", c.from_user.id, False)

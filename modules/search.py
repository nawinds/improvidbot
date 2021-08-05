from modules.logger import get_logger
from modules.text_func import get_text_variants
from modules.bot import bot
from modules.scores import add_score
from db import db_session
from db.videos import Video
from db.video_actors import Actor
from db.tags import Tag
from db.stats import Stats
from telebot.types import ForceReply, InlineQueryResultVideo
import difflib
import time
import pymorphy2

logger = get_logger("search")
text_field = ForceReply(selective=False)
morph = pymorphy2.MorphAnalyzer()


def search(q):
    logger.debug(f"Поиск по запросу: {q}")
    session = db_session.create_session()
    results = {}
    # search by ID
    if (len(q) == 1 and q[0].isdigit()) or any([i in q for i in ["id", "#", "№", "номер"]]):
        for a in q:
            if a.isdigit():
                video = session.query(Video).filter(Video.id == a, Video.active == True).first()
                if video.id in results.keys():
                    results[video.id] += 1000
                elif video:
                    results[video.id] = 1000
    variants, short = get_text_variants(q)
    qs = variants + short
    logger.debug(f"Запрос {q} был преобразован в варианты: {qs}")
    # search by query substrings
    for i in qs:
        find_result(i, results)
    rev_res = {}
    for key, value in results.items():
        if value not in rev_res.keys():
            rev_res[value] = [key]
        else:
            rev_res[value].append(key)
    ratings = list(rev_res.keys())
    ratings.sort(reverse=True)
    return rev_res, ratings


def find_result(q, results):
    session = db_session.create_session()
    tags = session.query(Tag).filter(Tag.tag.like(f"%{q}%")).all()
    logger.debug(f"По варианту были найдены теги: {tags}")
    for tag in tags:
        tag_coef = difflib.SequenceMatcher(None, q, tag.tag).ratio()
        if tag_coef > 0.2:
            video = session.query(Video).filter(Video.id == tag.video_id, Video.active == True).first()
            if video:
                tags_count = len(video.tags)
                if video.id in results.keys():
                    results[video.id] += tag.coef * tag_coef / tags_count
                else:
                    results[video.id] = tag.coef * tag_coef / tags_count
            else:
                logger.warn(f"Для тега {tag} не найдено видео")

    # TITLE like
    videos = session.query(Video).filter(Video.title.like(f"%{q}%"), Video.active == True).all()
    for i in videos:
        title_coef = difflib.SequenceMatcher(None, q, i.title).ratio()
        title_length = len(i.title)
        if i.id in results.keys():
            results[i.id] += 8 * title_coef * title_length / 35
        else:
            results[i.id] = 8 * title_coef * title_length / 35
    # description %like%
    videos = session.query(Video).filter(Video.description.like(f"%{q}%"), Video.active == True).all()
    for i in videos:
        desc_coef = difflib.SequenceMatcher(None, q, i.description).ratio()
        desc_length = len(i.description)
        if i.id in results.keys():
            results[i.id] += 7 * desc_coef * desc_length / 40
        else:
            results[i.id] = 7 * desc_coef * desc_length / 40
    actors = session.query(Actor).filter(Actor.name == q).all()
    for actor in actors:
        for i in actor.videos:
            if i.id in results.keys():
                results[i.id] += 0.1
            else:
                results[i.id] = 0.1
    return results


@bot.inline_handler(func=lambda query: True)
def query_text(inline_query):
    session = db_session.create_session()
    all_queries = session.query(Stats).filter(Stats.title == "all_queries").first()
    all_queries.value = str(int(all_queries.value) + 1)
    session.commit()
    start = time.time()
    rev_res, ratings = search(inline_query.query)
    count = 0
    out = []
    for rating in ratings:
        for res in rev_res[rating]:
            video = session.query(Video).filter(Video.id == res).first()
            if video:
                out.append(InlineQueryResultVideo(video.id, video.url, "video/mp4", video.thumb_url,
                                                  f"{video.title}",
                                                  description=f"{video.id}.{video.description} {video.actors}"))
            else:
                logger.error(f"Видео {res} не найдено при выполнении поиска")
            count += 1
            if count == 45:
                break
        if count == 45:
            break
    logger.debug(f"Поиск видео по запросу {inline_query.query} занял {time.time() - start} секунд")
    if not out:
        no_res_queries = session.query(Stats).filter(Stats.title == "no_res_queries").first()
        no_res_queries.value = str(int(no_res_queries.value) + 1)
        session.commit()
        logger.warn(f"По поисковому запросу \"{inline_query.query}\" пользователя "
                    f"{inline_query.from_user.id} ничего не нашлось")
    bot.answer_inline_query(inline_query.id, out, cache_time=10)


@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    logger.debug(f"Пользователь {chosen_inline_result.from_user.id} выбрал видео "
                 f"id {chosen_inline_result.result_id} по инлайн-запросу {chosen_inline_result.query}")
    session = db_session.create_session()
    add_score(chosen_inline_result.from_user.id, 20)
    rev_res, ratings = search(chosen_inline_result.query)
    selected_video_id = int(chosen_inline_result.result_id)
    video = session.query(Video).filter(Video.id == selected_video_id, Video.active == True).first()
    if not video:
        logger.error(f"При обработке выбранного в инлайн видео видео с id "
                     f"{selected_video_id} не было найдено")
        return
    video.used += 1
    session.commit()
    add_score(video.author_id, 20)
    variants, short = get_text_variants(chosen_inline_result.query)
    tags = variants + short
    videos = []
    count = 1
    for i in ratings:
        for v in rev_res[i]:
            if v != selected_video_id:
                videos.append(v)
                count += 1
            else:
                break
        if v == selected_video_id:
            break
    chosen_queries = session.query(Stats).filter(Stats.title == "chosen_queries").first()
    average_q_res = session.query(Stats).filter(Stats.title == "average_q_res").first()

    average_q_res.value = str((float(average_q_res.value) * int(chosen_queries.value) +
                               count) / (int(chosen_queries.value) + 1))
    chosen_queries.value = str(int(chosen_queries.value) + 1)
    session.commit()
    for tag in tags:
        tag_db = session.query(Tag).filter(Tag.tag == tag, Tag.video_id == selected_video_id).first()
        if tag_db:
            tag_db.coef += len(tag.split())
            session.commit()
        else:
            session.add(Tag(tag=tag, added_id=chosen_inline_result.from_user.id, video_id=selected_video_id,
                            coef=len(tag.split())))
            session.commit()
            logger.debug(f"После выбора инлайн-результата пользователем "
                         f"{chosen_inline_result.from_user.id} был добавлен тег \"{tag}\"")
        tag2_db = session.query(Tag).filter(Tag.tag == tag, Tag.video_id.in_(videos)).first()
        if tag2_db:
            tag2_db.coef -= len(tag.split()) * 0.33
            session.commit()

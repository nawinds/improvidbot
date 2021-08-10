import config
from modules.bot import bot
from modules.logger import get_logger
from db import db_session
from db.videos import Video
import os
import shutil
import sys
import traceback
from time import sleep
from PIL import Image
import cv2
import imagehash

logger = get_logger("repeats_search")


async def check_repeats(video, checking=1):
    logger.info(f"CHECKING REPEATS FOR {video.id}")
    os.mkdir(f"{config.LOCAL_PATH}/videos/{video.id}")
    res = open(f"{config.LOCAL_PATH}/videos/{video.id}/res.txt", "w")
    res.close()
    # download uploaded video
    v = await bot.get_file(video.url)
    downloaded_file = await bot.download_file(v.file_path)
    new = f"{config.LOCAL_PATH}/videos/{video.id}/{video.id}.mp4"
    with open(new, 'wb') as new_file:
        new_file.write(downloaded_file)

    os.mkdir(f"{config.LOCAL_PATH}/videos/{video.id}/frames{video.id}")
    frame_hashes = await hashes_get(video, video)
    os.remove(f"{config.LOCAL_PATH}/videos/{video.id}/{video.id}.mp4")

    session = db_session.create_session()
    videos = session.query(Video).filter(Video.active == True, Video.id != video.id,
                                         Video.id >= checking).all()
    for vid in range(len(videos)):
        os.mkdir(f"{config.LOCAL_PATH}/videos/{video.id}/frames{videos[vid].id}")
        v = await bot.get_file(videos[vid].url)
        downloaded_file = await bot.download_file(v.file_path)
        new = f"{config.LOCAL_PATH}/videos/{video.id}/{videos[vid].id}.mp4"
        with open(new, 'wb') as new_file:
            new_file.write(downloaded_file)

        frame_hashes2 = await hashes_get(videos[vid], video)
        os.remove(f"{config.LOCAL_PATH}/videos/{video.id}/{videos[vid].id}.mp4")
        cnt = 0
        for a in range(len(frame_hashes2)):
            if frame_hashes2[a] in frame_hashes:
                cnt += 1

        shutil.rmtree(f"{config.LOCAL_PATH}/videos/{video.id}/frames{videos[vid].id}")
        if cnt > 0:
            prev = open(f"{config.LOCAL_PATH}/videos/{video.id}/res.txt", "r").read()
            with open(f"{config.LOCAL_PATH}/videos/{video.id}/res.txt", "w") as res:
                res.write(prev + str(videos[vid].id) + " ")
    rep = open(f"{config.LOCAL_PATH}/videos/{video.id}/res.txt", "r").read().split()
    shutil.rmtree(f"{config.LOCAL_PATH}/videos/{video.id}")
    rep = session.query(Video).filter(Video.id.in_(rep)).all()
    logger.info(f"По результатам проверки повторений видео {video.id} имеет общие кадры с {rep}")
    return rep


async def hashes_get(video, uploaded):
    frame_hashes = []
    vidcap = cv2.VideoCapture(f"{config.LOCAL_PATH}/videos/{uploaded.id}/{video.id}.mp4")
    success, image = vidcap.read()
    count = 0
    while success:
        if count % 24 == 0 or uploaded.id == video.id:
            cv2.imwrite(f"{config.LOCAL_PATH}/videos/{uploaded.id}/frames{video.id}/%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vidcap.read()
        if count % 24 == 0 or uploaded.id == video.id:
            frame_hash = imagehash.average_hash(Image.open(
                f"{config.LOCAL_PATH}/videos/{uploaded.id}/frames{video.id}/%d.jpg" % count))
            frame_hashes.append(frame_hash)
        count += 1
    vidcap.release()
    cv2.destroyAllWindows()
    return frame_hashes


async def check_repeated_videos_after_start():
    last_e = None
    while True:
        try:
            session = db_session.create_session()
            to_check = os.listdir(f"{config.LOCAL_PATH}/videos")
            for v in to_check:
                dirs = os.listdir(f"{config.LOCAL_PATH}/videos/{v}")
                n = []
                for d in dirs:
                    if ".mp4" in d:
                        n.append(int(d.split(".")[0]))
                    elif "." not in d:
                        n.append(int(d[6:]))
                while int(v) in n:
                    n.remove(int(v))
                try:
                    vi = max(n)
                except ValueError:
                    vi = 1
                video = session.query(Video).filter(Video.id == v).first()
                shutil.rmtree(f"{config.LOCAL_PATH}/videos/{v}")
                sleep(0.5)
                if video:
                    rep = await check_repeats(video, vi)
                    if rep:
                        logger.warn(f"Видео {video.id} содержит кадры из "
                                    f"видео {', '.join([str(i.id) for i in rep])}!")
                        await bot.send_message(config.ADMIN_ID, f"Видео {video.id} содержит кадры из "
                                                          f"видео {', '.join([str(i.id) for i in rep])}!")
                        await bot.send_video(config.ADMIN_ID, video.url, caption=str(video.id))
                        for i in rep:
                            await bot.send_video(config.ADMIN_ID, i.url, caption=str(i.id))
                    else:
                        await bot.send_message(config.ADMIN_ID, f"Видео {video.id} проверено, повторов нет")
                        logger.info(f"Видео {video.id} проверено, повторов нет")
                else:
                    logger.warn("При запуске бота, обнаружена папка для проверки видео, которого нет в базе.")
            break
        except Exception as e:
            if e.__class__ != last_e.__class__:
                last_e = e
                traceback.print_exception(*sys.exc_info())
                logger.error(e, exc_info=True)
                sleep(2)

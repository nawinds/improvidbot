from modules.bot import bot
from modules.decorators import main_admin


@bot.message_handler(commands=["help"], func=lambda message: main_admin(message))
def help_admin(message):
    text = f"<b>ОБЩИЕ:</b>\n" \
           f"<b>/search q</b> — Поиск видео, где q — поисковый запрос\n" \
           f"<b>/top</b> — Топ активных пользователей\n" \
           f"<b>/all n</b> — Список названий всех видео базы страницами по 20 видео, где n — " \
           f"номер страницы\n" \
           f"<b>/all_full n</b> — Список названий и описаний всех видео базы страницами по 10 видео, где n " \
           f"— номер страницы\n""" \
           f"<b>/random</b> — Случайное видео из базы и полная информация по нему\n" \
           f"<b>/id n</b> — Видео из базы, где n — id видео и полная информация по нему\n" \
           f"<b>/only_media n</b> — Видео из базы, где n — id видео без дополнительной информации.\n" \
           f"<b>/my_videos</b> — Загруженные Вами видео\n" \
           f"<b>/my_referal</b> — Ваша реферальная ссылка\n" \
           f"<b>/articles</b> — Список всех статей\n\n" \
           f"<b>КОДЫ:</b>\n" \
           f"<b>/new_admin_code</b> — Новый пригласительный код админа\n" \
           f"<b>/edit_admin_title id. title</b> — Изменение названия админ-кода\n" \
           f"<b>/new_pr_code</b> — Новый pr-код\n" \
           f"<b>/edit_pr_title id. title</b> — Изменение названия pr-кода\n" \
           f"<b>/all_admin_codes</b> — Все неиспользованные админ-коды\n" \
           f"<b>/all_pr_codes</b> — Все pr-коды\n\n" \
           f"<b>СИСТЕМА:</b>\n" \
           f"<b>/logs file start stop</b> — Файл логов от строки до строки\n" \
           f"<b>/db</b> — Выгрузить БД\n" \
           f"<b>/memory</b> — Информация о расходе памяти\n" \
           f"<b>/stats</b> — Статистика\n\n" \
           f"<b>ПОЛЬЗОВАТЕЛИ:</b>\n" \
           f"<b>/add_score id value</b> — Добавление рейтинга пользователю. Максимум -400 баллов для ошибок " \
           f"при загрузке видео\n" \
           f"<b>/all_admins</b> — Список всех админов\n" \
           f"<b>/ban_admin id</b> — Разжаловать админа\n" \
           f"<b>/find_user @username</b> — Поиск пользователя п юзернейму\n" \
           f"<b>/find_user tg_id</b> — Поиск пользователя по id\n" \
           f"<b>/send tg_id message</b> — Отправка сообщения\n\n" \
           f"<b>ВИДЕО:</b>\n" \
           f"<b>/get_user_videos user_id</b> — Все видео, загруженные пользователем.\n" \
           f"<b>/edit_title id title</b> — Изменение названия\n" \
           f"<b>/edit_description id description</b> — Изменение описания\n" \
           f"<b>/edit_actors id actors</b> — Обновление состава актеров\n" \
           f"<b>/delete_tag id tag</b> — Удаление тега\n" \
           f"<b>/delete_all_tags id</b> — Удаление всех тегов\n" \
           f"<b>/add_tag id tag</b> — Добавление нового тега\n\n" \
           f"<b>/help</b> — Эта страница."
    bot.send_message(message.from_user.id, text, parse_mode="html")

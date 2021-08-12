import os

BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TOKEN = os.getenv("TOKEN")
LOGGER_TOKEN = os.getenv("LOGGER_TOKEN")
LOCAL_PATH = os.getenv("LOCAL_PATH")
DB_PATH = f"{LOCAL_PATH}/db/main.db"
LOGS_PATH = f"{LOCAL_PATH}/logs/main.log"
AIOGRAM_LOGS_PATH = f"{LOCAL_PATH}/logs/aiogram.log"
ACTORS = ["Антон Шастун", "Арсений Попов", "Сергей Матвиенко", "Дмитрий Позов",
          "Павел Воля", "Станислав Шеминов", "Оксана Суркова"]
ALIASES = {"Антон Шастун": ["Шастун", "Шаст", "Антон", "Тоша", "Антоха", "Артон", "Артоны", "Антох",
                            "Тоха", "Антош"],
           "Арсений Попов": ["Арсений", "Арс", "Попов", "Сеня", "Арсюша", "Артон", "Артоны"],
           "Сергей Матвиенко": ["Сергей", "Матвиенко", "Сережа", "Серж", "Серый", "Матвиеныч",
                                "Серега", "Сережка", "Сереж"],
           "Дмитрий Позов": ["Поз", "Позов", "Дима", "Митя", "Димас", "Димка", "Дмитрий"],
           "Павел Воля": ["Паша", "Павлик", "Павел", "Воля", "Пашка"],
           "Станислав Шеминов": ["Стас", "Станислав", "Шеминов", "Стасик"],
           "Оксана Суркова": ["Оксана", "Суркова", "Окси", "Оксан", "Оксанка"],
           "Импровизация": ["импра", "импровизации"]}
WHITE_SYMBOLS = list("0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMёйцукенгшщзхъфывапролджэячсмитьбю"
                     "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ ")


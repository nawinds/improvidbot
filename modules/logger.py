import logging
import telebot
import config
import time


class LoggerFH(logging.FileHandler):
    def __init__(self, filename, logger):
        super().__init__(filename, encoding="utf-8")
        self.bot = telebot.TeleBot(config.LOGGER_TOKEN)
        self.logger = logger

    def handle(self, record):
        super().handle(record)
        if record.levelno >= logging.ERROR:
            msg = self.format(record)
            msg = msg.split("\"")
            for part in range(len(msg)):
                if msg[part].startswith("/home"):
                    msg[part] = f"<u>{msg[part]}</u>"
            msg = "\"".join(msg)
            t0 = time.time()
            while time.time() - t0 < 10:
                try:
                    self.bot.send_message(config.ADMIN_ID, msg, parse_mode="HTML")
                    break
                except Exception:
                    # self.logger.exception("Exception while sending error %s to admin", msg)
                    time.sleep(1)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = LoggerFH(config.LOGS_PATH, logger)
    formatter = logging.Formatter('%(levelname)s %(asctime)s - '
                                  '%(name)s (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

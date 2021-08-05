from config import TOKEN
from modules.logger import get_logger
import telebot

bot_logger = get_logger("bot")


class Bot(telebot.TeleBot):
    logger = bot_logger

    def process_new_updates(self, updates):
        super().process_new_updates(updates)
        for update in updates:
            if update.message:
                bot_logger.debug(f"RECEIVED: FROM: {str(update.message.from_user.id)}\n"
                                 f"TEXT: {update.message.text}")

    def send_message(self, chat_id, text, disable_web_page_preview=None,
                     reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None, timeout=None):
        super().send_message(chat_id, text,
                             disable_web_page_preview=disable_web_page_preview,
                             reply_to_message_id=reply_to_message_id,
                             reply_markup=reply_markup,
                             parse_mode=parse_mode,
                             disable_notification=disable_notification,
                             timeout=timeout)
        bot_logger.debug(f"SENT: TO: {str(chat_id)}\n"
                         f"TEXT: {text}")


bot = Bot(TOKEN)

from abc import ABC
from config import TOKEN
from modules.logger import get_logger
import aiogram
import typing


bot_logger = get_logger("bot")


class Bot(aiogram.Bot):
    logger = bot_logger

    async def send_message(self,
                           chat_id: typing.Union[aiogram.types.base.Integer, aiogram.types.base.String],
                           text: aiogram.types.base.String,
                           parse_mode: typing.Optional[aiogram.types.base.String] = None,
                           entities: typing.Optional[typing.List[aiogram.types.MessageEntity]] = None,
                           disable_web_page_preview: typing.Optional[aiogram.types.base.Boolean] = None,
                           disable_notification: typing.Optional[aiogram.types.base.Boolean] = None,
                           reply_to_message_id: typing.Optional[aiogram.types.base.Integer] = None,
                           allow_sending_without_reply: typing.Optional[aiogram.types.base.Boolean] = None,
                           reply_markup: typing.Union[aiogram.types.InlineKeyboardMarkup,
                                                      aiogram.types.ReplyKeyboardMarkup,
                                                      aiogram.types.ReplyKeyboardRemove,
                                                      aiogram.types.ForceReply, None] = None,
                           ) -> aiogram.types.Message:
        bot_logger.debug(f"SENT: TO: {str(chat_id)}\n"
                         f"TEXT: {text}")
        return await super().send_message(chat_id, text, parse_mode, entities,
                                          disable_web_page_preview, disable_notification,
                                          reply_to_message_id,
                                          allow_sending_without_reply, reply_markup)


class Dispatcher(aiogram.Dispatcher):
    async def process_update(self, update: aiogram.types.Update):
        try:
            if update.message:
                bot_logger.debug(f"RECEIVED: FROM: {str(update.message.from_user.id)}\n"
                                 f"TEXT: {update.message.text}")
        except Exception as e:
            err = await self.errors_handlers.notify(update, e)
            if err:
                return err
            raise
        res = await super().process_update(update)
        return res


class Filter(aiogram.dispatcher.filters.filters.Filter, ABC):
    def __init__(self, func):
        self.func = func

    async def check(self, *args) -> bool:
        return self.func(*args)


bot = Bot(TOKEN)
dp = Dispatcher(bot)

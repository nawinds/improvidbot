from config import TOKEN
from modules.logger import get_logger
from aiogram import types
from aiogram.types import base
import aiogram
import typing


bot_logger = get_logger("bot")


class Dispatcher(aiogram.Dispatcher):
    async def process_update(self, update: types.Update):
        try:
            if update.message:
                bot_logger.debug(f"RECEIVED: FROM: {str(update.message.from_user.id)}\n"
                                 f"TEXT: {update.message.text}")
        except Exception as e:
            err = await self.errors_handlers.notify(update, e)
            if err:
                return err
            raise
        return await super().process_update(update)


class Bot(aiogram.Bot):
    logger = bot_logger

    async def send_message(self,
                           chat_id: typing.Union[base.Integer, base.String],
                           text: base.String,
                           parse_mode: typing.Optional[base.String] = None,
                           entities: typing.Optional[typing.List[types.MessageEntity]] = None,
                           disable_web_page_preview: typing.Optional[base.Boolean] = None,
                           disable_notification: typing.Optional[base.Boolean] = None,
                           reply_to_message_id: typing.Optional[base.Integer] = None,
                           allow_sending_without_reply: typing.Optional[base.Boolean] = None,
                           reply_markup: typing.Union[types.InlineKeyboardMarkup,
                                                      types.ReplyKeyboardMarkup,
                                                      types.ReplyKeyboardRemove,
                                                      types.ForceReply, None] = None,
                           ) -> types.Message:
        bot_logger.debug(f"SENT: TO: {str(chat_id)}\n"
                         f"TEXT: {text}")
        return await super().send_message(chat_id, text,
                                          parse_mode=parse_mode,
                                          entities=entities,
                                          disable_web_page_preview=disable_web_page_preview,
                                          disable_notification=disable_notification,
                                          reply_to_message_id=reply_to_message_id,
                                          allow_sending_without_reply=allow_sending_without_reply,
                                          reply_markup=reply_markup)


bot = Bot(TOKEN)
dispatcher = Dispatcher(bot)

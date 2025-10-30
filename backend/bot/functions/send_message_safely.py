import logging
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from html import escape
from aiogram import Bot

# Настройка логгера
logger = logging.getLogger("bot_logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

async def send_message_safely(bot, chat_id, text, reply_markup=None):
    """Безопасная отправка сообщения с обработкой исключений."""
    try:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)
        logger.info(f"Сообщение успешно отправлено пользователю {chat_id}.")
    except TelegramForbiddenError:
        logger.warning(f"Пользователь {chat_id} заблокировал бота. Сообщение не отправлено.")
        # Удаление или пометка пользователя в базе данных (если необходимо)
        # db.mark_user_inactive(chat_id)  # Пример вызова функции для базы данных
    except TelegramBadRequest as e:
        logger.error(f"Ошибка отправки сообщения для пользователя {chat_id}: {e}")
    except Exception as e:
        logger.critical(f"Неизвестная ошибка при отправке сообщения для пользователя {chat_id}: {e}")


async def edit_message_safely(bot, chat_id, message_id, text, reply_markup=None):
    """
    Безопасная обертка для метода edit_text.
    Логирует ошибки и предотвращает падение приложения.
    """
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
        )
        logger.info("Сообщение успешно отредактировано.")
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при редактировании сообщения: {e}")

class SafeBot(Bot):
    async def send_message(self, chat_id, text, *args, **kwargs):
        # Проверяем, является ли текст строкой
        if isinstance(text, str):
            # Экранируем только пользовательские данные
            safe_text = text.format_map(DefaultEscapeMap())
        else:
            safe_text = text  # Если это не строка, оставляем текст как есть
        return await super().send_message(chat_id, safe_text, *args, **kwargs)


class DefaultEscapeMap(dict):
    def __missing__(self, key):
        return "{" + key + "}"  # Оставляем маркеры формата нетронутыми

    def __getitem__(self, key):
        return escape(super().__getitem__(key)) if key in self else "{" + key + "}"
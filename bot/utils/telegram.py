from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def safe_delete(message: Message) -> None:
    """Try to delete a message; ignore errors (e.g., message already gone)."""
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

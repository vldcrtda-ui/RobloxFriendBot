from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.config import Settings
from bot.services.users import touch_user
from bot.utils.i18n import Translator
from bot.utils.locale import resolve_locale
from bot.db.session import session_scope
from bot.utils.telegram import safe_delete

router = Router(name="common")


@router.message(Command("help"))
async def help_command(
    message: Message,
    translator: Translator,
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    locale = resolve_locale(message, settings.default_language)
    async with session_scope(session_factory) as session:
        await touch_user(session, message.from_user.id)  # type: ignore[arg-type]
    if message.text and message.text.startswith("/"):
        await safe_delete(message)
    await message.answer(translator.t("help", locale))

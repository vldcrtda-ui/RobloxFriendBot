from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.config import Settings
from bot.db.session import session_scope
from bot.services.profile_messages import send_profile_message
from bot.services.users import delete_user, get_user, touch_user
from bot.utils.i18n import Translator
from bot.utils.locale import resolve_locale

router = Router(name="profile")


@router.message(Command("profile"))
async def profile(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
    state: FSMContext,
) -> None:
    base_locale = resolve_locale(message, settings.default_language)
    async with session_scope(session_factory) as session:
        user = await get_user(session, message.from_user.id)  # type: ignore[arg-type]
        if user:
            await touch_user(session, message.from_user.id)  # type: ignore[arg-type]

    if not user:
        await message.answer(translator.t("profile_missing", base_locale))
        return

    locale = user.languages[0] if user.languages else base_locale
    await send_profile_message(message, user, translator, locale)


@router.callback_query(F.data == "profile:edit")
async def edit_placeholder(
    callback: CallbackQuery,
    translator: Translator,
    settings: Settings,
) -> None:
    locale = resolve_locale(callback, settings.default_language)
    await callback.answer()
    if callback.message:
        await callback.message.answer(translator.t("edit_coming_soon", locale))


@router.callback_query(F.data == "profile:delete")
async def delete_profile(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
    state: FSMContext,
) -> None:
    locale = resolve_locale(callback, settings.default_language)
    async with session_scope(session_factory) as session:
        deleted = await delete_user(session, callback.from_user.id)  # type: ignore[arg-type]
    await callback.answer()
    if deleted and callback.message:
        await state.clear()
        await callback.message.answer(translator.t("profile_deleted", locale))
    elif callback.message:
        await callback.message.answer(translator.t("profile_missing", locale))

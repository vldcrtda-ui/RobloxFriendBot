from __future__ import annotations

import re
from difflib import SequenceMatcher

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.config import Settings
from bot.db.session import session_scope
from bot.handlers.states import RegisterState
from bot.keyboards.registration import games_keyboard, language_keyboard, skip_keyboard
from bot.services.games import list_games
from bot.services.schemas import RegistrationData
from bot.services.profile_messages import send_profile_message
from bot.services.users import get_user, upsert_user
from bot.utils.i18n import AVAILABLE_LOCALES, Translator
from bot.utils.locale import resolve_locale
from bot.utils.telegram import safe_delete

router = Router(name="register")

NICKNAME_RE = re.compile(r"^[A-Za-z0-9_-]{3,30}$")
MAX_BIO_LENGTH = 300
MAX_GAMES = 5


@router.message(
    StateFilter(
        RegisterState.wait_nick,
        RegisterState.wait_age,
        RegisterState.wait_language,
        RegisterState.wait_games,
        RegisterState.wait_bio,
        RegisterState.wait_photo,
    ),
    F.text.startswith("/"),
)
async def command_during_onboarding(
    message: Message,
    state: FSMContext,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
) -> None:
    if not message.from_user or message.from_user.is_bot:
        return
    locale = resolve_locale(message, settings.default_language)
    text = (message.text or "").strip()
    await state.clear()
    await safe_delete(message)

    if text.startswith("/start"):
        await cmd_start(message, state, session_factory, translator, settings)
        return
    if text.startswith("/profile"):
        async with session_scope(session_factory) as session:
            user = await get_user(session, message.from_user.id)  # type: ignore[arg-type]
        if user:
            await send_profile_message(
                message,
                user,
                translator,
                user.languages[0] if user.languages else locale,
            )
        else:
            await message.answer(translator.t("profile_missing", locale))
        return

    await message.answer(translator.t("cancel", locale))


@router.message(CommandStart(), StateFilter(None))
async def cmd_start(
    message: Message,
    state: FSMContext,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
) -> None:
    if not message.from_user or message.from_user.is_bot:
        return
    if message.text and message.text.startswith("/"):
        await safe_delete(message)
    await state.clear()
    locale = resolve_locale(message, default=settings.default_language)

    async with session_scope(session_factory) as session:
        existing = await get_user(session, message.from_user.id)  # type: ignore[arg-type]
    if existing:
        await message.answer(translator.t("already_registered", locale))
        await send_profile_message(
            message,
            existing,
            translator,
            existing.languages[0] if existing.languages else locale,
        )
        await message.answer(translator.t("main_menu_hint", locale))
        return

    await state.update_data(locale=locale)
    await message.answer(
        translator.t(
            "start_greeting",
            locale,
            username=message.from_user.first_name if message.from_user else "",
        )
    )
    await message.answer(translator.t("ask_nick", locale))
    await state.set_state(RegisterState.wait_nick)


@router.message(Command("cancel"))
async def cancel(
    message: Message,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    if message.text and message.text.startswith("/"):
        await safe_delete(message)
    locale = resolve_locale(message, settings.default_language)
    await state.clear()
    await message.answer(translator.t("cancel", locale))


@router.message(RegisterState.wait_nick)
async def process_nick(
    message: Message,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("locale") or resolve_locale(message, settings.default_language)
    nick = (message.text or "").strip()
    if not NICKNAME_RE.match(nick):
        await message.answer(translator.t("invalid_nick", locale))
        return
    await state.update_data(roblox_nick=nick)
    await state.set_state(RegisterState.wait_age)
    await message.answer(translator.t("ask_age", locale))


@router.message(RegisterState.wait_age)
async def process_age(
    message: Message,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("locale") or resolve_locale(message, settings.default_language)
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer(translator.t("invalid_age", locale))
        return
    age = int(text)
    if age < 8 or age > 99:
        await message.answer(translator.t("invalid_age", locale))
        return

    await state.update_data(age=age)
    await state.set_state(RegisterState.wait_language)
    await message.answer(
        translator.t("ask_language", locale),
        reply_markup=language_keyboard(translator, locale),
    )


@router.callback_query(RegisterState.wait_language, F.data.startswith("lang:"))
async def process_language(
    callback: CallbackQuery,
    state: FSMContext,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
) -> None:
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer()
        return
    locale = parts[1]
    await callback.answer()
    if locale not in AVAILABLE_LOCALES:
        locale = settings.default_language
    await state.update_data(language=locale, locale=locale)

    async with session_scope(session_factory) as session:
        games = await list_games(session)

    if not games:
        await callback.message.answer(translator.t("games_empty", locale))
        return

    game_payload = [{"id": game.id, "name": game.name, "alias": game.alias} for game in games]
    await state.update_data(selected_games=[], games_catalog=game_payload)
    await state.set_state(RegisterState.wait_games)
    await callback.message.answer(
        translator.t("ask_games", locale),
        reply_markup=games_keyboard(translator, locale, game_payload, set()),
    )


@router.message(RegisterState.wait_games)
async def search_games(
    message: Message,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(message, settings.default_language)
    if not message.text:
        await message.answer(translator.t("ask_games", locale))
        return

    query = message.text.strip().lower()
    games_catalog = data.get("games_catalog", [])
    selected = set(data.get("selected_games", []))

    def similarity(value: str) -> float:
        if not value:
            return 0.0
        return SequenceMatcher(None, query, value).ratio()

    scored = []
    for game in games_catalog:
        name = str(game.get("name", "")).lower()
        alias = str(game.get("alias", "")).lower()
        score = max(similarity(name), similarity(alias))
        if query in name:
            score += 0.35
        if alias and query in alias:
            score += 0.25
        if name.startswith(query):
            score += 0.2
        if alias and alias.startswith(query):
            score += 0.1
        scored.append((score, game))

    scored = [item for item in scored if item[0] >= 0.2]
    scored.sort(key=lambda x: x[0], reverse=True)
    matches = [game for _, game in scored[:20]]

    if not matches:
        await message.answer(translator.t("games_search_none", locale))
        return

    await message.answer(
        translator.t("games_search_found", locale, count=len(matches)),
        reply_markup=games_keyboard(translator, locale, matches, selected),
    )


@router.callback_query(RegisterState.wait_games, F.data.startswith("game:"))
async def toggle_game(
    callback: CallbackQuery,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(callback, settings.default_language)
    selected = set(data.get("selected_games", []))
    try:
        game_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer()
        return

    if game_id in selected:
        selected.remove(game_id)
    else:
        if len(selected) >= MAX_GAMES:
            await callback.answer(translator.t("games_limit", locale), show_alert=True)
            return
        selected.add(game_id)

    await state.update_data(selected_games=list(selected))
    games_catalog = data.get("games_catalog", [])
    await callback.message.edit_reply_markup(
        reply_markup=games_keyboard(translator, locale, games_catalog, selected)
    )
    await callback.answer()


@router.callback_query(RegisterState.wait_games, F.data == "games:done")
async def games_done(
    callback: CallbackQuery,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(callback, settings.default_language)
    selected = data.get("selected_games", [])
    if not selected:
        await callback.answer(translator.t("games_need_one", locale), show_alert=True)
        return

    await state.set_state(RegisterState.wait_bio)
    await callback.message.answer(
        translator.t("ask_bio", locale),
        reply_markup=skip_keyboard(translator.t("skip", locale)),
    )
    await callback.answer()


@router.message(RegisterState.wait_bio)
async def process_bio(
    message: Message,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(message, settings.default_language)
    bio = (message.text or "").strip()
    if len(bio) > MAX_BIO_LENGTH:
        await message.answer(translator.t("bio_too_long", locale))
        return
    await state.update_data(description=bio)
    await message.answer(translator.t("bio_saved", locale))
    await prompt_photo(message, state, translator, locale)


@router.callback_query(RegisterState.wait_bio, F.data == "skip")
async def skip_bio(
    callback: CallbackQuery,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(callback, settings.default_language)
    await state.update_data(description=None)
    await callback.message.answer(translator.t("bio_skipped", locale))
    await callback.answer()
    await prompt_photo(callback.message, state, translator, locale)


async def prompt_photo(message: Message, state: FSMContext, translator: Translator, locale: str) -> None:
    await state.set_state(RegisterState.wait_photo)
    await message.answer(
        translator.t("ask_photo", locale),
        reply_markup=skip_keyboard(translator.t("skip", locale)),
    )


@router.message(RegisterState.wait_photo, F.photo)
async def process_photo(
    message: Message,
    state: FSMContext,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(message, settings.default_language)
    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)
    await message.answer(translator.t("photo_saved", locale))
    await finalize_registration(message, state, session_factory, translator, settings)


@router.callback_query(RegisterState.wait_photo, F.data == "skip")
async def skip_photo(
    callback: CallbackQuery,
    state: FSMContext,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(callback, settings.default_language)
    await state.update_data(photo_id=None)
    await callback.answer(translator.t("photo_skipped", locale))
    await finalize_registration(callback.message, state, session_factory, translator, settings)


@router.message(RegisterState.wait_photo)
async def photo_expected(
    message: Message,
    state: FSMContext,
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(message, settings.default_language)
    await message.answer(
        translator.t("ask_photo", locale),
        reply_markup=skip_keyboard(translator.t("skip", locale)),
    )


async def finalize_registration(
    message: Message,
    state: FSMContext,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    settings: Settings,
) -> None:
    data = await state.get_data()
    locale = data.get("language") or data.get("locale") or resolve_locale(message, settings.default_language)

    payload = RegistrationData(
        tg_id=message.from_user.id,  # type: ignore[arg-type]
        username=message.from_user.username if message.from_user else None,
        roblox_nick=data["roblox_nick"],
        age=data["age"],
        languages=[locale],
        game_ids=[int(i) for i in data.get("selected_games", [])],
        description=data.get("description"),
        photo_id=data.get("photo_id"),
    )

    try:
        async with session_scope(session_factory) as session:
            user = await upsert_user(session, payload)
    except IntegrityError:
        await state.set_state(RegisterState.wait_nick)
        await state.update_data(locale=locale)
        await message.answer(translator.t("nick_taken", locale))
        await message.answer(translator.t("ask_nick", locale))
        return

    await state.clear()
    await message.answer(translator.t("registration_complete", locale))
    await message.answer(translator.t("main_menu_hint", locale))
    await send_profile_message(message, user, translator, locale)

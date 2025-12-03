from __future__ import annotations

from aiogram.types import Message

from bot.db.models import User
from bot.keyboards.profile import profile_actions_keyboard
from bot.utils.formatting import format_profile
from bot.utils.i18n import Translator


async def send_profile_message(
    target: Message,
    user: User,
    translator: Translator,
    locale: str,
    with_actions: bool = True,
) -> None:
    text = format_profile(user, translator, locale)
    markup = profile_actions_keyboard(translator, locale) if with_actions else None

    if user.photo_id:
        await target.answer_photo(user.photo_id, caption=text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)

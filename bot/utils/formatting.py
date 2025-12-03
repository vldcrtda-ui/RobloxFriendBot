from __future__ import annotations

from bot.db.models import User
from bot.utils.i18n import Translator


def format_profile(user: User, tr: Translator, locale: str) -> str:
    languages = ", ".join(user.languages) if user.languages else "-"
    games = ", ".join(game.name for game in user.games) if user.games else "-"
    lines = [
        f"<b>{tr.t('profile_title', locale)}</b>",
        tr.t("profile_username", locale, username=user.username or "—"),
        tr.t("profile_nick", locale, roblox_nick=user.roblox_nick),
        tr.t("profile_age", locale, age=user.age),
        tr.t("profile_langs", locale, languages=languages),
        tr.t("profile_games", locale, games=games),
    ]
    if user.description:
        lines.append(tr.t("profile_bio", locale, bio=user.description))
    else:
        lines.append(tr.t("profile_no_bio", locale))
    return "\n".join(lines)

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RegistrationData:
    tg_id: int
    username: Optional[str]
    roblox_nick: str
    age: int
    languages: List[str]
    game_ids: List[int]
    description: Optional[str] = None
    photo_id: Optional[str] = None

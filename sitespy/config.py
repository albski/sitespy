from dataclasses import dataclass
from pathlib import Path
from typing import List
from sitespy import telegram


@dataclass
class SpyEntry:
    """
    SpyEntry represents a site to spy on
    """

    url: str
    interval_seconds: float
    img_path: Path


@dataclass
class Config:
    """
    Singleton dataclass to maintain same structure as the corresponding config.json
    """

    telegram: telegram.Telegram
    spy_entries: List[SpyEntry]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Config, cls).__new__(cls)
        return cls.__instance


class ConfigManager:
    pass

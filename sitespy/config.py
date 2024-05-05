from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List
from sitespy import telegram as telegram_class
from sitespy import utils
from json import load as json_load
from json import dump as json_dump
import asyncio


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
    _telegram: telegram_class.Telegram
    _spy_entries: List[SpyEntry]
    _subscribers: List[asyncio.Queue] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def notify(self):
        for queue in self._subscribers:
            queue.put_nowait("UPDATED")

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)

    @property
    def telegram(self):
        return self._telegram

    @property
    def spy_entries(self):
        return self._spy_entries

    def set_telegram(self, telegram: telegram_class.Telegram):
        self._telegram = telegram
        self.notify()

    def add_spy_entry(self, spy_entry: SpyEntry):
        self._spy_entries.append(spy_entry)
        self.notify()

    def remove_spy_entry(self, spy_entry: SpyEntry):
        self._spy_entries.remove(spy_entry)
        self.notify()

    def update_spy_entry(self, old_spy_entry: SpyEntry, new_spy_entry: SpyEntry):
        self._spy_entries.remove(old_spy_entry)
        self._spy_entries.append(new_spy_entry)
        self.notify()

    def clear_spy_entries(self):
        self._spy_entries.clear()
        self.notify()


class ConfigManager:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__initialized = False
            return cls.__instance
        return cls.__instance

    def __init__(self, config: Config, path_manager: utils.PathManager):
        if self.__initialized:
            return

        self.config = config
        self.path_manager = path_manager
        self.config.subscribe(self.update)

        try:
            self.open = open(self.path_manager.config_file, "r+")
            self.json = json_load(self.open)
        except IOError as error:
            print(f"Failed to open or parse the config file: {error}")
            self.open = None
            self.json = None

        self.__initialized = True

    async def update(self, message):
        if message == "UPDATED":
            with open(self.path_manager.config_file, "w") as f:
                json_dump(asdict(self.config), f)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.open is not None:
            self.open.close()


if __name__ == "__main__":
    pass

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Callable
from json import load as json_load
from json import dump as json_dump
from sys import exit as sys_exit
import asyncio

from .telegram import Telegram
from . import utils


@dataclass
class SpyEntry:
    """SpyEntry represents a site to spy on."""

    url: str
    interval_seconds: float
    img_path: Path


@dataclass
class Config:
    """Config represents a data structured in config.json."""

    telegram: Telegram = field(default_factory=lambda: Telegram(placeholder=""))
    spy_entries: List[SpyEntry] = field(default_factory=list)


class ConfigManager:
    """
    ConfigManager manages config changes in cache.
    It is a publisher to Callable objects, who notifies about config changes.
    """

    def __init__(self):
        self.__config = Config()
        self.__subscribers: List[Callable] = []
        self.__loop = asyncio.get_running_loop()

    def subscribe(self, callback: Callable):
        self.__subscribers.append(callback)

    def notify(self):
        for subscriber in self.__subscribers:
            self.__loop.create_task(subscriber())

    def to_dict(self) -> dict[Any, Any]:
        return {
            "telegram": {"placeholder": self.__config.telegram.placeholder},
            "spy_entries": [
                {
                    "url": entry.url,
                    "interval_seconds": entry.interval_seconds,
                    "img_path": entry.img_path.as_posix(),
                }
                for entry in self.__config.spy_entries
            ],
        }

    @property
    def telegram(self) -> Telegram:
        return self.__config.telegram

    @telegram.setter
    def telegram(self, value: Telegram):
        self.__config.telegram = value
        self.notify()

    @property
    def spy_entries(self) -> List[SpyEntry]:
        return self.__config.spy_entries

    @spy_entries.setter
    def spy_entries(self, value: List[SpyEntry]):
        self.__config.spy_entries = value
        self.notify()


class ConfigHandler:
    """
    ConfigHandler handles all intermediaries between config in cache and config.json.
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton boilerplate."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__initialized = False
            return cls.__instance
        return cls.__instance

    def __init__(self, config: ConfigManager, path_manager: utils.PathManager):
        if self.__initialized:
            return

        self.config = config
        self.path_manager = path_manager

        self.config.subscribe(self.update_config)

        self.init_config_json()

        try:
            self.open = open(self.path_manager.config_file, "r+")
            self.json = json_load(self.open)
        except IOError as error:
            print(f"Failed to open or parse the config file: {error}")
            sys_exit(1)

        self.__initialized = True

    def init_config_json(self):
        if not self.path_manager.config_file.exists():
            try:
                with open(self.path_manager.config_file, "w") as file:
                    json_dump(self.config.to_dict(), file, indent=4)
                return
            except IOError as error:
                print(f"Failed to write to the config file: {error}")
                sys_exit(1)

        self.validate_config_json()

    def validate_config_json(self) -> bool:
        # TODO: deep compare if the structure of the Config is same as config.json
        return True

    async def update_config(self):
        """Asynchronously update the config file upon notification."""
        await asyncio.sleep(0)
        self.open.seek(0)
        self.open.truncate()
        json_dump(self.config.to_dict(), self.open, indent=4)
        self.open.flush()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.open is not None:
            self.open.close()


if __name__ == "__main__":
    from sitespy.utils import PathManager, Platform
    import sys

    async def main():
        platform = Platform.from_string(sys.platform)
        path_manager = PathManager(platform)

        config_manager = ConfigManager()
        ConfigHandler(config_manager, path_manager)
        config_manager.telegram = Telegram(placeholder="123")
        print("Config updated.")
        await asyncio.sleep(2)

    asyncio.run(main())

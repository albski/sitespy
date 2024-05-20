import asyncio
from dataclasses import dataclass, field
from json import dump as json_dump
from json import load as json_load
from pathlib import Path
from sys import exit as sys_exit
from typing import Any, List, Callable, Dict, Coroutine

from . import path
from .telegram import Telegram


@dataclass
class SpyEntry:
    """SpyEntry represents a site to spy on."""

    url: str
    interval_seconds: float
    img_path: Path


@dataclass
class Config:
    """Config represents a data structured in config.json."""

    telegram: Telegram = field(
        default_factory=lambda: Telegram(token="", chat_ids=[""])
    )
    spy_entries: List[SpyEntry] = field(default_factory=list)


class ConfigManager:
    """
    ConfigManager manages operations on config.
    It is a publisher to Async Callable objects who notifies about config changes.
    """

    def __init__(self):
        self.__config = Config()

        self.__subscribers: List[Callable[..., Coroutine[Any, Any, Any]]] = []
        self.__loop = asyncio.get_running_loop()

    def subscribe(self, callback: Callable[..., Coroutine[Any, Any, Any]]):
        self.__subscribers.append(callback)

    def notify(self):
        for subscriber in self.__subscribers:
            self.__loop.create_task(subscriber())

    def to_json_dict(self) -> dict[Any, Any]:
        return {
            "telegram": {
                "token": self.__config.telegram.token,
                "chat_ids": [chat_id for chat_id in self.__config.telegram.chat_ids],
            },
            "spy_entries": [
                {
                    "url": entry.url,
                    "interval_seconds": entry.interval_seconds,
                    "img_path": entry.img_path.as_posix(),
                }
                for entry in self.__config.spy_entries
            ],
        }

    @staticmethod
    def from_json_dict(json_dict: Dict) -> Config:
        # TODO: validate if json_dict is compliant to Config structure

        return Config(
            telegram=Telegram(
                token=json_dict["telegram"]["token"],
                chat_ids=[chat_id for chat_id in json_dict["telegram"]["chat_ids"]],
            ),
            spy_entries=[
                SpyEntry(
                    url=entry["url"],
                    interval_seconds=entry["interval_seconds"],
                    img_path=Path(entry["img_path"]),
                )
                for entry in json_dict["spy_entries"]
            ],
        )

    @property
    def config(self) -> Config:
        return self.__config

    @config.setter
    def config(self, value: Config):
        self.__config = value
        self.notify()

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
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        return cls.__instance

    def __init__(self, config_manager: ConfigManager, path_manager: path.PathManager):
        if self.__initialized:
            return

        self.config_manager = config_manager
        self.path_manager = path_manager

        self.config_manager.subscribe(self.update_config)

        self.init_config_json()

        try:
            self.open = open(self.path_manager.config_file, "r+")
            self.config_manager.config = ConfigManager.from_json_dict(
                json_load(self.open)
            )
        except IOError as error:
            print(f"Failed to open or parse the config file: {error}")
            sys_exit(1)

        self.__initialized = True

    def run(self): ...

    def init_config_json(self):
        if not self.path_manager.config_file.exists():
            try:
                with open(self.path_manager.config_file, "w") as file:
                    json_dump(self.config_manager.to_json_dict(), file, indent=4)
                return
            except IOError as error:
                print(f"Failed to write to the config file: {error}")
                sys_exit(1)

    async def update_config(self):
        """Asynchronously update the config file upon notification."""
        await asyncio.sleep(0)
        if not self.__initialized:
            return

        self.open.seek(0)
        self.open.truncate()
        json_dump(self.config_manager.to_json_dict(), self.open, indent=4)
        self.open.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.open is not None:
            self.open.close()

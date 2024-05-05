from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Self
from sitespy import telegram as telegram_class
from sitespy import utils
from json import load as json_load
from json import dump as json_dump
from sys import exit as sys_exit
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
class ConfigData:
    telegram: telegram_class.Telegram = telegram_class.Telegram(placeholder="")
    spy_entries: List[SpyEntry] = []


class Config:
    def __init__(self):
        self.__config_data: ConfigData = ConfigData()

        self.__subscribers: List[asyncio.Queue] = []

    @classmethod
    def from_dict(cls, dict_from_json: dict[Any, Any]) -> Self:
        instance = cls()

        instance.__config_data.telegram = telegram_class.Telegram(placeholder="123")

        instance.__config_data.spy_entries = [
            SpyEntry(
                url=entry["url"],
                interval_seconds=entry["interval_seconds"],
                img_path=Path(entry["img_path"]),
            )
            for entry in dict_from_json.get("spy_entries", [])
        ]

        return instance

    def to_dict(self) -> dict[Any, Any]:
        return {
            "telegram": {"placeholder": "123"},
            "spy_entries": [
                {
                    "url": entry.url,
                    "interval_seconds": entry.interval_seconds,
                    "img_path": entry.img_path.as_posix(),
                }
                for entry in self.__config_data.spy_entries
            ],
        }

    def notify(self):
        for queue in self.__subscribers:
            queue.put_nowait("UPDATED")

    def subscribe(self, subscriber):
        self.__subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.__subscribers.remove(subscriber)

    @property
    def telegram(self) -> telegram_class.Telegram:
        return self.__config_data.telegram

    @telegram.setter
    def telegram(self, value: telegram_class.Telegram):
        self.__config_data.telegram = value
        self.notify()

    @property
    def spy_entries(self) -> List[SpyEntry]:
        return self.__config_data.spy_entries

    @spy_entries.setter
    def spy_entries(self, value: List[SpyEntry]):
        self.__config_data.spy_entries = value
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

        self.init_config_json()

        try:
            self.open = open(self.path_manager.config_file, "r+")
            self.json = json_load(self.open)
        except IOError as error:
            print(f"Failed to open or parse the config file: {error}")
            self.open = None
            self.json = None
            # TODO: handle cases when those are None

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

    def validate_config_json(self):
        # TODO: validate config
        pass

    async def update(self, message):
        if message == "UPDATED" and self.open is not None:
            self.open.seek(0)
            json_dump(self.config.to_dict(), self.open, indent=4)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.open is not None:
            self.open.close()

        self.config.unsubscribe(self.update)


if __name__ == "__main__":
    from sitespy.utils import PathManager, Platform
    import sys

    loop = asyncio.get_event_loop()

    platform = Platform.from_string(sys.platform)
    path_manager = PathManager(platform)

    with open(path_manager.config_file, "r") as file:
        dict_from_json = json_load(file)

    config = Config.from_dict(dict_from_json)
    config_manager = ConfigManager(config, path_manager)

    async def simulate_config_update():
        await asyncio.sleep(5)

    loop.run_until_complete(simulate_config_update())

from os import path
from pathlib import Path
from enum import Enum, unique
from sys import platform


@unique
class Platform(Enum):
    WINDOWS = "win32"
    MAC = "darwin"
    LINUX = "linux"

    @classmethod
    def from_string(cls, platform_string):
        for _, member in cls.__members__.items():
            if member.value == platform_string:
                return member
        raise ValueError(f"{platform_string} is not a valid platform")


class ConfigManager:
    """
    Singleton manager for config and data.
    Supporting only Mac OS (Silicon) for prototype purposes.
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        return cls.__instance

    def __init__(self):
        self.__platform = Platform.from_string(platform())
        self.__app_dir: Path

    def _retrieve_dirs(self) -> None:
        match self.__platform:
            case Platform.MAC:
                user_dir = path.expanduser("~")
                self.__app_dir = path.join(
                    user_dir, "Library", "Application Support", "sitespy"
                )

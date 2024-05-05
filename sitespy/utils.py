from os import path, makedirs
from pathlib import Path
from enum import Enum, unique


@unique
class Platform(Enum):
    WINDOWS = "win32"
    MAC = "darwin"
    LINUX = "linux"

    @classmethod
    def from_string(cls, platform_string: str):
        for _, member in cls.__members__.items():
            if member.value == platform_string:
                return member
        raise ValueError(f"{platform_string} is not a valid platform")


class PathManager:
    """
    Singleton manager for data and config paths.
    Supporting only Mac OS (Silicon).
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__initialized = False
            return cls.__instance
        return cls.__instance

    def __init__(self, platform: Platform):
        if self.__initialized:
            return

        self.__platform = platform
        self.__app_dir: Path = PathManager.retrieve_app_dir(self.__platform)
        self.__config_file: Path = self.__app_dir / "config.json"
        self.__img_dir: Path = self.__app_dir / "img"

        self.__initialized = True

    @staticmethod
    def retrieve_app_dir(platform: Platform) -> Path:
        match platform:
            case Platform.MAC:
                user_dir = path.expanduser("~")
                app_dir: Path = Path(
                    path.join(user_dir, "Library", "Application Support", "sitespy")
                )

                if not app_dir.exists():
                    makedirs(app_dir, exist_ok=True)

                return app_dir

        raise Exception(f"Couldn't retrieve app dir in {__name__} for {platform}")

    @property
    def app_dir(self) -> Path:
        return self.__app_dir

    @property
    def config_file(self) -> Path:
        return self.__config_file

    @property
    def img_dir(self) -> Path:
        return self.__img_dir

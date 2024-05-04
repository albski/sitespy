from os import path
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


def create_dir(dir_paths: tuple[Path]) -> None:
    try:
        for p in dir_paths:
            p.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Dir cannot be created: {error}")


class PathManager:
    """
    Singleton manager for data and config paths.
    Supporting only Mac OS (Silicon).
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        return cls.__instance

    def __init__(self, platform: Platform):
        self.__platform = platform
        self.__app_dir: Path = PathManager.retrieve_app_dir(self.__platform)
        self.__config_file: Path = path.join(self.__app_dir, "config.json")
        self.__img_dir: Path = path.join(self.__app_dir, "img")

    @staticmethod
    def retrieve_app_dir(platform: Platform) -> tuple[Path]:
        match platform:
            case Platform.MAC:
                user_dir = path.expanduser("~")
                app_dir: Path = Path(
                    path.join(user_dir, "Library", "Application Support", "sitespy")
                )

                # implement it DRY way when match serves more cases
                if not app_dir.exists():
                    create_dir(app_dir)

                return app_dir

        raise Exception(f"Couldn't retrieve app dir in {__name__}")

    @property
    def app_dir(self) -> Path:
        return self.__app_dir

    @property
    def config_file(self) -> Path:
        return self.__config_file

    @property
    def img_dir(self) -> Path:
        return self.__img_dir

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

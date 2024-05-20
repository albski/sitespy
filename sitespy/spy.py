import asyncio

from . import utils
from . import config


# u cannot write to config_manager from here TODO: implement reader abstraction
class Spy:
    def __init__(
        self, config_manager: config.ConfigManager, messages_buffer: utils.AsyncBuffer
    ):
        self.config_manager = config_manager
        self.messages_buffer = messages_buffer

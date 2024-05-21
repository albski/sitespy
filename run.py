import asyncio
import sys
from sitespy import utils
from sitespy import telegram
from sitespy.config import ConfigHandler, ConfigManager
from sitespy.path import PathManager
from sitespy.platform import Platform
from sitespy.telegram import Telegram


async def process_buffer(
    buffer: utils.AsyncBuffer, telegram_bot: telegram.AsyncTelegramBot
):
    while True:
        result = await buffer.get()
        await telegram_bot.send_message(text=str(result))


async def main():
    platform = Platform.from_string(sys.platform)
    path_manager = PathManager(platform)

    config_manager = ConfigManager()
    ConfigHandler(config_manager, path_manager).run()

    config_manager.telegram = Telegram(token="123", chat_ids=["123"])
    print("config updated")

    send_messages_buffer = utils.AsyncBuffer()
    telegram_bot = telegram.AsyncTelegramBot(telegram_data=config_manager.telegram)

    asyncio.create_task(
        process_buffer(buffer=send_messages_buffer, telegram_bot=telegram_bot)
    )

    await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())

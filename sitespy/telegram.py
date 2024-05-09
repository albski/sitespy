import asyncio
from dataclasses import dataclass
from typing import List, Dict, Tuple
import httpx

# from abc import ABC, abstractmethod
#
#
# class TelegramData(ABC):
#
#     @abstractmethod
#     def validate(self): ...
#
#
# class TelegramToken:
#     def __init__(self, token: str):
#         self.token = token
#         self.validate()
#
#     def validate(self): ...
#
#
# class TelegramChatID:
#     def __init__(self, chat_id: str):
#         self.chat_id = chat_id
#         self.validate()
#
#     def validate(self): ...


@dataclass
class Telegram:
    token: str  # TelegramToken
    chat_ids: List[str]  # List[TelegramChatID]


class AsyncTelegramBot:
    def __init__(self, telegram_data: Telegram):
        self.telegram_data = telegram_data
        self.api_url = f"https://api.telegram.org/bot{self.telegram_data.token}/"

        self.client = httpx.AsyncClient()

    async def send_message(self, text: str):
        url = self.api_url + "sendMessage"
        client = self.client

        async def send_message_(chat_id):
            nonlocal url, text, client

            await asyncio.sleep(0)
            payload = {"chat_id": chat_id, "text": text}
            response = await client.post(url, json=payload)

            return {chat_id: str(response)}

        tasks = [send_message_(chat_id) for chat_id in self.telegram_data.chat_ids]
        gather = asyncio.gather(*tasks)
        results: Tuple[Dict[str, str]] = await gather

        for result in results:
            print(result.items())
            # todo: handle results in proper manner

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

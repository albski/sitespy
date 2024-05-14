import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Tuple

import httpx


class TelegramData(ABC):
    @abstractmethod
    def validate(self): ...


class TelegramToken:
    def __init__(self, token: str):
        self.token = token
        self.validate()

    def validate(self): ...


class TelegramChatID:
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.validate()

    def validate(self): ...


@dataclass
class Telegram:
    token: TelegramToken
    chat_ids: List[TelegramChatID]


class AsyncTelegramBot:
    def __init__(self, telegram_data: Telegram):
        self.telegram_data = telegram_data
        self.api_url = f"https://api.telegram.org/bot{self.telegram_data.token}/"

        self.client = httpx.AsyncClient()

    async def send_message(self, text: str):
        url = self.api_url + "sendMessage"

        async def send_message_to_chat(
            http_client: httpx.AsyncClient, chat_id: TelegramChatID
        ):
            nonlocal url, text

            await asyncio.sleep(0)
            payload = {"chat_id": chat_id, "text": text}

            async with asyncio.timeout(5):
                response = await http_client.post(url, json=payload)
                response.raise_for_status()
                return {chat_id: str(response)}

        tasks = [
            send_message_to_chat(self.client, chat_id)
            for chat_id in self.telegram_data.chat_ids
        ]
        gather_results = asyncio.gather(*tasks, return_exceptions=True)
        results: Tuple[Dict[str, str]] = await gather_results

        for result in results:
            print(result.items())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

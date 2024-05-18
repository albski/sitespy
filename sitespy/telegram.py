import asyncio
from dataclasses import dataclass
from typing import List, Dict
import httpx


@dataclass
class Telegram:
    token: str
    chat_ids: List[str]


class AsyncTelegramBot:
    def __init__(self, telegram_data: Telegram):
        self.telegram_data = telegram_data
        self.api_url = f"https://api.telegram.org/bot{self.telegram_data.token}/"

        self.client = httpx.AsyncClient()

    async def send_message(self, text: str, in_background: bool):
        url = self.api_url + "sendMessage"

        async def send_message_to_chat(
            http_client: httpx.AsyncClient, chat_id: str
        ) -> Dict[str, int]:
            """Returns {chat_id: status_code}"""
            nonlocal url, text

            await asyncio.sleep(0)
            payload = {"chat_id": chat_id, "text": text}

            async with asyncio.timeout(5):
                response = await http_client.post(url, json=payload)
                return {chat_id: response.status_code}

        tasks = [
            send_message_to_chat(self.client, chat_id)
            for chat_id in self.telegram_data.chat_ids
        ]

        if in_background:
            loop = asyncio.get_event_loop()
            [loop.create_task(task) for task in tasks]
            return

        await asyncio.gather(*tasks, return_exceptions=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

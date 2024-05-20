import asyncio


class AsyncBuffer:
    def __init__(self, maxsize: int = 100) -> None:
        self.queue = asyncio.Queue(maxsize=maxsize)

    async def put(self, item):
        await self.queue.put(item)

    async def get(self):
        await self.queue.get()

    async def is_empty(self) -> bool:
        return self.queue.empty()

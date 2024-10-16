from aiogram.filters import BaseFilter


class OrderFilter(BaseFilter):
    async def __call__(self, *args, **kwargs):
        # TODO: Get information from the database
        return True

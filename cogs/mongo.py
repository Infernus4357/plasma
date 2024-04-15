from motor.motor_asyncio import AsyncIOMotorClient

from discord.ext import commands


class Mongo(commands.Cog):
    """For database operations."""

    def __init__(self, bot):
        self.bot = bot
        self._client = AsyncIOMotorClient(bot.config.DATABASE_URI, tz_aware=True)

    @property
    def db(self):
        return self._client[self.bot.config.DATABASE_NAME]

    async def reserve_id(self, name, reserve=1):
        entry = await self.db.counter.find_one_and_update(
            {"_id": name},
            {"$inc": {"next": reserve}},
            upsert=True,
            return_document=True,
        )
        return entry["next"]


async def setup(bot):
    await bot.add_cog(Mongo(bot))

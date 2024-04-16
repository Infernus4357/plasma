from pathlib import Path

import discord
from discord.ext import commands

import config
from core.constants import DEFAULT_PREFIX
from core.context import CustomContext


async def determine_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    query = {"_id": message.guild.id}
    entry = await bot.mongo.db.guild.find_one_and_update(
        query, {"$setOnInsert": query}, upsert=True, return_document=True
    )

    prefix = entry.get("prefix", DEFAULT_PREFIX)
    return commands.when_mentioned_or(prefix)(bot, message)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            determine_prefix,
            intents=discord.Intents.all(),
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="/help"
            ),
            case_insensitive=True,
            strip_after_prefix=True,
        )

        self.config = config

    @property
    def mongo(self):
        return self.get_cog("Mongo")

    @property
    def redis(self):
        return self.get_cog("Redis")._pool

    async def setup_hook(self):
        for file in Path("cogs").glob("*.py"):
            name = f"cogs.{file.stem}"
            await self.load_extension(name)

    async def get_context(self, origin, /, *, cls=CustomContext):
        return await super().get_context(origin, cls=cls)


if __name__ == "__main__":
    bot = Bot()
    bot.run(config.BOT_TOKEN)

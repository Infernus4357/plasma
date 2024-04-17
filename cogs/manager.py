from PIL import Image
from io import BytesIO

import discord
from discord.ext import commands

from core.checks import is_manager
from core.constants import DEFAULT_PREFIX


class Manager(commands.Cog):
    """For managers to manage the server."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_manager().predicate(ctx)

    @commands.hybrid_command()
    async def prefix(self, ctx, *, prefix: commands.Range[str, 1, 10] = None):
        """Change the bot's command prefix for this server.

        Parameters
        -----------
        prefix: `str`
            The prefix you want to change to.
        """

        if prefix is None:
            entry = await self.bot.mongo.db.guild.find_one({"_id": ctx.guild.id})
            valid = entry.get("prefix", DEFAULT_PREFIX) if entry else DEFAULT_PREFIX
            await ctx.reply(f"My current prefix is `{valid}` in this server.")

        else:
            await self.bot.mongo.db.guild.update_one(
                {"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}, upsert=True
            )
            await ctx.reply(f"Changed prefix to `{prefix}` for this server.")

    @commands.hybrid_command()
    async def upload_emoji(self, ctx, file: discord.Attachment):
        """Upload an emoji to the server from an attached file.

        Parameters
        -----------
        file: `Attachment`
            The image file to be uploaded as an emoji.
        """

        await ctx.defer()

        name = file.filename.split(".")[0][:32]
        type = file.content_type.split("/")[1]

        if len(name) == 1:
            name += "_"

        try:
            if type == "gif":
                bytes = await file.read()
                emoji = await ctx.guild.create_custom_emoji(name=name, image=bytes)

            elif type in ("jpeg", "png"):
                image = Image.open(BytesIO(await file.read()))
                image = image.resize((128, 128))

                with BytesIO() as buffer:
                    image.save(buffer, type)
                    buffer.seek(0)
                    bytes = buffer.getvalue()
                    emoji = await ctx.guild.create_custom_emoji(name=name, image=bytes)

            else:
                raise commands.BadArgument(
                    "Unsupported file format. Please attach an image file in JPEG, PNG, or GIF format."
                )
        except discord.HTTPException as e:
            raise commands.BadArgument(e.text)

        await ctx.reply(f"**{ctx.author}** uploaded {emoji}")


async def setup(bot):
    await bot.add_cog(Manager(bot))

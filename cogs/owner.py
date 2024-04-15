from discord.ext import commands


class Owner(commands.Cog):
    """For bot owners to manage the bot."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.hybrid_command()
    async def sync(self, ctx):
        """Syncs application commands with the bot."""

        items = await self.bot.tree.sync()
        embed = ctx.response_embed(f"Synced `{len(items)}` commands globally.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Owner(bot))

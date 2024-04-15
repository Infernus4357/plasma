from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands

from .constants import TIME_REGEX


class BanConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await ctx.guild.fetch_ban(discord.Object(int(argument)))
        except discord.NotFound:
            raise commands.BadArgument("This member is not banned.")
        except ValueError:
            pass

        bans = await ctx.guild.bans()
        user = discord.utils.find(lambda u: str(u.user) == argument, bans)
        if user is None:
            raise commands.BadArgument("This member is not banned.")

        return user


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        match = TIME_REGEX.match(argument.casefold())
        if not match:
            raise commands.BadArgument("Invalid time duration format!")

        units = {k: int(v) for k, v in match.groupdict(default=0).items()}
        return ctx.message.created_at + relativedelta(**units)

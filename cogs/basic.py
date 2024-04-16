import datetime
import sys
import traceback

import discord
from discord.ext import commands

from core.enums import EmbedStyle
from core.utils import human_timedelta


class Basic(commands.Cog):
    """For basic bot operations."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.content != before.content:
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)

        elif isinstance(error, commands.CommandOnCooldown):
            embed = ctx.response_embed(
                f"You're on cooldown! Try again in {human_timedelta(datetime.timedelta(seconds=error.retry_after))}",
                style=EmbedStyle.FAILURE,
            )
            await ctx.send(embed=embed, ephemeral=True)

        elif isinstance(error, commands.ConversionError):
            embed = ctx.response_embed(str(error.original), style=EmbedStyle.FAILURE)
            await ctx.send(embed=embed, ephemeral=True)

        elif isinstance(error, (commands.UserInputError, commands.CheckFailure)):
            embed = ctx.response_embed(str(error), style=EmbedStyle.FAILURE)
            await ctx.send(embed=embed, ephemeral=True)

        elif isinstance(error, commands.CommandNotFound):
            return

        else:
            print(f"Ignoring exception in command {ctx.command}")
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    @commands.Cog.listener()
    async def on_error(self, event, error):
        if isinstance(error, discord.NotFound):
            return
        else:
            print(f"Ignoring exception in event {event}")
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    @commands.hybrid_command()
    async def ping(self, ctx):
        """Checks the bot's latency."""

        message = await ctx.send("Pong!")
        seconds = (message.created_at - ctx.message.created_at).total_seconds()
        await message.edit(content=f"Pong! **{seconds * 1000:.0f} ms**")

    @discord.app_commands.command()
    async def help(self, interaction, *, command: str = None):
        """Shows all available commands.

        Parameters
        -----------
        command: `str`
            The command to get help for.
        """

        ctx = await self.bot.get_context(interaction)

        if command:
            cmd = self.bot.get_command(command)
            cog = self.bot.get_cog(command)

            if cmd or cog:
                await ctx.send_help(command)
            else:
                embed = ctx.response_embed(
                    f"No command called `{command}` found.", style=EmbedStyle.FAILURE
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx.send_help()

    @help.autocomplete("command")
    async def help_command_autocomplete(self, interaction, current):
        context = await self.bot.get_context(interaction)
        options = await self.bot.help_command.filter_commands(
            self.bot.commands, context=context
        )
        choices = [
            discord.app_commands.Choice(name=option.name, value=option.name)
            for option in options
            if current.casefold() in option.name.casefold()
        ]
        return choices[:25]


async def setup(bot):
    await bot.add_cog(Basic(bot))

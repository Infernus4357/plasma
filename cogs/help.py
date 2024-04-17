import datetime
import inspect
import re

import discord
from discord.ext import commands

from core.enums import EmbedStyle
from core.menus import HelpPageSource, Paginator
from core.utils import human_timedelta


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"help": "Shows all available commands."})

    def command_not_found(self, string):
        return f"No command called `{string}` found."

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"Command `{command.qualified_name}` has no subcommands named `{string}`"
        return f"Command `{command.qualified_name}` has no subcommands."

    async def filter_commands(self, cmds, /, *, context=None, sort=True, key=None):
        context = context or self.context

        if sort and key is None:
            key = lambda c: c.name

        iterator = cmds if self.show_hidden else filter(lambda c: not c.hidden, cmds)

        if self.verify_checks is False:
            return sorted(iterator, key=key) if sort else list(iterator)

        if self.verify_checks is None and not context.guild:
            return sorted(iterator, key=key) if sort else list(iterator)

        async def predicate(cmd):
            try:
                return await cmd.can_run(context)
            except commands.CommandError:
                return False

        ret = []
        for cmd in iterator:
            valid = await predicate(cmd)
            if valid:
                ret.append(cmd)

        if sort:
            ret.sort(key=key)

        return ret

    async def send_error_message(self, error, /, *, modify=False):
        error = self.command_not_found(error) if modify else error
        embed = self.context.response_embed(error, style=EmbedStyle.FAILURE)
        await self.context.reply(embed=embed, ephemeral=True)

    def _prepare_embed(self, cmds, *, title, description):
        embed = discord.Embed(color=0xFE9AC9, title=title, description=description)
        embed.set_footer(
            text=f'Use "{self.context.clean_prefix}help command" for more info on a command.'
        )

        for cmd in cmds:
            name = self.get_command_signature(cmd)
            help = cmd.help.splitlines()[0] if cmd.help else "No help found..."
            embed.add_field(name=name, value=f"`{help}`", inline=False)

        return embed

    def get_examples(self, cmd):
        docstring = inspect.getdoc(cmd.callback)
        if not docstring:
            return None

        pattern = r"Examples\s*[\n-]+\s*(.*?)(?=Parameters|\Z)"
        matches = re.findall(pattern, docstring, re.DOTALL)
        return "\n".join(matches)

    async def send_bot_help(self, mapping):
        entries = []
        for cog, cmds in mapping.items():
            cmds = await self.filter_commands(cmds)
            if cog and len(cmds) > 0:
                entries.append((cog, cmds))

        paginator = Paginator(
            source=HelpPageSource(self.context, entries, color=0xFE9AC9)
        )
        await paginator.start(self.context)

    async def send_cog_help(self, cog):
        cmds = await self.filter_commands(cog.get_commands())

        if len(cmds) == 0:
            return await self.send_error_message(cog.qualified_name, modify=True)

        embed = self._prepare_embed(
            cmds,
            title=f"{cog.qualified_name} Commands",
            description=cog.description or "No Description",
        )
        await self.context.reply(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        cmds = await self.filter_commands(subcommands)
        if len(cmds) == 0:
            return await self.send_error_message(group.qualified_name, modify=True)

        embed = self._prepare_embed(
            cmds,
            title=self.get_command_signature(group),
            description=(
                group.help.splitlines()[0] if group.help else "No help found..."
            ),
        )

        if examples := self.get_examples(group):
            embed.description += "\n\n" + "**Examples**" + "\n" + examples

        await self.context.reply(embed=embed)

    async def send_command_help(self, command):
        try:
            valid = await command.can_run(self.context)
        except commands.CommandError:
            valid = False

        if not valid:
            return await self.send_error_message(command.name, modify=True)

        embed = discord.Embed(
            color=0xFE9AC9,
            title=f"{self.context.clean_prefix}{command.name} {command.signature}",
            description=(
                command.help.splitlines()[0] if command.help else "No help found..."
            ),
        )

        if aliases := command.aliases:
            value = " ".join([f"`{alias}`" for alias in aliases])
            embed.add_field(name="Aliases", value=value, inline=False)

        if cooldown := command.cooldown:
            value = human_timedelta(
                datetime.timedelta(seconds=cooldown.per / cooldown.rate)
            )
            embed.add_field(name="Cooldown", value=value, inline=False)

        if examples := self.get_examples(command):
            embed.add_field(name="Examples", value=examples, inline=False)

        await self.context.reply(embed=embed)


async def setup(bot):
    bot.old_help_command = bot.help_command
    bot.help_command = CustomHelpCommand()


async def teardown(bot):
    bot.help_command = bot.old_help_command
    del bot.old_help_command

import abc

import discord
from discord.ext import menus

from .constants import EXCLUDED_PAGINATOR_BUTTONS


class Paginator(menus.MenuPages, menus.Menu):
    def __init__(self, source, auto_defer=True, **kwargs):
        super().__init__(source, **kwargs)
        self.auto_defer = auto_defer
        self.clear_reactions_after = True

    def _prepare_view(self):
        if not self.should_add_reactions():
            return None

        def callback(button):
            async def button_callback(interaction):
                if interaction.user.id != self._author_id:
                    return

                if self.auto_defer:
                    await interaction.response.defer()

                try:
                    if button.lock:
                        async with self._lock:
                            if self._running:
                                await button(self, interaction)
                    else:
                        await button(self, interaction)
                except Exception as exc:
                    await self.on_menu_button_error(exc)

            return button_callback

        view = discord.ui.View(timeout=self.timeout)
        for i, (emoji, button) in enumerate(self.buttons.items()):
            if emoji in EXCLUDED_PAGINATOR_BUTTONS:
                continue

            item = discord.ui.Button(emoji=emoji, row=i // 5)
            item.callback = callback(button)
            view.add_item(item)

        self.view = view
        return view

    async def _internal_loop(self):
        self.__timed_out = False

        try:
            self.__timed_out = await self.view.wait()
        except Exception:
            pass
        finally:
            self._event.set()

            try:
                await self.finalize(self.__timed_out)
            except Exception:
                pass
            finally:
                self.__timed_out = False

            if self.bot.is_closed():
                return

            try:
                if self.delete_message_after:
                    return await self.message.delete()

                if self.clear_reactions_after:
                    return await self.message.edit(view=None)
            except Exception:
                pass

    async def send_initial_message(self, ctx, channel):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await ctx.reply(**kwargs, view=self._prepare_view())


class EmbedPageSource(menus.AsyncIteratorPageSource, abc.ABC):
    def __init__(
        self,
        iterator,
        *,
        color,
        title,
        icon_url=None,
        per_page=20,
        show_index=True,
        format_embed=lambda *x: None,
        format_entry=lambda *x: None,
    ):
        super().__init__(iterator, per_page=per_page)
        self.color = color
        self.title = title
        self.icon_url = icon_url
        self.show_index = show_index
        self.format_embed = format_embed
        self.format_entry = format_entry

    def _prepare_embed(self, menu, page):
        start = menu.current_page * self.per_page
        embed = discord.Embed(color=self.color)
        embed.set_author(name=self.title, icon_url=self.icon_url)

        if self.show_index:
            embed.set_footer(
                text=f"Showing entries {start + 1}–{start + len(page)} out of {len(self._cache)}"
            )

        return embed

    @abc.abstractmethod
    async def format_page(self, menu, page):
        raise NotImplementedError


class CodeBlockTablePageSource(EmbedPageSource):
    def justify(self, string, width):
        return string.rjust(width) if string.isdigit() else string.ljust(width)

    def _prepare_table(self, menu, page):
        start = menu.current_page * self.per_page
        table = []

        for i, x in enumerate(page, start=start):
            entry = (
                (f"{i+1}.", *self.format_entry(x))
                if self.show_index
                else self.format_entry(x)
            )
            table.append(entry)

        return table

    async def format_page(self, menu, page):
        embed = self._prepare_embed(menu, page)
        table = self._prepare_table(menu, page)

        width = [max(len(x) for x in column) for column in zip(*table)]
        lines = [
            "  ".join(self.justify(x, width[i]) for i, x in enumerate(line)).rstrip()
            for line in table
        ]

        embed.description = "```" + "\n".join(lines) + "```"
        self.format_embed(embed)

        return embed


class FieldsPageSource(EmbedPageSource):
    async def format_page(self, menu, page):
        start = menu.current_page * self.per_page
        embed = self._prepare_embed(menu, page)

        for i, x in enumerate(page, start=start):
            embed.add_field(**self.format_entry(i, x))

        return embed


class HelpPageSource(menus.ListPageSource):
    def __init__(self, ctx, entries, *, color, per_page=6):
        super().__init__(entries, per_page=per_page)
        self.ctx = ctx
        self.color = color

    async def format_page(self, menu, page):
        embed = discord.Embed(
            color=self.color,
            title=f"Command Categories (Page {menu.current_page + 1}/{self.get_max_pages()})",
            description=(
                f"Use `{self.ctx.clean_prefix}help <command>` for more info on a command.\n"
                f"Use `{self.ctx.clean_prefix}help <category>` for more info on a category."
            ),
        )

        for cog, commands in page:
            command_names = " ".join([f"`{command.name}`" for command in commands])
            embed.add_field(
                name=cog.qualified_name,
                value=f"{cog.description or 'No Description'}\n{command_names}",
                inline=False,
            )

        return embed

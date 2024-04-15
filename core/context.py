import discord
from discord.ext import commands

from .enums import EmbedStyle


class ConfirmationView(discord.ui.View):
    def __init__(self, ctx, *, timeout, delete_message_after):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.result = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            embed = self.ctx.response_embed(
                "You don't have permission to use this component!",
                style=EmbedStyle.FAILURE,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    async def finalize(self, result):
        self.result = result
        self.stop()

        if self.message:
            if self.delete_message_after:
                await self.message.delete()
            else:
                await self.message.edit(view=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction, button):
        await interaction.response.defer()
        await self.finalize(True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction, button):
        await interaction.response.defer()
        await self.finalize(False)

    async def on_timeout(self):
        if self.message:
            await self.message.delete()


class CustomContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def response_embed(self, message, *, style=EmbedStyle.SUCCESS):
        if style not in EmbedStyle:
            raise ValueError(f"Invalid style '{style.name}' provided.")

        embed = discord.Embed(
            color=style.value["color"],
            description=f"{style.value['emoji']} {message}",
        )
        return embed

    async def confirm(
        self,
        content=None,
        *,
        timeout=40,
        delete_message_after=True,
        cls=ConfirmationView,
        **kwargs,
    ):
        view = cls(self, timeout=timeout, delete_message_after=delete_message_after)
        view.message = await self.send(content, view=view, **kwargs)
        await view.wait()
        return view.result

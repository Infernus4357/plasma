from dataclasses import dataclass

import discord


@dataclass
class FakeAvatar:
    url: str


class FakeUser(discord.Object):
    def __str__(self):
        return str(self.id)

    @property
    def display_avatar(self):
        return FakeAvatar("https://cdn.discordapp.com/embed/avatars/0.png")

    @property
    def mention(self):
        return f"<@{self.id}>"

    async def send(self, *args, **kwargs):
        pass

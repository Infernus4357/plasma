from discord.ext import commands

from . import constants


def has_roles(*role_ids):
    async def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        if (
            await ctx.bot.is_owner(ctx.author)
            or ctx.author.id == ctx.guild.owner_id
            or ctx.author.guild_permissions.administrator
            or any(role.id in role_ids for role in ctx.author.roles)
        ):
            return True
        raise commands.CheckFailure()

    return commands.check(predicate)


def is_admin():
    return has_roles()


def is_manager():
    return has_roles(*constants.MANAGER_ROLES)


def is_moderator():
    return has_roles(*constants.MODERATOR_ROLES)


def is_trial_moderator():
    return has_roles(*constants.TRIAL_MODERATOR_ROLES)


def is_server_booster():
    async def predicate(ctx):
        try:
            return await is_admin()(ctx)
        except commands.CheckFailure:
            pass

        if ctx.author.premium_since is None:
            raise commands.CheckFailure("You are not a server booster.")
        return True

    return commands.check(predicate)


def in_guilds(*guild_ids):
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        if ctx.guild.id not in guild_ids:
            raise commands.CheckFailure("This command is not available in this guild.")
        return True

    return commands.check(predicate)


def community_server_only():
    return in_guilds(constants.COMMUNITY_SERVER_ID)


def exclusive_server_only():
    return in_guilds(constants.EXCLUSIVE_SERVER_ID)


def has_level(level):
    async def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        entry = await ctx.bot.mongo.db.member.find_one(
            {"_id": {"id": ctx.author.id, "guild_id": ctx.guild.id}}, {"level": 1}
        )
        if entry is None:
            return False

        return entry.get("level", 0) >= level

    return commands.check(predicate)

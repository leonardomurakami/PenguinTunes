from discord import Object
from discord.ext import commands
from sqlalchemy import select, update

from modules.globals import config
from modules.orm.database import Guild


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="refresh-guilds")
    async def refresh_guilds(self, ctx: commands.Context):
        """
        Owner only command, sync the command tree for all guilds.
        """
        if int(ctx.author.id) == int(config.bot_owner_id):
            for server in self.bot.guilds:
                await self.bot.tree.sync(guild=Object(id=server.id))
        else:
            await ctx.send("You must be the owner to use this command!")

    @commands.command(name="refresh")
    async def refresh(self, ctx: commands.Context):
        """
        Owner only command, sync the command tree for all guilds.
        """
        if int(ctx.author.id) == int(config.bot_owner_id):
            await self.bot.tree.sync()
        else:
            await ctx.send("You must be the owner to use this command!")

    @commands.hybrid_command(name="prefix")
    async def prefix(self, ctx: commands.Context, *, new_prefix: str = ""):
        """
        Sets a custom prefix for the bot in your server.
        """
        if not new_prefix: #if prefix is not passed, display current prefix
            async with self.bot.session as session:
                if ctx.guild.id in self.bot.guild_prefix_cache.keys():
                    prefix = self.bot.guild_prefix_cache[ctx.guild.id]
                else:
                    result = await session.execute(
                        select(Guild)
                            .where(Guild.id == int(ctx.guild.id))
                    )
                    prefix = result.scalars().first().prefix
                await ctx.send(f"Your current guild prefix is {prefix}")

        else: #else, set new prefix
            # TODO: Abstract database logic to a Repository pattern.
            async with self.bot.session as session:
                result = await session.execute(
                    update(Guild)
                        .where(Guild.id == int(ctx.guild.id))
                        .values(prefix=new_prefix)
                )
                self.bot.guild_prefix_cache[ctx.guild.id] = new_prefix

                await session.commit()
                await ctx.send(f"Changing prefix to {new_prefix}")
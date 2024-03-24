"""
Class Documentation: Config Cog

The Config class is a Discord bot cog that provides functionalities for managing the bot's configuration settings in different servers.

Class Methods:

1. __init__(self, bot)
   Initializes the Config cog with a reference to the bot instance.
   - bot: The instance of the bot that the cog is a part of.

2. refresh_guilds(self, ctx: commands.Context)
   Synchronizes the command tree for all guilds.
   - ctx: The context of the command.
   - Note: This is an owner-only command to sync command settings across all guilds the bot is a part of.

3. refresh(self, ctx: commands.Context)
   Synchronizes the command tree globally.
   - ctx: The context of the command.
   - Note: Similar to 'refresh_guilds', but this command applies globally.

4. prefix(self, ctx: commands.Context, *, new_prefix: str = "")
   Sets or displays the custom command prefix for the bot in the server where it's invoked.
   - ctx: The context of the command.
   - new_prefix: A string representing the new prefix. If empty, the current prefix is displayed.

Additional Notes:
- The Config cog allows for dynamic management of bot settings, particularly command prefixes, tailored to individual guild requirements.
- It utilizes SQLAlchemy for database operations, specifically for storing and retrieving custom prefix settings.
- The cog includes owner-only commands to ensure that critical bot settings are managed securely and responsibly.
- This cog plays a crucial role in maintaining the bot's operability and customizability across multiple Discord servers.
"""
import re
import discord

from discord import Object
from discord.ext import commands
from sqlalchemy import select, update

from modules.globals import config
from modules.orm.database import Cassino, Guild, RestrictedCommands


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
        if not new_prefix:  # if prefix is not passed, display current prefix
            async with self.bot.session as session:
                if ctx.guild.id in self.bot.guild_prefix_cache.keys():
                    prefix = self.bot.guild_prefix_cache[ctx.guild.id]
                else:
                    result = await session.execute(
                        select(Guild).where(Guild.id == int(ctx.guild.id))
                    )
                    prefix = result.scalars().first().prefix
                await ctx.send(f"Your current guild prefix is {prefix}")

        else:
            async with self.bot.session as session:
                result = await session.execute(
                    update(Guild)
                    .where(Guild.id == int(ctx.guild.id))
                    .values(prefix=new_prefix)
                )
                self.bot.guild_prefix_cache[ctx.guild.id] = new_prefix

                await session.commit()
                await ctx.send(f"Changing prefix to {new_prefix}")
    
    @commands.hybrid_command(name="change-nickname", aliases=["change-nick", "cn", "nick", "nickname"])
    async def change_nickname(self, ctx: commands.Context, *, new_nickname: str = ""):
        """
        Sets a custom nickname for someone else in the server
        """
        if mention_list := ctx.message.mentions:
            member = mention_list[0]
            new_nick = re.sub(r"<[^>]+>", "", new_nickname).strip()
            if not new_nick:
                new_nick = member.name
            try:
                await member.edit(nick=new_nick)
                await ctx.send(f"Changed {member.mention}'s nickname to {new_nick}")
            except discord.errors.Forbidden:
                await ctx.send(f"Could not change {member.mention}'s nickname.\nI don't have the required permissions to change this user's name.")
        

    @commands.hybrid_command(name="restrict", aliases=["restrict-command"])
    @commands.has_permissions(manage_messages=True)
    async def restrict(self, ctx: commands.Context, *, command: str):
        """
        Restricts a command to the channel the commands was used.
        """
        if (bot_command := self.bot.get_command(command)):
            command = bot_command.name #ensure name is picked, not alias
            async with self.bot.session as session:
                command_db = await session.get(RestrictedCommands, f"{str(ctx.guild.id)}_{command}")
                if not command_db:
                    if not ctx.channel.guild.id in self.bot.restricted_commands_cache.keys():
                        self.bot.restricted_commands_cache[ctx.channel.guild.id] = {}
                    self.bot.restricted_commands_cache[ctx.channel.guild.id][command] = ctx.channel.id
                    command_db = RestrictedCommands(command_id=f"{str(ctx.guild.id)}_{command}", channel=ctx.channel.id)
                    session.add(command_db)
                    await session.commit()
                    await session.refresh(command_db)
                else:
                    if not ctx.channel.guild.id in self.bot.restricted_commands_cache.keys():
                        self.bot.restricted_commands_cache[ctx.channel.guild.id] = {}
                    self.bot.restricted_commands_cache[ctx.channel.guild.id][command] = ctx.channel.id
                    command_db.channel = ctx.channel.id
                    await session.commit()
                    await session.refresh(command_db)
                await ctx.send(f"Restricted {command} to channel {ctx.channel.mention}")
        else:
            await ctx.send(f"{command} is not a valid command!", ephemeral=True, delete_after=10)

    @commands.command(name="source")
    async def source(self, ctx: commands.Context):
        """
        Displays the source code for the bot.
        """
        await ctx.send("[Github] - https://github.com/leonardomurakami/PenguinTunes")

    @commands.command(name="award")
    async def award(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Bot owner command to award a user with a specified amount of money.
        """
        if int(ctx.author.id) == int(config.bot_owner_id):
            async with self.bot.session as session:
                player = await session.get(Cassino, int(member.id))
                if not player:
                    player = Cassino(id=ctx.author.id, balance=1000)
                    session.add(player)
                    await session.commit()
                    await session.refresh(player)
                player.balance += amount
                await session.commit()
                await session.refresh(player)
            await ctx.send(f"🏆 {member.mention} has been awarded ${amount} for finding a bug! New balance: ${player.balance}")
        else:
            await ctx.send("You must be the owner to use this command!")
        
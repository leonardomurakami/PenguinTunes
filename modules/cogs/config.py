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
from modules.orm.database import Cassino, Guild, Command, CommandRestriction
from modules.utils._database_utils import get_session
from modules.utils._config_utils import is_command_allowed


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
        restricted = await is_command_allowed("change-nickname", self.bot, ctx)
        if not restricted:
            return
        
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
    async def restrict(self, ctx: commands.Context, *, params: str):
        """
        Restricts a command to the specified channel or role within the guild.
        
        Parameters:
        - command_name: Name of the command to restrict.
        - restriction_type: Type of restriction ('channel' or 'role').
        - restriction_target: ID of the channel or role to restrict the command to.
        """
        parts = params.split(maxsplit=2)
        if len(parts) < 2:
            await ctx.send("Please specify both the command name and the restriction type ('channel' or 'role').")
            return

        command_name, restriction_type = parts[0], parts[1]
        channel_mentions = ctx.message.channel_mentions
        role_mentions = ctx.message.role_mentions

        if restriction_type not in ["channel", "role"]:
            await ctx.send("Invalid restriction type. Please use 'channel' or 'role'")
            return
        
        if restriction_type == "channel":
            if not channel_mentions:
                await ctx.send("Please mention a channel to restrict the command to.")
                return
            restriction_target = channel_mentions[0].id
        
        if restriction_type == "role":
            if not role_mentions:
                await ctx.send("Please mention a role to restrict the command to.")
                return
            restriction_target = role_mentions[0].id

        if self.bot.get_command(command_name) is None:
            await ctx.send(f"Command {command_name} not found.")
            return

        async with get_session() as session:
            # Find or create the command in the Commands table
            stmt = select(Command).where(Command.guild_id == ctx.guild.id, Command.command_name == command_name)
            result = await session.execute(stmt)
            command_entry = result.scalars().first()
            
            if not command_entry:
                command_entry = Command(guild_id=ctx.guild.id, command_name=command_name)
                session.add(command_entry)
                await session.commit()

            # Update or insert the restriction
            stmt = select(CommandRestriction).where(
                CommandRestriction.command_id == command_entry.command_id,
                CommandRestriction.restriction_type == restriction_type,
                CommandRestriction.restriction_target == restriction_target
            )
            result = await session.execute(stmt)
            restriction_entry = result.scalars().first()

            if not restriction_entry:
                restriction_entry = CommandRestriction(command_id=command_entry.command_id, restriction_type=restriction_type, restriction_target=restriction_target)
                session.add(restriction_entry)
                await session.commit()

            # Update cache
            guild_restrictions = self.bot.restricted_commands_cache.setdefault(ctx.guild.id, {})
            command_restrictions = guild_restrictions.setdefault(command_name, {"channels": [], "roles": []})

            if restriction_type == "channel":
                if restriction_target not in command_restrictions["channels"]:
                    command_restrictions["channels"].append(restriction_target)
            elif restriction_type == "role":
                if restriction_target not in command_restrictions["roles"]:
                    command_restrictions["roles"].append(restriction_target)
            
            mention_string = f"<#{restriction_target}>" if restriction_type == "channel" else f"<@&{restriction_target}>"
            await ctx.send(f"Restricted {command_name} to {'channel' if restriction_type == 'channel' else 'role'} {mention_string}")

    @commands.hybrid_command(name="unrestrict", aliases=["unrestrict-command"])
    @commands.has_permissions(manage_messages=True)
    async def unrestrict(self, ctx: commands.Context, *, params: str):
        """
        Removes restrictions from a command within the guild.

        Parameters:
        - command_name: Name of the command to unrestrict.
        - restriction_type: Type of restriction being removed ('channel' or 'role').
        - restriction_target: ID of the channel or role from which to remove the restriction.
        """
        parts = params.split(maxsplit=2)
        if len(parts) < 2:
            await ctx.send("Please specify both the command name and the restriction type ('channel' or 'role').")
            return

        command_name, restriction_type = parts[0], parts[1]
        channel_mentions = ctx.message.channel_mentions
        role_mentions = ctx.message.role_mentions

        if restriction_type not in ["channel", "role"]:
            await ctx.send("Invalid restriction type. Please use 'channel' or 'role'.")
            return

        if restriction_type == "channel":
            if not channel_mentions:
                await ctx.send("Please mention a channel to remove the restriction from.")
                return
            restriction_target = channel_mentions[0].id

        if restriction_type == "role":
            if not role_mentions:
                await ctx.send("Please mention a role to remove the restriction from.")
                return
            restriction_target = role_mentions[0].id

        async with get_session() as session:
            # Find the command in the Commands table
            stmt = select(Command).where(Command.guild_id == ctx.guild.id, Command.command_name == command_name)
            result = await session.execute(stmt)
            command_entry = result.scalars().first()

            if command_entry:
                # Find and delete the restriction
                stmt = select(CommandRestriction).where(
                    CommandRestriction.command_id == command_entry.command_id,
                    CommandRestriction.restriction_type == restriction_type,
                    CommandRestriction.restriction_target == restriction_target
                )
                result = await session.execute(stmt)
                restriction_entry = result.scalars().first()

                if restriction_entry:
                    await session.delete(restriction_entry)
                    await session.commit()
                    await ctx.send(f"Removed restriction from {command_name}.")
                else:
                    await ctx.send(f"No {restriction_type} restriction found for {command_name}.")

                # Update cache
                if ctx.guild.id in self.bot.restricted_commands_cache:
                    guild_restrictions = self.bot.restricted_commands_cache[ctx.guild.id]
                    if command_name in guild_restrictions:
                        if restriction_type == "channel" and restriction_target in guild_restrictions[command_name]["channels"]:
                            guild_restrictions[command_name]["channels"].remove(restriction_target)
                        elif restriction_type == "role" and restriction_target in guild_restrictions[command_name]["roles"]:
                            guild_restrictions[command_name]["roles"].remove(restriction_target)

                        if not guild_restrictions[command_name]["channels"] and not guild_restrictions[command_name]["roles"]:
                            # If there are no more restrictions, remove the command from the cache
                            del guild_restrictions[command_name]
            else:
                await ctx.send(f"Command {command_name} not found.")


    @commands.command(name="source")
    async def source(self, ctx: commands.Context):
        """
        Displays the source code for the bot.
        """
        await ctx.send("[Github] - https://github.com/leonardomurakami/PenguinTunes")

    @commands.command(name="debug")
    async def debug(self, ctx: commands.Context):
        """
        Bot owner command to award a user with a specified amount of money.
        """
        restricted = await is_command_allowed("debug", self.bot, ctx)
        if not restricted:
            return
        
        if int(ctx.author.id) == int(config.bot_owner_id):
            await ctx.send(repr(self.bot))

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

     @commands.hybrid_command(name="role")
     @commands.has_permissions(manage_roles=True)
     async def add_role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
         """
         Adds a specified role to a user within the server, bot owner only.
     
         Parameters:
         - user: The user who should receive the role.
         - role: The role to be given to the user.
         """
         restricted = await is_command_allowed("role", self.bot, ctx)
         if not restricted:
             return
   
         if role in member.roles:
             await ctx.send(f"{member.mention} already has the {role.mention} role.")
         elif int(ctx.author.id) == int(config.bot_owner_id)::
             try:
                 await member.add_roles(role)
                 await ctx.send(f"{role.mention} role added to {member.mention}.")
             except discord.errors.Forbidden:
                 await ctx.send("I don't have permission to manage roles in this server.")
        

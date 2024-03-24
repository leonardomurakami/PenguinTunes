"""
Module Documentation: Config Utils Class

This module defines the `Struct` class, a flexible structure for organizing and handling data.

Class Description:
- `Struct` is a class that provides a structured way to organize data with optional headers and 
  custom iteration behavior. It is designed to be flexible and easy to use for various purposes.

Class Methods:
1. __init__(self, *args)
   Constructor for the Struct class.
   - Initializes the Struct with a header if provided.
   Parameters:
     - *args: Variable length argument list, the first argument is used as the header.

2. __repr__(self)
   Representation method for the Struct.
   - Returns a string representation of the Struct.
   - If a header is set, it returns the header; otherwise, it returns the default object 
     representation.

3. next(self)
   Fake iteration functionality.
   - Raises StopIteration to simulate the behavior of an iterator.
   - This method is a placeholder and does not provide actual iteration functionality.

4. __iter__(self)
   Custom iterator for the Struct.
   - Iterates over the attributes of the Struct instance.
   - Skips magic attributes (those starting with '__') and attributes that are instances of Struct.
   Yields:
     - Yields the values of the non-magic, non-Struct attributes of the instance.

5. __len__(self)
   Length method for the Struct.
   - Calculates the number of non-magic, non-Struct attributes in the Struct.
   Returns:
     - (int): The number of relevant attributes in the Struct instance.
"""


from discord.ext import commands
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from modules.utils._database_utils import get_session
from modules.orm.database import Command, CommandRestriction


from sqlalchemy.future import select
from discord.ext import commands
from sqlalchemy.exc import IntegrityError

from sqlalchemy.future import select
from discord.ext import commands
from sqlalchemy.exc import IntegrityError

async def is_command_allowed(command_name: str, bot: commands.Bot, ctx: commands.Context):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id
    user_roles = [role.id for role in ctx.author.roles]
    
    command_restrictions = bot.restricted_commands_cache.get(guild_id, {}).get(command_name, None)

    if command_restrictions:
        channels = command_restrictions.get('channels', [])
        roles = command_restrictions.get('roles', [])

    else:
        async with get_session() as session:
            # Query to find or insert the command in the database
            stmt = select(Command).where(
                Command.guild_id == ctx.guild.id,
                Command.command_name == command_name
            )
            result = await session.execute(stmt)
            command = result.scalars().first()

            if not command:
                new_command = Command(guild_id=ctx.guild.id, command_name=command_name)
                session.add(new_command)
                await session.commit()
                command = new_command

            stmt = select(CommandRestriction).where(
                CommandRestriction.command_id == command.command_id
            )

            restrictions = await session.execute(stmt)
            restrictions = restrictions.scalars().all()

            channels, roles = [], []
            for restriction in restrictions:
                if restriction.restriction_type == 'channel':
                    channels.append(restriction.restriction_target)
                elif restriction.restriction_type == 'role':
                    roles.append(restriction.restriction_target)
                    
            if guild_id not in bot.restricted_commands_cache:
                bot.restricted_commands_cache[guild_id] = {}

            bot.restricted_commands_cache[guild_id][command_name] = {'channels': channels, 'roles': roles}

    channel_allowed = channel_id in channels if channels else True
    role_allowed = any(role_id in roles for role_id in user_roles) if roles else True    

    if channel_allowed and role_allowed:
        return True
    else:
        await ctx.send(f"You're not allowed to use this command {'here' if not channel_allowed else 'due to lack of permissions'}.", delete_after=10)
        try:
            await ctx.message.delete(delay=10)
        except Exception:
            pass
        return False
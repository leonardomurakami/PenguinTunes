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


from sqlalchemy import select

from modules.orm.database import RestrictedCommands
from discord.ext import commands


class Struct(object):
    def __init__(self, *args):
        """
        Constructor for the Struct class.
        - Initializes the Struct with a header if provided.
        Parameters:
            - *args: Variable length argument list, the first argument is used as the header.
        """
        self.__header__ = str(args[0]) if args else None

    def __repr__(self):
        """
        Representation method for the Struct.
        - Returns a string representation of the Struct.
        - If a header is set, it returns the header; otherwise, it returns the default object
            representation.
        """
        if self.__header__ is None:
            return super(Struct, self).__repr__()
        return self.__header__

    def next(self):
        """
        Fake iteration functionality.
        - Raises StopIteration to simulate the behavior of an iterator.
        - This method is a placeholder and does not provide actual iteration functionality.
        """
        raise StopIteration

    def __iter__(self):
        """
        Custom iterator for the Struct.
        - Iterates over the attributes of the Struct instance.
        - Skips magic attributes (those starting with '__') and attributes that are instances of Struct.
        Yields:
            - Yields the values of the non-magic, non-Struct attributes of the instance.
        """
        ks = self.__dict__.keys()
        for k in ks:
            if not k.startswith("__") and not isinstance(k, Struct):
                yield getattr(self, k)

    def __len__(self):
        """
        Length method for the Struct.
        - Calculates the number of non-magic, non-Struct attributes in the Struct.
        Returns:
            - (int): The number of relevant attributes in the Struct instance.
        """
        ks = self.__dict__.keys()
        return len(
            [k for k in ks if not k.startswith("__") and not isinstance(k, Struct)]
        )


async def allowed_on_channel(command: str, bot: commands.Bot, ctx: commands.Context):
    """
    Check if command can be run in this channel. First checking if command is in bot.restricted_commands_cache, if not, then checking database.
    """
    if ctx.channel.guild.id in bot.restricted_commands_cache.keys():
        if command in bot.restricted_commands_cache[ctx.channel.guild.id].keys():
            if (
                bot.restricted_commands_cache[ctx.channel.guild.id][command] == ctx.channel.id or 
                not bot.restricted_commands_cache[ctx.channel.guild.id][command]
            ):
                return True
            else:
                await ctx.send(f"This command is restricted to <#{bot.restricted_commands_cache[ctx.channel.guild.id][command]}> in this guild.", ephemeral=True, delete_after=10)
                return False
    else:
        bot.restricted_commands_cache[ctx.channel.guild.id] = {}
            
    async with bot.session as session:
        result = await session.execute(
            select(RestrictedCommands).where(
                RestrictedCommands.command_id == f"{str(ctx.channel.guild.id)}_{command}"
            )
        )
        command = result.scalars().first()
        if not command:
            bot.restricted_commands_cache[ctx.channel.guild.id][command] = None
            return True
        else:
            bot.restricted_commands_cache[ctx.channel.guild.id][command] = command.channel
            if command.channel == ctx.channel.id:
                return True
            else:
                await ctx.send(f"This command is restricted to <#{bot.restricted_commands_cache[ctx.channel.guild.id][command]}> in this guild.", ephemeral=True, delete_after=10)
                return False
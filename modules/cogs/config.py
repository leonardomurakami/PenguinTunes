from discord import Object
from discord.ext import commands
from modules.globals import config

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='refresh-guilds')
    async def refresh_guilds(self, ctx: commands.Context):
        """
        Owner only command, sync the command tree for all guilds. 
        """
        if int(ctx.author.id) == int(config.bot_owner_id):
            for server in self.bot.guilds:
                await self.bot.tree.sync(guild=Object(id=server.id))
        else:
            await ctx.send(f'You must be the owner to use this command!')

    @commands.command(name='refresh')
    async def refresh(self, ctx: commands.Context):
        """
        Owner only command, sync the command tree for all guilds. 
        """
        if int(ctx.author.id) == int(config.bot_owner_id):
            await self.bot.tree.sync()
        else:
            await ctx.send(f'You must be the owner to use this command!')
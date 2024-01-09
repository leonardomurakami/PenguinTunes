import nextcord
import asyncio
import os

from nextcord.ext import commands
from modules.music import Music

intents = nextcord.Intents.all()
client = nextcord.Client()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("p!"),
    description='Simple music bot.',
    intents=intents,
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


bot.add_cog(Music(bot))
bot.run(os.getenv("TOKEN"))

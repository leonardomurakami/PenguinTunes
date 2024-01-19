"""
Class Documentation: Fun Cog

The Fun class is a Discord bot cog that provides miscellaneous fun functionalities.

Class Methods:

1. __init__(self, bot)
   Initializes the Fun cog with a reference to the bot instance.
   - bot: The instance of the bot that the cog is a part of.

2. sisyphus(self, ctx, *, quote = None)
   Creates an image with a quote superimposed on a Sisyphus base image.
   - ctx: The context of the command.
   - quote: A string representing the quote to be added to the image. If a Discord user is mentioned, their avatar is added to the image.

Additional Notes:
- The command 'sisyphus' allows users to generate images with custom quotes.
- It uses the Python Imaging Library (PIL) to draw text and images onto a base image.
- The command handles mentions in the quote by removing the mention text and optionally pasting the mentioned user's avatar onto the image.
- The final image is sent back to the Discord channel where the command was invoked.
"""
import datetime
import discord
import re
import textwrap

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from sqlalchemy import select
from modules.globals import config
from modules.orm.database import Cassino
from modules.player.cassino import SlotMachine
from modules.views.fun import CassinoView


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sisyphus")
    async def add_quote(self, ctx: commands.Context, *, quote=None):
        """
        Creates an image with a quote superimposed on a Sisyphus base image.
        - ctx: The context of the command.
        - quote: A string representing the quote to be added to the image. If a Discord user is mentioned, their avatar is added to the image.
        """
        base_image = Image.open(config.fun.sisyphus_image_path)
        font = ImageFont.truetype(config.fun.font_path, config.fun.font_size)
        if quote:
            draw = ImageDraw.Draw(base_image)
            text_position = (50, base_image.height // 2)
            wrapped_text = textwrap.fill(re.sub(r"<@\d+>", "", quote).strip(), width=40)
            draw.multiline_text(text_position, wrapped_text, fill=(0, 0, 0), font=font)

        if mention_list := ctx.message.mentions:
            member = mention_list[0]
            avatar_size = 40  # Adjust size as needed
            avatar_data = await member.display_avatar.read()
            avatar_image = Image.open(BytesIO(avatar_data))
            avatar_image = avatar_image.resize((avatar_size, avatar_size))
            avatar_position = (base_image.width // 2, base_image.height // 2)
            base_image.paste(avatar_image, avatar_position)

        final_buffer = BytesIO()
        base_image.save(final_buffer, "PNG")
        final_buffer.seek(0)
        await ctx.send(file=discord.File(final_buffer, "quote_image.png"))

    @commands.command(name="cassino")
    async def cassino(self, ctx: commands.Context):
        """
        Creates a cassino instance. All should be controlled by the view and buttons.
        - ctx: The context of the command.
        """
        await ctx.send(view=CassinoView(member=ctx.author))

    @commands.command(name="jackpot")
    async def jackpot(self, ctx: commands.Context):
        """
        Sends the current jackpot.
        - ctx: The context of the command.
        """
        slot_machine = SlotMachine()
        jackpot = await slot_machine.get_jackpot()
        await ctx.send(f"The current jackpot is ${jackpot}\nYou can claim it by getting a {(config.emoji.cassino.diamond + ' ')*3} in the cassino slots game!\nGood luck!")

    @commands.command(name="money", aliases=["balance"])
    async def balance(self, ctx: commands.Context):
        """
        Sends the player current money.
        - ctx: The context of the command.
        """
        async with self.bot.session as session:
            player = await session.get(Cassino, int(ctx.author.id))
            if not player:
                player = Cassino(id=ctx.author.id, balance=1000)
                session.add(player)
                await session.commit()
                await session.refresh(player)
        await ctx.send(f"You have ${player.balance}")


    @commands.command(name="daily")
    async def daily(self, ctx: commands.Context):
        """
        Gets 1000$ daily. Command can only be ran once a day.
        - ctx: The context of the command.
        """
        async with self.bot.session as session:
            player = await session.get(Cassino, int(ctx.author.id))
            if not player:
                player = Cassino(id=ctx.author.id, balance=1000)
                session.add(player)
                await session.commit()
                await session.refresh(player)
            if player.last_daily and player.last_daily.date() == datetime.datetime.now(datetime.timezone.utc).date():
                next_daily_time = player.last_daily + datetime.timedelta(days=1)
                aware_last_daily = next_daily_time.replace(tzinfo=datetime.timezone.utc)
                time_remaining = aware_last_daily - datetime.datetime.now(datetime.timezone.utc)
                hours, remainder = divmod(time_remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    time_message = f"{hours} hours and {minutes} minutes"
                else:
                    time_message = f"{minutes} minutes and {seconds} seconds"
                
                await ctx.send(f"You already claimed your daily for today! Come back in {time_message}.")
                return
            player.balance += 1000
            player.last_daily = datetime.datetime.now(datetime.timezone.utc)
            await session.commit()
            await session.refresh(player)
        await ctx.send(f"You claimed your daily! You now have ${player.balance}")

    @commands.command(name="leaderboard", aliases=["top"])
    async def leaderboard(self, ctx: commands.Context):
        """
        Sends the leaderboard.
        - ctx: The context of the command.
        """
        async with self.bot.session as session:
            players = await session.execute(select(Cassino).order_by(Cassino.balance.desc()).limit(10))
            players = players.scalars().all()
        embed = discord.Embed(title="Cassino Leaderboard", color=discord.Color.green())
        for player, emoji in zip(players, config.emoji.cassino.leaderboard):
            embed.add_field(name=f"{emoji} - {self.bot.get_user(player.id)}", value=f"${player.balance}", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context):
        """
        Sends the player stats.
        - ctx: The context of the command.
        """
        async with self.bot.session as session:
            player = await session.get(Cassino, int(ctx.author.id))
            if not player:
                player = Cassino(id=ctx.author.id, balance=1000)
                session.add(player)
                await session.commit()
                await session.refresh(player)
        embed = discord.Embed(title=f"{ctx.author.name}'s stats", color=discord.Color.green())
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="Balance", value=f"${player.balance}")
        embed.add_field(name="Money won", value=f"${player.money_won}")
        embed.add_field(name="Money lost", value=f"${player.money_lost}")
        embed.add_field(name="Slot wins", value=f"${player.slot_wins}")
        embed.add_field(name="Blackjack wins", value=f"${player.blackjack_wins}")
        await ctx.send(embed=embed)
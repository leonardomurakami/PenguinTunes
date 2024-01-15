import discord
import re
import textwrap

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from modules.globals import config

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sisyphus")
    async def add_quote(self, ctx, *, quote = None):
        base_image = Image.open(config.fun.sisyphus_image_path)
        font = ImageFont.truetype(config.fun.font_path, config.fun.font_size)
        if quote:
            draw = ImageDraw.Draw(base_image)
            text_position = (50, base_image.height//2)
            wrapped_text = textwrap.fill(re.sub(r'<@\d+>', '', quote).strip(), width=40)
            draw.multiline_text(text_position, wrapped_text, fill=(0, 0, 0), font=font)

        if (mention_list := ctx.message.mentions):
            member = mention_list[0]
            avatar_size = 40 # Adjust size as needed
            avatar_data = await member.display_avatar.read()
            avatar_image = Image.open(BytesIO(avatar_data))
            avatar_image = avatar_image.resize((avatar_size, avatar_size))
            avatar_position = (base_image.width//2, base_image.height//2)
            base_image.paste(avatar_image, avatar_position)

        final_buffer = BytesIO()
        base_image.save(final_buffer, "PNG")
        final_buffer.seek(0)
        await ctx.send(file=discord.File(final_buffer, 'quote_image.png'))
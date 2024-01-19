"""
Module Documentation: Bot Configuration

This module defines the configuration settings for a bot, organized into different sections. 
Each section represents a specific aspect of the bot's functionality and settings.

1. General Bot Configuration (`config`)
   - default_prefix: Default command prefix for the bot (`str`).
   - token: Token for the Discord bot, retrieved from environment variables (`str`).
   - bot_owner_id: Discord ID of the bot owner, retrieved from environment variables (`str`).

2. Fun Section Configuration (`config.fun`)
   - font_size: Font size for text-based fun features (`int`).
   - font_path: File path to the font used for text-based fun features (`str`).
   - sisyphus_image_path: File path to the image of Sisyphus used in fun features (`str`).

3. Database Configuration (`config.database`)
   - db_username: Database username, retrieved from environment variables (`str`).
   - db_password: Database password, retrieved from environment variables (`str`).
   - db_host: Database host address, retrieved from environment variables (`str`).
   - db_port: Database port, retrieved from environment variables (`str`).
   - db_database: Database name, retrieved from environment variables (`str`).
   - connection_url: Full connection URL for the database (`str`).
   - db_driver: Database driver used by sqlalchemy(`str`).

4. Lavalink Configuration (`config.lavalink`)
   - host: Host address for Lavalink server, retrieved from environment variables (`str`).
   - port: Port number for Lavalink server, retrieved from environment variables (`str`).
   - password: Password for Lavalink server, retrieved from environment variables (`str`).

5. Emoji Configuration (`config.emoji`)
   - success: Emoji used to indicate success (`str`).
   - fail: Emoji used to indicate failure (`str`).
   - queue_decorators: List of emojis used as decorators for queues (`list` of `str`).
   - av_emoji: Emojis used for player buttons, each with a specific function (`Section`).
"""
import os
from modules.utils._config_utils import Struct as Section

# configs

config = Section("Bot configs and constants")
config.default_prefix = "p!"
config.token = os.getenv("TOKEN")
config.bot_owner_id = os.getenv("BOT_OWNER_ID")

config.fun = Section("Fun section configuration and assets")
config.fun.font_size = 14
config.fun.font_path = "assets/fonts/Roboto-Light.ttf"
config.fun.sisyphus_image_path = "assets/pictures/sisyphus.jpg"
config.fun.cassino_adjustment_factor = 1.5
config.fun.house_retain = 0.1

config.database = Section("Database config section")
config.database.db_username = os.getenv("DB_USERNAME")
config.database.db_password = os.getenv("DB_PASSWORD")
config.database.db_host = os.getenv("DB_HOST")
config.database.db_port = os.getenv("DB_PORT")
config.database.db_database = os.getenv("DB_DATABASE")
config.database.connection_url = f"{config.database.db_username}:{config.database.db_password}@{config.database.db_host}:{config.database.db_port}/{config.database.db_database}"
config.database.db_driver = "mysql+asyncmy"

config.lavalink = Section("Lavalink config section")
config.lavalink.host = os.getenv("LAVALINK_SERVER_HOST")
config.lavalink.port = os.getenv("LAVALINK_SERVER_PORT")
config.lavalink.password = os.getenv("LAVALINK_SERVER_PASSWORD")

config.emoji = Section("Emoji config section, holds constants mostly")
config.emoji.success = "\u2705"
config.emoji.fail = "\u274c"

config.emoji.queue_decorators = Section("Emoji decorators for queue")
config.emoji.queue_decorators = [
    "\U0001F535",
    "\u26ab",
    "\U0001F7E3",
    "\U0001F7E4",
    "\U0001F7E2",
    "\U0001F7E1",
    "\U0001F7E0",
    "\u26aa",
]

config.emoji.av_emoji = Section("Emojis for player buttons")
config.emoji.av_emoji.pause_play = "\u23ef\ufe0f"
config.emoji.av_emoji.last_track = "\u23ee\ufe0f"
config.emoji.av_emoji.next_track = "\u23ed\ufe0f"
config.emoji.av_emoji.shuffle = "\U0001F500"
config.emoji.av_emoji.autoplay = "\U0001F195"
config.emoji.av_emoji.repeat = "\U0001F501"
config.emoji.av_emoji.repeat_one = "\U0001F502"
config.emoji.av_emoji.wireless = "\U0001F6DC"
config.emoji.av_emoji.mobile = "\U0001F4F6"
config.emoji.av_emoji.play = "\u25b6\ufe0f"
config.emoji.av_emoji.pause = "\u23f8\ufe0f"

config.emoji.alphanumeric = Section("Emojis for alphanumeric")
config.emoji.alphanumeric.zero = "\u0030\ufe0f\u20e3"
config.emoji.alphanumeric.one = "\u0031\ufe0f\u20e3"
config.emoji.alphanumeric.two = "\u0032\ufe0f\u20e3"
config.emoji.alphanumeric.three = "\u0033\ufe0f\u20e3"
config.emoji.alphanumeric.four = "\u0034\ufe0f\u20e3"
config.emoji.alphanumeric.five = "\u0035\ufe0f\u20e3"
config.emoji.alphanumeric.six = "\u0036\ufe0f\u20e3"
config.emoji.alphanumeric.seven = "\u0037\ufe0f\u20e3"
config.emoji.alphanumeric.eight = "\u0038\ufe0f\u20e3"
config.emoji.alphanumeric.nine = "\u0039\ufe0f\u20e3"
config.emoji.alphanumeric.ten = "\U0001f51f"
config.emoji.alphanumeric.star = "\u2b50"

config.emoji.cassino = Section("Emojis for cassino")
config.emoji.cassino.diamond = "\U0001F48E"
config.emoji.cassino.cherry = "\U0001F352"
config.emoji.cassino.lemon = "\U0001F34B"
config.emoji.cassino.orange = "\U0001F34A"
config.emoji.cassino.apple = "\U0001F34E"
config.emoji.cassino.grapes = "\U0001F347"
config.emoji.cassino.banana = "\U0001F34C"
config.emoji.cassino.slots = "\U0001F3B0"
config.emoji.cassino.leaderboard = [
   config.emoji.alphanumeric.star,
   config.emoji.alphanumeric.two,
   config.emoji.alphanumeric.three, 
   config.emoji.alphanumeric.four, 
   config.emoji.alphanumeric.five, 
   config.emoji.alphanumeric.six, 
   config.emoji.alphanumeric.seven, 
   config.emoji.alphanumeric.eight, 
   config.emoji.alphanumeric.nine,
   config.emoji.alphanumeric.ten
]
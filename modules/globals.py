import os
from modules._config import Struct as Section

# configs

config = Section("Bot configs and constants")
config.default_prefix = "p!"
config.token = os.getenv("TOKEN")
config.bot_owner_id = os.getenv("BOT_OWNER_ID")

config.lavalink = Section("Lavalink config section")
config.lavalink.host = os.getenv("LAVALINK_SERVER_HOST")
config.lavalink.port = os.getenv("LAVALINK_SERVER_PORT")
config.lavalink.password = os.getenv("LAVALINK_SERVER_PASSWORD")

config.emoji = Section("Emoji config section, holds constants mostly")
config.emoji.success="\u2705"
config.emoji.fail="\u274c"

config.emoji.queue_decorators = Section("Emoji decorators for queue")
config.emoji.queue_decorators = [
    "\U0001F535", "\u26ab", "\U0001F7E3", 
    "\U0001F7E4", "\U0001F7E2", "\U0001F7E1", 
    "\U0001F7E0", "\u26aa"
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

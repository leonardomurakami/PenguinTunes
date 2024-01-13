import logging
import asyncio
import discord
import os
import wavelink

from starlight import PaginateHelpCommand
from modules.globals import BOT_PREFIX
from discord.ext import commands
from modules.cogs.music import Music
from utils import create_track_embed, milliseconds_to_mm_ss
from modules.views.music_view import PlayerView

class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        discord.utils.setup_logging()
        super().__init__(
            command_prefix=BOT_PREFIX, 
            intents=intents, 
            description="Piplup",
            help_command=PaginateHelpCommand()
        )

    async def setup_hook(self) -> None:
        nodes = [
            wavelink.Node(uri="http://lavalink:2333", password=os.getenv("LAVALINK_SERVER_PASSWORD")),
        ]
        await wavelink.Pool.connect(nodes=nodes, client=self)

    async def on_ready(self):
        logging.info(f"Logged in: {self.user} | {self.user.id}")

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        logging.info(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return
        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        embed=create_track_embed(track, original)
        view=PlayerView(player=player, timeout=track.length)
        await player.home.send(embed=embed, view=view)

    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return
        if player.queue:
            await player.play(player.queue.get())
        else:
            await player.channel.send(f"The queue is over. Goodbye!")
            await player.disconnect()

bot: Bot = Bot()

async def main() -> None:
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())

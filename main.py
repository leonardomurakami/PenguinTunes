import logging
import asyncio
import discord
import os
import wavelink

from modules.configs import BOT_PREFIX
from discord.ext import commands
from modules.music import Music

class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        discord.utils.setup_logging()
        super().__init__(command_prefix=BOT_PREFIX, intents=intents, description="Piplup")

    async def setup_hook(self) -> None:
        nodes = [
            wavelink.Node(uri="http://localhost:2333", password=os.getenv("LAVALINK_SERVER_PASSWORD")),
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
        embed: discord.Embed = discord.Embed(title="Now Playing")
        embed.description = f"**{track.title}** by `{track.author}`"
        if track.artwork:
            embed.set_image(url=track.artwork)
        if original and original.recommended:
            embed.description += f"\n\n`This track was recommended via {track.source}`"
        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)
        await player.home.send(embed=embed)

async def main() -> None:
    bot = Bot()
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())



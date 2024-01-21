import logging
import asyncio
import discord
import os
import wavelink

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from starlight import PaginateHelpCommand
from discord.ext import commands

from modules.utils._text_utils import create_track_embed
from modules.globals import config
from modules.cogs.music import Music
from modules.cogs.fun import Fun
from modules.cogs.config import Config
from modules.views.music import PlayerView
from modules.orm.database import Guild
from modules.utils._database_utils import get_session

# TODO: Implement commands outside of Music cog. Fun cog, Modding cog.
# TODO: Implement simple dashboard to visualize, queue, control playstate of music from web.
# TODO: Allow members to save a playlist to bots database for quick players
# FIXME: Bot won't leave channel if music is paused, no matter how long it stays paused.


class Bot(commands.Bot):
    """
    This class represents a Discord bot built using the discord.py library, integrated with Wavelink for music playback.

    Attributes:
        session (AsyncSession): Represents a SQLAlchemy session for database operations.

    The bot is configured with a specific command prefix and intents. It includes a custom help command and
    methods for handling music playback events using Wavelink nodes.

    Methods:
        setup_hook: Asynchronously sets up Wavelink nodes for music playback.
        on_ready: Logs information when the bot successfully logs in.
        on_wavelink_node_ready: Logs information when a Wavelink node is connected.
        on_wavelink_track_start: Handles the event when a track starts playing.
        on_wavelink_track_end: Handles the event when a track finishes playing.
    """

    def __init__(self) -> None:
        """
        Initializes the Bot instance with a specific command prefix, intents, description, and a custom help command.
        Sets up logging and initializes the superclass.
        """
        self.guild_prefix_cache = {}
        self.restricted_commands_cache = {}
        
        intents = discord.Intents.all()
        discord.utils.setup_logging()
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            description="Piplup",
            help_command=PaginateHelpCommand(),
        )

    async def get_prefix(self, message):
        if not message.guild:
            return commands.when_mentioned_or(config.default_prefix)(bot, message)
        if message.guild.id in self.guild_prefix_cache.keys():
            prefix = self.guild_prefix_cache[message.guild.id]
        else:
            async with self.session as session:
                result = await session.execute(
                    select(Guild).where(Guild.id == int(message.guild.id))
                )
                guild = result.scalars().first()
                if not guild:
                    await session.execute(
                        insert(Guild).values(
                            id=message.guild.id, prefix=config.default_prefix
                        )
                    )
                    await session.commit()
                    prefix = config.default_prefix
                else:
                    prefix = guild.prefix
        return commands.when_mentioned_or(prefix)(self, message)

    @property
    def session(self) -> AsyncSession:
        """
        Property that returns an AsyncSession object for database interactions.
        """
        return get_session()

    async def setup_hook(self) -> None:
        """
        Asynchronously sets up the necessary Wavelink nodes for music playback.
        This method is a part of the bot's setup process.
        """
        nodes = [
            wavelink.Node(
                uri=f"{config.lavalink.host}:{config.lavalink.port}",
                password=config.lavalink.password,
            ),
        ]
        await wavelink.Pool.connect(nodes=nodes, client=self)

    async def on_ready(self):
        """
        Event listener that is called when the bot is ready. It logs the bot's username and ID.
        """
        logging.info("Logged in: %s | %s", self.user, self.user.id)

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        """
        Event listener called when a Wavelink node is successfully connected.
        Logs information about the node.

        Args:
            payload (wavelink.NodeReadyEventPayload): The payload containing information about the Wavelink node that has just connected.
        """

        logging.info(
            "Wavelink Node connected: %s | Resumed: %s", payload.node, payload.resumed
        )

    def log(self, message: str) -> None:
        """
        Logs a message to the console.

        Args:
            message (str): The message to log.
        """
        logging.info(message)

    async def on_wavelink_track_start(
        self, payload: wavelink.TrackStartEventPayload
    ) -> None:
        """
        Event listener for when a track starts playing.
        It creates an embed and view for the playing track and sends it to the player's designated channel.

        Args:
            payload (wavelink.TrackStartEventPayload): Payload containing information about the track that started playing.
        """
        player: wavelink.Player | None = payload.player
        if not player:
            return
        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        embed = create_track_embed(track, original)
        view = PlayerView(player=player, timeout=track.length)
        await player.home.send(embed=embed, view=view)

    async def on_wavelink_track_end(
        self, payload: wavelink.TrackEndEventPayload
    ) -> None:
        """
        Event listener for when a track ends.
        It plays the next track in the queue if available, or sends a message indicating the end of the queue.

        Args:
            payload (wavelink.TrackEndEventPayload): Payload containing information about the track that has ended.
        """
        player: wavelink.Player | None = payload.player
        if not player:
            return
        if player.queue:
            await player.play(player.queue.get())  # HACK: Is this necessary?
        elif player.autoplay == wavelink.AutoPlayMode.disabled:
            await player.home.send("The queue is over. Goodbye!")
            await player.disconnect()

    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        await player.channel.send(
            f"The player has been inactive for `{player.inactive_timeout}` seconds. Goodbye!"
        )
        await player.disconnect()

    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return
        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()


bot: Bot = Bot()


async def main() -> None:
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.add_cog(Config(bot))
        await bot.add_cog(Fun(bot))
        await bot.start(os.getenv("TOKEN"))


asyncio.run(main())

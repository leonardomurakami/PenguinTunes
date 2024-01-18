"""
Class Documentation: Music Cog

The Music class is a Discord bot cog that provides music playback functionality. It includes commands for controlling music playback in a Discord server.

Class Methods:

1. __init__(self, bot)
   Initializes the Music cog with a reference to the bot instance.
   - bot: The instance of the bot that the cog is a part of.

2. stop(self, ctx: commands.Context)
   Stops music playback and clears the queue.
   - ctx: The context of the command, which includes information about the command invocation.

3. shuffle(self, ctx: commands.Context)
   Shuffles the current music queue.
   - ctx: The context of the command.

4. play(self, ctx: commands.Context, *, query: str)
   Plays a song based on a given query.
   - ctx: The context of the command.
   - query: A search term or URL to find and play music.

5. skip(self, ctx: commands.Context)
   Skips the current song in the queue.
   - ctx: The context of the command.

6. pause(self, ctx: commands.Context)
   Pauses or resumes the current song.
   - ctx: The context of the command.

7. leave(self, ctx: commands.Context)
   Disconnects the bot from the voice channel.
   - ctx: The context of the command.

8. nightcore(self, ctx: commands.Context)
   Applies a nightcore filter to the music.
   - ctx: The context of the command.

9. normal(self, ctx: commands.Context)
   Resets any active music filters to normal.
   - ctx: The context of the command.

10. queue(self, ctx: commands.Context)
    Displays the current music queue.
    - ctx: The context of the command.

11. nowplaying(self, ctx: commands.Context)
    Shows information about the currently playing song.
    - ctx: The context of the command.

12. autoplay(self, ctx: commands.Context, *, autoplay_mode: str)
    Sets the autoplay mode for the bot.
    - ctx: The context of the command.
    - autoplay_mode: A string representing the autoplay mode. Valid modes include 'enabled', 'partial', 'disabled'.

13. volume(self, ctx: commands.Context, volume: float)
    Changes the player's volume.
    - ctx: The context of the command.
    - volume: A float representing the new volume level, with valid values between 0 and 1.

14. loop(self, ctx: commands.Context, loop_mode: str)
    Changes the player's loop mode.
    - ctx: The context of the command.
    - loop_mode: A string representing the loop mode. Valid modes are 'normal', 'loop', 'loop_all'.

Additional Notes:
- The Music cog integrates with the wavelink library for music playback and control.
- It uses various commands to manage music in a voice channel, such as playing, pausing, skipping, and adjusting volume.
- The cog also supports more advanced features like shuffling the queue, setting autoplay modes, and applying audio filters.
- The cog is designed to be added to a discord.ext.commands.Bot or discord.ext.commands.AutoShardedBot instance for use in a Discord bot application.
"""
import random
from typing import cast
import discord
import wavelink

from discord.ext import commands

from modules.globals import config
from modules.utils._text_utils import create_track_embed, milliseconds_to_mm_ss

# TODO: Make player.queue write to a database to allow seamless bot restarts without losing current music queue


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #playback commands
    @commands.hybrid_command(name="stop", aliases=["clear", "stopplaying"])
    async def stop(self, ctx: commands.Context):
        """
        Stops the music playback and clears the queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        player.queue.clear()
        player.autoplay = wavelink.AutoPlayMode.disabled
        await player.seek(player.current.length)
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="shuffle", aliases=["randomize", "random"])
    async def shuffle(self, ctx: commands.Context):
        """
        Shuffles the music queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        player.queue.shuffle()
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="play", aliases=["p", "add", "enqueue", "addsong"])
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """
        Plays a song based on the given query. The query can be a URL or a search term.
        Prefix query with 'music:' for YouTube music searches.

        Parameters:
        query: A string representing the search query or URL for the track.
        """
        if not ctx.guild:
            return

        player: wavelink.Player
        player = cast(wavelink.Player, ctx.voice_client)

        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            except AttributeError:
                await ctx.send(
                    "Please join a voice channel first before using this command."
                )
                return
            except discord.ClientException:
                await ctx.send(
                    "I was unable to join this voice channel. Please try again."
                )
                return

        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await ctx.send(
                f"You can only play songs in {player.home.mention}, as the player has already started there."
            )
            return

        if query.startswith("http"):
            tracks: wavelink.Search = await wavelink.Playable.search(query)
        elif query.startswith("music:"):
            tracks: wavelink.Search = await wavelink.Playable.search(
                query, source="ytmsearch:"
            )
        elif query.startswith("spotify:"):
            tracks: wavelink.Search = await wavelink.Playable.search(
                query, source="spsearch:"
            )
        else:
            tracks: wavelink.Search = await wavelink.Playable.search(
                query, source="ytsearch:"
            )
        if not tracks:
            await ctx.send(
                f"{ctx.author.mention} - Could not find any tracks with that query. Please try again."
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(
                f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue."
            )
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await ctx.send(f"Added **`{track}`** to the queue.")

        if not player.playing:
            await player.play(player.queue.get(), volume=30)

    @commands.hybrid_command(name="skip", aliases=["fs", "forceskip"])
    async def skip(self, ctx: commands.Context) -> None:
        """
        Skips the current song in the queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        if player.queue:
            await player.seek(player.current.length)
        else:
            await player.stop()
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="pause", aliases=["resume", "unpause", "despause"])
    async def pause(self, ctx: commands.Context):
        """
        Toggles playback pause/resume.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        if player.playing:
            await player.pause(not player.paused)
            await ctx.message.add_reaction(f"{config.emoji.success}")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.hybrid_command(name="leave", aliases=["disconnect", "dc"])
    async def leave(self, ctx: commands.Context) -> None:
        """
        Disconnects the player from the voice channel.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        await player.disconnect()
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="queue", aliases=["q", "next", "upnext"])
    async def queue(self, ctx: commands.Context) -> None:
        """
        Displays the current music queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        if player.queue:
            queue_description = ""
            if player.current:
                time_to_music = player.current.length - player.position
            else:
                time_to_music = 0
            for track in player.queue[:10]:
                queue_description += f"{random.choice(config.emoji.QUEUE_DECORATORS)} {track.title[:20]} by {track.author} | in {milliseconds_to_mm_ss(time_to_music)}\n"
                time_to_music += track.length

            embed: discord.Embed = discord.Embed(title="Next up!")
            embed.description = queue_description
            if len(player.queue) > 10:
                embed.description += f"\n...and {len(player.queue) - 10} more tracks"
            embed.color = discord.Color.blurple()
            await player.home.send(embed=embed)
            await ctx.message.add_reaction(f"{config.emoji.success}")
        else:
            await ctx.send("Queue is empty. Try adding some music to it")
            await ctx.message.add_reaction(f"{config.emoji.fail}")

    @commands.hybrid_command(name="np", aliases=["nowplaying", "current", "currentsong"])
    async def nowplaying(self, ctx: commands.Context) -> None:
        """
        Shows information about the currently playing song.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        track = player.current
        embed = create_track_embed(track, None)
        embed.remove_field(0)
        embed.add_field(
            name="Current",
            value=f"{milliseconds_to_mm_ss(player.position)}/{milliseconds_to_mm_ss(track.length)}",
        )
        await player.home.send(embed=embed)

    @commands.hybrid_command(name="autoplay", aliases=["ap", "autopl"])
    async def autoplay(self, ctx: commands.Context, *, autoplay_mode: str) -> None:
        """
        Sets the autoplay mode for the bot. Use p!help autoplay to see modes.

        Parameters:
        autoplay_mode: A string representing the autoplay mode. 'enabled', 'partial', 'disabled'.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        autoplay_enum = {
            "enabled": wavelink.AutoPlayMode.enabled,
            "partial": wavelink.AutoPlayMode.partial,
            "disabled": wavelink.AutoPlayMode.disabled,
        }
        if autoplay_mode in ["enabled", "partial", "disabled"]:
            await ctx.send(
                f"Autoplay mode changed from {player.autoplay} to {autoplay_mode}"
            )
            player.autoplay = autoplay_enum[autoplay_mode]
            await ctx.message.add_reaction(f"{config.emoji.success}")
        else:
            await ctx.send(
                "Invalid mode passed. Valid modes are: {enabled, partial, disabled}"
            )
            await ctx.message.add_reaction(f"{config.emoji.fail}")

    @commands.hybrid_command(name="volume", aliases=["vol"])
    async def volume(self, ctx: commands.Context, volume: float) -> None:
        """
        Changes the player's volume.

        Parameters:
        volume: An integer or float representing the new volume level.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        if volume > 0 and volume <= 0.2:
            volume = volume * 1000
        elif volume > 0.2 and volume <= 1:
            volume = 200
        else:
            await ctx.send(
                "Invalid volume passed. Value should be from 0 to 1 [Default is 0.1]"
            )
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        player.set_volume(volume)
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="loop", aliases=["repeat"])
    async def loop(self, ctx: commands.Context, loop_mode: str) -> None:
        """
        Changes the player's loop mode. Use p!help loop to see modes.

        Parameters:
        loop_mode: A string representing the loop mode. Valid modes: 'normal', 'loop', 'loop_all'
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        loop_enum = {
            "normal": wavelink.QueueMode.normal,
            "loop": wavelink.QueueMode.loop,
            "loop_all": wavelink.QueueMode.loop_all,
        }
        if loop_mode in ["normal", "loop", "loop_all"]:
            if loop_mode == "normal":
                mode_explanation = "not loop either track or history"
            elif loop_mode == "loop":
                mode_explanation = "continuously loop one track"
            else:
                mode_explanation = "continuously loop through all tracks"
            player.queue.mode = loop_enum[loop_mode]
            await ctx.send(f"The bot is now set to {mode_explanation}")
            await ctx.message.add_reaction(f"{config.emoji.success}")
        else:
            await ctx.send(
                "Invalid or missing loop mode. Should be: {normal, loop, loop_all}"
            )
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return
        
    @commands.hybrid_command(name="nightcore")
    async def nightcore(self, ctx: commands.Context) -> None:
        """
        Sets the music filter to a nightcore style.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="normal", aliases=["removefilter", "nofilter", "resetfilters", "reset"])
    async def normal(self, ctx: commands.Context) -> None:
        """
        Resets the music filter to normal, removing any active filters.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        filters: wavelink.Filters = player.filters
        filters.reset()
        await player.set_filters(filters)
        await ctx.message.add_reaction(f"{config.emoji.success}")

    @commands.hybrid_command(name="nightcore")
    async def nightcore(self, ctx: commands.Context) -> None:
        """
        Sets the music filter to a nightcore style.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{config.emoji.fail}")
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)
        await ctx.message.add_reaction(f"{config.emoji.success}")
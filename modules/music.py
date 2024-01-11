import random
from typing import cast
import discord
import wavelink

from discord.ext import commands

from modules.globals import BOT_PREFIX, QUEUE_DECORATORS, GREEN_CHECKMARK_EMOJI, RED_CROSS_EMOJI
from utils import create_track_embed, milliseconds_to_mm_ss


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='stop')
    async def stop(self, ctx: commands.Context):
        """
        Stops the music playback and clears the queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        player.queue.clear()
        player.seek(player.current.length)
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")

    @commands.command(name='shuffle')
    async def shuffle(self, ctx: commands.Context):
        """
        Shuffles the music queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        player.queue.shuffle()
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")


    @commands.command(name='play', alias=['mp'])
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
                await ctx.send("Please join a voice channel first before using this command.")
                return
            except discord.ClientException:
                await ctx.send("I was unable to join this voice channel. Please try again.")
                return

        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await ctx.send(f"You can only play songs in {player.home.mention}, as the player has already started there.")
            return
        
        if query.startswith("http"):
            tracks: wavelink.Search = await wavelink.Playable.search(query)
        elif query.startswith("music:"):
            tracks: wavelink.Search = await wavelink.Playable.search(query, source="ytmsearch:")
        else:
            tracks: wavelink.Search = await wavelink.Playable.search(query, source="ytsearch:")
        if not tracks:
            await ctx.send(f"{ctx.author.mention} - Could not find any tracks with that query. Please try again.")
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await ctx.send(f"Added **`{track}`** to the queue.")

        if not player.playing:
            await player.play(player.queue.get(), volume=30)
    
    @commands.command(name='skip')
    async def skip(self, ctx: commands.Context) -> None:
        """
        Skips the current song in the queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        if player.queue:
            await player.seek(player.current.length)
        else:
            await player.stop()
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")
        
    @commands.command(name='pause', aliases=['resume', 'unpause', 'despause'])
    async def pause(self, ctx: commands.Context):
        """
        Toggles playback pause/resume.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        if player.playing:
            await player.pause(not player.paused)
            await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name='leave')
    async def leave(self, ctx: commands.Context) -> None:
        """
        Disconnects the player from the voice channel.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return

        await player.disconnect()
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")

    @commands.command(name='nightcore')
    async def nightcore(self, ctx: commands.Context) -> None:
        """
        Sets the music filter to a nightcore style.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")

    @commands.command()
    async def normal(self, ctx: commands.Context) -> None:
        """
        Resets the music filter to normal, removing any active filters.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return

        filters: wavelink.Filters = player.filters
        filters.reset()
        await player.set_filters(filters)
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")

    

    @commands.command(name='queue')
    async def queue(self, ctx: commands.Context) -> None:
        """
        Displays the current music queue.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        if player.queue:
            queue_description = ""
            if player.current:
                time_to_music = player.current.length - player.position
            else:
                time_to_music = 0
            for track in player.queue[:10]:
                queue_description += f"{random.choice(QUEUE_DECORATORS)} {track.title[:20]} by {track.author} | in {milliseconds_to_mm_ss(time_to_music)}\n"
                time_to_music += track.length
            
            embed: discord.Embed = discord.Embed(title="Next up!")
            embed.description = queue_description
            if len(player.queue) > 10:
                embed.description += f"\n...and {len(player.queue) - 10} more tracks"
            embed.color = discord.Color.blurple()
            await player.home.send(embed=embed)
            await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")
        else:
            await ctx.send("Queue is empty. Try adding some music to it")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")

    @commands.command(name='np')
    async def nowplaying(self, ctx: commands.Context) -> None:
        """
        Shows information about the currently playing song.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        track = player.current
        embed = create_track_embed(track, None)
        embed.remove_field(0)
        embed.add_field(name = 'Current', value=f"{milliseconds_to_mm_ss(player.position)}/{milliseconds_to_mm_ss(track.length)}")
        await player.home.send(embed=embed)
        
    @commands.command(name='autoplay')
    async def autoplay(self, ctx: commands.Context, *, autoplay_mode: str) -> None:
        """
        Sets the autoplay mode for the bot. Use p!help autoplay to see modes.
        
        Parameters:
        autoplay_mode: A string representing the autoplay mode. 'enabled', 'partial', 'disabled'.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        autoplay_enum = {
            "enabled": wavelink.AutoPlayMode.enabled,
            "partial": wavelink.AutoPlayMode.partial,
            "disabled": wavelink.AutoPlayMode.disabled,
        }
        if autoplay_mode in ['enabled', 'partial', 'disabled']:
            await ctx.send(f"Autoplay mode changed from {player.autoplay} to {autoplay_mode}")
            player.autoplay = autoplay_enum[autoplay_mode]
            await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")
        else:
            await ctx.send("Invalid mode passed. Valid modes are: {enabled, partial, disabled}")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")

    @commands.command(name='volume')
    async def volume(self, ctx: commands.Context, volume: int | float) -> None:
        """
        Changes the player's volume.

        Parameters:
        volume: An integer or float representing the new volume level.
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        if volume > 0 and volume <= 0.2:
            volume = volume * 1000
        elif volume > 0.2 and volume <= 1:
            volume = 200
        else:
            await ctx.send("Invalid volume passed. Value should be from 0 to 1 [Default is 0.1]")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return
        
        player.set_volume(volume)
        await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")

    @commands.command(name='loop')
    async def loop(self, ctx: commands.Context, loop_mode: str) -> None:
        """
        Changes the player's loop mode. Use p!help autoplay to see modes.

        Parameters:
        loop_mode: A string representing the loop mode. Valid modes: 'normal', 'loop', 'loop_all'
        """
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            await ctx.send("The bot is not connected to a voice channel")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return

        loop_enum = {
            "normal": wavelink.QueueMode.normal,
            "loop": wavelink.QueueMode.loop,
            "loop_all": wavelink.QueueMode.loop_all
        }
        if loop_mode in ['normal', 'loop', 'loop_all']:
            if loop_mode == 'normal':
                mode_explanation = "not loop either track or history"
            elif loop_mode == 'loop':
                mode_explanation = "continuously loop one track"
            else:
                mode_explanation = "continuously loop through all tracks"
            player.queue.mode = loop_enum[loop_mode]
            await ctx.send(f"The bot is now set to {mode_explanation}")
            await ctx.message.add_reaction(f"{GREEN_CHECKMARK_EMOJI}")
        else:
            await ctx.send("Invalid or missing loop mode. Should be: {normal, loop, loop_all}")
            await ctx.message.add_reaction(f"{RED_CROSS_EMOJI}")
            return

from ctypes import cast
import discord
import wavelink

from discord.ext import commands

from modules.configs import BOT_PREFIX


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='leave')
    async def leave(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Bot is not connected to any channel.")
    
    @commands.command(name='play')
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """Play a song with the given query."""
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

        # # Turn on AutoPlay to enabled mode.
        # # enabled = AutoPlay will play songs for us and fetch recommendations...
        # # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
        # # disabled = AutoPlay will do nothing...
        # player.autoplay = wavelink.AutoPlayMode.enabled

        # Lock the player to this channel...
        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await ctx.send(f"You can only play songs in {player.home.mention}, as the player has already started there.")
            return
        
        tracks: wavelink.Search = await wavelink.Playable.search(query)
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
    async def skip(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        if not player.playing:
            return await ctx.send("Nothing is playing.")
        if player.queue.is_empty:
            return await player.stop()
        
        await player.skip(force=True)
        await ctx.message.add_reaction("\u2705")
        
    @commands.command(name='pause', aliases=['resume', 'unpause', 'despause'])
    async def pause(self, ctx: commands.Context):
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return
        if player.playing:
            await player.pause(not player.paused)
            await ctx.message.add_reaction("\u2705")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name='leave', aliases=["dc"])
    async def leave(self, ctx: commands.Context) -> None:
        """Disconnect the Player."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.disconnect()
        await ctx.message.add_reaction("\u2705")

    @commands.command()
    async def nightcore(self, ctx: commands.Context) -> None:
        """Set the filter to a nightcore style."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)

        await ctx.message.add_reaction("\u2705")

    @commands.command()
    async def normal(self, ctx: commands.Context) -> None:
        """Set the filter to a normal style, ditching all filters."""
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.reset()
        await player.set_filters(filters)

        await ctx.message.add_reaction("\u2705")
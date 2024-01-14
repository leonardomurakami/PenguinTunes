"""
Module to hold all utility functions for bot.
Should be refactored if too long.
"""
import discord

def milliseconds_to_mm_ss(milliseconds: int):
    """Convert milliseconds to HH:MM:SS, if HH == 00, convert to MM:SS"""
    seconds = milliseconds // 1000
    hours, minutes, seconds = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"

def create_track_embed(track, original):
    """Default NowPlaying track embed"""
    embed: discord.Embed = discord.Embed(title="Now Playing")
    embed.description = f'```css\n{track.title}\n```'
    embed.color = discord.Color.blurple()
    embed.add_field(name = 'Duration', value=milliseconds_to_mm_ss(track.length))
    embed.add_field(name = 'Author', value=track.author)
    embed.add_field(name = 'URL', value=f'[Click]({track.uri})')
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    if original and original.recommended:
        embed.description += f"\n\n`This track was recommended via {track.source}`"
    if track.album.name:
        embed.add_field(name="Album", value=track.album.name)
    return embed

"""
Module Documentation: Discord Bot Utilities

This module provides utility functions related to Discord bot operations, including time formatting 
and creating embedded messages for Discord.

1. milliseconds_to_mm_ss(milliseconds: int)
   Converts milliseconds to a time format.
   - If hours are non-zero, converts to HH:MM:SS format.
   - If hours are zero, converts to MM:SS format.
   Parameters:
     - milliseconds (int): Time in milliseconds to be converted.
   Returns:
     - (str): Formatted time string.

2. create_track_embed(track, original)
   Creates a default 'Now Playing' track embed for Discord.
   - Sets the embed title to "Now Playing".
   - Includes track title, duration, author, URL, and artwork if available.
   - Adds additional details if the track is recommended or has an album name.
   Parameters:
     - track: An object representing the track, expected to have title, length, author, uri, 
              artwork, source, and album attributes.
     - original: An object representing the original context of the track, expected to have a 
                 recommended attribute.
   Returns:
     - discord.Embed: A Discord Embed object populated with track details.
"""

import discord
import wavelink


def milliseconds_to_mm_ss(milliseconds: int):
    """
    Converts milliseconds to a time format.
    - If hours are non-zero, converts to HH:MM:SS format.
    - If hours are zero, converts to MM:SS format.
    Parameters:
        - milliseconds (int): Time in milliseconds to be converted.
    Returns:
        - (str): Formatted time string.
    """
    seconds = milliseconds // 1000
    hours, minutes, seconds = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return (
        f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"
    )


def create_track_embed(track: wavelink.Playable, original: wavelink.Playable):
    """
    Creates a default 'Now Playing' track embed for Discord.
    - Sets the embed title to "Now Playing".
    - Includes track title, duration, author, URL, and artwork if available.
    - Adds additional details if the track is recommended or has an album name.
    Parameters:
        - track: An object representing the track, expected to have title, length, author, uri,
                artwork, source, and album attributes.
        - original: An object representing the original context of the track, expected to have a
                    recommended attribute.
    Returns:
        - discord.Embed: A Discord Embed object populated with track details.
    """
    embed: discord.Embed = discord.Embed(title="Now Playing")
    embed.description = f"```css\n{track.title}\n```"
    embed.color = discord.Color.blurple()
    embed.add_field(name="Duration", value=milliseconds_to_mm_ss(track.length))
    embed.add_field(name="Author", value=track.author)
    embed.add_field(name="URL", value=f"[Click]({track.uri})")
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    if original and original.recommended:
        embed.description += f"\n\n`This track was recommended via {track.source}`"
    if track.album.name:
        embed.add_field(name="Album", value=track.album.name)
    return embed

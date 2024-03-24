"""
Class Documentation: PlayerView

The PlayerView class is a subclass of `discord.ui.View` that provides an interactive interface for music player controls using buttons in Discord.

Class Methods:

1. __init__(self, *, player: wavelink.Player, timeout: float = 180)
   Initializes the PlayerView with a specific music player and optional timeout.
   - player: The `wavelink.Player` instance associated with this view.
   - timeout: The duration in seconds after which the view becomes inactive. Defaults to 180 seconds.

2. add_item(self, item: discord.ui.Item)
   Adds an interactive item (button) to the view.
   - Overridden from `discord.ui.View`.

3. destroy_view(self)
   Removes the view from the message it's attached to.
   - Can be used to clean up the interface after it's no longer needed.

4. disable_all_items(self)
   Disables all interactive items (buttons) in the view.
   - Useful for preventing further interaction once certain conditions are met, like the end of music playback.

5. on_timeout(self)
   Defines the behavior when the view times out.
   - Disables all items and attempts to destroy the view.

Additional Notes:
- `PlayerView` utilizes `MusicButton`, a custom button class, for creating various music control buttons like play/pause, next track, shuffle, etc.
- Each button is configured with specific labels and actions, derived from the `config.emoji.av_emoji` settings.
- This class offers a user-friendly way to control music playback directly from a Discord message, enhancing the bot's interactivity and usability.
- The view and buttons are tightly integrated with the `wavelink.Player` instance, allowing real-time control over the music player.
"""
import discord
import wavelink

from modules.buttons.music import MusicButton
from modules.globals import config


class PlayerView(discord.ui.View):
    def __init__(self, *, player: wavelink.Player, timeout: float = 180):
        if player is None:
            raise ValueError("Player cannot be None")
        if timeout < 0:
             raise ValueError("Timeout cannot be negative")

        super().__init__(timeout=timeout)
        self.player = player
        self.add_item(
            MusicButton(
                player, label=config.emoji.av_emoji.last_track, action="reset", row=0
            )
        )
        self.add_item(
            MusicButton(
                player, label=config.emoji.av_emoji.pause_play, action="pause", row=0
            )
        )
        self.add_item(
            MusicButton(
                player,
                label=config.emoji.av_emoji.next_track,
                action="next_track",
                row=0,
            )
        )
        self.add_item(
            MusicButton(
                player, label=config.emoji.av_emoji.repeat_one, action="loop", row=1
            )
        )
        self.add_item(
            MusicButton(
                player, label=config.emoji.av_emoji.shuffle, action="shuffle", row=1
            )
        )
        self.add_item(
            MusicButton(
                player, label=config.emoji.av_emoji.mobile, action="autoplay", row=1
            )
        )

    async def destroy_view(self):
        await self.message.edit(view=None)

    async def disable_all_items(self):
        for item in self.children:
            item.disable = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        try:
            for item in self.children:
                item.disable = True
            await self.destroy_view()
        except Exception:
            pass

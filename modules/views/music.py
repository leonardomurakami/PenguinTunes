import discord
import wavelink

from modules.buttons.music import MusicButton
from modules.globals import config

class PlayerView(discord.ui.View):
    def __init__(self, *, player: wavelink.Player, timeout: float | None = 180):
        super().__init__(timeout=timeout)

        self.player = player
        self.add_item(MusicButton(player, label=config.emoji.av_emoji.repeat_one, action='loop'))
        self.add_item(MusicButton(player, label=config.emoji.av_emoji.last_track, action='reset'))
        self.add_item(MusicButton(player, label=config.emoji.av_emoji.pause_play, action='pause'))
        self.add_item(MusicButton(player, label=config.emoji.av_emoji.next_track, action='next_track'))
        self.add_item(MusicButton(player, label=config.emoji.av_emoji.shuffle, action='shuffle'))

    async def destroy_view(self):
        await self.message.edit(view=None)

    async def disable_all_items(self):
        for item in self.children:
            item.disable = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        try:
            self.destroy_view()
        except Exception as e:
            pass
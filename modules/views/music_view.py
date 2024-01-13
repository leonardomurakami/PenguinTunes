import discord
import wavelink

from modules.globals import AV_EMOJIS
from modules.buttons.music_buttons import LoopButton, ShuffleButton, NextTrackButton, ResetButton, PauseButton

class PlayerView(discord.ui.View):
    def __init__(self, *, player: wavelink.Player, timeout: float | None = 180):
        super().__init__(timeout=timeout)

        self.player = player
        self.add_item(LoopButton(player))
        self.add_item(ResetButton(player))
        self.add_item(PauseButton(player))
        self.add_item(NextTrackButton(player))
        self.add_item(ShuffleButton(player))

    def get_initial_loop_style(self):
        if self.player.queue.mode == wavelink.QueueMode.normal:
            return discord.ButtonStyle.grey
        else:
            return discord.ButtonStyle.blurple

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

import discord
import wavelink

from modules.globals import AV_EMOJIS


class MusicButton(discord.ui.Button):
    def __init__(self, player: wavelink.Player, label: str, style: discord.ButtonStyle | None = discord.ButtonStyle.secondary):
        self.player = player
        super().__init__(style=discord.ButtonStyle.secondary, label=label)

class LoopButton(MusicButton):
    def __init__(self, player):
        loop_style = discord.ButtonStyle.blurple if player.queue.mode != wavelink.QueueMode.normal else discord.ButtonStyle.grey
        super().__init__(player, AV_EMOJIS['repeat_one'], style=loop_style)
        
    async def callback(self, interaction: discord.Interaction):
        if self.player.queue.mode == wavelink.QueueMode.normal:
            self.style = discord.ButtonStyle.blurple
            self.player.queue.mode = wavelink.QueueMode.loop
        else:
            self.player.queue.mode = wavelink.QueueMode.normal
            self.style = discord.ButtonStyle.grey
        await interaction.response.edit_message(view=self.view)
        
class ShuffleButton(MusicButton):
    def __init__(self, player):
        super().__init__(player, AV_EMOJIS['shuffle'])
    
    async def callback(self, interaction: discord.Interaction):
        self.player.queue.shuffle()
        await interaction.response.defer()

class ResetButton(MusicButton):
    def __init__(self, player):
        super().__init__(player, AV_EMOJIS['last_track'])

    async def callback(self, interaction: discord.Interaction):
        await self.player.seek(0)
        await interaction.response.defer()

class PauseButton(MusicButton):
    def __init__(self, player):
        super().__init__(player, AV_EMOJIS['play'])

    async def callback(self, interaction: discord.Interaction):
        if self.player.paused:
            self.style = discord.ButtonStyle.grey
        else:
            self.style = discord.ButtonStyle.red
        await self.player.pause(not self.player.paused)
        await interaction.response.edit_message(view=self.view)

class NextTrackButton(MusicButton):
    def __init__(self, player):
        super().__init__(player, AV_EMOJIS['next_track'])

    async def callback(self, interaction: discord.Interaction):
        await self.player.seek(self.player.current.length)
        await interaction.response.defer()
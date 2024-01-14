import discord
import wavelink

from modules.globals import config


class MusicButton(discord.ui.Button):
    def __init__(self, player: wavelink.Player, label: str, action: str, style: discord.ButtonStyle | None = discord.ButtonStyle.secondary):
        self.player = player
        self.action = action
        super().__init__(style=self.initial_style(player, action), label=label)

    async def callback(self, interaction: discord.Interaction):
        if self.action == "loop":
            await self.toggle_loop(interaction)
        elif self.action == "shuffle":
            await self.shuffle(interaction)
        elif self.action == "reset":
            await self.reset(interaction)
        elif self.action == "pause":
            await self.pause(interaction)
        elif self.action == "next_track":
            await self.next_track(interaction)

    def initial_style(self, player, action):
        if action == "loop":
            return discord.ButtonStyle.blurple if player.queue.mode != wavelink.QueueMode.normal else discord.ButtonStyle.grey
        else:
            return discord.ButtonStyle.grey
        

    async def toggle_loop(self, interaction):
        if self.player.queue.mode == wavelink.QueueMode.normal:
            self.style = discord.ButtonStyle.blurple
            self.player.queue.mode = wavelink.QueueMode.loop
        else:
            self.player.queue.mode = wavelink.QueueMode.normal
            self.style = discord.ButtonStyle.grey
        await interaction.response.edit_message(view=self.view)

    async def shuffle(self, interaction):
        self.player.queue.shuffle()
        await interaction.response.defer()

    async def reset(self, interaction):
        await self.player.seek(0)
        await interaction.response.defer()

    async def pause(self, interaction):
        if self.player.paused:
            self.style = discord.ButtonStyle.grey
        else:
            self.style = discord.ButtonStyle.red
        await self.player.pause(not self.player.paused)
        await interaction.response.edit_message(view=self.view)

    async def next_track(self, interaction):
        await self.player.seek(self.player.current.length)
        await interaction.response.defer()

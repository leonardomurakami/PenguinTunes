import discord
import wavelink

from modules.globals import config


class MusicButton(discord.ui.Button):
    def __init__(self, player: wavelink.Player, label: str, action: str, row: int | None = None, style: discord.ButtonStyle | None = discord.ButtonStyle.secondary):
        self.player = player
        self.action = action
        super().__init__(style=self.initial_style(action), label=self.initial_label(action, label), row=row)

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
        elif self.action == "autoplay":
            await self.autoplay(interaction)

    def initial_label(self, action, label):
        if action == "loop":
            if self.player.queue.mode == wavelink.QueueMode.normal:
                return config.emoji.av_emoji.repeat
            elif self.player.queue.mode == wavelink.QueueMode.loop_all:
                return config.emoji.av_emoji.repeat
            else:
                return config.emoji.av_emoji.repeat_one
        elif action == "autoplay":
            if self.player.autoplay == wavelink.AutoPlayMode.disabled:
                return config.emoji.av_emoji.mobile
            else:
                return config.emoji.av_emoji.wireless
        elif action == "pause":
            if self.player.paused:
                return config.emoji.av_emoji.pause
            else:
                return config.emoji.av_emoji.play
        else:
            return label

    def initial_style(self, action):
        if action == "loop":
            return discord.ButtonStyle.blurple if self.player.queue.mode != wavelink.QueueMode.normal else discord.ButtonStyle.grey
        if action == "autoplay":
            return discord.ButtonStyle.blurple if self.player.autoplay != wavelink.AutoPlayMode.disabled else discord.ButtonStyle.grey
        if action == "pause":
            return discord.ButtonStyle.red if self.player.paused else discord.ButtonStyle.grey
        else:
            return discord.ButtonStyle.grey
        

    async def toggle_loop(self, interaction):
        if self.player.queue.mode == wavelink.QueueMode.normal:
            self.style = discord.ButtonStyle.blurple
            self.label = config.emoji.av_emoji.repeat
            self.player.queue.mode = wavelink.QueueMode.loop_all
        elif self.player.queue.mode == wavelink.QueueMode.loop_all:
            self.style = discord.ButtonStyle.blurple
            self.label = config.emoji.av_emoji.repeat_one
            self.player.queue.mode = wavelink.QueueMode.loop
        else:
            self.style = discord.ButtonStyle.grey
            self.label = config.emoji.av_emoji.repeat
            self.player.queue.mode = wavelink.QueueMode.normal
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
            self.label = config.emoji.av_emoji.play
        else:
            self.style = discord.ButtonStyle.red
            self.label = config.emoji.av_emoji.pause
        await self.player.pause(not self.player.paused)
        await interaction.response.edit_message(view=self.view)

    async def next_track(self, interaction):
        await self.player.seek(self.player.current.length)
        await interaction.response.defer()

    async def autoplay(self, interaction):
        if self.player.autoplay == wavelink.AutoPlayMode.disabled:
            self.style = discord.ButtonStyle.blurple
            self.label = config.emoji.av_emoji.wireless
            self.player.autoplay = wavelink.AutoPlayMode.enabled
            self.player.home.send("Autoplay enabled.")
        else:
            self.style = discord.ButtonStyle.grey
            self.label = config.emoji.av_emoji.mobile
            self.player.autoplay = wavelink.AutoPlayMode.disabled
            self.player.home.send("Autoplay disabled.")
        await interaction.response.edit_message(view=self.view)

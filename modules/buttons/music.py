"""
Class Documentation: MusicButton

The MusicButton class is a subclass of `discord.ui.Button` that provides interactive buttons for music player controls in Discord.

Class Methods:

1. __init__(self, player: wavelink.Player, label: str, action: str, row: int = None, style: discord.ButtonStyle = discord.ButtonStyle.secondary)
   Initializes the MusicButton with specific properties.
   - player: The `wavelink.Player` instance associated with the button.
   - label: The text label displayed on the button.
   - action: The action to be performed when the button is clicked.
   - row: The row where the button should be placed in the Discord UI.
   - style: The style of the button (color/theme).

2. callback(self, interaction: discord.Interaction)
   The asynchronous callback executed when the button is clicked.
   - interaction: The interaction instance associated with the button click.

3. initial_label(self, action, label)
   Determines the initial label for the button based on the action and player state.
   - action: The action associated with the button.
   - label: The default label for the button.

4. initial_style(self, action)
   Determines the initial style (color/theme) of the button based on the action and player state.
   - action: The action associated with the button.

5. toggle_loop(self, interaction)
   Toggles the loop mode of the player.
   - interaction: The interaction instance associated with the button click.

6. shuffle(self, interaction)
   Shuffles the current music queue.
   - interaction: The interaction instance associated with the button click.

7. reset(self, interaction)
   Resets the current track to the beginning.
   - interaction: The interaction instance associated with the button click.

8. pause(self, interaction)
   Toggles the pause state of the player.
   - interaction: The interaction instance associated with the button click.

9. next_track(self, interaction)
   Skips to the next track in the queue.
   - interaction: The interaction instance associated with the button click.

10. autoplay(self, interaction)
    Toggles the autoplay mode of the player.
    - interaction: The interaction instance associated with the button click.

Additional Notes:
- `MusicButton` allows users to interact with the music player directly from a Discord message.
- The buttons dynamically change their appearance and functionality based on the current state of the music player.
- This class enhances the user experience by providing intuitive and responsive controls for music playback.
"""
import discord
import wavelink

from modules.globals import config


class MusicButton(discord.ui.Button):
    def __init__(
        self,
        player: wavelink.Player,
        label: str,
        action: str,
        row: int = None,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
    ):
        """
        Initializes the MusicButton with specific properties.
        - player: The `wavelink.Player` instance associated with the button.
        - label: The text label displayed on the button.
        - action: The action to be performed when the button is clicked.
        - row: The row where the button should be placed in the Discord UI.
        - style: The style of the button (color/theme).
        """
        self.player = player
        self.action = action
        super().__init__(
            style=self.initial_style(action),
            label=self.initial_label(action, label),
            row=row,
        )

    def get_disabled(self):
        return self.disabled

    async def callback(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
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
        """
        Determines the initial label for the button based on the action and player state.
        - action: The action associated with the button.
        - label: The default label for the button.
        """
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
        """
        Determines the initial style (color/theme) of the button based on the action and player state.
        - action: The action associated with the button.
        """
        if action == "loop":
            return (
                discord.ButtonStyle.blurple
                if self.player.queue.mode != wavelink.QueueMode.normal
                else discord.ButtonStyle.grey
            )
        if action == "autoplay":
            return (
                discord.ButtonStyle.blurple
                if self.player.autoplay != wavelink.AutoPlayMode.disabled
                else discord.ButtonStyle.grey
            )
        if action == "pause":
            return (
                discord.ButtonStyle.red
                if self.player.paused
                else discord.ButtonStyle.grey
            )
        else:
            return discord.ButtonStyle.grey

    async def toggle_loop(self, interaction):
        """
         Toggles the loop mode of the player.
        - interaction: The interaction instance associated with the button click.
        """
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
        """
        Shuffles the current queue of the player.
        - interaction: The interaction instance associated with the button click.
        """
        self.player.queue.shuffle()
        await interaction.response.defer()

    async def reset(self, interaction):
        """
        Resets music to the start.
        - interaction: The interaction instance associated with the button click.
        """
        await self.player.seek(0)
        await interaction.response.defer()

    async def pause(self, interaction):
        """
        Pauses the music.
        - interaction: The interaction instance associated with the button click.
        """
        if self.player.paused:
            self.style = discord.ButtonStyle.grey
            self.label = config.emoji.av_emoji.play
        else:
            self.style = discord.ButtonStyle.red
            self.label = config.emoji.av_emoji.pause
        await self.player.pause(not self.player.paused)
        await interaction.response.edit_message(view=self.view)

    async def next_track(self, interaction):
        """
        Skips to the next track.
        - interaction: The interaction instance associated with the button click.
        """
        if self.player.current:
            await self.player.seek(self.player.current.length)
        await interaction.response.defer()

    async def autoplay(self, interaction):
        """
        Toggles autoplay .
        - interaction: The interaction instance associated with the button click.
        """
        if self.player.autoplay == wavelink.AutoPlayMode.disabled:
            self.style = discord.ButtonStyle.blurple
            self.label = config.emoji.av_emoji.wireless
            self.player.autoplay = wavelink.AutoPlayMode.enabled
            await self.player.home.send("Autoplay enabled.")
        else:
            self.style = discord.ButtonStyle.grey
            self.label = config.emoji.av_emoji.mobile
            self.player.autoplay = wavelink.AutoPlayMode.disabled
            await self.player.home.send("Autoplay disabled.")
        await interaction.response.edit_message(view=self.view)

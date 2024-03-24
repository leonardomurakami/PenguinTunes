import discord
import pytest
import wavelink

from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine

# Fixture to mock database engine creation
@pytest.fixture(autouse=True)
def mock_database_engine():
    with patch('modules.utils._database_utils.get_session') as mock_engine:
        yield mock_engine

@pytest.fixture(autouse=True)
def mock_wavelink_player():
    with patch('wavelink.Player') as mock_player:
        yield mock_player

@pytest.fixture(autouse=True)
def mock_member():
    with patch('discord.Member') as mock_member:
        yield mock_member

@pytest.fixture(autouse=True)
def mock_discord_message():
    with patch('discord.Message') as mock_message:
        yield mock_message

class TestFunView:
    # The 'prepare_menu' method should clear all items and add a 'CassinoSelect' button to the view.
    @pytest.mark.asyncio
    async def test_prepare_menu_clear_items_and_add_button(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)
        view.add_item(discord.ui.Button())

        # When
        view.prepare_menu()

        # Then
        assert len(view.children) == 1
        assert isinstance(view.children[0], CassinoSelect)
        assert view.timeout == None

    # The 'set_bet' method should set the bet value.
    @pytest.mark.asyncio
    async def test_set_bet_set_bet_value(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)

        # When
        view.set_bet(100)

        # Then
        assert view.bet == 100

    # The 'get_bet' method should return the bet value.
    @pytest.mark.asyncio
    async def test_get_bet_return_bet_value(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)
        view.bet = 200

        # When
        bet = view.get_bet()

        # Then
        assert bet == 200

    # The 'prepare_dig_trash' method should create a new 'CassinoPlayer' and add 'DigTrashButton' items to the view.
    @pytest.mark.asyncio
    async def test_prepare_dig_trash_create_new_cassino_player_and_add_buttons(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect
        from modules.player.player import CassinoPlayer
        from modules.buttons.dig_trash.buttons import DigTrashButton

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)

        # When
        await view.prepare_dig_trash()

        # Then
        assert isinstance(view.cassino_player, CassinoPlayer)
        assert len(view.children) == 2
        assert isinstance(view.children[0], DigTrashButton)
        assert isinstance(view.children[1], DigTrashButton)

    # The 'prepare_menu' method should handle a timeout value of None.
    @pytest.mark.asyncio
    async def test_prepare_menu_handle_timeout_none(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)

        # When
        view.prepare_menu()

        # Then
        assert view.timeout == None

    # The 'set_bet' method should handle a bet value of 0.
    @pytest.mark.asyncio
    async def test_set_bet_handle_bet_value_zero(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)

        # When
        view.set_bet(0)

        # Then
        assert view.bet == 0

    # The 'get_bet' method should handle a null cassino player.
    @pytest.mark.asyncio
    async def test_get_bet_handle_null_cassino_player(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)
        view.cassino_player = None

        # When
        bet = view.get_bet()

        # Then
        assert bet == None

    # The 'prepare_dig_trash' method should handle a null cassino player.
    @pytest.mark.asyncio
    async def test_prepare_dig_trash_handle_null_cassino_player(mock_database_engine, mock_member):
        from modules.views.fun import CassinoView
        from modules.buttons.cassino import CassinoSelect
        from modules.player.player import CassinoPlayer
        from modules.buttons.dig_trash.buttons import DigTrashButton

        # Given
        view = CassinoView(member=discord.Member(), timeout=None)
        view.cassino_player = None

        # When
        await view.prepare_dig_trash()

        # Then
        assert isinstance(view.cassino_player, CassinoPlayer)
        assert len(view.children) == 2
        assert isinstance(view.children[0], DigTrashButton)
        assert isinstance(view.children[1], DigTrashButton)

class TestMusicView:
    # Initializes PlayerView with a wavelink.Player instance and optional timeout
    @pytest.mark.asyncio
    async def test_initializes_playerview_with_player_and_timeout(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = wavelink.Player()
        timeout = 180

        # When
        view = PlayerView(player=player, timeout=timeout)

        # Then
        assert view.player == player
        assert view.timeout == timeout

    # Adds interactive items (buttons) to the view
    @pytest.mark.asyncio
    async def test_adds_interactive_items_to_view(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = wavelink.Player()
        timeout = 180
        view = PlayerView(player=player, timeout=timeout)

        # When
        items = view.children

        # Then
        assert len(items) == 6

    # Disables all interactive items (buttons) in the view
    @pytest.mark.asyncio
    async def test_disables_all_items_in_view(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = wavelink.Player()
        timeout = 180
        view = PlayerView(player=player, timeout=timeout)
        view.message = MagicMock()
        view.message.edit = AsyncMock()

        # When
        await view.disable_all_items()

        # Then
        view.message.edit.assert_called_once()

    # Defines behavior when the view times out
    @pytest.mark.asyncio
    async def test_defines_behavior_on_timeout(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = wavelink.Player()
        timeout = 180
        view = PlayerView(player=player, timeout=timeout)
        view.message = MagicMock()
        view.message.edit = AsyncMock()

        # When
        await view.on_timeout()

        # Then
        view.message.edit.assert_called_once()

    # All of the interactive items (buttons) are added to the view
    @pytest.mark.asyncio
    async def test_no_items_added_to_view(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = wavelink.Player()
        timeout = 180

        # When
        view = PlayerView(player=player, timeout=timeout)
        items = view.children

        # Then
        assert len(items) == 6

    # The wavelink.Player instance is None
    @pytest.mark.asyncio
    async def test_player_instance_is_none(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = None
        timeout = 180

        # When, Then
        try:
            PlayerView(player=player, timeout=timeout)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == "Player cannot be None"

    # Timeout is set to a negative value
    @pytest.mark.asyncio
    async def test_timeout_is_negative(self, mock_wavelink_player):
        from modules.views.music import PlayerView
        # Given
        player = wavelink.Player()
        timeout = -180

        # When, Then
        try:
            PlayerView(player=player, timeout=timeout)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == "Timeout cannot be negative"


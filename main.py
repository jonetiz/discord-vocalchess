from client import *
import os
from dotenv import load_dotenv
from chess_functions import DiscordChessGame, ChessPlayer
import typing

def main():
    # load environment variables from .env
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True

    client = VocalChessClient(intents=intents)

    @client.tree.command()
    async def challenge_cpu(interaction: discord.Interaction, color: typing.Optional[typing.Literal['white', 'black']] = 'white', elo: typing.Optional[int] = 1500):
        """Challenge the CPU to a chess game."""

        # create appropriate ChessPlayer objects
        if color == 'white':
            white_player = ChessPlayer(interaction.user, 1500)
            black_player = ChessPlayer(client.user, elo)
        else:
            white_player = ChessPlayer(client.user, elo)
            black_player = ChessPlayer(interaction.user, 1500)

        # create chess game instance
        game = DiscordChessGame(channel = interaction.channel_id, white = white_player, black = black_player)

        # CPU makes first move if player is black
        if color == 'black':
            client.engine.set_elo_rating(elo)
            # reset board
            client.engine.set_position(None)
            move = client.engine.get_best_move()
            game.game.push_uci(move)

        e = game.get_embed()

        # add this game to the games so it can be tracked by the discord bot
        client.games.append(game)

        await interaction.response.send_message(file = e['file'], embed = e['embed'])

        game.message = interaction

    async def challenge(interaction: discord.Integration, opponent: discord.User, color: typing.Optional[typing.Literal['white', 'black']] = 'white'):
        """Challenge another user to a chess game."""
        if color == 'white':
            white_player = ChessPlayer(interaction.user, 1500)
            black_player = ChessPlayer(opponent, 1500)
        else:
            white_player = ChessPlayer(opponent, 1500)
            black_player = ChessPlayer(interaction.user, 1500)

        game = DiscordChessGame(channel = interaction.channel_id, white = white_player, black = black_player)

        e = game.get_embed()

        client.games.append(game)

        await interaction.response.send_message(file = e['file'], embed = e['embed'])

        game.message = interaction

    @client.event
    async def on_message_delete(message: discord.Message):
        # if it's an interaction
        if message.interaction:
            message_id = message.interaction.id
            for game in client.games:
                # if it's one of our games, remove it from the tracker
                if message_id == game.message.id:
                    print(f"Deleted {game}")
                    client.games.remove(game)

    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()
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
    async def player_stats(interaction: discord.Interaction, user: typing.Optional[discord.User]):
        """Give player statistics"""
        if not user:
            user = interaction.user

        player = ChessPlayer(user)

        embed = discord.Embed()
        embed.set_author(name=f"VocalChess Statistics - {user.display_name}")
        embed.add_field(name="Elo Rating", value=f"{player.elo}", inline=True)
        embed.add_field(name="Wins / Losses / Draws", value=f"{player.wins} / {player.loss} / {player.draw}", inline=True)

        await interaction.response.send_message(embed = embed)

    @client.tree.command()
    async def challenge_cpu(interaction: discord.Interaction, color: typing.Optional[typing.Literal['white', 'black']] = 'white', elo: typing.Optional[int] = 1500):
        """Challenge the CPU to a chess game."""

        # create appropriate ChessPlayer objects
        if color == 'white':
            white_player = ChessPlayer(interaction.user)
            black_player = ChessPlayer(client.user, elo, bot=True)
        else:
            white_player = ChessPlayer(client.user, elo, bot=True)
            black_player = ChessPlayer(interaction.user)

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

    @client.tree.command()
    async def challenge(interaction: discord.Integration, opponent: discord.User, color: typing.Optional[typing.Literal['white', 'black']] = 'white'):
        """Challenge another user to a chess game."""
        if color == 'white':
            white_player = ChessPlayer(interaction.user)
            black_player = ChessPlayer(opponent)
        else:
            white_player = ChessPlayer(opponent)
            black_player = ChessPlayer(interaction.user)

        game = DiscordChessGame(channel = interaction.channel_id, white = white_player, black = black_player)

        e = game.get_embed()

        client.games.append(game)

        await interaction.response.send_message(file = e['file'], embed = e['embed'])

        game.message = interaction

    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()
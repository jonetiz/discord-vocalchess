from client import *
import os
from dotenv import load_dotenv
from chess_functions import DiscordChessGame

def main():
    # load environment variables from .env
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True

    client = VocalChessClient(intents=intents)

    @client.tree.command()
    async def challenge_cpu(interaction: discord.Interaction):
        """Challenge the CPU to a chess game."""

        game = DiscordChessGame(channel = interaction.channel_id, challenger = interaction.user, other_player = client.user)
        e = game.get_embed()

        client.games.append(game)

        await interaction.response.send_message(file = e['file'], embed = e['embed'])
        game.message = interaction

    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()
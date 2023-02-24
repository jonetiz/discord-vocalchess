import discord
from discord import app_commands
from chess_functions import DiscordChessGame
from typing import List

MY_GUILD = discord.Object(id=1078456129580957779)

class VocalChessClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.games: List[DiscordChessGame] = []

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        for game in self.games:
            if message.channel.id == game.channel and (message.author.id == game.challenger.id or message.author.id == game.other_player.id):
                # If the message is in the same channel as the game as the author is the challenger or player, attempt to make a move (if it's a valid move)
                try:
                    game.game.push_san(message.content)
                except:
                    pass
                else:
                    game.moves.append(message.content)
                    await message.delete()
                    await game.update_message()



    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello, {interaction.user.mention}!')
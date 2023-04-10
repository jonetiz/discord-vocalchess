import discord
from chess_functions import DiscordChessGame
from typing import List
import stockfish
import asyncio

MY_GUILD = discord.Object(id=1078456129580957779)

class VocalChessClient(discord.Bot):
    # initialize stockfish with depth of 18; only one instance for the whole bot
    engine = stockfish.Stockfish(path="stockfish-windows-2022-x86-64-avx2.exe", depth=18)
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True # required to use message.content in on_message
        super().__init__(intents=intents)
        self.games: List[DiscordChessGame] = []

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        await self.change_presence(activity=discord.Game("Chess"))

    async def on_message(self, message: discord.Message):
        for game in self.games:
            if message.channel.id == game.channel and ((message.author.id == game.white.user.id and game.game.turn) or (message.author.id == game.black.user.id and not game.game.turn)):
                # If the message is in the same channel as the game as the author is the challenger or player, attempt to make a move (if it's a valid move)
                try:
                    game.try_move(message.content)
                except Exception as e:
                    msg: discord.Message = await message.reply(f"{e}\nThe /move_help command may help if you are confused.")
                    await asyncio.sleep(5)
                    await msg.delete()
                    await message.delete() 
                else:
                    # if it's a cpu game, make cpu move
                    if game.black.user is self.user or game.white.user is self.user:
                        #start = time.time()

                        # set engine elo rating
                        if game.black.user is self.user:
                            self.engine.set_elo_rating(game.black.elo)
                        else:
                            self.engine.set_elo_rating(game.white.elo)

                        # feed engine the board position
                        self.engine.set_fen_position(game.game.fen())

                        # get best move from engine
                        move = self.engine.get_best_move()
                        #end = time.time()
                        #print(end - start)

                        # push uci to the game
                        game.game.push_uci(move)

                    # try to end game if it's over
                    game.end_game()

                    await message.delete()
                    await game.update_message()

    async def on_message_delete(self, message: discord.Message):
        # if it's an interaction
        if message.interaction:
            message_id = message.interaction.id
            for game in self.games:
                # if it's one of our games, remove it from the tracker
                if message_id == game.ctx.interaction.id:
                    print(f"Deleted {game}")
                    self.games.remove(game)
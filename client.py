import discord
from discord.ext import tasks
from discord.utils import get
from chess_functions import DiscordChessGame, ChessPlayer
from typing import List
import stockfish
import sqlite3

class VocalChessView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        

class CPUGameView(VocalChessView):
    @discord.ui.button(label="Offer Draw", custom_id="drawoffer_cpu", style=discord.ButtonStyle.primary, emoji="🤝")
    async def draw_callback(self, button, interaction: discord.Interaction):
        game: DiscordChessGame = self.game
        engine: stockfish.Stockfish = self.engine
        if game.black.bot:
            # if the evaluation is greater than 500 centipawns (white favor), accept draw
            if engine.get_evaluation()['value'] > 500:
                game.end_game(force_draw=True)
                await interaction.response.send_message("Your draw offer was accepted.", ephemeral=True, delete_after=5)
                await game.update_message()
            else:
                await interaction.response.send_message("Your draw offer was rejected.", ephemeral=True, delete_after=5)
        else:
            if engine.get_evaluation()['value'] < -500:
                game.end_game(force_draw=True)
                await interaction.response.send_message("Your draw offer was accepted.", ephemeral=True, delete_after=5)
                await game.update_message()
            else:
                await interaction.response.send_message("Your draw offer was rejected.", ephemeral=True, delete_after=5)

    @discord.ui.button(label="Forfeit", custom_id="forfeit_cpu", style=discord.ButtonStyle.secondary, emoji="🇫🇷")
    async def forfeit_callback(self, button, interaction: discord.Interaction):
        game: DiscordChessGame = self.game
        game.end_game(forfeit=game.game.turn)
        await interaction.response.send_message("You have forfeitted.", ephemeral=True, delete_after=5)
        await game.update_message()

    @discord.ui.button(label="Delete", custom_id="delete_cpu", style=discord.ButtonStyle.danger)
    async def delete_callback(self, button, interaction: discord.Interaction):
        try:
            game: DiscordChessGame = self.game
            game.end_game(forfeit=game.game.turn)
        except:
            pass
        await interaction.message.delete()

class GameView(VocalChessView):
    @discord.ui.button(label="Offer Draw", custom_id="drawoffer", style=discord.ButtonStyle.success, emoji="🤝")
    async def draw_callback(self, button, interaction: discord.Interaction):
        game: DiscordChessGame = self.game
        other_user = game.white.user if interaction.user is game.black.user else game.black.user
        await interaction.channel.send(f"{interaction.user.display_name} has offered a draw.")
        await game.update_message()
    @discord.ui.button(label="Forfeit", custom_id="forfeit", style=discord.ButtonStyle.secondary, emoji="🇫🇷")
    async def forfeit_callback(self, button, interaction: discord.Interaction):
        game: DiscordChessGame = self.game
        game.end_game(forfeit=game.game.turn)
        await interaction.response.send_message("You have forfeitted.", ephemeral=True, delete_after=5)
        await game.update_message()

class GameOfferView(VocalChessView):
    @discord.ui.button(label="Accept Game", custom_id="accept_game", style=discord.ButtonStyle.success)
    async def accept_callback(self, button, interaction: discord.Interaction):
        if self.color == 'white':
            white_player = ChessPlayer(self.interaction.user)
            black_player = ChessPlayer(self.opponent)
        else:
            white_player = ChessPlayer(self.opponent)
            black_player = ChessPlayer(self.interaction.user)

        channel = await self.interaction.guild.create_text_channel(name=f"{white_player.user.display_name} vs {black_player.user.display_name}", category=self.client.get_channel(self.client.guild_data[self.interaction.guild.id].category_id))
        game = DiscordChessGame(channel = channel.id, white = white_player, black = black_player)

        e = game.get_embed()

        self.client.games.append(game)

        view = GameView()
        view.game = game
        ctx = await channel.send(file = e['file'], embed = e['embed'], view = view)
        game.ctx = ctx

        await interaction.response.send_message(content = f"A chess game has started in {channel.mention}!", delete_after = 30, ephemeral = True)
        await self.message.delete()

    @discord.ui.button(label="Decline Game", custom_id="decline_game", style=discord.ButtonStyle.danger)
    async def decline_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_message("You have declined the game offer.", ephemeral=True, delete_after=5)
        await self.message.delete()

class GuildInfo:
    """Data structure for holding guild information."""
    def __init__(self, archive: bool = False, archive_channel: int = 0, category_id: int = 0):
        self.archive = archive
        self.archive_channel = archive_channel
        self.category_id = category_id
        
    def update(self, guild_id: int):
        """Upsert this GuildInfo object into the database"""
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO guilds (id, archive, archive_channel, category_id) VALUES ({guild_id}, {self.archive}, {self.archive_channel}, {self.category_id})
            ON CONFLICT(id) DO UPDATE SET archive = {self.archive}, archive_channel = {self.archive_channel}, category_id = {self.category_id}
        """)
        conn.commit()
        cur.close()
        conn.close()

class VocalChessClient(discord.Bot):
    # initialize stockfish with depth of 18; only one instance for the whole bot
    engine = stockfish.Stockfish(path="stockfish-windows-2022-x86-64-avx2.exe", depth=18)

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True # required to use message.content in on_message
        super().__init__(intents=intents)
        self.games: List[DiscordChessGame] = []
        self.guild_data: dict[GuildInfo] = {}

        self.timer = 0
        self.sink: discord.sinks.MP3Sink

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS guilds (id INT PRIMARY KEY, archive INT, archive_channel INT, category_id INT)
        """)
        cur.execute(f"""
            SELECT * FROM guilds
        """)
        results = cur.fetchall()
        cur.close()
        conn.close()

        for result in results:
            self.guild_data[result[0]] = GuildInfo(result[1], result[2], result[3])

    def set_guild_setting(self, guild_id: int, setting: str, value):
        guild_data: GuildInfo = self.guild_data[guild_id] if self.guild_data.get(guild_id) else GuildInfo()
        guild_data.__setattr__(setting, value)
        guild_data.update(guild_id)
        self.guild_data[guild_id] = guild_data

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.add_view(CPUGameView())
        self.add_view(GameView())
        self.add_view(GameOfferView())
        await self.change_presence(activity=discord.Game("Chess"))

    async def on_message(self, message: discord.Message):
        for game in self.games:
            if message.channel.id == game.channel and ((message.author.id == game.white.user.id and game.game.turn) or (message.author.id == game.black.user.id and not game.game.turn)):
                # If the message is in the same channel as the game as the author is the challenger or player, attempt to make a move (if it's a valid move)
                try:
                    game.try_move(message.content)
                except Exception as e:
                    await message.reply(f"{e}\nThe /move_help command may help if you are confused.", delete_after=5) 
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
                    if not game.black.bot and not game.white.bot:
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
    
    @tasks.loop(seconds=1)
    async def check_voice(self):
        pass
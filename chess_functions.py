import discord
from datetime import datetime
import chess
import chess.pgn
import io
from board_image import *
import sqlite3

class ChessPlayer:
    def __init__(self, user: discord.User, elo: int = 1500, bot: bool = False):
        self.user = user
        self.bot = bot
        if not self.load() or self.bot:
            self.elo = elo
            self.wins = 0
            self.loss = 0
            self.draw = 0

    def load(self):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY, elo INT, wins INT, loss INT, draw INT)
        """)
        cur.execute(f"""
            SELECT * FROM users WHERE id = {self.user.id}
        """)
        results = cur.fetchone()
        if results:
            self.elo = results[1]
            self.wins = results[2]
            self.loss = results[3]
            self.draw = results[4]
            return True
        else:
            return False

    def save(self):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY, elo INT, wins INT, loss INT, draw INT)
        """)
        cur.execute(f"""
            INSERT INTO users (id, elo, wins, loss, draw) VALUES ({self.user.id}, {self.elo}, {self.wins}, {self.loss}, {self.draw})
            ON CONFLICT(id) DO UPDATE SET elo = {self.elo}, wins = {self.wins}, loss = {self.loss}, draw = {self.draw} WHERE id = {self.user.id}
        """)
        conn.commit()

class DiscordChessGame:
    def __init__(self, channel, white: ChessPlayer, black: ChessPlayer):
        self.game = chess.Board()
        self.channel = channel
        self.white = white
        self.black = black
        self.message: discord.Interaction

    def get_board_image(self, size=1800):
        lastmove = ()

        if self.game.move_stack:
            last_move = self.game.move_stack[-1]
            lastmove = (last_move.from_square, last_move.to_square)

        board_img = ChessBoardImage(pieces, self.game.piece_map(), lastmove)
        img_io = io.BytesIO()
        board_img.img.save(img_io, "jpeg")
        img_io.seek(0)

        return img_io

    def get_moves(self, nl = True):
        """Returns a string of moves in standard algebraic notation"""
        string_to_return = "1. _"
        line_ctr = 1
        moves = []
        tempgame = chess.Board()
        for move in self.game.move_stack:
            # san = ""
            # if move.drop:
            #     if move.drop != chess.PAWN:
            #         san += chess.piece_symbol(move.drop).upper()
            #     san += move.to_square
            
            # if move.promotion:
            #     san += "=" + move.promotion
            
            # if self.game.is_kingside_castling(move):
            #     san = "O-O"
            # elif self.game.is_queenside_castling(move):
            #     san = "O-O-O"

            # capture = self.game.is_capture(move)
            san = tempgame.san_and_push(move)
            moves.append(san)

        if moves:
            string_to_return = ""
            for i,j in zip(moves[0::2], moves[1::2]):
                str = f"{line_ctr}. {i} {j} "
                str += "\n" if nl else ""
                string_to_return += str
                line_ctr += 1
            if len(moves) % 2 != 0:
                string_to_return += f"{line_ctr}. {moves[-1]}"

        return string_to_return
    
    def get_embed(self):
        players = f"{self.white.user} ({self.white.elo}) vs. {self.black.user} ({self.black.elo})"

        moves = self.get_moves()

        embed = discord.Embed()
        embed.set_author(name=f"Chess Game - {players}")
        outcome = self.game.outcome()
        if outcome:
            if outcome.result() == '1/2-1/2':
                embed.set_author(name=f"Chess Game - {players} - DRAW")
            else:
                embed.set_author(name=f"Chess Game - {players} - {self.get_winner().user.display_name} WINS!")
        embed.set_image(url="attachment://board.png")
        embed.add_field(name="Moves", value=f"```{moves}```", inline=True)
        embed.set_footer(text=f"Game started \non {datetime.now().strftime('%B %d, %Y')}")

        dict = {
            "embed": embed,
            "file": discord.File(self.get_board_image(), "board.png")
        }

        return dict
    
    def get_winner(self) -> bool | ChessPlayer:
        """Return the winning ChessPlayer"""
        if self.game.is_checkmate():
            if self.game.turn:
                return self.black
            else:
                return self.white
        else:
            return False
        
    def end_game(self) -> bool:
        """Check if game is over, then recalculate elo of players, update W/L, and save ChessPlayer objects."""
        # only end game if it has actually ended
        outcome = self.game.outcome()
        if outcome:
            # bot games do not affect elo or W/L/D statistics
            if not self.white.bot and not self.black.bot:
                for player in (self.black, self.white):
                    other_player: ChessPlayer
                    if player is self.black:
                        other_player = self.white
                    else:
                        other_player = self.black
                    
                    # k-factor is a variable that plays into the Elo rating system;
                    # this calculation follows FIDE regulations.

                    # k-factor is 40 for all players under 2300 with less than 30 games
                    k = 40
                    # if player has at least 30 games and less than 2400 elo, their k-factor is 20
                    if (player.wins + player.loss + player.draw) >= 30 and player.elo < 2400:
                        k = 20
                    # if player's elo is at least 2400, their k-factor is 10
                    if player.elo >= 2400:
                        k = 10

                    # expected_score is 1 / (1+10 * (Rat_B - Rat_A)/400)
                    expected_score = 1 / (1+10*((other_player.elo - player.elo)/400))

                    # elo is calculated from current_elo + k(score - expected score)
                    # where score = 1 for win, 0 for loss, and 0.5 for draw

                    if outcome.result == '1/2-1/2':
                        player.elo = round(player.elo + k*(0.5 - expected_score))
                        player.draw += 1
                    else:
                        if self.get_winner() is player:
                            player.elo = round(player.elo + k*(1 - expected_score))
                            player.wins += 1
                        else:
                            player.elo = round(player.elo + k*(0 - expected_score))
                            player.loss += 1

                    # save player to database
                    player.save()

            # game is over
            return True
        else:
            # game is not ready to end yet
            return False

    async def update_message(self):
        e = self.get_embed()
        await self.message.edit_original_response(attachments = [e['file']], embed = e['embed'])
    
    def try_move(self, move: str):
        """Try resolving a move from a string (likely discord message content). Returns True if successful, False if not."""
        # First try algebraic notation
        try:
            self.game.push_san(move)
        except:
            # Try UCI notation
            try:
                self.game.push_uci(move)
            except:
                # if algebraic and universal chess notation both failed, try resolving using our own methods

                # make move string all lower-case
                move_arr = move.lower().split(" ")

                piece_aliases = {
                    "K": ["king"],
                    "Q": ["queen"],
                    "B": ["bishop"],
                    "N": ["knight", "nite", "night", "horse"],
                    "R": ["rook"],
                    "P": ["pawn", "a", "b", "c", "d", "e", "f", "g", "h"]
                }

                operations = ["x", "to", "takes", "take", "capture", "captures"]

                # resolve the operation
                known_operation = ""
                for word in move_arr:
                    if word in operations:
                        known_operation = word
                        break
                
                # TODO: want functionality including but not limited to:
                # "Knight takes f6", "Knight takes on f6", "Knight f6"
                # "Queen takes Queen", "Knight takes Queen"
                move_made = False
                
                return move_made
            else:
                # if UCI worked, return True
                return True
        else:
            # if it worked, return True
            return True

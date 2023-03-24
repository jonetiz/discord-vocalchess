import discord
from datetime import datetime
import chess
import chess.svg
import io
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

class ChessPlayer:
    def __init__(self, user: discord.User, elo: int):
        self.user = user
        self.elo = elo

class DiscordChessGame:
    def __init__(self, channel, white: ChessPlayer, black: ChessPlayer):
        self.game = chess.Board()
        self.channel = channel
        self.white = white
        self.black = black
        self.moves = []
        self.message: discord.Interaction

    def get_board_image(self, size=1800):
        lastmove=None
        check=None
        if self.game.move_stack:
            lastmove=self.game.move_stack[-1]
            if self.game.is_check():
                print("CHECK!")
                check = self.game.king(self.game.turn)

        img = chess.svg.board(
            self.game, size=size, lastmove=lastmove, check=check
        )
        drawing = svg2rlg(io.StringIO(img))

        try:
            png_bytes = renderPM.drawToString(drawing, fmt='PNG')
        except:
            pass
        png_io = io.BytesIO(png_bytes)
        return png_io
    
    def get_moves(self, nl = True):
        """Returns a string of moves in standard algebraic notation"""
        string_to_return = "1. _"
        line_ctr = 1
        if self.moves:
            string_to_return = ""
            for i,j in zip(self.moves[0::2], self.moves[1::2]):
                str = f"{line_ctr}. {i} {j} "
                str += "\n" if nl else ""
                string_to_return += str
                line_ctr += 1
            if len(self.moves) % 2 != 0:
                string_to_return += f"{line_ctr}. {self.moves[-1]}"

        return string_to_return
    
    def get_embed(self):
        players = f"{self.white.user} ({self.white.elo}) vs. {self.black.user} ({self.black.elo})"

        moves = self.get_moves()

        embed = discord.Embed()
        embed.set_author(name=f"Chess Game - {players}")
        if self.game.is_checkmate():
            embed.set_author(name=f"Chess Game - {players} - <WINNER> WINS!")
        embed.set_image(url="attachment://board.png")
        embed.add_field(name="Moves", value=f"```{moves}```", inline=True)
        embed.set_footer(text=f"Game started \non {datetime.now().strftime('%B %d, %Y')}")

        dict = {
            "embed": embed,
            "file": discord.File(self.get_board_image(), "board.png")
        }

        return dict
    
    async def update_message(self):
        e = self.get_embed()
        await self.message.edit_original_response(attachments = [e['file']], embed = e['embed'])
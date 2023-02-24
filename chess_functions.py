import discord
from datetime import datetime
import chess
import chess.svg
import io
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

class DiscordChessGame:
    moves = []
    message: discord.Interaction
    def __init__(self, channel, challenger: discord.User, other_player: discord.User):
        self.game = chess.Board()
        self.channel = channel
        self.challenger = challenger
        self.other_player = other_player


    def get_board_image(self, size=1800):
        lastmove=None
        check=None
        if self.game.move_stack:
            lastmove=self.game.move_stack[-1]
            if self.game.is_check():
                check = self.game.king(self.game.turn)

        img = chess.svg.board(
            self.game, size=size, lastmove=lastmove, check=check
        )
        drawing = svg2rlg(io.StringIO(img))

        try:
            png_bytes = renderPM.drawToString(drawing, fmt='PNG')
        except:
            pass
        png_io = io.BytesIO()
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
        players = f"{self.challenger} vs. {self.other_player}"

        moves = self.get_moves()

        embed = discord.Embed()
        embed.set_author(name=f"Chess Game - {players}")
        embed.set_image(url="attachment://board.png")
        embed.add_field(name="Moves", value=f"```{moves}```", inline=True)
        embed.set_footer(text=f"Game Started by {self.challenger}\non {datetime.now().strftime('%B %d, %Y')}")

        dict = {
            "embed": embed,
            "file": discord.File(self.get_board_image(), "board.png")
        }

        return dict
    
    async def update_message(self):
        e = self.get_embed()
        await self.message.edit_original_response(attachments = [e['file']], embed = e['embed'])
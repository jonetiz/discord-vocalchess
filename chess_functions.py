import discord
from datetime import datetime
import chess
import chess.pgn
import io
from board_image import *

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
        if self.game.is_checkmate():
            if self.game.turn:
                winner = self.black.user.display_name.upper()
            else:
                winner = self.white.user.display_name.upper()
            embed.set_author(name=f"Chess Game - {players} - {winner} WINS!")
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
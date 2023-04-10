import discord
from datetime import datetime
import chess
import chess.pgn
import io
from board_image import *
import sqlite3
import re

class ChessPlayer:
    def __init__(self, user: discord.User, elo: int = 1500, wins: int = 0, loss: int = 0, draw: int = 0, bot: bool = False):
        self.user = user
        self.bot = bot
        self.elo = elo
        self.wins = wins
        self.loss = loss
        self.draw = draw

    def load(self):
        with sqlite3.connect("database.db") as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY, elo INT, wins INT, loss INT, draw INT)
            """)
            conn.commit()

            with conn.execute(f"""
                    SELECT * FROM users WHERE id = {self.user.id}
                """) as cursor:
                results = cursor.fetchone()
                if results:
                    self.elo = results[1]
                    self.wins = results[2]
                    self.loss = results[3]
                    self.draw = results[4]
                    return True
                else:
                    return False

    def save(self):
        with sqlite3.connect("database.db") as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY, elo INT, wins INT, loss INT, draw INT)
            """)
            conn.execute(f"""
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
        self.ctx: discord.ApplicationContext

    def __repr__(self):
        return f"< Chess Game between {self.white.user.name} and {self.black.user.name} >"

    def get_board_image(self, size=1800):
        lastmove = ()

        if self.game.move_stack:
            last_move = self.game.move_stack[-1]
            lastmove = (last_move.from_square, last_move.to_square)

        mirror = not self.game.turn

        board_img = ChessBoardImage(pieces, self.game.piece_map(), lastmove, mirror)
        img_io = io.BytesIO()
        board_img.img.save(img_io, "jpeg")
        img_io.seek(0)

        return img_io

    def get_moves(self, nl = True):
        """Returns a string of moves in standard algebraic notation"""
        string_to_return = "1. _"
        line_ctr = 1
        moves = []
        # create a temporary game
        tempgame = chess.Board()
        # push each move to the temp game, getting the san of each move
        for move in self.game.move_stack:
            san = tempgame.san_and_push(move)
            moves.append(san)

        # format moves into lines for the embed
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
        """Return a discord embed object representing the chess game"""
        players = f"{self.white.user} ({self.white.elo}) vs. {self.black.user} ({self.black.elo})"

        # formatted move list in san
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
        await self.ctx.edit(file = e['file'], embed = e['embed'])
    
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

                # split input string by spaces, hyphens, and underscores
                move_arr = re.split(' |-|_', move.lower())

                # check castling and en-passant
                for word in move_arr:
                    if word in ("castle", "castles", "longcastle", "longcastles", "shortcastle", "shortcastles"):
                        # if we are trying to castle

                        if not self.game.has_castling_rights(self.game.turn):
                            # make no move if player doesn't have castling rights
                            raise chess.IllegalMoveError(f'{"White" if self.game.turn else "Black"} does not have castling rights.')
                        
                        try:
                            # if there are no castling moves, raise IllegalMoveError
                            self.game.generate_castling_moves().__next__()
                        except:
                            raise chess.IllegalMoveError('There are no legal castling moves in the current position.')
                        
                        if "longcastle" in move_arr or "longcastles" in move_arr or "long" in move_arr or "queen" in move_arr or "queenside" in move_arr:
                            # if "long", "queen", or "queenside" is designated in the move_arr, do a long castle
                            #print("long castle")
                            try:
                                self.game.push_san("O-O-O")
                            except:
                                raise chess.IllegalMoveError('Queen-side castling is not legal in the current position.')
                            else:
                                return "O-O-O"
                        else:
                            #print("short castle")
                            try:
                                self.game.push_san("O-O")
                            except:
                                raise chess.IllegalMoveError('King-side castling is not legal in the current position.')
                            else:
                                return "O-O"
                    elif word in ("en-passant", "ep", "e.p.", "passant", "pasant"):
                        # if we're trying en passant
                        if not self.game.has_legal_en_passant():
                            raise chess.IllegalMoveError(f'There is no legal en-passant in the current position.')
                        
                        legal_moves: list[chess.Move] = []
                        for move in self.game.generate_legal_ep():
                            legal_moves.append(move)

                        move_to_play: chess.Move = None
                        for move in legal_moves:
                            if not move_to_play:
                                move_to_play = move
                            else:
                                # if there are multiple legal en-passants
                                move_to_play = None
                                for word in move_arr:
                                    # go through each word in the message
                                    if word in chess.FILE_NAMES:
                                        # if the word is a file, determine which file it is
                                        for i, file in enumerate(chess.FILE_NAMES):
                                            # track down the file the user said
                                            if file == word:
                                                for m in legal_moves:
                                                    # if this move's piece file is i, just do the thingy
                                                    if chess.square_file(m.from_square) == i:
                                                        move_to_play = m
                                                        break
                            
                        # if there is no en-passant move defined
                        if not move_to_play:
                            raise chess.AmbiguousMoveError(f'There are multiple or no legal en-passants in the current position. Clarify by typing which piece is to play en-passant.')

                        return self.game.san_and_push(move_to_play)

                # move_to = square id of last "word" in move_arr, must be a square name
                move_to = None
                if move_arr[-1] not in chess.SQUARE_NAMES:
                    raise chess.IllegalMoveError(f'{move_arr[-1]} is not a valid square.')
                else:
                    # get the square index from the square name
                    for i, name in enumerate(chess.SQUARE_NAMES):
                        if move_arr[-1] == name:
                            move_to = i


                # map chess pieces to their aliases
                piece_aliases = {
                    chess.KING: ["king"],
                    chess.QUEEN: ["queen"],
                    chess.BISHOP: ["bishop"],
                    chess.KNIGHT: ["knight", "nite", "night", "horse"],
                    chess.ROOK: ["rook"],
                    chess.PAWN: ["pawn", "a", "b", "c", "d", "e", "f", "g", "h"]
                }
                
                # a set of squares on which pieces may be moved, populated by piece resolution below
                candidates_to_move: chess.SquareSet = None

                # resolve the piece
                for piece in piece_aliases:
                    # for each piece_alias
                    for alias in piece_aliases[piece]:
                        if move_arr[0] == alias:
                            #  print(piece)
                            # find all of the pieces that match the given piece on the given side
                            candidates_to_move = self.game.pieces(piece, self.game.turn)

                            # handle promotion case
                            if "promote" in move_arr or "promotes" in move_arr:
                                if piece == chess.PAWN:
                                    # only pawns can promote
                                    for square in candidates_to_move:
                                        if chess.square_rank(square) == 6:
                                            # if it's on the 7th rank, it may be able to promote
                                            for move in self.game.generate_legal_moves():
                                                if move.to_square == move_to:
                                                    # if this is the correct move based on the move_to variable, determine what we're promoting to
                                                    promotion = chess.QUEEN # default to queen if otherwise undefined 
                                                    for piece in range(2, 6):
                                                        for alias in piece_aliases[piece]:
                                                            if alias in move_arr[1:]:
                                                                # we don't need the first piece of move_arr since that's the piece we want to move, find the other one
                                                                promotion = piece
                                                    move_to_play = chess.Move(square, move_to, promotion)
                                                    return self.game.san_and_push(move_to_play)

                            break

                # raise error if we don't have any candidates to move (most likely invalid move supplied)
                if not candidates_to_move:
                    raise chess.InvalidMoveError(f'Could not resolve any {"White" if self.game.turn else "Black"} "{move_arr[0]}" pieces.')
                
                #print(candidates_to_move)

                piece_to_move: chess.Square = None
                # potentially narrow down the candidates to a specific one, if given a file (ie. Rook H to f4)
                for word in move_arr:
                    for i, file in enumerate(chess.FILE_NAMES): 
                        if file == word:
                            # if the word is the file
                            # print(word)
                            for square in candidates_to_move:
                                # for each square object in candidates_to_move SquareSet
                                if chess.square_file(square) == i:
                                    # if the file of the square is the integer value of the file, set that square to piece_to_move
                                    piece_to_move = square
                                    print(square)
                                    break

                # print(piece_to_move)

                # need to explicitly say "is not None" in case piece_to_move = 0 (which it can be for square a1)
                if piece_to_move is not None:
                    # if piece_to_move is set from above, formulate move from the known piece's square and the known square to move to
                    move = chess.Move(piece_to_move, move_to)
                    if self.game.is_legal(move):
                        #print(game.board_fen())
                        return self.game.san_and_push(move)
                    else:
                        raise chess.IllegalMoveError(f'Could not move {move_arr[0]} from {chess.SQUARE_NAMES[piece_to_move]} to {chess.SQUARE_NAMES[move_to]}')
                else:
                    #print("No specific piece!")
                    # if piece_to_move is *not* set, determine which piece(s) in candidates_to_move are able to legally make the move; if it's multiple, ask user to clarify.
                    move_to_play: chess.Move = None
                    for square in candidates_to_move:
                        temp_move = chess.Move(square, move_to)
                        #print(temp_move)
                        if self.game.is_legal(temp_move):
                            if not move_to_play:
                                move_to_play = temp_move
                            else:
                                raise chess.AmbiguousMoveError(f'There are multiple {move_arr[0]}s that can move to {chess.SQUARE_NAMES[move_to]}')

                    return self.game.san_and_push(move_to_play)
            else:
                # if UCI worked, return True
                return True
        else:
            # if it worked, return True
            return True

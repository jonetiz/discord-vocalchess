import chess
import re

def test(move):

    # TESTING ONLY
    game = chess.Board()
    game.set_fen('rnbqkbn1/pppp1ppP/8/4pP2/8/8/PPPP2P1/R3K2R w KQq e6 1 1')
    ######

    # split input string by spaces, hyphens, and underscores
    move_arr = re.split(' |-|_', move.lower())

    # check castling and en-passant
    for word in move_arr:
        if word in ("castle", "castles", "longcastle", "longcastles", "shortcastle", "shortcastles"):
            # if we are trying to castle

            if not game.has_castling_rights(game.turn):
                # make no move if player doesn't have castling rights
                raise chess.IllegalMoveError(f'{"White" if game.turn else "Black"} does not have castling rights.')
            
            try:
                # if there are no castling moves, raise IllegalMoveError
                game.generate_castling_moves().__next__()
            except:
                raise chess.IllegalMoveError('There are no legal castling moves in the current position.')
            
            if "longcastle" in move_arr or "longcastles" in move_arr or "long" in move_arr or "queen" in move_arr or "queenside" in move_arr:
                # if "long", "queen", or "queenside" is designated in the move_arr, do a long castle
                #print("long castle")
                try:
                    game.push_san("O-O-O")
                except:
                    raise chess.IllegalMoveError('Queen-side castling is not legal in the current position.')
                else:
                    return "O-O-O"
            else:
                #print("short castle")
                try:
                    game.push_san("O-O")
                except:
                    raise chess.IllegalMoveError('King-side castling is not legal in the current position.')
                else:
                    return "O-O"
        elif word in ("en-passant", "ep", "e.p.", "passant", "pasant"):
            if not game.has_legal_en_passant():
                raise chess.IllegalMoveError(f'There is no legal en-passant in the current position.')
            
            for move in game.generate_legal_ep():
                # logically, there can only be one legal en-passant at a time, so we only need to take the first legal en-passant
                return game.san_and_push(move)
        
    # move_to = last word in move_arr
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
        for alias in piece_aliases[piece]:
            if move_arr[0] == alias:
                #  print(piece)
                # find all of the pieces that match the given piece on the given side
                candidates_to_move = game.pieces(piece, game.turn)

                # handle promotion case
                if "promote" in move_arr or "promotes" in move_arr:
                    if piece == chess.PAWN:
                        # only pawns can promote
                        for square in candidates_to_move:
                            if chess.square_rank(square) == 6:
                                # if it's on the 7th rank, it may be able to promote
                                for move in game.generate_legal_moves():
                                    if move.to_square == move_to:
                                        # if this is the correct move based on the move_to variable, determine what we're promoting to
                                        promotion = chess.QUEEN # default to queen if otherwise undefined 
                                        for piece in range(2, 6):
                                            for alias in piece_aliases[piece]:
                                                if alias in move_arr[1:]:
                                                    # we don't need the first piece of move_arr since that's the piece we want to move, find the other one
                                                    promotion = piece
                                        move_to_play = chess.Move(square, move_to, promotion)
                                        return game.san_and_push(move_to_play)

                break

    # raise error if we don't have any candidates to move (most likely invalid move supplied)
    if not candidates_to_move:
        raise chess.InvalidMoveError(f'Could not resolve any {"White" if game.turn else "Black"} "{move_arr[0]}" pieces.')
    
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

    print(piece_to_move)

    # need to explicitly say "is not None" in case piece_to_move = 0 (which it can be for square a1)
    if piece_to_move is not None:
        # if piece_to_move is set from above, formulate move from the known piece's square and the known square to move to
        move = chess.Move(piece_to_move, move_to)
        if game.is_legal(move):
            #print(game.board_fen())
            return game.san_and_push(move)
        else:
            raise chess.IllegalMoveError(f'Could not move {move_arr[0]} from {chess.SQUARE_NAMES[piece_to_move]} to {chess.SQUARE_NAMES[move_to]}')
    else:
        #print("No specific piece!")
        # if piece_to_move is *not* set, determine which piece(s) in candidates_to_move are able to legally make the move; if it's multiple, ask user to clarify.
        move_to_play: chess.Move = None
        for square in candidates_to_move:
            temp_move = chess.Move(square, move_to)
            #print(temp_move)
            if game.is_legal(temp_move):
                if not move_to_play:
                    move_to_play = temp_move
                else:
                    raise chess.AmbiguousMoveError(f'There are multiple {move_arr[0]}s that can move to {chess.SQUARE_NAMES[move_to]}')

        return game.san_and_push(move_to_play)
        
print(test("h promotes to knight h8"))
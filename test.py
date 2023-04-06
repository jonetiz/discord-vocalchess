import chess

def test(move):
    game = chess.Board()

    move_arr = move.lower().split(" ")

    piece_aliases = {
        chess.KING: ["k", "king"],
        chess.QUEEN: ["q", "queen"],
        chess.BISHOP: ["b", "bishop"],
        chess.KNIGHT: ["n", "k", "knight", "nite", "night", "horse"],
        chess.ROOK: ["r", "rook"],
        chess.PAWN: ["p", "pawn", "a", "b", "c", "d", "e", "f", "g", "h"]
    }

    operations = ["x", "to", "takes", "take", "capture", "captures"]
    # print(move_arr)
    
    # a set of squares on which pieces may be moved, populated by piece resolution below
    candidates_to_move: chess.SquareSet

    # resolve the piece
    for piece in piece_aliases:
        for alias in piece_aliases[piece]:
            for word in move_arr:
                if word == alias:
                   #  print(piece)
                    # find all of the pieces that match the given piece on the given side
                    candidates_to_move = game.pieces(piece, game.turn)
                    break

    print(candidates_to_move)

    # resolve the operation
    known_operation: tuple
    for i, word in enumerate(move_arr):
        if word in operations:
            known_operation = (i, word)
            break

    specific_piece: chess.Square
    # potentially narrow down the candidates to a specific one, if given a file (ie. Rook H to f4)
    for word in move_arr[0:known_operation[0]]:
        for i, file in enumerate(chess.FILE_NAMES): 
            if file == word:
                print(word)
                for square in candidates_to_move:
                    if chess.square_file(square) == i:
                        specific_piece = square
                        # set specific_piece to the squares in candidates_to_move where file is word
                        pass


test("h to f4")
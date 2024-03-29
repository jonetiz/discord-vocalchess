from PIL import Image, ImageDraw, ImageFont

from chess import Piece, SQUARE_NAMES

def generate_piece_images() -> dict:
    """Create a dictionary of PIL Image objects corresponding to each chess piece keyed by FEN notation of the piece."""
    out = {}
    spritesheet = Image.open('rsc/chess-sprites.png')

    # white pieces
    out['K'] = spritesheet.crop((0, 0, 200, 200))
    out['Q'] = spritesheet.crop((200, 0, 400, 200))
    out['B'] = spritesheet.crop((400, 0, 600, 200))
    out['N'] = spritesheet.crop((600, 0, 800, 200))
    out['R'] = spritesheet.crop((800, 0, 1000, 200))
    out['P'] = spritesheet.crop((1000, 0, 1200, 200))

    # black pieces
    out['k'] = spritesheet.crop((0, 200, 200, 400))
    out['q'] = spritesheet.crop((200, 200, 400, 400))
    out['b'] = spritesheet.crop((400, 200, 600, 400))
    out['n'] = spritesheet.crop((600, 200, 800, 400))
    out['r'] = spritesheet.crop((800, 200, 1000, 400))
    out['p'] = spritesheet.crop((1000, 200, 1200, 400))
    return out

class ChessBoardImage:
    def __init__(self, pieces: dict, board_position: dict, lastmove: tuple = (), mirror = False, size=800, dark: tuple = (110, 109, 107), light: tuple = (144, 143, 141)):
        def get_pixels_of_coords(coordinates: str):
            """Get the pixel location of chess notation coordinates (ie. a8 should return (0,0) and f3 should return ((size/8)*5, (size/8)*5))"""
            out_x = 0
            out_y = 0
            
            if mirror:
                match coordinates[0]:
                    case "h":
                        out_x = 0
                    case "g":
                        out_x = size//8
                    case "f":
                        out_x = 2*size//8
                    case "e":
                        out_x = 3*size//8
                    case "d":
                        out_x = 4*size//8
                    case "c":
                        out_x = 5*size//8
                    case "b":
                        out_x = 6*size//8
                    case "a":
                        out_x = 7*size//8

                match coordinates[1]:
                    case "8":
                        out_y = 7*size//8
                    case "7":
                        out_y = 6*size//8
                    case "6":
                        out_y = 5*size//8
                    case "5":
                        out_y = 4*size//8
                    case "4":
                        out_y = 3*size//8
                    case "3":
                        out_y = 2*size//8
                    case "2":
                        out_y = size//8
                    case "1":
                        out_y = 0
            else:
                match coordinates[0]:
                    case "a":
                        out_x = 0
                    case "b":
                        out_x = size//8
                    case "c":
                        out_x = 2*size//8
                    case "d":
                        out_x = 3*size//8
                    case "e":
                        out_x = 4*size//8
                    case "f":
                        out_x = 5*size//8
                    case "g":
                        out_x = 6*size//8
                    case "h":
                        out_x = 7*size//8

                match coordinates[1]:
                    case "8":
                        out_y = 0
                    case "7":
                        out_y = size//8
                    case "6":
                        out_y = 2*size//8
                    case "5":
                        out_y = 3*size//8
                    case "4":
                        out_y = 4*size//8
                    case "3":
                        out_y = 5*size//8
                    case "2":
                        out_y = 6*size//8
                    case "1":
                        out_y = 7*size//8

            return (out_x, out_y)

        # draw image with designated size and additional 10% for borders
        self.img = Image.new(mode="RGB", size=(size,size), color=(0,0,0))
        board = ImageDraw.Draw(self.img, "RGBA")

        # draw the squares of the chess board
        for i in range(8):
            # alternate colors based on row
            if i % 2 == 0:
                board.rectangle(xy = [(i*size/8, 0), ((i*size/8)+size/8, size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 1*size/8), ((i*size/8)+size/8, 2*size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 2*size/8), ((i*size/8)+size/8, 3*size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 3*size/8), ((i*size/8)+size/8, 4*size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 4*size/8), ((i*size/8)+size/8, 5*size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 5*size/8), ((i*size/8)+size/8, 6*size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 6*size/8), ((i*size/8)+size/8, 7*size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 7*size/8), ((i*size/8)+size/8, 8*size/8)], fill=dark, outline = None)
            else:
                board.rectangle(xy = [(i*size/8, 0), ((i*size/8)+size/8, size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 1*size/8), ((i*size/8)+size/8, 2*size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 2*size/8), ((i*size/8)+size/8, 3*size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 3*size/8), ((i*size/8)+size/8, 4*size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 4*size/8), ((i*size/8)+size/8, 5*size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 5*size/8), ((i*size/8)+size/8, 6*size/8)], fill=light, outline = None)
                board.rectangle(xy = [(i*size/8, 6*size/8), ((i*size/8)+size/8, 7*size/8)], fill=dark, outline = None)
                board.rectangle(xy = [(i*size/8, 7*size/8), ((i*size/8)+size/8, 8*size/8)], fill=light, outline = None)
    
        outline_font = ImageFont.truetype("rsc/DejaVuSans.ttf", size=size//25)

        dark_text = (0,0,0)
        light_text = (255,255,255)
        
        # highlight last move squares
        if lastmove != ():
            coords_1 = get_pixels_of_coords(SQUARE_NAMES[lastmove[0]])
            board.rectangle(xy = [coords_1, (coords_1[0]+size//8, coords_1[1]+size//8)], fill=(114, 137, 218, 127), outline = None)
            coords_2 = get_pixels_of_coords(SQUARE_NAMES[lastmove[1]])
            board.rectangle(xy = [coords_2, (coords_2[0]+size//8, coords_2[1]+size//8)], fill=(114, 137, 218, 127), outline = None)

        # draw each peice image
        for piece in board_position:
            piece_image = pieces[f'{board_position[piece].symbol()}'].resize((size//8, size//8))
            self.img.paste(piece_image, get_pixels_of_coords(SQUARE_NAMES[piece]), piece_image)

        # draw file markers
        board.text(xy = (1*size/8-size//30, size-size//20), text = "a" if not mirror else "h", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (2*size/8-size//30, size-size//20), text = "b" if not mirror else "g", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (3*size/8-size//30, size-size//20), text = "c" if not mirror else "f", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (4*size/8-size//30, size-size//20), text = "d" if not mirror else "e", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (5*size/8-size//30, size-size//20), text = "e" if not mirror else "d", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (6*size/8-size//30, size-size//20), text = "f" if not mirror else "c", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (7*size/8-size//30, size-size//20), text = "g" if not mirror else "b", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (8*size/8-size//30, size-size//20), text = "h" if not mirror else "a", align = "center", font = outline_font, fill = dark_text)

        # draw rank markers
        board.text(xy = (size//200, 0), text = "8" if not mirror else "1", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 1*size/8), text = "7" if not mirror else "2", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (size//200, 2*size/8), text = "6" if not mirror else "3", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 3*size/8), text = "5" if not mirror else "4", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (size//200, 4*size/8), text = "4" if not mirror else "5", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 5*size/8), text = "3" if not mirror else "6", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (size//200, 6*size/8), text = "2" if not mirror else "7", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 7*size/8), text = "1" if not mirror else "8", align = "center", font = outline_font, fill = light_text)

pieces = generate_piece_images()

# asd = {63: Piece.from_symbol('r'), 62: Piece.from_symbol('n'), 61: Piece.from_symbol('b'), 60: Piece.from_symbol('k'), 59: Piece.from_symbol('q'), 58: Piece.from_symbol('b'), 57: Piece.from_symbol('n'), 56: Piece.from_symbol('r'), 55: Piece.from_symbol('p'), 54: Piece.from_symbol('p'), 53: Piece.from_symbol('p'), 51: Piece.from_symbol('p'), 50: Piece.from_symbol('p'), 49: Piece.from_symbol('p'), 48: Piece.from_symbol('p'), 36: Piece.from_symbol('p'), 28: Piece.from_symbol('P'), 15: Piece.from_symbol('P'), 14: Piece.from_symbol('P'), 13: Piece.from_symbol('P'), 11: Piece.from_symbol('P'), 10: Piece.from_symbol('P'), 9: Piece.from_symbol('P'), 8: Piece.from_symbol('P'), 7: Piece.from_symbol('R'), 6: Piece.from_symbol('N'), 5: Piece.from_symbol('B'), 4: Piece.from_symbol('K'), 3: Piece.from_symbol('Q'), 2: Piece.from_symbol('B'), 1: Piece.from_symbol('N'), 0: Piece.from_symbol('R')}

# ChessBoardImage(pieces, asd, (52, 36), False).img.show()
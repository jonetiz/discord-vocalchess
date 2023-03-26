from PIL import Image, ImageDraw, ImageFont
import time

from chess import Piece, SQUARE_NAMES

def generate_piece_images() -> dict:
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
    def __init__(self, pieces: dict, board_position: dict, lastmove: tuple = (), size=800, dark: tuple = (110, 109, 107), light: tuple = (144, 143, 141)):
        # start = time.time()

        def get_pixels_of_coords(coordinates: str):
            """Get the pixel location of chess notation coordinates (ie. a8 should return (0,0) and f3 should return ((size/8)*5, (size/8)*5))"""
            out_x = 0
            out_y = 0

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
        for i in range(8):
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

        dark_text = dark
        light_text = light

        # for debug: displays full default black setup
        # self.img.paste(pieces['r'].resize((size//8, size//8)), (0*size//8, 0), pieces['r'].resize((size//8, size//8)))
        # self.img.paste(pieces['n'].resize((size//8, size//8)), (1*size//8, 0), pieces['n'].resize((size//8, size//8)))
        # self.img.paste(pieces['b'].resize((size//8, size//8)), (2*size//8, 0), pieces['b'].resize((size//8, size//8)))
        # self.img.paste(pieces['q'].resize((size//8, size//8)), (3*size//8, 0), pieces['q'].resize((size//8, size//8)))
        # self.img.paste(pieces['k'].resize((size//8, size//8)), (4*size//8, 0), pieces['k'].resize((size//8, size//8)))
        # self.img.paste(pieces['b'].resize((size//8, size//8)), (5*size//8, 0), pieces['b'].resize((size//8, size//8)))
        # self.img.paste(pieces['n'].resize((size//8, size//8)), (6*size//8, 0), pieces['n'].resize((size//8, size//8)))
        # self.img.paste(pieces['r'].resize((size//8, size//8)), (7*size//8, 0), pieces['r'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (0*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (1*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (2*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (3*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (4*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (5*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (6*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        # self.img.paste(pieces['p'].resize((size//8, size//8)), (7*size//8, size//8), pieces['p'].resize((size//8, size//8)))
        
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
        board.text(xy = (1*size/8-size//30, size-size//20), text = "a", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (2*size/8-size//30, size-size//20), text = "b", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (3*size/8-size//30, size-size//20), text = "c", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (4*size/8-size//30, size-size//20), text = "d", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (5*size/8-size//30, size-size//20), text = "e", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (6*size/8-size//30, size-size//20), text = "f", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (7*size/8-size//30, size-size//20), text = "g", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (8*size/8-size//30, size-size//20), text = "h", align = "center", font = outline_font, fill = dark_text)

        # draw rank markers
        board.text(xy = (size//200, 0), text = "8", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 1*size/8), text = "7", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (size//200, 2*size/8), text = "6", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 3*size/8), text = "5", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (size//200, 4*size/8), text = "4", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 5*size/8), text = "3", align = "center", font = outline_font, fill = light_text)
        board.text(xy = (size//200, 6*size/8), text = "2", align = "center", font = outline_font, fill = dark_text)
        board.text(xy = (size//200, 7*size/8), text = "1", align = "center", font = outline_font, fill = light_text)

        # end = time.time()
        # print(end - start)

pieces = generate_piece_images()

# asd = {63: Piece.from_symbol('r'), 62: Piece.from_symbol('n'), 61: Piece.from_symbol('b'), 60: Piece.from_symbol('k'), 59: Piece.from_symbol('q'), 58: Piece.from_symbol('b'), 57: Piece.from_symbol('n'), 56: Piece.from_symbol('r'), 55: Piece.from_symbol('p'), 54: Piece.from_symbol('p'), 53: Piece.from_symbol('p'), 51: Piece.from_symbol('p'), 50: Piece.from_symbol('p'), 49: Piece.from_symbol('p'), 48: Piece.from_symbol('p'), 36: Piece.from_symbol('p'), 28: Piece.from_symbol('P'), 15: Piece.from_symbol('P'), 14: Piece.from_symbol('P'), 13: Piece.from_symbol('P'), 11: Piece.from_symbol('P'), 10: Piece.from_symbol('P'), 9: Piece.from_symbol('P'), 8: Piece.from_symbol('P'), 7: Piece.from_symbol('R'), 6: Piece.from_symbol('N'), 5: Piece.from_symbol('B'), 4: Piece.from_symbol('K'), 3: Piece.from_symbol('Q'), 2: Piece.from_symbol('B'), 1: Piece.from_symbol('N'), 0: Piece.from_symbol('R')}

# ChessBoardImage(pieces, asd, ('e7', 'e5')).img.show()
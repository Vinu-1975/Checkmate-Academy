from .base import Piece
import pygame as pg

class Queen(Piece):
    def __init__(self, position, colour, piece_type=None, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.legal_directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        self.colour = colour
        self.position = position
        if piece_type is not None:
            self.piece_set = piece_type
        if colour == 'black':
            self.piece = 'q'
        else:
            self.piece = 'Q'

        self.picture = pg.image.load(
            "data/img/pieces/" + self.piece_set + "/" + colour[0] + self.piece.lower() + ".png").convert_alpha()

    def update_legal_moves(self, board, eps, captures):
        self.legal_positions = []
        x = self.position[1]
        y = self.position[0]
        for direction in self.legal_directions:
            for i in range(1, 9):
                try:
                    if -1 < y + direction[0] * i < 8 and -1 < x + direction[1] * i < 8:
                        if board[y + direction[0] * i][x + direction[1]*i] == ' ':
                            self.legal_positions.append((direction[1] * i, direction[0]*i))
                        elif board[y + direction[0] * i][x + direction[1]*i].colour != self.colour and not captures:
                            self.legal_positions.append((direction[1] * i, direction[0] * i))
                            break
                        elif board[y + direction[0] * i][x + direction[1]*i].colour != self.colour and board[y + direction[0] * i][x + direction[1]*i].piece.lower() == 'k' and captures:
                            self.legal_positions.append((direction[1] * i, direction[0] * i))
                        elif board[y + direction[0] * i][x + direction[1]*i].colour != self.colour and captures:
                            self.legal_positions.append((direction[1] * i, direction[0] * i))
                            break
                        elif board[y + direction[0] * i][x + direction[1] * i].colour == self.colour and captures:
                            self.legal_positions.append((direction[1] * i, direction[0] * i))
                            break
                        else:
                            break
                except:
                    continue





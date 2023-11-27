from .base import Piece
import pygame as pg

class Knight(Piece):
    def __init__(self, position, colour, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.legal_directions = [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
        self.colour = colour
        self.position = position
        if colour == 'black':
            self.piece = 'n'
        else:
            self.piece = 'N'
        self.picture = pg.image.load(
            "data/img/pieces/" + self.piece_set + "/" + colour[0] + self.piece.lower() + ".png").convert_alpha()

    def update_legal_moves(self, board, eps, captures):
        self.legal_positions = []
        x = self.position[1]
        y = self.position[0]
        for direction in self.legal_directions:
            try:
                if -1 < y + direction[0] < 8 and -1 < x + direction[1] < 8:
                    if board[y + direction[0]][x + direction[1]] == ' ':
                        self.legal_positions.append((direction[1], direction[0]))
                    elif board[y + direction[0]][x + direction[1]].colour != self.colour:
                        self.legal_positions.append((direction[1], direction[0]))
                    elif board[y + direction[0]][x + direction[1]].colour == self.colour and captures:
                        self.legal_positions.append((direction[1], direction[0]))
            except:
                continue

    def check(self, board):
        self.checks = []
        x = self.position[1]
        y = self.position[0]
        for direction in self.legal_directions:
            temp_check = []
            try:
                piece = board[y + direction[0]][x + direction[1]]
                if -1 < y + direction[0] < 8 and -1 < x + direction[1] < 8:
                    if piece == ' ':
                        pass
                    elif piece.colour != self.colour and piece.piece.lower() == 'k':
                        temp_check.append(self.position)
                        temp_check.append((y + direction[0], x + direction[1]))
                        for i in temp_check:
                            self.checks.append(i)
                        return True
            except:
                continue

        return False
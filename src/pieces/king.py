from .base import Piece
import pygame as pg


class King(Piece):
    def __init__(self, position, colour, castling_rights, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.castling_rights = castling_rights
        self.legal_directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        self.colour = colour
        self.position = position
        if colour == 'black':
            self.piece = 'k'
        else:
            self.piece = 'K'
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
        if not self.has_moved:
            blanks = 0
            try:
                for i in range(1, 3):
                     if board[self.position[0]][self.position[1] + i] == ' ':
                        blanks += 1
            except:
                pass
            try:
                if board[self.position[0]][self.position[1] + 3].piece.lower() == 'r' and board[self.position[0]][self.position[1] + 3].has_moved == False and blanks == 2:
                    self.legal_positions.append((2, 0))
            except:
                pass
            blanks = 0
            for i in range(1, 4):
                if board[self.position[0]][self.position[1] - i] == ' ':
                    blanks += 1
            try:
                if board[self.position[0]][self.position[1] - 4].piece.lower() == 'r' and not board[self.position[0]][self.position[1] - 4].has_moved and blanks == 3:
                    self.legal_positions.append((-2, 0))
            except:
                pass

    def trim_checks(self, board, turn, map, in_check):
        # todo : cant move to a square controlled by enemy.

        updated_moves = []
        for move in self.legal_positions:
            if (self.position[0] + move[1], self.position[1] + move[0]) not in map:
                if (move[0] == 2 or move[0] == -2) and in_check:
                    pass
                elif (move[0] == 2) and (self.position[0], self.position[1] + 1) in map:  # castle through check
                    pass
                elif (move[0] == -2) and (self.position[0], self.position[1] - 1) in map:  # castle through check
                    pass

                else:
                    updated_moves.append(move)
        self.legal_positions = updated_moves

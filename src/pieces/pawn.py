from .base import Piece
import pygame as pg


class Pawn(Piece):
    def __init__(self, position, colour, has_moved=False, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.has_moved = has_moved
        self.colour = colour
        self.position = position
        if colour == 'black':
            self.direction = 1
            self.piece = 'p'
            self.legal_directions = [(0, 1), (0, 2)]
        else:
            self.direction = -1
            self.piece = 'P'
            self.legal_directions = [(0, -1), (0, -2)]
        self.picture = pg.image.load(
            "data/img/pieces/" + self.piece_set + "/" + colour[0] + self.piece.lower() + ".png").convert_alpha()

    def update_legal_moves(self, board, eps, captures):
        self.legal_positions = []

        # move forward logic
        if not captures:
            x = self.position[1]
            y = self.position[0] + self.direction
            for i in range(2):
                try:
                    if board[y + i*self.direction][x] == ' ':
                        self.legal_positions.append((0, self.direction*i + self.direction))
                    else:
                        break
                    if self.has_moved:
                        break
                except:
                    continue

        # catching logic
        x = self.position[1] + 1
        y = self.position[0] + self.direction
        pawns_available_to_catch = 0
        if not captures:
            for i in range(2):
                try:
                    if board[y][x - 2*i] != ' ' and -1 < x - 2*i < 8:
                        if board[y][x - 2*i].colour != self.colour:
                            self.legal_positions.append((board[y][x - 2*i].position[1] - self.position[1], board[y][x - 2*i].position[0] - self.position[0]))
                            pawns_available_to_catch += 1
                except:
                    continue

        if captures: # case calculating opponents king moves
            # the commented code caused erroneous moves. Don't care if capture is off board anyway

            # if self.position[1] + 1 < 8 and 0 < self.position[0] + self.direction < 7:
            self.legal_positions.append((1, self.direction))
            # if self.position[1] - 1 > 0 and 0 < self.position[0] + self.direction < 7:
            self.legal_positions.append((-1, self.direction))

        # en-passant
        if eps != '-':
            if self.position[0] == 3 and self.colour == 'white' or self.position[0] == 4 and self.colour == 'black':
                if self.position[1] - int(eps[4]) == 1 or self.position[1] - int(eps[4]) == -1:
                    self.legal_positions.append((int(eps[4]) - self.position[1],
                                                 self.position[0] - int(eps[1])))

    def check(self, board):
        self.checks = []
        x = self.position[1] + 1
        y = self.position[0] + self.direction
        for i in range(2):
            try:
                if board[y][x - 2 * i] != ' ' and -1 < x - 2 * i < 8:
                    if board[y][x - 2 * i].colour != self.colour and board[y][x - 2 * i].piece.lower() == 'k':
                        self.checks.append(board[y][x - 2 * i].position)
                        self.checks.append(self.position)
                        return True
            except:
                continue

        return False




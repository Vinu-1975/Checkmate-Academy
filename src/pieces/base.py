'''
Common class for all pieces.
'''

import pygame as pg
from pygame import sprite

class Piece(sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.piece_set = 'chessmonk'
        self.dead = False
        self.position = None
        self.colour = None
        self.piece = None
        self.legal_directions = None
        self.checks = []
        self.legal_positions = []
        self.pin_lines = set()
        self.legal_directions = None
        self.clicked = False
        self.size = 100
        self.is_alive = True
        self.has_moved = False
        self.picture = None

    def click(self):
        self.clicked = True

    def update(self, screen, offset, turn, flipped, board):
        #find and draw legal moves.
        # move the piece under the mouse
        self.clicked = True
        for i in self.legal_positions:
            if board[(self.position[0] + i[1])][(self.position[1] + i[0])] == ' ':
                if -1 < (self.position[1] + i[0]) < 8 and -1 < (self.position[0] + i[1]) < 8 and turn == self.colour[0]:
                    if not flipped:
                        pg.draw.circle(screen, (0, 204, 204), ((self.position[1] + i[0])*self.size + offset[0] + self.size/2, (self.position[0] + i[1])*self.size + offset[1] + self.size/2), self.size/4)
                    else:
                        pg.draw.circle(screen, (0, 204, 204), ((-self.position[1]+7 - i[0])*self.size + offset[0] + self.size/2, (-self.position[0]+7 - i[1])*self.size + offset[1] + self.size/2), self.size/4)
            else:
                if -1 < (self.position[1] + i[0]) < 8 and -1 < (self.position[0] + i[1]) < 8 and turn == self.colour[0]:
                    if not flipped:
                        pg.draw.rect(screen, (237, 109, 100), ((self.position[1] + i[0])*self.size + offset[0] + self.size/6, (self.position[0] + i[1])*self.size + offset[1] + self.size/6, 2*self.size/3, 2*self.size/3), border_radius=int(self.size/8))
                    else:
                        pg.draw.rect(screen, (237, 109, 100), ((-self.position[1]+7 - i[0])*self.size + offset[0] + self.size/6, (-self.position[0]+7 - i[1])*self.size + offset[1] + self.size/6, 2*self.size/3, 2*self.size/3), border_radius=int(self.size/8))

    def update_legal_moves(self, board, eps=None, captures=False):
        pass

    def check(self, board):
        self.checks = []
        x = self.position[1]
        y = self.position[0]
        for direction in self.legal_directions:
            temp_check = []
            for i in range(1, 9):
                try:
                    piece = board[y + direction[0] * i][x + direction[1] * i]
                    if -1 < y + direction[0] * i < 8 and -1 < x + direction[1] * i < 8:
                        if piece == ' ':
                            temp_check.append((y + direction[0] * i, x + direction[1] * i))
                        elif piece.colour != self.colour and piece.piece.lower() == 'k':
                            temp_check.append((y + direction[0] * i, x + direction[1] * i))
                            temp_check.append(self.position)
                            for i in temp_check:
                                self.checks.append(i)
                            return True
                        else:
                            break
                    else:
                        break
                except:
                    continue
        return False

    def trim_checks(self, board, turn, map=None, in_check=False):
        updated_moves = []
        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                if piece != ' ':
                    if len(piece.checks) > 0:
                        if piece.colour[0] != turn:
                            if piece.piece.lower() != 'k':
                                for move in self.legal_positions:
                                    # print('Piece, position moves: ')
                                    # print(self.piece, self.position)
                                    # print((self.position[0] + move[1], self.position[1] + move[0]))
                                    if (self.position[0] + move[1], self.position[1] + move[0]) in piece.checks:
                                        updated_moves.append(move)
                                self.legal_positions = updated_moves

    def pin_line_update(self, board):
        self.pin_lines.clear()
        x = self.position[1]
        y = self.position[0]
        self.pin_lines.add((y, x))
        for direction in self.legal_directions:
            count = 0
            temp_pins = []
            piece_pinned = ''
            for i in range(1, 9):
                try:
                    piece = board[y + direction[0] * i][x + direction[1] * i]
                    if -1 < y + direction[0] * i < 8 and -1 < x + direction[1] * i < 8:
                        if piece == ' ':
                            temp_pins.append((y + direction[0] * i, x + direction[1] * i))
                        elif piece.colour != self.colour and count < 1:
                            temp_pins.append((y + direction[0] * i, x + direction[1] * i))
                            piece_pinned = piece.piece + str(piece.position)
                            count += 1
                        elif piece.colour != self.colour and piece.piece.lower() == 'k':
                            for i in temp_pins:
                                self.pin_lines.add(i)
                            break
                        elif piece.colour == self.colour:
                            break
                        else:
                            break
                    else:
                        break
                except:
                    continue
        # if len(self.pin_lines) > 1:
        #     print(self.piece, self.position, self.pin_lines)

    def trim_pin_moves(self, board):
        x = self.position[1]
        y = self.position[0]
        for pin in self.pin_lines:
            try:
                if board[pin[0]][pin[1]].colour != self.colour:
                    piece = board[pin[0]][pin[1]]
                    updated_moves = []
                    for legal_pos in piece.legal_positions:
                        if (piece.position[0] + legal_pos[1], piece.position[1] + legal_pos[0]) in list(self.pin_lines):
                            updated_moves.append(legal_pos)
                    piece.legal_positions = updated_moves
            except:
                continue


    def make_move(self, board, offset, turn, flipped, i=None, j=None):
        # ai move's using i amd j
        if i == None:
            x = int((pg.mouse.get_pos()[0] - offset[0]) // self.size)
            y = int((pg.mouse.get_pos()[1] - offset[1]) // self.size)
        else:
            x = i
            y = j
        if flipped and i is None:
            x = -x+7
            y = -y+7

        if (x - self.position[1], y - self.position[0]) in self.legal_positions and self.colour[0] == turn:
            self.position = (y, x)
            self.has_moved = True
            return True
        else:
            return False

    def draw(self, offset, screen, size, flipped):
        self.size = size
        if self.picture.get_size() != (self.size, self.size):
            self.picture = pg.image.load(
                "data/img/pieces/" + self.piece_set + "/" + self.colour[0] + self.piece.lower() + ".png").convert_alpha()
            self.picture = pg.transform.smoothscale(self.picture, (self.size, self.size))
        if self.clicked:
            screen.blit(self.picture,
                        (pg.mouse.get_pos()[0] - self.size / 2 ,
                         pg.mouse.get_pos()[1] - self.size / 2)
                        )
        else:
            if not flipped:
                screen.blit(self.picture,
                        (offset[0] + self.size * self.position[1], offset[1] + self.size * self.position[0]))
            else:
                screen.blit(self.picture,
                            (offset[0] + self.size * (-self.position[1]+7), offset[1] + self.size * (-self.position[0]+7)))

    def change_type(self, piece_type):
        self.piece_set = piece_type
        self.picture = pg.image.load(
            "data/img/pieces/" + self.piece_set + "/" + self.colour[0] + self.piece.lower() + ".png").convert_alpha()
        self.picture = pg.transform.smoothscale(self.picture, (self.size, self.size))

    def __del__(self):
        self.dead = True
        self.clicked = False
        self.kill()
        # print('a', self.colour, self.piece.upper(), 'has died')


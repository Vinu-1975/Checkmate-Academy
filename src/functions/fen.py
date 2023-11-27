from src.pieces.rook import Rook
from src.pieces.bishop import Bishop
from src.pieces.queen import Queen
from src.pieces.king import King
from src.pieces.knight import Knight
from src.pieces.pawn import Pawn

board_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']


def create_FEN(board, turn, castle_rights, en_p_s, fmn):
    fen_string = ''
    for row in range(8):
        blanks = 0
        for col in range(8):
            if board[row][col] == ' ':
                blanks += 1
            else:
                if blanks > 0:
                    fen_string += str(blanks)
                    blanks = 0
                fen_string += board[row][col].piece
        if blanks > 0:
            fen_string += str(blanks)
        if row != 7:
            fen_string += '/'
    fen_string += ' ' + turn + ' ' + castle_rights + ' '
    if en_p_s == '-':
        fen_string += '-'
    else:
        fen_string += board_letters[int(en_p_s[4])]
        if int(en_p_s[1]) == 4:
            fen_string += '6'
        else:
            fen_string += str(int(en_p_s[1]))
    fen_string += ' 0 '
    fen_string += str(fmn)
    return fen_string


def take_one(moves: str):
    move_array = moves.split(' ')
    if move_array[-2][1] == '.':
        move_array.pop()
        move_array.pop()
    else:
        move_array.pop()
    move = ' '.join(move_array)
    move += ' /'
    print(move)
    return move


def square_on(number):
    return tuple((7 - (int(number[1]) - 1), int(board_letters.index(number[0]))))


def translate_move(r, c, x, y):
    return board_letters[c] + str(8 - r) + board_letters[y] + str(8 - x)


def FEN_to_board(fen_string):
    board = [[] for i in range(8)]
    fen_list = fen_string.split(' ')
    piece_placement_list = fen_list[0].split('/')
    for i, row in enumerate(piece_placement_list):
        for char in row:
            if char.isdigit():
                for k in range(int(char)):
                    board[i].append(' ')
            else:
                board[i].append(char)
    # board.reverse()
    return board


def parse_FEN(fen_string):
    board = [[] for i in range(8)]
    fen_list = fen_string.split(' ')
    piece_placement_list = fen_list[0].split('/')

    for i, row in enumerate(piece_placement_list):
        count = 0
        for j, char in enumerate(row):
            if char.isdigit():
                count += int(char)
                for k in range(int(char)):
                    board[i].append(' ')
            else:
                match char:
                    case 'r':
                        board[i].append(Rook(position=(i, count), colour='black'))
                    case 'R':
                        board[i].append(Rook(position=(i, count), colour='white'))
                    case 'p':
                        if i == 1:
                            board[i].append(Pawn(position=(i, count), colour='black'))
                        else:
                            board[i].append(Pawn(position=(i, count), colour='black', has_moved=True))
                    case 'P':
                        if i == 6:
                            board[i].append(Pawn(position=(i, count), colour='white'))
                        else:
                            board[i].append(Pawn(position=(i, count), colour='white', has_moved=True))
                    case 'n':
                        board[i].append(Knight(position=(i, count), colour='black'))
                    case 'N':
                        board[i].append(Knight(position=(i, count), colour='white'))
                    case 'b':
                        board[i].append(Bishop(position=(i, count), colour='black'))
                    case 'B':
                        board[i].append(Bishop(position=(i, count), colour='white'))
                    case 'k':
                        k = False
                        q = False
                        if 'k' in fen_list[2]:
                            k = True
                        if 'q' in fen_list[2]:
                            q = True
                        board[i].append(
                            King(position=(i, count), colour='black', castling_rights=dict(king=k, queen=q)))

                    case 'K':
                        k = False
                        q = False
                        if 'K' in fen_list[2]:
                            k = True
                        if 'Q' in fen_list[2]:
                            q = True
                        board[i].append(
                            King(position=(i, count), colour='white', castling_rights=dict(king=k, queen=q)))
                    case 'q':
                        board[i].append(Queen(position=(i, count), colour='black'))
                    case 'Q':
                        board[i].append(Queen(position=(i, count), colour='white'))

                count += 1

    turn = fen_list[1]

    castle_rights = fen_list[2]

    en_passant_square = fen_list[3]

    # eps square here is translated into the location of the pawn that made the move
    if fen_list[3] != '-':
        if turn == 'w':
            en_passant_square = str((int(en_passant_square[1]) - 2, int(board_letters.index(en_passant_square[0]))))
        else:
            en_passant_square = str((int(en_passant_square[1]), int(board_letters.index(en_passant_square[0]))))

    halfmoves_since_last_capture = int(fen_list[4])

    fullmove_number = int(fen_list[5])

    return board, turn, castle_rights, en_passant_square, halfmoves_since_last_capture, fullmove_number

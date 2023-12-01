import datetime
import random
import sys
import time

from src.engine.settings import SettingsMenu, EndGameMenu
from src.functions.fen import *
import pygame as pg
from src.functions.timer import *
from src.pieces.queen import Queen
from src.pieces.base import Piece
from stockfish import Stockfish
import chess
import chess.engine
import chess.pgn
import pygame_menu as pm
import platform
import navigation

# "8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3" - can en passant out of check!
# "rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9" - 39 moves can promote to other pieces
# rnbq1bnr/ppp1p1pp/3p4/6P1/1k1PPp1P/1PP2P1B/PB6/RN1QK2R b KQkq - 0 13 - king cant go to a4 here


EVAL_ON = False


def print_eval(evaluation):
    if evaluation["type"] == "cp":
        return "Evaluation = " + str(round(evaluation["value"] / 100, 2))
    else:
        if evaluation["value"] < 0:
            return "Mate in " + str(-evaluation["value"])
        else:
            return "Mate in " + str(evaluation["value"])


class Engine2:
    def __init__(self):
        self.fun = 0
        self.puzzle_mode = False
        self.player_vs_ai = None
        self.ai_vs_ai = None
        self.evaluation = ""
        self.best_move = ""
        self.game_just_ended = False
        self.engine = "stockfish"
        pg.init()
        pg.display.set_caption("Chess", "chess")
        pg.font.init()
        self.last_move = []
        self.highlighted = []
        self.arrows = []
        self.flipped = False
        self.flip_enabled = True
        self.sound_enabled = True
        self.platform = None
        if "Windows" in platform.platform():
            self.platform = "Windows/" + self.engine + ".exe"
        if "macOS" in platform.platform():
            self.platform = "macOS/stockfish"
        print("lit/" + self.engine + "/" + self.platform)
        if self.ai_vs_ai:
            try:
                self.stockfish = Stockfish(
                    "lit/" + self.engine + "/" + self.platform,
                    depth=99,
                    parameters={
                        "Threads": 6,
                        "Minimum Thinking Time": 100,
                        "Hash": 64,
                        "Skill Level": 20,
                        "UCI_Elo": 3000,
                    },
                )
            except FileNotFoundError:
                print(
                    "Stockfish program located in '"
                    + "lit/"
                    + self.engine
                    + "/"
                    + self.platform
                    + "' is non respondent please install stockfish here: https://stockfishchess.org/download/"
                )
                sys.exit(0)
        else:
            try:
                self.stockfish = Stockfish(
                    "lit/" + self.engine + "/" + self.platform,
                    depth=1,
                    parameters={
                        "Threads": 1,
                        "Minimum Thinking Time": 1,
                        "Hash": 2,
                        "Skill Level": 0.001,
                        "UCI_LimitStrength": "true",
                        "UCI_Elo": 0,
                    },
                )
            except FileNotFoundError:
                print(
                    "Stockfish program located in '"
                    + "lit/"
                    + self.engine
                    + "/"
                    + self.platform
                    + "' is non respondent please install stockfish here: https://stockfishchess.org/download/"
                )
                sys.exit(0)
        self.stockfish.set_fen_position(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        self.ai_strength = 0

        # self.engine_ = chess.engine.SimpleEngine.popen_uci('lit/stockfish/Windows/stockfish.exe')
        self.game = chess.pgn.Game()

        if self.ai_vs_ai:
            self.game.headers["Event"] = "Computer Vs Computer"
            self.game.headers["Black"] = "Computer"
            self.game.headers["White"] = "Computer"
        elif self.player_vs_ai:
            self.game.headers["Event"] = "Player Vs Computer"
            self.game.headers["Black"] = "Computer"
            self.game.headers["White"] = "Player"
        else:
            self.game.headers["Event"] = "Player Vs Player"
            self.game.headers["Black"] = "Player"
            self.game.headers["White"] = "Player"

        self.game.headers["Site"] = "UK"
        self.game.headers["WhiteElo"] = "?"
        self.game.headers["BlackElo"] = "?"
        self.game.headers["Date"] = (
            str(datetime.datetime.now().year)
            + "/"
            + str(datetime.datetime.now().month)
            + "/"
            + str(datetime.datetime.now().day)
        )

        self.piece_type = "chessmonk"
        self.board_style = "marble.png"

        self.screen = pg.display.set_mode(
            (
                pg.display.get_desktop_sizes()[0][1] - 70,
                pg.display.get_desktop_sizes()[0][1] - 70,
            ),
            pg.RESIZABLE,
            vsync=1,
        )
        self.settings = SettingsMenu(
            title="Settings",
            width=self.screen.get_width(),
            height=self.screen.get_height(),
            surface=self.screen,
            parent=self,
            theme=pm.themes.THEME_DARK,
        )
        # "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        icon = pg.image.load("data/img/pieces/cardinal/bk.png").convert_alpha()
        pg.display.set_icon(icon)
        (
            self.board,
            self.turn,
            self.castle_rights,
            self.en_passant_square,
            self.halfmoves_since_last_capture,
            self.fullmove_number,
        ) = parse_FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.game_fens = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
        self.black_pieces = pg.sprite.Group()
        self.white_pieces = pg.sprite.Group()
        self.all_pieces = pg.sprite.Group()

        self.map = []
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece != " ":
                    self.all_pieces.add(piece)
                    if piece.colour == "black":
                        self.black_pieces.add(piece)
                    else:
                        self.white_pieces.add(piece)

        self.size = int((pg.display.get_window_size()[1] - 200) / 8)
        self.default_size = int(pg.display.get_window_size()[1] - 200 / 8)
        self.font = pg.font.SysFont("segoescript", 30)
        self.updates = False
        self.arrow_colour = (252, 177, 3)
        self.colours = [(118, 150, 86), (238, 238, 210)]
        # self.colours = [(50, 50, 50), (255, 255, 255)]
        self.colours2 = [(150, 86, 86), (238, 215, 210)]
        self.colours3 = [(186, 202, 68), (255, 251, 171)]
        self.colours4 = [(252, 111, 76), (252, 137, 109)]
        self.tx = None
        self.ty = None
        self.txr = None
        self.tyr = None
        self.left = False
        self.background = pg.image.load("data/img/background_dark.png").convert()
        self.background = pg.transform.smoothscale(
            self.background,
            (pg.display.get_window_size()[0], pg.display.get_window_size()[1]),
        )
        self.board_background = pg.image.load(
            "data/img/boards/" + self.board_style
        ).convert()
        self.board_background = pg.transform.smoothscale(
            self.board_background, (self.size * 8, self.size * 8)
        )
        self.offset = [
            pg.display.get_window_size()[0] / 2 - 4 * self.size,
            pg.display.get_window_size()[1] / 2 - 4 * self.size,
        ]
        # self.update_board()
        self.update_legal_moves()
        self.prev_board = self.board
        self.debug = False
        self.node = self.game
        self.show_numbers = True
        if EVAL_ON:
            self.get_eval()
        self.clock = pg.time.Clock()
        self.settings.confirm()
        # print(self.board)

    def run(self) -> None:
        self.draw_board()
        # print(self.last_move)
        # print(self.all_pieces)
        if self.puzzle_mode:
            self.display_puzzle(self.puzzle_fen)
        else:
            if self.updates:
                self.update_board()
            piece_active = None
            for piece in self.all_pieces:
                # print(piece)
                if piece.clicked:
                    piece_active = piece
                    break
            if piece_active is not None:
                self.draw_pieces(piece_active)
            else:
                self.draw_pieces()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.game_just_ended = False
                    if event.button == 1 and not self.game_just_ended:
                        self.left = True
                        self.click_left()
                    elif event.button == 3:
                        self.click_right()
                    elif event.button == 4 or event.button == 5:
                        self.flip_board()
                elif event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1 and self.updates:
                        self.left = False
                        self.un_click_left()
                    elif event.button == 1:
                        self.left = False
                    elif event.button == 2:
                        if len(self.game_fens) > 1:
                            self.undo_move(False)
                            self.un_click_right(False)
                        elif len(self.game_fens) == 1:
                            self.undo_move(True)
                            self.un_click_right(False)
                    elif event.button == 3 and not self.left:
                        self.un_click_right(True)
                    elif event.button == 3:
                        self.updates_kill()
                        self.left = False
                    self.updates = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_m:
                        navigation.open_main_menu()
                        return
                    if event.key == pg.K_s and pg.key.get_mods() & pg.KMOD_CTRL:
                        self.end_game("Game saved and Reset")
                    if event.key == pg.K_f and pg.key.get_mods() & pg.KMOD_CTRL:
                        print(self.game_fens[-1])
                    if event.key == pg.K_e and pg.key.get_mods() & pg.KMOD_CTRL:
                        self.evaluation = self.get_eval()
                    if event.key == pg.K_r and pg.key.get_mods() & pg.KMOD_CTRL:
                        self.flip_board()
                    if event.key == pg.K_h and pg.key.get_mods() & pg.KMOD_CTRL:
                        self.stockfish.set_skill_level(20)
                        self.best_move = str(self.stockfish.get_best_move_time(200))
                        self.stockfish.set_skill_level(self.ai_strength)
                    if event.key == pg.K_u:
                        if len(self.game_fens) > 1:
                            self.undo_move(False)
                            self.un_click_right(False)
                        elif len(self.game_fens) == 1:
                            self.undo_move(True)
                            self.un_click_right(False)
                    if event.key == pg.K_ESCAPE:
                        self.settings.run()
                elif event.type == pg.VIDEORESIZE:
                    # There's some code to add back window content here.
                    self.screen = pg.display.set_mode(
                        (event.w, event.h), pg.RESIZABLE, vsync=1
                    )
                    self.settings.resize_event()
                    self.background = pg.image.load(
                        "data/img/background_dark.png"
                    ).convert()
                    self.background = pg.transform.smoothscale(
                        self.background,
                        (
                            pg.display.get_window_size()[0],
                            pg.display.get_window_size()[1],
                        ),
                    )
                    self.board_background = pg.image.load(
                        "data/img/boards/" + self.board_style
                    ).convert()
                    if (
                        self.default_size >= pg.display.get_window_size()[1]
                        or self.default_size >= pg.display.get_window_size()[0]
                    ):
                        self.show_numbers = False
                        if (
                            pg.display.get_window_size()[0]
                            < pg.display.get_window_size()[1]
                        ):
                            self.size = int((pg.display.get_window_size()[0]) / 8)
                        else:
                            self.size = int((pg.display.get_window_size()[1]) / 8)
                    elif (
                        self.default_size
                        < pg.display.get_window_size()[1]
                        < self.default_size + 200
                    ) or (
                        self.default_size
                        < pg.display.get_window_size()[0]
                        < self.default_size + 1000
                    ):
                        self.show_numbers = True
                        if (
                            pg.display.get_window_size()[0]
                            < pg.display.get_window_size()[1]
                        ):
                            self.size = int((pg.display.get_window_size()[0] - 200) / 8)
                        else:
                            self.size = int((pg.display.get_window_size()[1] - 200) / 8)
                    else:
                        self.show_numbers = True
                    if self.size <= 1:
                        self.size = 1
                    self.board_background = pg.transform.smoothscale(
                        self.board_background, (self.size * 8, self.size * 8)
                    )
                    self.offset = [
                        pg.display.get_window_size()[0] / 2 - 4 * self.size,
                        pg.display.get_window_size()[1] / 2 - 4 * self.size,
                    ]

            if self.ai_vs_ai:
                self.un_click_left()
            pg.display.flip()
            self.clock.tick(150)

    def get_eval(self) -> str:
        """
        Get board evaluation
        :return: Evaluation string
        """
        print(self.game_fens)
        self.stockfish.set_depth(20)
        eve = print_eval(self.stockfish.get_evaluation())
        self.stockfish.set_depth(99)
        return eve

    @timeit
    def un_click_left(self) -> None:
        """
        Left click release event logic. Calls make_move which makes a move if it is legal
        :return: None
        """
        self.highlighted.clear()
        self.arrows.clear()
        if self.ai_vs_ai:
            self.ai_make_move(0, 0, 0)
            if EVAL_ON:
                self.get_eval()
        else:
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] != " ":
                        if self.board[row][col].clicked:
                            # Make move if legal
                            if self.board[row][col].make_move(
                                self.board,
                                self.offset,
                                self.turn,
                                self.flipped,
                                None,
                                None,
                            ):
                                x = int(
                                    (pg.mouse.get_pos()[0] - self.offset[0])
                                    // self.size
                                )
                                y = int(
                                    (pg.mouse.get_pos()[1] - self.offset[1])
                                    // self.size
                                )
                                if self.flipped:
                                    x = -x + 7
                                    y = -y + 7
                                if self.turn == "w":
                                    self.fun += 1
                                    if self.fun == 2:
                                        self.turn = "b"
                                        self.fun = 0
                                    move = translate_move(row, col, y, x)
                                    if self.board[row][col] != " ":
                                        if self.board[row][col].piece == "P":
                                            if y == 0:
                                                move += "q"
                                    self.last_move.append(move)
                                    self.node = self.node.add_variation(
                                        chess.Move.from_uci(move)
                                    )
                                else:
                                    self.fullmove_number += 1
                                    self.fun += 1
                                    if self.fun == 2:
                                        self.turn = "w"
                                        self.fun = 0
                                    if not self.player_vs_ai:
                                        move = translate_move(row, col, y, x)
                                        if self.board[row][col] != " ":
                                            if self.board[row][col].piece == "p":
                                                if y == 7:
                                                    move += "q"

                                        self.last_move.append(move)
                                        self.node = self.node.add_variation(
                                            chess.Move.from_uci(move)
                                        )

                                self.moved()
                                if self.board[y][x] != " ":
                                    self.board[y][x].clicked = False
                                if EVAL_ON:
                                    self.get_eval()
                                if self.player_vs_ai:
                                    self.ai_make_move(y, row, col)
                                    if EVAL_ON:
                                        self.get_eval()
                            else:
                                self.board[row][col].clicked = False
                            break

    # Rest of the game logic remains unchanged

    def change_pieces(self, piece_type: str) -> None:
        """
        Changes the piece style.
        :param piece_type: string name of the piece type.
        :return: None
        """
        self.piece_type = piece_type
        for piece in self.all_pieces:
            piece.change_type(piece_type)

    def change_board(self, board_type):
        """
        Changes the Board style.
        :param board_type: filename of the board located in 'data/img/boards/'
        :return: None
        """
        self.board_style = board_type
        self.board_background = pg.image.load(
            "data/img/boards/" + self.board_style
        ).convert()
        self.board_background = pg.transform.smoothscale(
            self.board_background, (self.size * 8, self.size * 8)
        )

    def check_resize(self):
        """
        Checks if the window has been resized and handles resizing
        :return: None
        """
        self.screen = pg.display.set_mode(
            (self.screen.get_width(), self.screen.get_height()), pg.RESIZABLE, vsync=1
        )
        self.background = pg.image.load("data/img/background_dark.png").convert()
        self.background = pg.transform.smoothscale(
            self.background,
            (pg.display.get_window_size()[0], pg.display.get_window_size()[1]),
        )
        self.board_background = pg.image.load(
            "data/img/boards/" + self.board_style
        ).convert()
        if (
            self.default_size >= pg.display.get_window_size()[1]
            or self.default_size >= pg.display.get_window_size()[0]
        ):
            self.show_numbers = False
            if pg.display.get_window_size()[0] < pg.display.get_window_size()[1]:
                self.size = int((pg.display.get_window_size()[0]) / 8)
            else:
                self.size = int((pg.display.get_window_size()[1]) / 8)
        elif (
            self.default_size
            < pg.display.get_window_size()[1]
            < self.default_size + 200
        ) or (
            self.default_size
            < pg.display.get_window_size()[0]
            < self.default_size + 1000
        ):
            self.show_numbers = True
            if pg.display.get_window_size()[0] < pg.display.get_window_size()[1]:
                self.size = int((pg.display.get_window_size()[0] - 200) / 8)
            else:
                self.size = int((pg.display.get_window_size()[1] - 200) / 8)
        else:
            self.show_numbers = True
        if self.size <= 1:
            self.size = 1
        self.board_background = pg.transform.smoothscale(
            self.board_background, (self.size * 8, self.size * 8)
        )
        self.offset = [
            pg.display.get_window_size()[0] / 2 - 4 * self.size,
            pg.display.get_window_size()[1] / 2 - 4 * self.size,
        ]

    def change_mode(self, mode: str):
        """
        Changes the game mode to Player vs Player, Player vs AI, or AI vs AI
        :param mode: String of the mode: 'pvp', 'pvai', or 'aivai'
        :return: None
        """
        if mode == "pvp":
            self.ai_vs_ai = False
            self.player_vs_ai = False
        elif mode == "aivai":
            self.ai_vs_ai = True
            self.player_vs_ai = False
        elif mode == "pvai":
            self.ai_vs_ai = False
            self.player_vs_ai = True

    def ai_make_move(self, y: int, row: int, col: int):
        """
        :param y: the moves column number; For promotion logic
        :param row: Row position of the piece to move
        :param col: Column position of the piece to move
        :return: None
        """
        # Engine Moves
        self.draw_board()
        self.draw_pieces()
        pg.display.flip()
        time.sleep(0.15)
        move = self.move_strength(self.ai_strength)
        if move is not None:
            self.last_move.append(move)
            if self.board[row][col] != " ":
                if self.board[row][col].piece == "p":  # auto promote queen
                    if y == 7 or y == 0:
                        move += "q"
            self.node = self.node.add_variation(chess.Move.from_uci(move))
            self.engine_make_move(move)  # Making the move
        else:
            print("Fault")
            self.end_game("Fault")
            self.reset_game()

    def move_strength(self, strength: int) -> str | None:
        """
        Get the best move given the strength input
        :param strength: the strength of the move to be generated
        :return: Move - the algebraic notation of the move as a string
        """
        # return moves[0]["Move"]
        if self.ai_vs_ai:
            if self.turn == "w":
                # self.stockfish.set_skill_level(20)
                a = 15 * (strength + 1)
            else:
                # self.stockfish.set_skill_level(1)
                a = 15 * (strength + 1)
        else:
            a = random.randint(2, 5)
        move = self.stockfish.get_best_move_time(a)
        return move

    def change_ai_strength(self, num: int) -> None:
        """
        Set skill level of the AI
        :param num: strength of the AI from 0-20
        :return: None
        """
        self.ai_strength = num
        self.stockfish.set_skill_level(num)

    def un_click_right(self, left_click: bool) -> None:
        """
        Handle right unclick event. Used for highlights and arrows
        :param left_click: is currently clicking left?
        :return: None
        """
        txr = int((pg.mouse.get_pos()[0] - self.offset[0]) // self.size)
        tyr = int((pg.mouse.get_pos()[1] - self.offset[1]) // self.size)
        if self.flipped:
            txr = 7 - txr
            tyr = 7 - tyr
        if left_click:
            if self.txr == txr and self.tyr == tyr:
                if (tyr, txr) in self.highlighted:
                    self.highlighted.remove((tyr, txr))
                else:
                    self.highlighted.append((tyr, txr))
            else:
                if ((self.tyr, self.txr), (tyr, txr)) in self.arrows:
                    self.arrows.remove(((self.tyr, self.txr), (tyr, txr)))
                else:
                    if (
                        -1 < self.txr < 8
                        and -1 < self.tyr < 8
                        and -1 < txr < 8
                        and -1 < tyr < 8
                    ):
                        self.arrows.append(((self.tyr, self.txr), (tyr, txr)))

        for pieces in self.all_pieces:
            pieces.clicked = False

    def updates_kill(self) -> None:
        """
        kill updating the clicked pieces. used to unclick all pieces
        :return: None
        """
        self.updates = False
        for pieces in self.all_pieces:
            pieces.clicked = False
        self.left = False

    def moved(self) -> None:
        """
        Called after make_move to update legal moves,
        check for the end of game, and play sounds
        :return: None
        """
        self.prev_board = self.board
        eps_moved_made = False
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece != " ":
                    if piece.position != (i, j):
                        # piece no longer on the square of the board
                        self.board[i][j] = " "

                        # has a pawn moved 2 squares. en-passant check
                        if (
                            piece.piece.lower() == "p"
                            and piece.position[0] - i == 2 * piece.direction
                        ):
                            self.en_passant_square = str(
                                (
                                    piece.position[0]
                                    + int((piece.position[0] - i) / 2),
                                    piece.position[1],
                                )
                            )
                        else:
                            self.en_passant_square = "-"

                        # has a pawn been captured with enpassant
                        if piece.piece.lower() == "p":
                            if piece.position[0] - i == piece.direction and (
                                piece.position[1] - j == 1
                                or piece.position[1] - j == -1
                            ):
                                if (
                                    self.board[piece.position[0]][piece.position[1]]
                                    == " "
                                ):
                                    eps_moved_made = True
                                    self.board[piece.position[0] - piece.direction][
                                        piece.position[1]
                                    ].dead = True
                                    self.board[piece.position[0] - piece.direction][
                                        piece.position[1]
                                    ] = " "

                        # king has castled
                        castle = False
                        if piece.piece.lower() == "k":
                            if (
                                piece.position[1] - j == 2
                                or piece.position[1] - j == -2
                            ):
                                castle = True
                                if piece.position[1] < 4:
                                    self.board[piece.position[0]][3] = self.board[
                                        piece.position[0]
                                    ][0]
                                    self.board[piece.position[0]][0] = " "
                                    self.board[piece.position[0]][3].position = (
                                        piece.position[0],
                                        3,
                                    )
                                else:
                                    self.board[piece.position[0]][5] = self.board[
                                        piece.position[0]
                                    ][7]
                                    self.board[piece.position[0]][7] = " "
                                    self.board[piece.position[0]][5].position = (
                                        piece.position[0],
                                        5,
                                    )

                        piece_sound = self.board[piece.position[0]][piece.position[1]]

                        # update the board
                        if self.board[piece.position[0]][piece.position[1]] != " ":
                            self.board[piece.position[0]][piece.position[1]].dead = True
                        self.board[piece.position[0]][piece.position[1]] = piece

                        # promotion
                        promote = False
                        if piece.piece.lower() == "p":
                            if piece.position[0] == int(3.5 + piece.direction * 3.5):
                                self.promotion(piece)
                                promote = True

                        if (castle or promote) and self.sound_enabled:
                            pg.mixer.music.load("data/sounds/castle.mp3")
                            pg.mixer.music.play(1)
                        elif (
                            piece_sound == " "
                            and not eps_moved_made
                            and self.sound_enabled
                        ):
                            pg.mixer.music.load("data/sounds/move.mp3")
                            pg.mixer.music.play(1)
                        elif self.sound_enabled:
                            pg.mixer.music.load("data/sounds/capture.mp3")
                            pg.mixer.music.play(1)

                        break
        for p in self.all_pieces:
            if p.dead:
                self.all_pieces.remove(p)
        for p in self.black_pieces:
            if p.dead:
                self.black_pieces.remove(p)
        for p in self.white_pieces:
            if p.dead:
                self.white_pieces.remove(p)

        # update next players legal moves
        if self.update_legal_moves() and self.sound_enabled:
            pg.mixer.music.load("data/sounds/check.aiff")
            pg.mixer.music.play(1)

        legal_moves = self.count_legal_moves()
        # print('Number of legal moves', legal_moves)
        # print FEN notation of position
        self.game_fens.append(
            create_FEN(
                self.board,
                self.turn,
                self.castle_rights,
                self.en_passant_square,
                self.fullmove_number,
            )
        )
        self.stockfish.set_fen_position(self.game_fens[-1])
        # print(self.game_fens[-1])
        if not self.player_vs_ai and not self.ai_vs_ai and self.flip_enabled:
            self.flip_board()

        if self.node.board().is_repetition():
            if self.sound_enabled:
                pg.mixer.music.load("data/sounds/mate.wav")
                pg.mixer.music.play(1)
                time.sleep(0.15)
                pg.mixer.music.play(1)
            self.end_game("DRAW BY REPETITION")
        elif self.node.board().is_stalemate():
            if self.sound_enabled:
                pg.mixer.music.load("data/sounds/mate.wav")
                pg.mixer.music.play(1)
                time.sleep(0.15)
                pg.mixer.music.play(1)
            self.end_game("INSUFFICIENT MATERIAL")
        elif self.node.board().is_insufficient_material():
            if self.sound_enabled:
                pg.mixer.music.load("data/sounds/mate.wav")
                pg.mixer.music.play(1)
                time.sleep(0.15)
                pg.mixer.music.play(1)
            self.end_game("INSUFFICIENT MATERIAL")
        elif self.node.board().is_checkmate() or legal_moves == 0:
            if self.sound_enabled:
                pg.mixer.music.load("data/sounds/mate.wav")
                pg.mixer.music.play(1)
                time.sleep(0.15)
                pg.mixer.music.play(1)
            if self.node.board().outcome().winner:
                self.end_game("CHECKMATE WHITE WINS !!")
            else:
                self.end_game("CHECKMATE BLACK WINS !!")
        # pprint(self.board, indent=3)

    def end_game(self, end_text: str) -> None:
        """
        Called when the game has ended. Saves the game in 'data/games/' and displays the end game menu
        :param end_text: string of the end of match. i.e. "Checkmate White Wins!"
        :return: None
        """
        self.game_just_ended = True
        dt = datetime.datetime.now()
        dt = dt.strftime("%Y%m%d_%H%M%S_%f")
        print(self.game, file=open("data/games/" + dt + ".pgn", "w"), end="\n\n")
        game_str = str(self.game)
        time.sleep(1)
        self.reset_game()

        # End game screen
        self.end_game_menu = EndGameMenu(
            title="Game Over",
            width=self.screen.get_width(),
            height=self.screen.get_height(),
            surface=self.screen,
            parent=self,
            theme=pm.themes.THEME_DARK,
        )
        self.end_game_menu.set_file_path_and_text("data/games/" + dt + ".pgn", end_text)
        self.end_game_menu.run()

    def reset_game(self) -> None:
        """
        Resets the game to the starting FEN position
        :return: None
        """
        self.updates_kill()
        (
            self.board,
            self.turn,
            self.castle_rights,
            self.en_passant_square,
            self.halfmoves_since_last_capture,
            self.fullmove_number,
        ) = parse_FEN(self.game_fens[0])
        self.game_fens = [self.game_fens[0]]
        for p in self.all_pieces:
            self.all_pieces.remove(p)
        for p in self.black_pieces:
            self.black_pieces.remove(p)
        for p in self.white_pieces:
            self.white_pieces.remove(p)
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                try:
                    if piece != " ":
                        self.all_pieces.add(piece)
                        if piece.colour == "black":
                            self.black_pieces.add(piece)
                        else:
                            self.white_pieces.add(piece)
                except:
                    pass
        for piece in self.all_pieces:
            piece.change_type(self.piece_type)
            piece.clicked = False
        self.last_move = []
        self.game = chess.pgn.Game()
        self.game.headers["Event"] = "Player Vs Computer"
        self.game.headers["Site"] = "UK"
        self.game.headers["Date"] = (
            str(datetime.datetime.now().year)
            + "/"
            + str(datetime.datetime.now().month)
            + "/"
            + str(datetime.datetime.now().day)
        )
        if self.ai_vs_ai:
            self.game.headers["Event"] = "Computer Vs Computer"
            self.game.headers["Black"] = "Computer"
            self.game.headers["White"] = "Computer"
        elif self.player_vs_ai:
            self.game.headers["Event"] = "Player Vs Computer"
            self.game.headers["Black"] = "Computer"
            self.game.headers["White"] = "Player"
        else:
            self.game.headers["Event"] = "Player Vs Player"
            self.game.headers["Black"] = "Player"
            self.game.headers["White"] = "Player"

        self.game.headers["WhiteElo"] = "?"
        self.game.headers["BlackElo"] = "?"
        self.node = self.game
        self.stockfish.set_fen_position(self.game_fens[0])
        self.update_legal_moves()

    def undo_move(self, one: bool) -> None:
        """
        Undo last move, and update legal moves
        :param one: Is the length of the game ONLY ONE move?
        :return: None
        """
        if len(self.last_move) > 0:
            if one:
                (
                    self.board,
                    self.turn,
                    self.castle_rights,
                    self.en_passant_square,
                    self.halfmoves_since_last_capture,
                    self.fullmove_number,
                ) = parse_FEN(self.game_fens[0])
            else:
                self.game_fens.pop()
                (
                    self.board,
                    self.turn,
                    self.castle_rights,
                    self.en_passant_square,
                    self.halfmoves_since_last_capture,
                    self.fullmove_number,
                ) = parse_FEN(self.game_fens[-1])
            for p in self.all_pieces:
                self.all_pieces.remove(p)
            for p in self.black_pieces:
                self.black_pieces.remove(p)
            for p in self.white_pieces:
                self.white_pieces.remove(p)
            for i, row in enumerate(self.board):
                for j, piece in enumerate(row):
                    try:
                        if piece != " ":
                            self.all_pieces.add(piece)
                            if piece.colour == "black":
                                self.black_pieces.add(piece)
                            else:
                                self.white_pieces.add(piece)
                    except:
                        pass
            for piece in self.all_pieces:
                piece.change_type(self.piece_type)
            self.last_move.pop()
            self.node = (
                self.node.parent
            )  # allows for undoes to show in analysis on https://chess.com/analysis
            if not self.player_vs_ai and not self.ai_vs_ai and self.flip_enabled:
                self.flip_board()

            self.update_board()
            self.update_legal_moves()

    # @timeit
    def update_legal_moves(self) -> bool:
        """
        Update the all legal moves
        :return: True if in check, false if not in check
        """
        castle = []
        in_check = False
        for piece in self.all_pieces:
            if piece.piece.lower() == "k":
                if not piece.has_moved:
                    castle.append(piece.colour)
            if piece.colour[0] == self.turn:
                piece.update_legal_moves(
                    self.board, self.en_passant_square, captures=False
                )
            else:
                if piece.piece.lower() in ["b", "r", "q", "n", "p"]:
                    if piece.check(self.board):
                        in_check = True
                if piece.piece.lower() in ["b", "r", "q"]:
                    piece.pin_line_update(self.board)

        self.handle_fen_castle(castle)

        if self.turn == "w":
            self.map = self.create_map(self.black_pieces)
        else:
            self.map = self.create_map(self.white_pieces)

        # if in_check:
        if self.turn == "w":
            for piece in self.white_pieces:
                piece.trim_checks(self.board, self.turn, self.map, in_check)
        else:
            for piece in self.black_pieces:
                piece.trim_checks(self.board, self.turn, self.map, in_check)

        if self.turn == "w":
            for piece in self.black_pieces:
                if piece.piece.lower() in ["b", "r", "q"]:
                    piece.trim_pin_moves(self.board)
        else:
            for piece in self.white_pieces:
                if piece.piece.lower() in ["b", "r", "q"]:
                    piece.trim_pin_moves(self.board)
        return in_check

    def make_move_board(self, move: tuple, piece: Piece) -> None:
        """
        Make the move on the board, and call "piece.make_move()" and "moved()" to handle sounds and end game checks
        :param move: square the piece is moving to
        :param piece: The piece that is moving
        :return: None
        """
        if self.board[piece.position[0]][piece.position[1]].make_move(
            self.board,
            self.offset,
            self.turn,
            self.flipped,
            piece.position[1] + move[0],
            piece.position[0] + move[1],
        ):
            if self.turn == "w":
                self.turn = "b"
            else:
                self.fullmove_number += 1
                self.turn = "w"
            self.moved()
            self.board[piece.position[0]][piece.position[1]].clicked = False

    def engine_make_move(self, move: str) -> None:
        """
        Engine makes the move. Used for AI moves where move notation is for example "a2a4" or "f1e3".
        This function is similar to "make_move_board".
        :param move: Move to make. e.g. "a2a4" or "f1e3"
        :return: None
        """
        try:
            square1 = square_on(move[0:2])
            square2 = square_on(move[2:4])
            the_move = (square2[0] - square1[0], square2[1] - square1[1])
            piece = self.board[square1[0]][square1[1]]
            if piece.make_move(
                self.board,
                self.offset,
                self.turn,
                self.flipped,
                piece.position[1] + the_move[1],
                piece.position[0] + the_move[0],
            ):
                if self.turn == "w":
                    self.turn = "b"
                else:
                    self.fullmove_number += 1
                    self.turn = "w"
                self.moved()
                self.board[piece.position[0]][piece.position[1]].clicked = False

        except:
            pass

    def create_map(self, pieces: list[Piece]) -> list[tuple]:
        """
        Returns a list of squares the pieces attack
        :param pieces: list of pieces to check attacking squares
        :return: list of the attacked squares
        """
        map = set()
        for piece in pieces:
            piece.update_legal_moves(self.board, "-", captures=True)
            for move in piece.legal_positions:
                map.add((piece.position[0] + move[1], piece.position[1] + move[0]))
        return list(map)

    def count_legal_moves(self) -> int:
        """
        Get the number of legal moves
        :return: Number of legal moves
        """
        count = 0
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece != " ":
                    if piece.colour[0] == self.turn:
                        count += len(piece.legal_positions)
        return count

    def promotion(self, piece: Piece) -> None:
        """
        Promote the given piece to a queen
        :param piece: A piece to promote
        :return: None
        """
        self.all_pieces.remove(piece)
        self.board[piece.position[0]][piece.position[1]] = Queen(
            position=(piece.position[0], piece.position[1]),
            colour=piece.colour,
            piece_type=self.piece_type,
        )
        self.all_pieces.add(self.board[piece.position[0]][piece.position[1]])
        if piece.colour == "black":
            self.black_pieces.remove(piece)
            self.black_pieces.add(self.board[piece.position[0]][piece.position[1]])
        else:
            self.white_pieces.remove(piece)
            self.white_pieces.add(self.board[piece.position[0]][piece.position[1]])

    def handle_fen_castle(self, castle: list[str]) -> None:
        """
        Update castle rights
        :param castle: either ["black", "white"], ["black"], or ["white"]
        :return: None
        """
        if "black" in castle and "white" in castle:
            self.castle_rights = "KQkq"
        elif "black" in castle:
            self.castle_rights = "kq"
        elif "white" in castle:
            self.castle_rights = "KQ"
        else:
            self.castle_rights = "-"

        try:
            if self.board[0][0] == " " and "q" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("q", "")
            elif self.board[0][0].piece != "r" and "q" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("q", "")
            elif (
                self.board[0][0].piece == "r"
                and self.board[0][0].has_moved
                and "q" in self.castle_rights
            ):
                self.castle_rights = self.castle_rights.replace("q", "")
        except:
            pass
        try:
            if self.board[0][7] == " " and "k" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("k", "")
            elif self.board[0][7].piece != "r" and "k" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("k", "")
            elif (
                self.board[0][7].piece == "r"
                and self.board[0][7].has_moved
                and "k" in self.castle_rights
            ):
                self.castle_rights = self.castle_rights.replace("k", "")
        except:
            pass
        try:
            if self.board[7][0] == " " and "Q" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("Q", "")
            elif self.board[7][0].piece != "R" and "Q" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("Q", "")
            elif (
                self.board[7][0].piece == "R"
                and self.board[7][0].has_moved
                and "Q" in self.castle_rights
            ):
                self.castle_rights = self.castle_rights.replace("Q", "")
        except:
            pass
        try:
            if self.board[7][7] == " " and "K" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("K", "")
            elif self.board[7][7].piece != "R" and "K" in self.castle_rights:
                self.castle_rights = self.castle_rights.replace("K", "")
            elif (
                self.board[7][7].piece == "R"
                and self.board[7][7].has_moved
                and "K" in self.castle_rights
            ):
                self.castle_rights = self.castle_rights.replace("K", "")
        except:
            pass

        if self.castle_rights == "":
            self.castle_rights = "-"

    def click_right(self) -> None:
        """
        handle Right click event. Stores the co-ordinates of the click. Used for highlighting and arrows
        :return: None
        """
        self.txr = int((pg.mouse.get_pos()[0] - self.offset[0]) // self.size)
        self.tyr = int((pg.mouse.get_pos()[1] - self.offset[1]) // self.size)
        if self.flipped:
            self.txr = 7 - self.txr
            self.tyr = 7 - self.tyr

    def click_left(self) -> None:
        """
        Handle left click event. Stores co-ordinates of mouse and sets updates to true to enable drawing of clicked piece.
        :return: None
        """
        self.tx = int((pg.mouse.get_pos()[0] - self.offset[0]) // self.size)
        self.ty = int((pg.mouse.get_pos()[1] - self.offset[1]) // self.size)
        self.updates = True

    def update_board(self) -> None:
        """
        If currently clicking a piece then update the pieces positions
        :return: None
        """
        try:
            if not self.flipped:
                if -1 < self.tx < 8 and -1 < self.ty < 8:
                    if self.board[self.ty][self.tx] != " ":
                        self.board[self.ty][self.tx].update(
                            self.screen,
                            self.offset,
                            self.turn,
                            self.flipped,
                            self.board,
                        )
            else:
                if -1 < self.tx < 8 and -1 < self.ty < 8:
                    if self.board[-self.ty + 7][-self.tx + 7] != " ":
                        self.board[-self.ty + 7][-self.tx + 7].update(
                            self.screen,
                            self.offset,
                            self.turn,
                            self.flipped,
                            self.board,
                        )
        except:
            pass

    def draw_board(self) -> None:
        """
        Draw the board, with highlighted squares and last moves. Draw numbers on the sides of the board.
        :return: None
        """

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.board_background, (self.offset[0], self.offset[1]))
        square1 = None
        square2 = None
        if len(self.last_move) > 1:
            square1 = square_on(self.last_move[-1][0:2])
            square2 = square_on(self.last_move[-1][2:4])
        elif len(self.last_move) == 1:
            square1 = square_on(self.last_move[0][0:2])
            square2 = square_on(self.last_move[0][2:4])
        count = 1
        for row in range(8):
            for col in range(8):
                if self.flipped:
                    row_new = -row + 7
                    col_new = -col + 7
                else:
                    row_new = row
                    col_new = col
                surface = pg.Surface((self.size, self.size))
                surface.set_alpha(200)
                if self.debug and (row_new, col_new) in self.map:
                    surface.fill(self.colours2[count % 2])
                    self.screen.blit(
                        surface,
                        (
                            self.offset[0] + self.size * col_new,
                            self.offset[1] + self.size * row_new,
                        ),
                    )
                else:
                    if (row, col) in self.highlighted:
                        surface.fill(self.colours4[count % 2])
                        self.screen.blit(
                            surface,
                            (
                                self.offset[0] + self.size * col_new,
                                self.offset[1] + self.size * row_new,
                            ),
                        )
                    else:
                        if len(self.last_move) != 0:
                            if (row, col) in [square1, square2]:
                                surface.fill(self.colours3[count % 2])
                                self.screen.blit(
                                    surface,
                                    (
                                        self.offset[0] + self.size * col_new,
                                        self.offset[1] + self.size * row_new,
                                    ),
                                )
                            else:
                                surface.fill(self.colours[count % 2])
                                self.screen.blit(
                                    surface,
                                    (
                                        self.offset[0] + self.size * col_new,
                                        self.offset[1] + self.size * row_new,
                                    ),
                                )
                        else:
                            surface.fill(self.colours[count % 2])
                            self.screen.blit(
                                surface,
                                (
                                    self.offset[0] + self.size * col_new,
                                    self.offset[1] + self.size * row_new,
                                ),
                            )
                count += 1
            count += 1

        # draw letters + numbers
        if self.show_numbers:
            for i in range(8):
                number = 8 - i
                if self.flipped:
                    number = -number + 9
                surface = self.font.render(str(number), False, (255, 255, 255))
                self.screen.blit(
                    surface,
                    (
                        self.offset[0] - self.size / 2,
                        self.offset[1] + self.size / 2 + self.size * i - 13,
                    ),
                )  # draw numbers
            for i in range(8):
                letter = board_letters[i]
                if self.flipped:
                    letter = board_letters[7 - i]
                surface = self.font.render(str(letter), False, (255, 255, 255))
                self.screen.blit(
                    surface,
                    (
                        self.offset[0] + self.size / 2 - 8 + self.size * i,
                        self.offset[1] + 17 * self.size / 2 - 25,
                    ),
                )  # draw letters
            surface = self.font.render("Settings = ESC", False, (255, 255, 255))
            self.screen.blit(surface, (20, 20))
            if self.evaluation != "":
                surface = self.font.render(self.evaluation, False, (255, 255, 255))
                self.screen.blit(
                    surface, (self.screen.get_width() / 2 - surface.get_width() / 2, 20)
                )

            if self.best_move != "":
                surface = self.font.render(
                    "Hint: " + self.best_move, False, (255, 255, 255)
                )
                self.screen.blit(
                    surface, (self.screen.get_width() - surface.get_width() - 10, 20)
                )

    def draw_pieces(self, piece_selected: Piece = None):
        """
        Draws all the pieces and the selected piece last so that it appears on top.
        Also draws the arrows.
        :param piece_selected:
        :return:
        """
        for piece in self.all_pieces:
            if piece != piece_selected:
                piece.draw(self.offset, self.screen, self.size, self.flipped)

        # Draw the piece last, if it is being clicked/dragged
        if piece_selected is not None:
            piece_selected.draw(self.offset, self.screen, self.size, False)

        self.draw_arrows()

    def draw_arrows(self):
        off = (self.offset[0] + self.size / 2, self.offset[1] + self.size / 2)
        for start, end in self.arrows:
            surface = pg.Surface(
                (pg.display.get_window_size()[0], pg.display.get_window_size()[1]),
                pg.SRCALPHA,
            )
            surface.set_alpha(200)
            if self.flipped:
                pg.draw.line(
                    surface,
                    self.arrow_colour,
                    (
                        off[0] + self.size * (7 - start[1]),
                        off[1] + self.size * (7 - start[0]),
                    ),
                    (
                        off[0] + self.size * (7 - end[1]),
                        off[1] + self.size * (7 - end[0]),
                    ),
                    10,
                )
            else:
                pg.draw.line(
                    surface,
                    self.arrow_colour,
                    (off[0] + self.size * start[1], off[1] + self.size * start[0]),
                    (off[0] + self.size * end[1], off[1] + self.size * end[0]),
                    10,
                )
            self.screen.blit(surface, (0, 0))

    def flip_enable(self, value):
        if value == 1:
            self.flip_enabled = True
        else:
            self.flip_enabled = False

    def sounds_enable(self, value):
        if value == 1:
            self.sound_enabled = True
        else:
            self.sound_enabled = False

    def flip_board(self):
        self.flipped = not self.flipped

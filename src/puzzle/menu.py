
from .puzzle import Puzzle
import pygame as pg
import pygame_menu as pm
import navigation


fen_list = {
    "I":"r1bq1rk1/ppn1bppp/4pn2/1B6/2P5/5NB1/PP2QPPP/RN3RK1 w - - 1 0",
    "II":"r2b1rk1/pp3pp1/2n4p/q2N4/2B3b1/P4N2/1P2QPPP/R2R2K1 w - - 1 0",
    "III":"r2qr1k1/pb3ppp/1p3b2/3P4/3p2Q1/1P1B4/P2B1PPP/R3R1K1 w - - 1 0",
    "IV":"5rk1/5ppp/r1N2q2/p1PQ4/8/8/PbB2PPP/5RK1 w - - 1 0",
    "V":"3rk2r/pp3ppp/1n2p3/4q3/8/4B3/PP3PPP/R2QR1K1 w k - 1 0",
}


def puzzle_menu():
    # Initialize Pygame and create a surface
    pg.init()
    learn_surface = pg.display.set_mode((800,600))

    # Create a new Pygame Menu for learning options
    learn_menu = pm.Menu("Chess Puzzles", 800,600, theme=pm.themes.THEME_DARK)

    # Add options for different chess pieces or topics
    learn_menu.add.button("I", lambda: puzzle("I"))
    learn_menu.add.button("II", lambda: puzzle("II"))
    learn_menu.add.button("III", lambda: puzzle("III"))
    learn_menu.add.button("IV", lambda: puzzle("IV"))
    learn_menu.add.button("V", lambda: puzzle("V"))
    # ... Add more options as needed

    # Add a button to go back to the main menu
    learn_menu.add.button("Back to Main Menu", navigation.open_main_menu)

    # Run the learn menu
    learn_menu.mainloop(learn_surface)



# Functions for each learning topic
def puzzle(puzzle_no):
    puzz = Puzzle(fen_list[puzzle_no])
    while puzz:
        puzz.run()
        
navigation.open_puzzle_menu = puzzle_menu
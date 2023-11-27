
from .tut import Tutorial
import pygame as pg
import pygame_menu as pm


fen_list = {
    "R":"R7/8/8/8/8/8/8/8 w - - 0 1",
    "B":"B7/8/8/8/8/8/8/8 w - - 0 1",
    "P":"8/8/8/8/8/8/P7/8 w - - 0 1",
    "Q":"Q7/8/8/8/8/8/8/8 w - - 0 1",
    "K":"K7/8/8/8/8/8/8/8 w - - 0 1",
    "N":"N7/8/8/8/8/8/8/8 w - - 0 1",
}


def learn_chess():
    # Initialize Pygame and create a surface
    pg.init()
    learn_surface = pg.display.set_mode((600, 400))

    # Create a new Pygame Menu for learning options
    learn_menu = pm.Menu("Learn Chess", 600, 400, theme=pm.themes.THEME_DARK)

    # Add options for different chess pieces or topics
    learn_menu.add.button("Rook", learn_rook)
    learn_menu.add.button("Bishop", learn_bishop)
    learn_menu.add.button("Knight", learn_knight)
    learn_menu.add.button("King", learn_king)
    learn_menu.add.button("Queen", learn_queen)
    learn_menu.add.button("Pawn", learn_pawn)
    # ... Add more options as needed

    # Add a button to go back to the main menu
    # learn_menu.add.button("Back to Main Menu", main_menu)

    # Run the learn menu
    learn_menu.mainloop(learn_surface)

# Functions for each learning topic
def learn_rook():
    # Implement rook learning functionality
    run_tutorial = Tutorial(fen_list["R"])
    while True:
        run_tutorial.run()

def learn_bishop():
    run_tutorial = Tutorial(fen_list["B"])
    while True:
        run_tutorial.run()

def learn_pawn():
    run_tutorial = Tutorial(fen_list["P"])
    while True:
        run_tutorial.run()
def learn_queen():
    run_tutorial = Tutorial(fen_list["Q"])
    while True:
        run_tutorial.run()
def learn_king():
    run_tutorial = Tutorial(fen_list["K"])
    while True:
        run_tutorial.run()
def learn_knight():
    run_tutorial = Tutorial(fen_list["N"])
    while True:
        run_tutorial.run()

# ... Implement more functions as needed

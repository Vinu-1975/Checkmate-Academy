from .engine import Engine
from .engine2 import Engine2
import pygame as pg
import pygame_menu as pm
import navigation


fen_list = {
    "R": "R7/8/8/8/8/8/8/8 w - - 0 1",
    "B": "B7/8/8/8/8/8/8/8 w - - 0 1",
    "P": "8/8/8/8/8/8/P7/8 w - - 0 1",
    "Q": "Q7/8/8/8/8/8/8/8 w - - 0 1",
    "K": "K7/8/8/8/8/8/8/8 w - - 0 1",
    "N": "N7/8/8/8/8/8/8/8 w - - 0 1",
}


def modes_menu():
    # Initialize Pygame and create a surface
    pg.init()
    learn_surface = pg.display.set_mode((800,600))

    # Create a new Pygame Menu for learning options
    mode_menu = pm.Menu("Modes", 800,600, theme=pm.themes.THEME_DARK)

    # Add options for different chess pieces or topics
    mode_menu.add.button("Original Chess", original_chess)
    mode_menu.add.button("Double Dash Chess", double_dash_chess)
    # ... Add more options as needed

    # Add a button to go back to the main menu
    mode_menu.add.button("Back to Main Menu", navigation.open_main_menu)

    # Run the learn menu
    mode_menu.mainloop(learn_surface)

def original_chess():
    original = Engine()
    while True:
        original.run()

def double_dash_chess():
    ddc = Engine2()
    while True:
        ddc.run()

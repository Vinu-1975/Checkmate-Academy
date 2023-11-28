import timeit

import pygame as pg
import pygame_menu as pm

from src.engine.engine import Engine
# from tutorial.tut import Tutorial
from src.puzzle.puzzle import Puzzle
from src.tutorial.main import learn_chess
from src.functions.fen import parse_FEN
from src.puzzle.menu import puzzle_menu


# from src.puzzles.puzzle_extract import print_extracts

# All games are saved to data/games/ as a pgn file.


def start_game():
    engine = Engine()
    while True:
        engine.run()


def learn_chess_menu():
    learn_chess()
    

def solve_puzzles():
    # Implement puzzle solving functionality
    puzzle_menu()
    


def my_stats():
    # Implement statistics functionality
    pass


def main_menu():
    pg.init()
    surface = pg.display.set_mode((600, 400))
    menu = pm.Menu("Welcome", 600, 400, theme=pm.themes.THEME_DARK)

    menu.add.button("Play Chess", start_game)
    menu.add.button("Learn Chess", learn_chess)
    menu.add.button("Solve Chess Puzzles", solve_puzzles)
    menu.add.button("My Stats", my_stats)
    menu.add.button("Quit", pm.events.EXIT)

    menu.mainloop(surface)


if __name__ == "__main__":
    main_menu()

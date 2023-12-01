import timeit

import pygame as pg
import pygame_menu as pm

from src.engine.engine import Engine
from src.engine.modes import modes_menu

# from tutorial.tut import Tutorial
from src.puzzle.puzzle import Puzzle
from src.tutorial.main import learn_chess
from src.functions.fen import parse_FEN
import navigation
from src.puzzle.menu import puzzle_menu


# from src.puzzles.puzzle_extract import print_extracts

# All games are saved to data/games/ as a pgn file.


def start_game():
    modes_menu()


def learn_chess_menu():
    learn_chess()


def solve_puzzles():
    puzzle_menu()





class BackgroundTheme(pm.themes.Theme):
    def __init__(self, bg_image_path):
        super(BackgroundTheme, self).__init__()
        self.background_image = pg.image.load(bg_image_path)
        self.background_image = pg.transform.scale(self.background_image, (800,600))

    def draw_background(self, surface):
        surface.blit(self.background_image, (0, 0))


def main_menu():
    pg.init()
    surface = pg.display.set_mode((800,600))

    # Load background image
    bg_image = pg.image.load(
        "data/img/menu/bg3.png"
    ).convert()  # Use convert() for matching the display
    bg_image = pg.transform.scale(bg_image, (800,600))

    # Adjust these values as needed to ensure visibility over your background
    my_theme = pm.themes.Theme(
        background_color=(0, 0, 0, 0),  # Fully transparent
        title_background_color=(0, 0, 0, 0),
        title_font_color=(255, 255, 255),
        widget_font_color=(255, 255, 255),
    )

    menu = pm.Menu("Welcome", 800,600, theme=my_theme)

    menu.add.button("Play Chess", start_game)
    menu.add.button("Learn Chess", learn_chess)
    menu.add.button("Solve Chess Puzzles", solve_puzzles)
    menu.add.button("Quit", pm.events.EXIT)

    clock = pg.time.Clock()

    while True:
        # Handle events
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()

        # Blit the background image
        surface.blit(bg_image, (0, 0))

        # Draw the menu
        menu.update(events)
        menu.draw(surface)

        # Update the display
        pg.display.flip()
        clock.tick(60)  # Cap the frame rate


if __name__ == "__main__":
    navigation.open_main_menu = main_menu
    main_menu()

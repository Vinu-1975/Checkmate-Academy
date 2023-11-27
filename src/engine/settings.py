import os

import pygame_menu as pm
from pygame_menu.controls import Controller


class SettingsMenu(pm.menu.Menu):
    def __init__(self, surface, parent,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = surface
        self.o_size = self.screen.get_size()
        self.parent = parent
        custom_controller = Controller()
        custom_controller.apply = self.btn_apply
        self.back = self.add.button('Back', self.exit_menu, accept_kwargs=True, font_shadow=True,
                        font_shadow_color=(100, 100, 100), font_background_color=(255, 0, 0), cursor=11, font_color=(0, 0, 0))
        self.back.set_controller(custom_controller)
        view = self.add.button('View Controls', self.view_controls, accept_kwargs=True, font_shadow=True,
                        font_shadow_color=(100, 100, 100), font_background_color=(100, 100, 100), cursor=11,
                        font_color=(0, 0, 0))
        view.set_controller(custom_controller)
        self.pieces = [
            ('Alila', 'alila'),
            ('Alpha', 'alpha'),
            ('Cardinal', 'cardinal'),
            ('Chessicons', 'chessicons'),
            ('Chessmonk', 'chessmonk'),
            ('Dubrovny', 'dubrovny'),
            ('Gioco', 'gioco'),
            ('Horsey', 'horsey'),
            ('Kosal', 'kosal'),
            ('Maya', 'maya'),
            ('Metaltops', 'metaltops'),
            ('Pirouetti', 'pirouetti'),
            ('Regular', 'regular'),
            ('Riohacha', 'riohacha'),
            ('Staunty', 'staunty'),
            ('Tatiana', 'tatiana'),
        ]

        self.ai_strength = [
            ('0', 0),
            ('1', 1),
            ('2', 2),
            ('3', 3),
            ('4', 4),
            ('5', 5),
            ('6', 6),
            ('7', 7),
            ('8', 8),
            ('9', 9),
            ('10', 10),
            ('11', 11),
            ('12', 12),
            ('13', 13),
            ('14', 14),
            ('15', 15),
            ('16', 16),
            ('17', 17),
            ('18', 18),
            ('19', 19),
            ('20', 20),
        ]
        self.board_background = [
            ('Cherry', 'cherry_800x.jpg'),
            ('Coffee', 'coffee-beans.jpg'),
            ('Maple', 'maple.jpg'),
            ('Marble', 'marble.png'),
            ('Sand', 'sand.jpg'),
        ]

        self.modes = [
            ('Player vs AI', 'pvai'),
            ('Player vs Player', 'pvp'),
            ('AI vs AI', 'aivai'),
        ]

        file = open('data/settings/settings.txt', 'r')
        lines = file.readlines()
        self.label1 = self.add.label('Game Mode:')
        self.mode = self.add.dropselect('', self.modes, int(lines[0].replace('\n', '')), selection_box_width=350,
                                            selection_option_font_size=None, placeholder='Select Mode',
                                            selection_box_height=6, cursor=11)
        self.mode.set_controller(custom_controller)

        self.label3 = self.add.label('Flip Board:')
        self.flip = self.add.toggle_switch('', int(lines[4]), cursor=11)
        self.flip.set_controller(custom_controller)

        self.label3 = self.add.label('Sounds:')
        self.sounds = self.add.toggle_switch('', int(lines[5]), cursor=11)
        self.sounds.set_controller(custom_controller)


        self.label3 = self.add.label('Pieces:')
        self.piece = self.add.dropselect('', self.pieces, int(lines[1].replace('\n', '')), selection_box_width=350, selection_option_font_size=None, placeholder='Select Piece Type', selection_box_height=6, cursor=11)
        self.piece.set_controller(custom_controller)

        self.label4 = self.add.label('Board Style:')
        self.board = self.add.dropselect('', self.board_background, int(lines[2].replace('\n', '')), selection_box_width=350,
                                            selection_option_font_size=None, placeholder='Select Board Style',
                                            selection_box_height=6, cursor=11)
        self.board.set_controller(custom_controller)

        self.label5 = self.add.label('AI Strength:')
        self.strength = self.add.dropselect('', self.ai_strength, int(lines[3].replace('\n', '')), selection_box_width=350, selection_option_font_size=None, placeholder='Select Strength', selection_box_height=6, cursor=11)
        self.strength.set_controller(custom_controller)

        self.confirms = self.add.button('Confirm', self.confirm, accept_kwargs=True, font_shadow=True,
                        font_shadow_color=(100, 100, 100), font_background_color=(0, 200, 0), cursor=11, font_color=(0,0,0))
        self.confirms.set_controller(custom_controller)

        self.resized = False

    def run(self):
        self.enable()
        self.mainloop(self.screen, self.resize_event, fps_limit=120)

    def resize_event(self):
        if self.screen.get_size() != self.o_size:
            self.resized = True
            self.resize(self.screen.get_width(), self.screen.get_height())
            self.render()
            self.o_size = self.screen.get_size()

    def confirm(self):
        chosen = self.piece.get_value()[0][1]
        self.parent.change_pieces(chosen)
        self.parent.change_mode(self.mode.get_value()[0][1])
        self.parent.change_board(self.board.get_value()[0][1])
        self.parent.change_ai_strength(self.strength.get_value()[0][1])
        self.parent.flip_enable(int(self.flip.get_value()))
        self.parent.sounds_enable(int(self.sounds.get_value()))
        with open('data/settings/settings.txt', 'w') as file:
            file.writelines(str(self.mode.get_index())+'\n')
            file.writelines(str(self.piece.get_index())+'\n')
            file.writelines(str(self.board.get_index())+'\n')
            file.writelines(str(self.strength.get_index())+'\n')
            file.writelines(str(int(self.flip.get_value()))+'\n')
            file.writelines(str(int(self.sounds.get_value()))+'\n')
        self.mode.get_index()
        self.exit_menu()

    def view_controls(self):
        self.disable()
        control_menu = Controls(title='Controls', width=self.screen.get_width(), height=self.screen.get_height(),surface=self.screen, parent=self, theme=pm.themes.THEME_DARK)
        control_menu.run()

    def btn_apply(self, event, ob):
        applied = event.key == 27
        if applied:
            self.exit_menu()


    def exit_menu(self):
        self.disable()
        if self.resized:
            self.parent.check_resize()


class Controls(pm.menu.Menu):
    def __init__(self, surface, parent,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = surface
        self.o_size = self.screen.get_size()
        self.parent = parent
        custom_controller = Controller()
        custom_controller.apply = self.btn_apply
        self.button = self.add.button('Back', self.exit_menu, accept_kwargs=True, font_shadow=True,
                        font_shadow_color=(100, 100, 100), font_background_color=(255, 0, 0), cursor=11,
                        font_color=(0, 0, 0))
        self.button.set_controller(custom_controller)
        self.text = self.add.label('Undo - U\nSave and reset - Ctrl + S\nPrint game FEN position - Ctrl + F\nGet current evaluation - Crtl + E\nReverse board - Ctrl + R\nHint - Crtl + H', font_size=20, border_color=(150,150,150), border_width=3, label_id='123')
        self.resized = False

    def run(self):
        self.enable()
        self.mainloop(self.screen, self.resize_event, fps_limit=120)

    def resize_event(self):
        if self.screen.get_size() != self.o_size:
            self.resized = True
            self.resize(self.screen.get_width(), self.screen.get_height())
            self.render()
            self.force_surface_cache_update()
            self.o_size = self.screen.get_size()

    def btn_apply(self, event, ob):
        applied = event.key == 27
        if applied:
            self.exit_menu()

    def exit_menu(self):
        self.disable()
        self.parent.enable()



class EndGameMenu(pm.menu.Menu):
    def __init__(self, surface, parent,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = surface
        self.o_size = self.screen.get_size()
        self.parent = parent
        custom_controller = Controller()
        custom_controller.apply = self.btn_apply
        self.button = self.add.button('View PGN file', self.view_file, accept_kwargs=True, font_shadow=True,
                                      font_shadow_color=(100, 100, 100), font_background_color=(20, 20, 200), cursor=11,
                                      font_color=(0, 0, 0))
        self.button = self.add.button('Reset', self.exit_menu, accept_kwargs=True, font_shadow=True,
                        font_shadow_color=(100, 100, 100), font_background_color=(255, 0, 0), cursor=11,
                        font_color=(0, 0, 0))
        self.button.set_controller(custom_controller)
        self.resized = False
        self.file_path = None

    def run(self):
        self.enable()
        self.mainloop(self.screen, self.resize_event, fps_limit=120)

    def set_file_path_and_text(self, path, text):
        self.add.label(text, max_char=1000)
        self.file_path = path

    def view_file(self):
        os.system('notepad ' + self.file_path)

    def resize_event(self):
        if self.screen.get_size() != self.o_size:
            self.resized = True
            self.resize(self.screen.get_width(), self.screen.get_height())
            self.render()
            self.force_surface_cache_update()
            self.o_size = self.screen.get_size()

    def btn_apply(self, event, ob):
        applied = event.key == 27
        if applied:
            self.exit_menu()

    def exit_menu(self):
        self.disable()
        if self.resized:
            self.parent.check_resize()




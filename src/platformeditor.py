import gc
import random
import sys
import tracemalloc
import pygame

from .mainwindow import MainWindow

from .camera import Camera

from .util import get_image
from .windowevents import GameAppEventHandler, PlayerMotionEventHandler, StopHandling
from .sprites import Platform, Player
from .ui import Subwindow
from tkinter import *


class Input(Toplevel):
    def __init__(self, default_text, callback):
        super().__init__()
        Label(self, text='Enter arguments in format (x, y, tile_w, tile_h):', anchor='e').pack(
            fill='x'
        )
        self._e = Entry(self)
        self._e.pack(fill='x')
        self._e.insert(0, default_text)
        self._usrcb = callback
        Button(self, text='OK', command=self._cb).pack(fill='x')
        self.focus()
        self._e.focus_force()
        self.bind('<Return>', self._cb)

    def _cb(self, e=None):
        self._usrcb(self._e.get())
        self.destroy()


class Output(Toplevel):
    def __init__(self, ls):
        super().__init__()
        self._e = Text(self)
        self._e.pack(fill='both', expand=True)
        s = '\n'.join(repr(it) for it in ls)

        self._e.insert('0.0', s)
        self.focus()
        self._e.focus_force()
        self.bind('<Return>', self.destroy)


class GameApp:
    def __init__(self):
        if not pygame.get_init():
            raise RuntimeError('pygame is not initialised')

        self._root = Tk()
        self._root.withdraw()
        pygame.display.set_mode(
            (400, 400),
            pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.HWACCEL,
            vsync=1,
        )
        pygame.display.set_caption('Vnezapni Gamejam Game')
        # if sys.platform.startswith('win'):
        #     import ctypes
        #     from ctypes import wintypes

        #     hwnd = pygame.display.get_wm_info().get('window', 0) if pygame.display.get_init() else 0
        #     proc = ctypes.WinDLL('User32.dll').SetFocus
        #     proc.restype = wintypes.HWND
        #     proc.argtypes = [wintypes.HWND]
        #     proc(hwnd)

        self._screen = pygame.display.get_surface()
        self._is_running = True
        self._dt = 0
        self.is_paused = False

        self.reload()
        try:
            with open('edmem', 'r') as f:
                self._plat_init_args = eval(f.read())
        except (IOError, ValueError):
            self._plat_init_args = [
                (100, 100, 10, 0),
                (61, 40, 0, 3),
            ]
            with open('edmem', 'w') as f:
                f.write(repr(self._plat_init_args))
        self._ip = None

    def reload(self):
        self._player = Player(200, 100)
        self._spears = pygame.sprite.Group()
        self._enemies = pygame.sprite.Group()

        self._camera = Camera(400, 400, self._player)
        self._was_game_over = False

        self._ui = MainWindow(self, self._screen)
        self._ui.capture_surface = self._screen

        self._event_handlers = (
            self._ui,
            GameAppEventHandler(self, self._camera),
            PlayerMotionEventHandler(self._player, self._spears, self._enemies),
        )

    def run(self):
        clock = pygame.time.Clock()

        while self._is_running:
            self._root.update()
            self._dt = clock.tick() / 1000

            self._platforms = pygame.sprite.Group()
            for args in self._plat_init_args:
                # try:
                p = Platform(*args)
                # except pygame.error: # out of memory
                #     ...
                self._platforms.add(p)

            for event in pygame.event.get():

                xy = self._camera.reverse_apply(pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self._plat_init_args.append((*xy, 0, 0))
                        self.dump_edmem()
                    elif event.key == pygame.K_2:
                        for idx, target in enumerate(self._plat_init_args):
                            if Platform(*target).rect.collidepoint(xy):

                                def cb(text):
                                    self._plat_init_args[idx] = eval(text)
                                    self._ip = None
                                    self.dump_edmem()

                                self._ip = Input(repr(target), cb)

                                break
                    elif event.key == pygame.K_3:
                        global o
                        o = Output(self._plat_init_args)
                        self.dump_edmem()
                    elif event.key == pygame.K_4:
                        for idx, target in enumerate(self._plat_init_args):
                            if Platform(*target).rect.collidepoint(xy):
                                del self._plat_init_args[idx]
                                if self._ip is not None:
                                    self._ip.destroy()
                                    self._ip = None
                                self.dump_edmem()

                for handler in self._event_handlers:
                    try:
                        handler.process_event(event)
                    except StopHandling:
                        break

            for handler in self._event_handlers:
                handler.update()

            if not self.is_paused:
                self.update()
            self._camera.update()
            if len(self._spears) > 5:
                sorted_spears = sorted(self._spears, key=lambda s: s.creation_time)
                sorted_spears[0].kill()

            if self._player.rect.y > 1000 and not self._was_game_over:
                self._ui.show_game_over()
                self._was_game_over = True

            self._screen.fill("#C8FFFD")
            # self._platforms.draw(self._screen)
            # self._screen.blit(self._player.image, self._player.rect)

            for sprite in (
                self._player,
                *self._enemies,
                *self._spears,
                *self._platforms,
            ):
                screen_pos = self._camera.apply(sprite)
                self._screen.blit(sprite.image, screen_pos)

            self._ui.draw(self._screen)

            if self.is_paused:
                for bar_rect in pygame.Rect(10, 10, 10, 30), pygame.Rect(30, 10, 10, 30):
                    self._screen.fill('#000000', bar_rect.inflate(2, 2))
                    self._screen.fill('#ffffff', bar_rect)

            # self._screen.blit(font.render(f'FPS: {clock.get_fps()}', True, '#00ff00'), (10, 10))

            pygame.display.flip()

    def stop(self):
        self._is_running = False
        self._root.destroy()

    def dump_edmem(self):
        with open('edmem', 'w') as f:
            f.write(repr(self._plat_init_args))

    def update(self):
        group = pygame.sprite.Group(self._player, self._enemies, *self._platforms, self._spears)
        group.update(self._dt, group)

import random
import pygame

from .mainwindow import MainWindow

from .camera import Camera

from .util import get_image
from .windowevents import GameAppEventHandler, PlayerMotionEventHandler, StopHandling
from .sprites import Platform, Player
from .ui import Subwindow


class GameApp:
    def __init__(self):
        if not pygame.get_init():
            raise RuntimeError('pygame is not initialised')

        pygame.display.set_mode(
            (400, 400),
            pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.HWACCEL,
            vsync=1,
        )
        pygame.display.set_caption('Vnezapni Gamejam Game')

        self._screen = pygame.display.get_surface()
        self._is_running = True
        self._dt = 0
        self.is_paused = False

        self.reload()

    def reload(self):
        self._player = Player(100, 0)
        self._spears = pygame.sprite.Group()
        self._platforms = pygame.sprite.Group(
            Platform(100, 100, 10, 0),
            Platform(60, 60, 0, 0),
        )

        self._camera = Camera(400, 400, self._player)

        self._ui = MainWindow(self, self._screen)
        self._ui.capture_surface = self._screen

        self._event_handlers = (
            self._ui,
            GameAppEventHandler(self, self._camera),
            PlayerMotionEventHandler(self._player, self._spears),
        )

    def run(self):
        clock = pygame.time.Clock()
        was_game_over = False
        font = pygame.font.SysFont('Sans', 20)

        while self._is_running:
            self._dt = clock.tick() / 1000

            for event in pygame.event.get():
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

            if self._player.rect.y > 1000 and not was_game_over:
                self._ui.show_game_over()
                was_game_over = True

            self._screen.fill("#C8FFFD")
            # self._platforms.draw(self._screen)
            # self._screen.blit(self._player.image, self._player.rect)

            for sprite in (
                self._player,
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

    def update(self):
        self._player.update(self._dt, self._platforms)
        self._spears.update(self._dt, self._platforms)

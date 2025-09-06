import pygame
import abc

from .camera import Camera

from .sprites import Player, Spear


class StopHandling(Exception):
    '''Exception to prevent the current event from handling by other event handlers.

    If a handler raises it, make sure that the handler is above the others.
    '''


class BaseEventHandler(abc.ABC):
    @abc.abstractmethod
    def process_event(self, e: pygame.Event):
        pass


class GameAppEventHandler(BaseEventHandler):
    def __init__(self, app: 'GameApp', camera: 'Camera'):
        self._app = app
        self._camera = camera

    def process_event(self, e):
        if e.type == pygame.QUIT:
            self._app.stop()

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self._app.stop()
            elif e.key == pygame.K_p:
                self._app.is_paused = not self._app.is_paused
            elif e.key == pygame.K_F5:
                self._app.update()
            elif e.key == pygame.K_F6:
                self._app.reload()

        elif e.type == pygame.VIDEORESIZE:
            self._camera.width = e.w
            self._camera.height = e.h


class PlayerMotionEventHandler(BaseEventHandler):
    def __init__(self, player: 'Player', spear_group: pygame.sprite.Group):
        self._player = player
        self._actions = set()
        self._spears = spear_group

    def process_event(self, e: pygame.Event):
        """Обрабатывает события клавиатуры"""
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_a:
                self._actions.add('left')
                if 'right' in self._actions:
                    self._player.stop_horizontal()
                else:
                    self._player.move_left()
            elif e.key == pygame.K_d:
                self._actions.add('right')
                if 'left' in self._actions:
                    self._player.stop_horizontal()
                else:
                    self._player.move_right()
            elif e.key == pygame.K_w:
                self._actions.add('jump')
            elif e.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                spear = Spear(self._player.rect.topleft, self._player.velocity)
                self._spears.add(spear)

        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_a:
                self._actions.discard('left')
                if 'right' not in self._actions:
                    self._player.stop_horizontal()
                else:
                    self._player.move_right()

            elif e.key == pygame.K_d:
                self._actions.discard('right')
                if 'left' not in self._actions:
                    self._player.stop_horizontal()
                else:
                    self._player.move_left()

            elif e.key == pygame.K_w:
                self._actions.discard('jump')

        if 'jump' in self._actions and self._player.is_grounded:
            self._player.jump()

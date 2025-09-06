import pygame
import abc


class StopHandling(Exception):
    '''Exception to prevent the current event from handling by other event handlers.

    If a handler raises it, make sure that the handler is above the others.
    '''

class BaseEventHandler(abc.ABC):
    @abc.abstractmethod
    def process_event(self, e: pygame.Event):
        pass


class GameAppEventHandler(BaseEventHandler):
    def __init__(self, app: 'GameApp'):
        self._app = app

    def process_event(self, e):
        if e.type == pygame.QUIT:
            self._app.stop()

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self._app.stop()
import pygame
from .windowevents import GameAppEventHandler, StopHandling

class GameApp:
    def __init__(self):
        if not pygame.get_init():
            raise RuntimeError('pygame is not initialised')

        pygame.display.set_mode(
            (400, 400),
            # pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.HWACCEL,
            # vsync=1,
        )
        pygame.display.set_caption('Vnezapni Gamejam Game')

        self._screen = pygame.display.get_surface()
        self._is_running = True
        
        self._event_handlers = (
            GameAppEventHandler(self),
        )

    def run(self):
        while self._is_running:
            for event in pygame.event.get():
                for handler in self._event_handlers:
                    try:
                        handler.process_event(event)
                    except StopHandling:
                        break

            self._screen.fill('#003300')

            pygame.display.flip()

    def stop(self):
        self._is_running = False
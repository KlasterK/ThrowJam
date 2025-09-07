import pygame
import argparse
from .gameapp import GameApp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform-editor', action='store_true')
    args = parser.parse_args()

    if args.platform_editor:
        global GameApp
        from .platformeditor import GameApp

    pygame.init()
    app = GameApp()
    app.run()
    pygame.quit()


if __name__ == '__main__':
    main()

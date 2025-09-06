import random
from pathlib import Path
from typing import Literal

import pygame
import pygame._sdl2


def blend(bg: pygame.Color, fg: pygame.Color, alpha: float | None = None) -> pygame.Color:
    '''Blends two colors together.

    If alpha is given, colors' alpha channels will be blended, otherwise
    the foreground color's alpha will be used for blending and alpha channels will not be blended.
    '''

    if alpha is None:
        alpha = fg.a / 0xFF
        blended_alpha_channel = bg.a
    else:
        alpha = max(0, min(1, alpha))
        blended_alpha_channel = int(fg.a * alpha + bg.a * (1 - alpha))

    return pygame.Color(
        int(fg.r * alpha + bg.r * (1 - alpha)),
        int(fg.g * alpha + bg.g * (1 - alpha)),
        int(fg.b * alpha + bg.b * (1 - alpha)),
        blended_alpha_channel,
    )


_images_cache = {}
ASSETS_ROOT=Path('./assets')

def get_image(
    name: str,
    scale_to: tuple[int, int] | None = None,
    scale_type: Literal['smooth', 'pixel'] = 'pixel',
) -> pygame.Surface | None:
    if name in _images_cache:
        image = _images_cache[name]
    else:
        icon_path = ASSETS_ROOT / name
        try:
            image = pygame.image.load(icon_path).convert_alpha()
        except IOError:
            # pygame._sdl2.messagebox('Fatal', f'Could not load texture `{name}`\nAssets root: `{ASSETS_ROOT!s}`')
            # raise
            return None
        _images_cache[name] = image

    if scale_to is None:
        return image

    if scale_type == 'smooth':
        return pygame.transform.smoothscale(image, scale_to)
    else:
        return pygame.transform.scale(image, scale_to)

def get_font():
    return pygame.font.SysFont('Sans', 20)
import pygame
from pygame.math import Vector2

from .util import get_image


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_w, tile_h):
        """
        Создает платформу из составных текстур

        Args:
            x, y: координаты левого верхнего угла платформы
            tile_w: количество тайлов в средней части по горизонтали
            tile_h: количество тайлов в средней части по вертикали
        """
        super().__init__()
        self.x = x
        self.y = y
        self.tile_w = tile_w
        self.tile_h = tile_h

        self.load_textures()
        self.build_image()

        # Создаем прямоугольник для позиционирования и коллизий
        self.rect = self.image.get_rect(topleft=(x, y))
        # Создаем маску для точных коллизий
        self.mask = pygame.mask.from_surface(self.image)

    def load_textures(self):
        self._texs = {
            key: get_image(f'platform/{key}.png')
            for key in (
                'topleft',
                'topright',
                'bottomleft',
                'bottomright',
                'top',
                'left',
                'bottom',
                'right',
                'center',
            )
        }

    def build_image(self):
        """Создает изображение платформы из составных частей"""
        # Получаем размеры текстур
        c_tl = self._texs['topleft'].get_rect()
        c_tr = self._texs['topright'].get_rect()
        c_bl = self._texs['bottomleft'].get_rect()
        c_br = self._texs['bottomright'].get_rect()

        s_top = self._texs['top'].get_rect()
        s_bottom = self._texs['bottom'].get_rect()
        s_left = self._texs['left'].get_rect()
        s_right = self._texs['right'].get_rect()

        mid_rect = self._texs['center'].get_rect()

        # Вычисляем общий размер платформы
        total_width = c_tl.width + self.tile_w * s_top.width + c_tr.width
        total_height = c_tl.height + self.tile_h * s_left.height + c_bl.height

        # Создаем поверхность для платформы
        self.image = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Прозрачный фон

        # Рисуем верхнюю строку
        x, y = 0, 0
        self.image.blit(self._texs['topleft'], (x, y))
        x += c_tl.width

        for i in range(self.tile_w):
            self.image.blit(self._texs['top'], (x, y))
            x += s_top.width

        self.image.blit(self._texs['topright'], (x, y))

        # Рисуем средние строки
        for j in range(self.tile_h):
            x, y = 0, c_tl.height + j * s_left.height
            self.image.blit(self._texs['left'], (x, y))
            x += s_left.width

            for i in range(self.tile_w):
                self.image.blit(self._texs['center'], (x, y))
                x += mid_rect.width

            self.image.blit(self._texs['right'], (x, y))

        # Рисуем нижнюю строку
        x, y = 0, total_height - c_bl.height
        self.image.blit(self._texs['bottomleft'], (x, y))
        x += c_bl.width

        for i in range(self.tile_w):
            self.image.blit(self._texs['bottom'], (x, y))
            x += s_bottom.width

        self.image.blit(self._texs['bottomright'], (x, y))

    def update(self, dt):
        """Метод update для совместимости (платформа статична)"""
        pass

    def draw(self, surface, camera=None):
        """Отрисовывает платформу с учетом камеры (если provided)"""
        if camera:
            surface.blit(self.image, camera.apply(self))
        else:
            surface.blit(self.image, self.rect)


class Physical(pygame.sprite.Sprite):
    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.rect = pygame.FRect()
        
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        
        self.gravity = Vector2(0, 980)  # 980 px/s**2 
        self.max_speed = 300
        
        self.is_grounded = False

    def update(self, dt, platforms):
        self.velocity += self.acceleration * dt
        self.velocity += self.gravity * dt
        
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        self.rect.move_ip(self.velocity * dt)
        
        self.check_vertical_collisions(platforms)
        self.check_horizontal_collisions(platforms)
        
        self.acceleration = Vector2(0, 0)

    def check_horizontal_collisions(self, platforms):
        """Проверяет коллизии по горизонтали"""
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.velocity.x > 0:  # Движение вправо
                self.rect.right = platform.rect.left
                self.velocity.x = 0
            elif self.velocity.x < 0:  # Движение влево
                self.rect.left = platform.rect.right
                self.velocity.x = 0

    def check_vertical_collisions(self, platforms: pygame.sprite.Group) -> None:
        self.is_grounded = False
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for platform in hits:
            if self.velocity.y > 0:  # Падение вниз
                self.rect.bottom = platform.rect.top
                self.velocity.y = 0
                self.is_grounded = True
            elif self.velocity.y < 0:  # Прыжок вверх
                self.rect.top = platform.rect.bottom
                self.velocity.y = 0

class Player(Physical):
    def __init__(self, x, y):
        Physical.__init__(self)
        self.rect.update(x, y, 50, 50)
        
        # Настройки игрока
        self.jump_force = -400  # Отрицательное значение = вверх
        self.move_speed = 4000

        self._facing = 'right'

        self.image = get_image('player_idle.png')
        
        # # Визуализация
        # self.image.fill(self.color)
        # pygame.draw.rect(self.image, (255, 255, 255), (10, 10, 10, 10))  # Глаза

    def move_left(self):
        """Движение влево"""
        if self.is_grounded:
            self.acceleration.x = -self.move_speed
            if self._facing == 'right':
                self.image = pygame.transform.flip(self.image, True, False)
            self._facing = 'left'

    def move_right(self):
        """Движение вправо"""
        if self.is_grounded:
            self.acceleration.x = self.move_speed
            if self._facing == 'left':
                self.image = pygame.transform.flip(self.image, True, False)
            self._facing = 'right'

    def jump(self):
        if self.is_grounded:
            self.velocity.y = self.jump_force
            self.is_grounded = False

    def stop_horizontal(self):
        self.acceleration.x = 0
        self.velocity.x = 0

class Spear(Physical):
    ...

import pygame
from pygame.math import Vector2

from .util import get_image

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, tile_size=100):
        """
        Создает платформу с повторяющейся серединой текстуры
        
        Args:
            x, y: координаты левого верхнего угла
            width, height: размеры платформы
            texture_path: путь к текстуре (300x100 пикселей)
            tile_size: размер тайла для повторения (по умолчанию 100)
        """
        super().__init__()
        
        self.width = width
        self.height = height
        self.tile_size = tile_size
        
        # Создаем поверхность для всей платформы
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.load_texture()
        self.mask = pygame.mask.from_surface(self.image)

    def load_texture(self):
        # Загружаем исходную текстуру
        original_texture = get_image('platform/a.png')
        
        # Масштабируем до нужной высоты, сохраняя пропорции
        original_height = original_texture.get_height()
        scale_factor = self.height / original_height
        scaled_width = int(original_texture.get_width() * scale_factor)
        scaled_tile_size = int(self.tile_size * scale_factor)
        
        # Масштабируем всю текстуру
        scaled_texture = pygame.transform.scale(original_texture, 
                                                (scaled_width, self.height))
        
        # Разрезаем текстуру на части
        left_part = scaled_texture.subsurface((0, 0, scaled_tile_size, self.height))
        middle_part = scaled_texture.subsurface((scaled_tile_size, 0, scaled_tile_size, self.height))
        right_part = scaled_texture.subsurface((scaled_tile_size * 2, 0, scaled_tile_size, self.height))
        
        # Отрисовываем левую часть
        self.image.blit(left_part, (0, 0))
        
        # Отрисовываем правую часть
        right_x = self.width - scaled_tile_size
        self.image.blit(right_part, (right_x, 0))
        
        # Отрисовываем повторяющуюся середину
        middle_width = self.width - 2 * scaled_tile_size
        if middle_width > 0:
            self.draw_middle_part(middle_part, scaled_tile_size, middle_width)
            

    def draw_middle_part(self, middle_part, tile_width, available_width):
        """Отрисовывает повторяющуюся среднюю часть"""
        current_x = tile_width
        
        # Рисуем полные тайлы
        full_tiles_count = available_width // tile_width
        for _ in range(full_tiles_count):
            self.image.blit(middle_part, (current_x, 0))
            current_x += tile_width
        
        # Рисуем оставшуюся часть (если есть)
        remaining_width = available_width % tile_width
        if remaining_width > 0:
            partial_tile = middle_part.subsurface((0, 0, remaining_width, self.height))
            self.image.blit(partial_tile, (current_x, 0))

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

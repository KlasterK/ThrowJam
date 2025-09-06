import pygame

class Camera:
    def __init__(self, width, height, target=None):
        """
        Камера, которая следует за целевым объектом
        
        Args:
            width, height: размеры области видимости (обычно размер экрана)
            target: целевой объект (игрок), за которым следует камера
        """
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.target = target
        self.offset = pygame.math.Vector2(0, 0)
        
        # Плавность движения камеры
        self.smoothness = 0.05
        self.dead_zone = 50  # Зона, в которой камера не двигается

    def set_target(self, target):
        """Устанавливает целевой объект"""
        self.target = target

    def update(self):
        """Обновляет позицию камеры"""
        if self.target:
            # Целевая позиция (центр камеры должен быть на цели)
            target_x = self.target.rect.centerx - self.width // 2
            target_y = self.target.rect.centery - self.height // 2
            
            # Плавное перемещение камеры (LERP)
            current_x = self.camera_rect.x
            current_y = self.camera_rect.y
            
            # Проверяем dead zone
            dx = abs(target_x - current_x)
            dy = abs(target_y - current_y)
            
            if dx > self.dead_zone or dy > self.dead_zone:
                # Плавное движение к цели
                new_x = current_x + (target_x - current_x) * self.smoothness
                new_y = current_y + (target_y - current_y) * self.smoothness
                
                self.camera_rect.x = new_x
                self.camera_rect.y = new_y
            
            # Обновляем offset для отрисовки
            self.offset.x = self.camera_rect.x
            self.offset.y = self.camera_rect.y

    def apply(self, entity):
        """Применяет смещение камеры к объекту"""
        if isinstance(entity, pygame.Rect):
            return entity.move(-self.camera_rect.x, -self.camera_rect.y)
        else:
            return entity.rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def apply_pos(self, pos):
        """Применяет смещение камеры к позиции"""
        return (pos[0] - self.camera_rect.x, pos[1] - self.camera_rect.y)

    def reverse_apply(self, pos):
        """Обратное преобразование (экранные координаты в мировые)"""
        return (pos[0] + self.camera_rect.x, pos[1] + self.camera_rect.y)
import time
from functools import lru_cache

class ResponsiveScaler:
    """
    Sistema de escalado responsivo reutilizable para cualquier elemento visual.
    """
    def __init__(self, base_width=1280, base_height=720):
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = base_width
        self.current_height = base_height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.aspect_ratio = base_width / base_height
        self.last_update_time = 0
        self.update_interval = 0.2  # segundos

    def update(self, width, height):
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            if width == self.current_width and height == self.current_height:
                return False
        if width == self.current_width and height == self.current_height:
            return False
        self.current_width = width
        self.current_height = height
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.aspect_ratio = width / height
        self.last_update_time = current_time
        return True

    @lru_cache(maxsize=1024)
    def sx(self, value):
        """Escala un valor horizontal."""
        return int(value * self.scale_x)

    @lru_cache(maxsize=1024)
    def sy(self, value):
        """Escala un valor vertical."""
        return int(value * self.scale_y)

    @lru_cache(maxsize=256)
    def sf(self, size):
        """Escala un tamaño de fuente de manera balanceada."""
        scale_factor = (self.scale_x * 0.6 + self.scale_y * 0.4)
        return max(12, int(size * scale_factor))

    def scale_rect(self, x, y, width, height):
        """Escala un rectángulo completo."""
        return (
            self.sx(x),
            self.sy(y),
            self.sx(width),
            self.sy(height)
        )

    def get_centered_rect(self, width, height, vertical_offset=0, horizontal_offset=0):
        """Obtiene un rectángulo centrado en la pantalla con dimensiones escaladas."""
        scaled_width = self.sx(width)
        scaled_height = self.sy(height)
        x = (self.current_width - scaled_width) // 2 + self.sx(horizontal_offset)
        y = (self.current_height - scaled_height) // 2 + self.sy(vertical_offset)
        return (x, y, scaled_width, scaled_height)

    def maintain_aspect_ratio(self, width, height):
        """Ajusta dimensiones para mantener la relación de aspecto."""
        target_ratio = width / height
        if target_ratio > self.aspect_ratio:
            new_width = self.sx(width)
            new_height = int(new_width / target_ratio)
        else:
            new_height = self.sy(height)
            new_width = int(new_height * target_ratio)
        return new_width, new_height
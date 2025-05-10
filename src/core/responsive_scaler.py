import time
from functools import lru_cache

class ResponsiveScaler:
    """
    Sistema mejorado de escalado responsivo para interfaces PyGame.
    Adaptado para ser rápido, limpio y robusto.
    """

    def __init__(self, base_width=1280, base_height=720, uniform=False):
        self.base_width = base_width
        self.base_height = base_height
        self.uniform = uniform  # Escalado proporcional si es True
        self._width = base_width
        self._height = base_height
        self._last_update = 0
        self._scale_x = 1.0
        self._scale_y = 1.0
        self._scale_avg = 1.0
        self._update_scales(base_width, base_height)

    def update(self, width: int, height: int) -> bool:
        """
        Actualiza las proporciones de escala si cambió el tamaño.
        Devuelve True si hubo cambio real.
        """
        if (width, height) == (self._width, self._height):
            return False

        self._width = width
        self._height = height
        self._last_update = time.time()
        self._update_scales(width, height)
        self.clear_cache()
        return True

    def _update_scales(self, width, height):
        self._scale_x = width / self.base_width
        self._scale_y = height / self.base_height
        if self.uniform:
            avg = (self._scale_x + self._scale_y) / 2
            self._scale_x = self._scale_y = avg
        self._scale_avg = (self._scale_x * 0.6 + self._scale_y * 0.4)

    def clear_cache(self):
        """Limpia la caché de funciones escaladas."""
        self.sx.cache_clear()
        self.sy.cache_clear()
        self.sf.cache_clear()

    @property
    def scale_x(self):
        return self._scale_x

    @property
    def scale_y(self):
        return self._scale_y

    @property
    def scale_avg(self):
        return self._scale_avg

    @lru_cache(maxsize=1024)
    def sx(self, value: float | int) -> int:
        return int(value * self._scale_x)

    @lru_cache(maxsize=1024)
    def sy(self, value: float | int) -> int:
        return int(value * self._scale_y)

    @lru_cache(maxsize=512)
    def sf(self, size: float | int) -> int:
        return max(12, int(size * self._scale_avg))

    def scale_rect(self, x, y, w, h):
        """Escala un rectángulo."""
        return self.sx(x), self.sy(y), self.sx(w), self.sy(h)

    def get_centered_rect(self, w, h, vertical_offset=0, horizontal_offset=0):
        """Devuelve un rectángulo centrado con dimensiones escaladas."""
        sw = self.sx(w)
        sh = self.sy(h)
        cx = (self._width - sw) // 2 + self.sx(horizontal_offset)
        cy = (self._height - sh) // 2 + self.sy(vertical_offset)
        return cx, cy, sw, sh

    def maintain_aspect_ratio(self, width, height):
        """
        Mantiene la relación de aspecto base al escalar.
        """
        target_ratio = width / height
        base_ratio = self.base_width / self.base_height

        if target_ratio > base_ratio:
            new_height = self.sy(height)
            new_width = int(new_height * base_ratio)
        else:
            new_width = self.sx(width)
            new_height = int(new_width / base_ratio)

        return new_width, new_height

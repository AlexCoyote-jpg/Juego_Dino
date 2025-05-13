from chatbot.event_handlers import process_events
import pygame
from chatbot.bot_ui import (
    dibujar_entrada, dibujar_botones, renderizar_historial,
    state, historial, scroll_manager, get_visual_constants, set_render_area, get_botones
)

class ChatBotScreen:
    def __init__(self, parent, area_rect=None):
        self.parent = parent
        self.area = area_rect if area_rect else pygame.Rect(0, 0, 900, 600)
        self.fade_alpha = 0
        # Precrea el fondo de puntos para no redibujarlo en cada frame
        self._background = None
        self._bg_area_size = None
        self._last_render_size = None  # Almacena el último tamaño para detectar cambios

    def _get_scroll_area(self, constants):
        return pygame.Rect(
            constants["SCROLL_MARGIN"],
            constants["SCROLL_MARGIN"],
            constants["ANCHO"] - 2 * constants["SCROLL_MARGIN"] - constants["SCROLL_WIDTH"],
            int(constants["ALTO"] * 0.7)
        )

    def handle_events(self, events):
        # Detectar cambios de tamaño y actualizar solo cuando sea necesario
        if self._last_render_size != (self.area.width, self.area.height):
            self._last_render_size = (self.area.width, self.area.height)
            set_render_area(self.area.width, self.area.height)
            self._background = None  # Forzar regeneración del fondo
        
        constants = get_visual_constants()
        SCROLL_AREA = self._get_scroll_area(constants)
        
        # Optimización: filtrar eventos solo una vez
        filtered_events = []
        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                if self.area.collidepoint(event.pos):
                    local_pos = (event.pos[0] - self.area.x, event.pos[1] - self.area.y)
                    # Crear una copia del evento con posición local
                    filtered_event = pygame.event.Event(event.type, {**event.__dict__, 'pos': local_pos})
                    filtered_events.append(filtered_event)
                # No añadir eventos de mouse que estén fuera del área
            else:
                filtered_events.append(event)
                
        # Optimización: calcular altura total solo cuando sea necesario
        if any(event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL) 
               for event in filtered_events):
            dummy_surface = pygame.Surface((constants["ANCHO"], constants["ALTO"]))
            _, total_height = renderizar_historial(dummy_surface)
            max_scroll = max(0, total_height - SCROLL_AREA.height)
        else:
            # Usar un valor predeterminado para eventos que no son de scroll
            max_scroll = getattr(historial, 'get_total_height', lambda: 0)() - SCROLL_AREA.height
            max_scroll = max(0, max_scroll)
            
        process_events(
            filtered_events, state, historial, scroll_manager,
            max_scroll=max_scroll,
            scroll_area=SCROLL_AREA,
            bar_rect=pygame.Rect(
                self.area.width - constants["SCROLL_WIDTH"] - constants["SCROLL_MARGIN"],
                SCROLL_AREA.y,
                constants["SCROLL_WIDTH"],
                SCROLL_AREA.height
            ),
            botones=get_botones()
        )

    def update(self, dt):
        """Actualiza las animaciones con velocidad adaptativa al framerate"""
        animation_speed = get_visual_constants().get("RESPUESTA_ANIMACION_VELOCIDAD", 4)
        if state['esperando_respuesta']:
            self.fade_alpha = min(self.fade_alpha + animation_speed, 30)
        else:
            self.fade_alpha = max(self.fade_alpha - animation_speed * 3, 0)

    def _draw_background(self, sub_surface, constants):
        """Dibuja el fondo con patrón de puntos, optimizado con caché"""
        current_size = (self.area.width, self.area.height)
        
        # Regenerar fondo solo cuando cambie el tamaño
        if self._background is None or self._bg_area_size != current_size:
            self._background = pygame.Surface(current_size)
            self._background.fill(constants["COLOR_FONDO"])
            
            # Optimización: calcular espaciado dinámico basado en tamaño
            dot_spacing = max(10, min(20, int(self.area.width / 45)))
            for y in range(0, self.area.height, dot_spacing):
                for x in range(0, self.area.width, dot_spacing):
                    pygame.draw.circle(self._background, (240, 240, 240), (x, y), 1)
            self._bg_area_size = current_size
            
        sub_surface.blit(self._background, (0, 0))

    def draw(self, pantalla):
        set_render_area(self.area.width, self.area.height)
        constants = get_visual_constants()
        SCROLL_AREA = self._get_scroll_area(constants)
        # Extraemos una subsuperficie para limitar el renderizado al área
        sub_surface = pantalla.subsurface(self.area)
        self._draw_background(sub_surface, constants)
        renderizar_historial(sub_surface)
        if state['esperando_respuesta']:
            fade_surf = pygame.Surface((self.area.width, self.area.height), pygame.SRCALPHA)
            fade_surf.fill((100, 100, 255, self.fade_alpha))
            sub_surface.blit(fade_surf, (0, 0))
            t = pygame.time.get_ticks() % 1000 / 1000
            r = 5 + 2 * abs(t - 0.5)
            pygame.draw.circle(sub_surface, (52, 152, 219),
                               (SCROLL_AREA.centerx, SCROLL_AREA.bottom + 20), int(r))
        pygame.draw.line(sub_surface, (220, 220, 220),
                         (20, self.area.height - 70), (self.area.width - 20, self.area.height - 70), 2)
        dibujar_entrada(sub_surface)
        dibujar_botones(sub_surface)
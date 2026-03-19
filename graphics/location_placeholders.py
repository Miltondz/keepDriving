"""
Placeholders gráficos para ubicaciones (taller, hotel, tienda) y eventos en la carretera.
Mientras se generan los assets definitivos, usamos formas geométricas y colores.
"""
import pygame
import math
from core.config import BASE_RESOLUTION, ROAD_Y

W, H = BASE_RESOLUTION

# ============================================================================
# COLORES
# ============================================================================
COLOR_ROAD = (40, 40, 45)
COLOR_ROAD_LINE = (200, 200, 100)
COLOR_SHOULDER = (60, 55, 50)

# Colores para tipos de ubicaciones
LOCATION_COLORS = {
    'gas_station': (255, 200, 50),    # Amarillo/naranja
    'repair': (200, 80, 80),          # Rojo
    'shop': (80, 180, 200),           # Cyan
    'hotel': (150, 100, 200),         # Púrpura
    'restaurant': (200, 150, 80),     # Naranja
}

# ============================================================================
# INDICADORES DE EVENTOS EN CARRETERA
# ============================================================================

class EventIndicator:
    """Dibuja indicadores visuales cuando se acerca un evento."""
    
    # Distancia a la que aparece el indicador (km)
    VISIBLE_DISTANCE = 5.0
    
    @staticmethod
    def draw_warning_triangle(surface, x, y, color=(255, 200, 0)):
        """Dibuja un triángulo de advertencia."""
        size = 20
        points = [
            (x, y - size),
            (x - size, y + size),
            (x + size, y + size),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 2)
    
    @staticmethod
    def draw_danger_triangle(surface, x, y, color=(200, 50, 50)):
        """Dibuja un triángulo de peligro."""
        EventIndicator.draw_warning_triangle(surface, x, y, color)
    
    @staticmethod
    def draw_info_circle(surface, x, y, color=(100, 150, 255)):
        """Dibuja un círculo de información."""
        pygame.draw.circle(surface, color, (x, y), 12)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 12, 2)
        # Signo de interrogación
        font = pygame.font.Font(None, 16)
        txt = font.render("i", True, (255, 255, 255))
        surface.blit(txt, (x - 4, y - 8))
    
    @staticmethod
    def draw_npc_indicator(surface, x, y, color=(150, 200, 150)):
        """Dibuja indicador de NPC (persona en la roadside)."""
        # Cabeza
        pygame.draw.circle(surface, color, (x, y - 10), 8)
        # Cuerpo
        pygame.draw.rect(surface, color, (x - 6, y - 2, 12, 20))
        # Brazo (thumb)
        pygame.draw.line(surface, color, (x + 6, y + 5), (x + 14, y + 2), 3)
    
    @classmethod
    def draw_indicator(cls, surface, indicator_type, x, y):
        """Dibuja el indicador apropiado según el tipo."""
        if indicator_type == "warning":
            cls.draw_warning_triangle(surface, x, y)
        elif indicator_type == "danger":
            cls.draw_danger_triangle(surface, x, y)
        elif indicator_type == "info":
            cls.draw_info_circle(surface, x, y)
        elif indicator_type == "npc":
            cls.draw_npc_indicator(surface, x, y)
    
    @classmethod
    def render_approaching_event(cls, surface, distance_km, event_info):
        """
        Renderiza un indicador cuando se acerca un evento.
        distance_km: distancia hasta el evento
        event_info: dict con 'type' y 'tags'
        """
        if distance_km > cls.VISIBLE_DISTANCE:
            return None
        
        # Calcular posición en pantalla (más cerca = más grande)
        alpha = 1.0 - (distance_km / cls.VISIBLE_DISTANCE)
        size_mult = 0.5 + (alpha * 0.5)
        
        # Posición en la derecha de la pantalla (carril)
        x = W - 80
        y = ROAD_Y - 30
        
        # Determinar tipo de indicador
        indicator_type = event_info.get('type', 'warning')
        
        # Dibujar
        cls.draw_indicator(surface, indicator_type, x, y)
        
        # Texto de distancia
        font = pygame.font.Font(None, 14)
        dist_text = f"{distance_km:.1f}km"
        txt = font.render(dist_text, True, (200, 200, 200))
        surface.blit(txt, (x + 15, y - 5))
        
        return True


# ============================================================================
# PLACEHOLDERS DE UBICACIONES (TALLER, HOTEL, TIENDA)
# ============================================================================

class LocationPlaceholder:
    """Dibuja placeholders geométricos para ubicaciones."""
    
    @staticmethod
    def draw_gas_station(surface, x, y, scale=1.0):
        """Dibuja un placeholders de gasolinera (rectángulo con泵)."""
        w, h = int(80 * scale), int(60 * scale)
        # Fondo
        pygame.draw.rect(surface, LOCATION_COLORS['gas_station'], (x, y, w, h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
        
        # Texto
        font = pygame.font.Font(None, 20)
        txt = font.render("GAS", True, (0, 0, 0))
        surface.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))
        
        # Precio
        price_rect = pygame.Rect(x + w - 25, y, 25, 15)
        pygame.draw.rect(surface, (255, 255, 255), price_rect)
        font_sm = pygame.font.Font(None, 10)
        txt_sm = font_sm.render("$", True, (0, 0, 0))
        surface.blit(txt_sm, (x + w - 15, y + 2))
    
    @staticmethod
    def draw_repair_shop(surface, x, y, scale=1.0):
        """Dibuja un placeholders de taller (rectángulo con llave)."""
        w, h = int(80 * scale), int(60 * scale)
        # Fondo
        pygame.draw.rect(surface, LOCATION_COLORS['repair'], (x, y, w, h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
        
        # Llave (círculo y línea)
        cx, cy = x + w//2, y + h//2
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 12, 2)
        pygame.draw.line(surface, (255, 255, 255), (cx - 8, cy), (cx + 8, cy), 3)
        
        # Texto
        font = pygame.font.Font(None, 16)
        txt = font.render("FIX", True, (255, 255, 255))
        surface.blit(txt, (x + w//2 - txt.get_width()//2, y + 5))
    
    @staticmethod
    def draw_shop(surface, x, y, scale=1.0):
        """Dibuja un placeholders de tienda (rectángulo con bolsa)."""
        w, h = int(80 * scale), int(60 * scale)
        # Fondo
        pygame.draw.rect(surface, LOCATION_COLORS['shop'], (x, y, w, h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
        
        # Bolsa de compras (triángulo)
        bx, by = x + w//2, y + h//2
        points = [(bx, by - 15), (bx - 12, by + 10), (bx + 12, by + 10)]
        pygame.draw.polygon(surface, (255, 255, 255), points)
        
        # Texto
        font = pygame.font.Font(None, 16)
        txt = font.render("SHOP", True, (0, 0, 0))
        surface.blit(txt, (x + w//2 - txt.get_width()//2, y + 5))
    
    @staticmethod
    def draw_hotel(surface, x, y, scale=1.0):
        """Dibuja un placeholders de hotel (rectángulo con cama)."""
        w, h = int(80 * scale), int(60 * scale)
        # Fondo
        pygame.draw.rect(surface, LOCATION_COLORS['hotel'], (x, y, w, h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
        
        # Cama (rectángulo)
        bx, by = x + w//2 - 15, y + h//2 - 5
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, 30, 15))
        # Almohada
        pygame.draw.rect(surface, (200, 200, 220), (bx + 2, by + 2, 8, 10))
        
        # Texto
        font = pygame.font.Font(None, 16)
        txt = font.render("HOTEL", True, (255, 255, 255))
        surface.blit(txt, (x + w//2 - txt.get_width()//2, y + 5))
    
    @staticmethod
    def draw_rest_stop(surface, x, y, scale=1.0):
        """Dibuja un placeholders de área de descanso."""
        w, h = int(60 * scale), int(40 * scale)
        # Fondo
        pygame.draw.rect(surface, (100, 150, 100), (x, y, w, h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
        
        # Pícnic (rectángulo y líneas)
        font = pygame.font.Font(None, 14)
        txt = font.render("REST", True, (255, 255, 255))
        surface.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))
    
    @classmethod
    def draw_location(cls, surface, location_type, x, y, scale=1.0):
        """Dibuja el placeholder apropiado según el tipo de ubicación."""
        if location_type == 'gas_station':
            cls.draw_gas_station(surface, x, y, scale)
        elif location_type == 'repair':
            cls.draw_repair_shop(surface, x, y, scale)
        elif location_type == 'shop':
            cls.draw_shop(surface, x, y, scale)
        elif location_type == 'hotel':
            cls.draw_hotel(surface, x, y, scale)
        elif location_type == 'rest':
            cls.draw_rest_stop(surface, x, y, scale)
        else:
            # Generic location
            pygame.draw.rect(surface, (150, 150, 150), (x, y, int(60*scale), int(40*scale)))
            pygame.draw.rect(surface, (0, 0, 0), (x, y, int(60*scale), int(40*scale)), 2)


# ============================================================================
# RENDERIZADO DE UBICACIONES EN EL MUNDO
# ============================================================================

def render_approaching_location(surface, location_data, distance_km):
    """
    Renderiza una ubicación cuando el jugador se acerca.
    location_data: dict con 'type', 'name', 'services'
    """
    VISIBLE_DISTANCE = 10.0  # km
    
    if distance_km > VISIBLE_DISTANCE:
        return None
    
    # Posición en pantalla
    x = W // 2
    y = ROAD_Y - 100
    
    # Escala según proximidad
    scale = 1.0 - (distance_km / VISIBLE_DISTANCE) * 0.5
    scale = max(0.5, scale)
    
    # Dibujar cada servicio
    services = location_data.get('services', [])
    service_spacing = 70
    
    for i, service in enumerate(services):
        sx = x - (len(services) * service_spacing // 2) + i * service_spacing
        LocationPlaceholder.draw_location(surface, service, sx, y, scale)
    
    return True
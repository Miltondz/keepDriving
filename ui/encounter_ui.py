"""
Encounter UI — renders the turn-based encounter panel over the game.
Handles keyboard navigation (1/2/3 to choose, ESC to wait).
Panel derecho muestra avatar o escena del evento.
"""
import pygame
import math
import os
from core.config import BASE_RESOLUTION, COLORS

W, H = BASE_RESOLUTION

# UI colors
C_PANEL_BG = (18, 15, 28)
C_PANEL_BRD = (80, 60, 120)
C_TITLE_BG = (40, 20, 60)
C_TEXT = (220, 215, 235)
C_DIM = (130, 120, 150)
C_HIGHLIGHT = (255, 215, 70)
C_DISABLED = (80, 70, 90)
C_OUTCOME_POS = (80, 200, 120)
C_OUTCOME_NEG = (200, 80, 80)

# Panel derecho - dimensiones
RIGHT_PANEL_W = 120  # Ancho del panel de avatar/escena
RIGHT_PANEL_X = W - RIGHT_PANEL_W - 5


def _wrap_text(text, font, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = cur + (" " if cur else "") + word
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class EncounterUI:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 22)
        self.font_body = pygame.font.Font(None, 15)
        self.font_key = pygame.font.Font(None, 18)
        
        # Panel de la derecha: avatar/escena
        self.avatar_surfaces = {}
        self._load_avatars()
        
        # Escenas/escenarios para eventos
        self.scene_surfaces = {}
        self._create_scenes()

        self.encounter = None
        self.options_list = []
        self.selected = 0
        self.outcome_text = ""
        self.outcome_timer = 0.0
        self.outcome_positive = True
        
        # Animación
        self._slide_y = H
        self._target_y = H - 175
        
        # Avatar actual a mostrar
        self.current_avatar = None
        self.current_scene = None

    def _load_avatars(self):
        """Carga los avatares de personajes."""
        avatars_dir = os.path.join("assets", "sprites", "portraits")
        if os.path.exists(avatars_dir):
            for f in os.listdir(avatars_dir):
                if f.endswith('.png'):
                    name = f.replace('.png', '').replace('portrait_', '').replace('p_', '')
                    path = os.path.join(avatars_dir, f)
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        # Escalar a tamaño del panel
                        scaled = pygame.transform.smoothscale(img, (RIGHT_PANEL_W - 10, RIGHT_PANEL_W - 10))
                        self.avatar_surfaces[name.lower()] = scaled
                    except:
                        pass
    
    def _create_scenes(self):
        """Crea escenas geométricas para eventos sin avatar."""
        # Crear superficies de escenas
        self.scene_surfaces = {}
        
        # Escena genérica de peligro
        danger_surf = pygame.Surface((RIGHT_PANEL_W - 10, 80), pygame.SRCALPHA)
        # Triángulo de advertencia
        pygame.draw.polygon(danger_surf, (200, 100, 50), [(55, 10), (10, 70), (100, 70)])
        self.scene_surfaces['danger'] = danger_surf
        
        # Escena de policía
        police_surf = pygame.Surface((RIGHT_PANEL_W - 10, 80), pygame.SRCALPHA)
        pygame.draw.rect(police_surf, (60, 80, 120), (25, 20, 70, 50))  # Coche
        pygame.draw.circle(police_surf, (200, 50, 50), (35, 15), 8)  # Luz 1
        pygame.draw.circle(police_surf, (50, 50, 200), (85, 15), 8)  # Luz 2
        self.scene_surfaces['police'] = police_surf
        
        # Escena de naturaleza/vista
        scenic_surf = pygame.Surface((RIGHT_PANEL_W - 10, 80), pygame.SRCALPHA)
        pygame.draw.rect(scenic_surf, (100, 180, 255), (20, 40, 80, 30))  # Cielo
        pygame.draw.rect(scenic_surf, (80, 150, 80), (30, 30, 20, 30))  # Montaña 1
        pygame.draw.rect(scenic_surf, (60, 130, 60), (60, 20, 40, 40))  # Montaña 2
        self.scene_surfaces['scenic'] = scenic_surf
        
        # Escena de obstáculo
        obstacle_surf = pygame.Surface((RIGHT_PANEL_W - 10, 80), pygame.SRCALPHA)
        pygame.draw.rect(obstacle_surf, (120, 80, 40), (30, 20, 40, 50))  # Árbol/roca
        pygame.draw.line(obstacle_surf, (80, 60, 30), (30, 20), (10, 5), 3)  # Rama
        pygame.draw.line(obstacle_surf, (80, 60, 30), (70, 20), (90, 5), 3)  # Rama
        self.scene_surfaces['obstacle'] = obstacle_surf
        
        # Escena de clima
        weather_surf = pygame.Surface((RIGHT_PANEL_W - 10, 80), pygame.SRCALPHA)
        pygame.draw.rect(weather_surf, (150, 140, 100), (0, 0, RIGHT_PANEL_W - 10, 80))  # Niebla
        pygame.draw.circle(weather_surf, (220, 200, 100), (30, 20), 15)  # Sol tenue
        self.scene_surfaces['weather'] = weather_surf
        
        # Escena por defecto
        default_surf = pygame.Surface((RIGHT_PANEL_W - 10, 80), pygame.SRCALPHA)
        pygame.draw.rect(default_surf, (60, 50, 80), (20, 20, 80, 50), 2)
        pygame.draw.circle(default_surf, (150, 150, 150), (60, 45), 15)
        self.scene_surfaces['default'] = default_surf

    def _get_scene_for_encounter(self, encounter):
        """Determina qué escena mostrar según el tipo de encuentro."""
        if not encounter:
            return self.scene_surfaces.get('default')
        
        tags = encounter.tags if hasattr(encounter, 'tags') else []
        
        # Mapeo de tags a escenas
        if any(t in tags for t in ['police_check', 'police_speed', 'police_speed_fatal']):
            return self.scene_surfaces.get('police')
        elif any(t in tags for t in ['scenic_view', 'rest_stop']):
            return self.scene_surfaces.get('scenic')
        elif any(t in tags for t in ['fog', 'sandstorm', 'heat_shimmer', 'weather']):
            return self.scene_surfaces.get('weather')
        elif any(t in tags for t in ['fallen_tree', 'rockslide', 'muddy_road']):
            return self.scene_surfaces.get('obstacle')
        elif any(t in tags for t in ['breakdown', 'flat_tire', 'traffic_jam']):
            return self.scene_surfaces.get('danger')
        
        return self.scene_surfaces.get('default')

    def _get_avatar_for_encounter(self, encounter, passenger=None):
        """
        Determina qué avatar mostrar. Prioridad:
        1. Avatar del pasajero (si es un encuentro de hitchhiker)
        2. Avatar definido en el JSON del encuentro
        3. Avatar por defecto según tags (fallback)
        """
        # 1. Si hay un pasajero, usar su avatar
        if passenger and hasattr(passenger, 'avatar'):
            avatar_name = passenger.avatar.lower()
            if avatar_name in self.avatar_surfaces:
                return self.avatar_surfaces[avatar_name]
        
        # 2. Si el encuentro tiene un avatar definido en el JSON
        if hasattr(encounter, 'avatar') and encounter.avatar:
            avatar_name = encounter.avatar.lower()
            if avatar_name in self.avatar_surfaces:
                return self.avatar_surfaces[avatar_name]
                
        # 3. Fallbacks por tags si no hay nada específico
        tags = getattr(encounter, 'tags', [])
        if any(t in tags for t in ['police_check', 'police_speed']):
            return self.avatar_surfaces.get('cop')
        if 'hitchhiker' in tags:
            return self.avatar_surfaces.get('hiker_guy')
        if 'gas_station' in tags:
            return self.avatar_surfaces.get('gas_worker')
            
        return None

    def show(self, encounter, options_list, passenger=None):
        self.encounter = encounter
        self.options_list = options_list
        self.selected = 0
        self.outcome_text = ""
        self.outcome_timer = 0.0
        self._slide_y = H

        # Determinar avatar/escena (pasar pasajero si existe)
        self.current_avatar = self._get_avatar_for_encounter(encounter, passenger)
        self.current_scene = self._get_scene_for_encounter(encounter)

    def hide(self):
        self.encounter = None
        self.outcome_text = ""
        self.current_avatar = None
        self.current_scene = None

    def is_visible(self):
        return self.encounter is not None or self.outcome_timer > 0

    def handle_input(self, event) -> int | None:
        """Returns chosen option index or None."""
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_1, pygame.K_KP1):
            return self._choose(0)
        if event.key in (pygame.K_2, pygame.K_KP2):
            return self._choose(1)
        if event.key in (pygame.K_3, pygame.K_KP3):
            return self._choose(2)
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = max(0, self.selected - 1)
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = min(len(self.options_list) - 1, self.selected + 1)
        if event.key == pygame.K_RETURN:
            return self._choose(self.selected)
        return None

    def _choose(self, idx) -> int | None:
        if 0 <= idx < len(self.options_list):
            opt, available = self.options_list[idx]
            if available:
                return idx
        return None

    def show_outcome(self, result: dict, positive: bool):
        parts = []
        if 'fuel' in result and result['fuel'] != 0:
            sign = "+" if result['fuel'] > 0 else ""
            parts.append(f"Fuel {sign}{result['fuel']}")
        if 'sanity' in result and result['sanity'] != 0:
            sign = "+" if result['sanity'] > 0 else ""
            parts.append(f"Sanity {sign}{result['sanity']}")
        if 'money' in result and result['money'] != 0:
            sign = "+" if result['money'] > 0 else ""
            parts.append(f"Cash {sign}${result['money']}")
        if 'condition' in result and result['condition'] != 0:
            sign = "+" if result['condition'] > 0 else ""
            parts.append(f"Car {sign}{result['condition']}")
        self.outcome_text = " · ".join(parts) if parts else "Nothing changed."
        self.outcome_positive = positive
        self.outcome_timer = 2.5
        self.encounter = None

    def update(self, dt):
        if self.encounter:
            self._slide_y += (self._target_y - self._slide_y) * min(1, dt * 12)
        if self.outcome_timer > 0:
            self.outcome_timer -= dt

    def render(self, surface):
        if self.outcome_timer > 0:
            self._render_outcome(surface)
            return
        if not self.encounter:
            return
        self._render_panel(surface)
        self._render_right_panel(surface)

    def _render_panel(self, surface):
        """Renderiza el panel principal de decisiones."""
        panel_w = W - RIGHT_PANEL_W - 15  # Reducir ancho para dejar espacio al panel derecho
        panel_y = int(self._slide_y)
        panel_h = H - panel_y

        # Semi-transparent overlay
        overlay = pygame.Surface((W - RIGHT_PANEL_W - 5, panel_y), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        surface.blit(overlay, (0, 0))

        # Panel background
        pygame.draw.rect(surface, C_PANEL_BG, (5, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, C_PANEL_BRD, (5, panel_y, panel_w, panel_h), 2)

        # Title bar
        pygame.draw.rect(surface, C_TITLE_BG, (5, panel_y, panel_w, 20))
        title = self.font_title.render(self.encounter.title, True, C_HIGHLIGHT)
        surface.blit(title, (10, panel_y + 2))

        # Description
        y = panel_y + 24
        for line in _wrap_text(self.encounter.description, self.font_body, panel_w - 10):
            txt = self.font_body.render(line, True, C_TEXT)
            surface.blit(txt, (10, y))
            y += 13

        # Flavour
        y += 2
        for line in _wrap_text(self.encounter.flavour, self.font_body, panel_w - 10):
            txt = self.font_body.render(line, True, C_DIM)
            surface.blit(txt, (10, y))
            y += 12

        # Options
        y += 4
        for i, (opt, available) in enumerate(self.options_list):
            is_sel = (i == self.selected)
            col = C_TEXT if available else C_DISABLED
            bg = (40, 30, 60) if is_sel and available else C_PANEL_BG
            row_h = 18
            pygame.draw.rect(surface, bg, (8, y, panel_w - 6, row_h))
            if is_sel and available:
                pygame.draw.rect(surface, C_PANEL_BRD, (8, y, panel_w - 6, row_h), 1)

            # Key hint
            key_txt = self.font_key.render(f"[{i+1}]", True, C_HIGHLIGHT if available else C_DISABLED)
            surface.blit(key_txt, (12, y + 1))

            # Option text
            label = opt.text
            if opt.item_required and not available:
                label += " (no item)"
            txt = self.font_key.render(label, True, col)
            surface.blit(txt, (38, y + 1))

            # Colored dot for option type
            pygame.draw.circle(surface, opt.icon_color, (panel_w - 5, y + row_h // 2), 4)
            y += row_h + 2

        # Footer hint
        hint = self.font_body.render("↑↓ navigate · ENTER / 1 2 3 choose", True, C_DIM)
        surface.blit(hint, (10, H - 14))

    def _render_right_panel(self, surface):
        """Renderiza el panel derecho con avatar o escena."""
        panel_x = W - RIGHT_PANEL_W - 5
        panel_y = int(self._slide_y)
        panel_h = H - panel_y
        
        # Fondo del panel
        pygame.draw.rect(surface, C_PANEL_BG, (panel_x, panel_y, RIGHT_PANEL_W, panel_h))
        pygame.draw.rect(surface, C_PANEL_BRD, (panel_x, panel_y, RIGHT_PANEL_W, panel_h), 2)
        
        # Título del panel
        panel_title = self.font_body.render("SCENE", True, C_DIM)
        surface.blit(panel_title, (panel_x + 5, panel_y + 2))
        
        # Dibujar avatar o escena
        content_y = panel_y + 20
        
        if self.current_avatar:
            # Mostrar avatar
            surface.blit(self.current_avatar, (panel_x + 5, content_y))
        elif self.current_scene:
            # Mostrar escena
            surface.blit(self.current_scene, (panel_x + 5, content_y))

    def _render_outcome(self, surface):
        # Flash banner
        alpha = min(255, int(self.outcome_timer / 2.5 * 255))
        col = C_OUTCOME_POS if self.outcome_positive else C_OUTCOME_NEG
        bar = pygame.Surface((W, 30), pygame.SRCALPHA)
        bar.fill((*col, 180))
        surface.blit(bar, (0, H // 2 - 15))
        txt = self.font_title.render(self.outcome_text, True, (255, 255, 255))
        surface.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 10))
"""
High-Fidelity Dashboard Interface — Keep Driving.
Uses dash_inferior.png scaled proportionally (497x90) centred in a 640x90
black strip. Left/right black bars are 71px each.

*** GUÍA DE MODDING (MODIFICACIÓN) ***
- Este archivo (hud.py) controla cómo se dibujan los elementos de la interfaz en la pantalla.
- Si ves un método como `pygame.draw.rect(my_surface, (R, G, B), (X, Y, Ancho, Alto))`
  puedes cambiar los valores (R,G,B) para alterar colores, o X e Y para mover el elemento.
- Las imágenes base (dash_inferior, hud_road) se cargan en la función `_build_bg()`.
"""
import pygame
import math
import os
from core.config import BASE_RESOLUTION, MAX_FUEL, MAX_SANITY

W, H = BASE_RESOLUTION
DASH_H  = 90
DASH_Y  = H - DASH_H

# The asset is rendered into a 497px-wide area starting at x=71
# Scale factor from the 640x115 calibration coordinates → 497x90:
#   sx = 497/640 ≈ 0.7766
#   sy = 90 /115 ≈ 0.7826
# All element x-positions get 71px added (left black bar).

HUD_ASSET_W  = 497
HUD_OFFSET_X = (W - HUD_ASSET_W) // 2   # 71

def _scale_x(x640):
    """Convert a coord that was calibrated for the 640px-wide asset."""
    return HUD_OFFSET_X + int(x640 * HUD_ASSET_W / 640)

def _scale_y(y115):
    """Convert a coord that was calibrated for the 115px-tall asset."""
    return int(y115 * DASH_H / 115)


class HUD:
    def __init__(self, player, car_manager, world_map=None):
        self.player      = player
        self.car_manager = car_manager
        self.world_map   = world_map
        self.font_lcd    = pygame.font.Font(None, 20)
        self.font_tiny   = pygame.font.Font(None, 14)
        self.font_bold   = pygame.font.Font(None, 16)
        self._font_digital = pygame.font.Font(None, 24) # Reduced from 28
        self._pulse      = 0.0

        self.bg_img = None
        self.upper_img = None
        self.road_img = None
        self.player_sprite = None
        self.road_scroll = 0.0
        self._build_bg()

    def _build_bg(self):
        """Load dash_inferior.png, scale proportionally to 90px high,
        centre it on a 640x90 canvas with alpha."""
        src_path = os.path.join("assets", "ui", "dash_inferior.png")
        bg = pygame.Surface((W, DASH_H), pygame.SRCALPHA)
        if os.path.exists(src_path):
            src = pygame.image.load(src_path).convert_alpha()
            sw, sh = src.get_size()
            target_w = int(sw / sh * DASH_H)
            offset   = (W - target_w) // 2
            scaled   = pygame.transform.smoothscale(src, (target_w, DASH_H))
            bg.blit(scaled, (offset, 0))
        self.bg_img = bg

        # Load upper HUD
        upper_path = os.path.join("assets", "ui", "hud_upper.png")
        if os.path.exists(upper_path):
            self.upper_img = pygame.image.load(upper_path).convert_alpha()
        else:
            self.upper_img = None

        # Load road tile
        road_path = os.path.join("assets", "ui", "hud_road.png")
        if os.path.exists(road_path):
            self.road_img = pygame.image.load(road_path).convert_alpha()
        else:
            self.road_img = None

        # Load player sprite for interior view
        p_path = os.path.join("assets", "sprites", "portraits", "kid.png")
        if os.path.exists(p_path):
            p_src = pygame.image.load(p_path).convert_alpha()
            # It's huge, scale to seat size (approx 38x38)
            self.player_sprite = pygame.transform.smoothscale(p_src, (38, 38))
        else:
            self.player_sprite = None

    def update_fuel(self, **_):    pass
    def update_sanity(self, **_):  pass

    def update(self, dt):
        """Update road scroll and pulse animations."""
        self._pulse = (self._pulse + dt * 4) % (2 * math.pi)
        
        # Scroll road based on car speed / Desplazamiento de carretera basado en la velocidad
        if self.car_manager:
            speed = self.car_manager.car.speed # km/h
            # COMENTARIO PARA MODIFICAR: 
            # Multiplicador de velocidad de scroll visual. 
            # Reducido de 8.0 a 3.0 para que la velocidad del suelo sea más realista.
            self.road_scroll += speed * dt * 3.0
            if self.road_img:
                self.road_scroll %= self.road_img.get_width()

    def render(self, surface, music_manager=None):
        my_surface = pygame.Surface((W, DASH_H))
        
        # ── ROAD SECTION (Behind dashboard gap) ──────────────────────────────
        # COMENTARIO PARA MODIFICAR: 
        # rx y ry controlan donde comienza a dibujarse la carretera de fondo.
        # ry=67 está subido para que no se superponga con el marco del dashboard.
        # rw es el ancho (pixels), rh el alto (pixels).
        rx, ry = 110, 67 
        rw, rh = 370, 13
        
        # Draw road scrolling / Bucle para animar la carretera
        if self.road_img:
            tw = self.road_img.get_width()
            start_x = -(self.road_scroll % tw)
            for ox in range(int(start_x), rw, tw):
                my_surface.blit(self.road_img, (rx + ox, ry))
        else:
            # Procedural asphalt road with moving dashed lanes
            pygame.draw.rect(my_surface, (25, 25, 30), (rx, ry, rw, rh))
            pygame.draw.rect(my_surface, (15, 15, 20), (rx, ry, rw, rh), 1)
            
            # Moving dashes
            dash_w = 20
            dash_gap = 15
            cycle = dash_w + dash_gap
            offset = -(self.road_scroll % cycle)
            
            cy = ry + rh // 2
            for px in range(int(offset), rw, cycle):
                if px + dash_w > 0:
                    dx = max(0, px)
                    dw = min(dash_w, px + dash_w - dx)
                    if dx + dw <= rw:
                        pygame.draw.rect(my_surface, (200, 200, 100), (rx + dx, cy - 1, dw, 2))

        # ── RADAR ICONS (World Events) / EVENTOS DEL RADAR ──────────────────
        # Aquí determinamos dónde dibujar los puntos de colores en la mini carretera.
        # car_x representa la posición de tu ícono (el cuadrado azul). 
        # Multiplicar `rw * 0.25` lo coloca exactamente a un 25% (un cuarto) de distancia desde la izquierda.
        car_x = rx + int(rw * 0.25)
        
        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            radar_scale = rw / 5.0 # pixels per km (Cambiar el 5.0 comprime o expande el radar)
            dist_to_next = node.km_per_encounter - node.distance_since_last
            for i, enc in enumerate(node.encounters_remaining):
                dist = dist_to_next + i * node.km_per_encounter
                ex_pos = car_x + int(dist * radar_scale)
                if rx <= ex_pos <= rx + rw:
                    # COLORES PARA MODIFICAR: Aquí puedes cambiar de qué color es cada evento. (RGB)
                    color = (200, 100, 255) # Por defecto: Hitchhiker (morado)
                    if any(k in enc for k in ['fuel', 'gas', 'shop']): color = (255, 230, 100) # Amarillo (Gasolinera)
                    elif any(k in enc for k in ['accident', 'flat', 'rock', 'tree']): color = (255, 80, 50) # Rojo (Peligros)
                    pygame.draw.circle(my_surface, color, (ex_pos, ry + 6), 3) # ry+6 lo centra verticalmente en la vía
                    if dist < 0.2:
                        # Halo blanco si estás muy cerca del evento
                        pygame.draw.circle(my_surface, (255, 255, 255), (ex_pos, ry + 6), 5, 1)

            dist_to_end = node.length_km - node.km_driven
            sx_pos = car_x + int(dist_to_end * radar_scale)
            if rx <= sx_pos <= rx + rw:
                pygame.draw.rect(my_surface, (255, 215, 70), (sx_pos - 2, ry + 1, 6, 11))
                pygame.draw.rect(my_surface, (50, 40, 0), (sx_pos - 2, ry + 1, 6, 11), 1)

        # ── DASHBOARD BACKGROUND (With potential transparent gap if asset allows, or blit normally) ─────
        # Note: If dash_inferior.png is fully opaque, we still blit it. 
        # If it has a central gap, the road will show through.
        my_surface.blit(self.bg_img, (0, 0))
        
        # ── PLAYER ICON ON RADAR ───────────────────────────────────────────
        # COMENTARIO PARA MODIFICAR: El cuadrado azul es tu coche en la vista inferior.
        # Está fijado a la posición (car_x). Color actual: (100, 200, 255) (Celeste). Ancho 10, Alto 6.
        pygame.draw.rect(my_surface, (100, 200, 255), (car_x - 5, ry + 3, 10, 6))

        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            dist_to_next = max(0.0, node.km_per_encounter - node.distance_since_last)
            next_km_str = f"{dist_to_next:.1f} KM"
            driven_km_str = f"{node.km_driven:.1f} KM"
        else:
            next_km_str = "--"
            driven_km_str = "--"

        # ── LOWER HUD: INFO TEXTS AL COSTADO DEL RADAR ──────────────────────
        # COMENTARIO PARA MODIFICAR: 
        # Aquí se imprimen los textos en las zonas negras laterales en el HUD inferior
        # Textos ajustados 60px hacia arriba y el derecho movido 20px.
        txt_l1 = self.font_tiny.render("DRIVEN:", True, (120, 130, 140))
        txt_l2 = self.font_tiny.render(driven_km_str, True, (120, 130, 140))
        my_surface.blit(txt_l1, (20, ry - 54))
        my_surface.blit(txt_l2, (20, ry - 43))
        
        txt_r1 = self.font_tiny.render("NEXT POI:", True, (120, 130, 140))
        txt_r2 = self.font_tiny.render(next_km_str, True, (120, 130, 140))
        # Desplazados 60px adicionales a la derecha (605 -> 665)
        my_surface.blit(txt_r1, (580, ry - 54))
        my_surface.blit(txt_r2, (580, ry - 43))

        sanity_pct = self.player.sanity / MAX_SANITY
        speed_val  = int(self.car_manager.car.speed)

        # Render upper HUD if available / Renderizado del panel superior
        if self.upper_img:
            surface.blit(self.upper_img, (0, 0))
            
            # ── UPPER HUD: PLAYER AVATAR (In-Seat) / AVATAR DEL CONDUCTOR ───
            # COMENTARIO PARA MODIFICAR: 
            # Cambia (120, 10) para mover el avatar de asiento a izquierda, derecha, etc.
            if self.player_sprite:
                surface.blit(self.player_sprite, (120, 10))
            else:
                pygame.draw.rect(surface, (100, 150, 200), (120, 10, 38, 38), 2)

        # ENERGY: adjusted based on test27
        ex, ey = 98, 23
        bw, bh, gap_x = 7, 10, 4
        for i in range(5):
            filled = sanity_pct >= (i + 1) / 5.0
            col = (200, 40, 40) if i >= 4 else (50, 160, 80)
            dim = (40, 10, 10)  if i >= 4 else (15, 30, 15)
            pygame.draw.rect(my_surface, col if filled else dim,
                             (ex + i * (bw + gap_x), ey, bw, bh))

        # STATUS: adjusted based on test27
        sx, sy = 77, 46
        sw, sh, sgap = 13, 11, 5
        for i in range(5):
            bx = sx + i * (sw + sgap)
            pygame.draw.rect(my_surface, (20, 25, 20), (bx, sy, sw, sh))
            pygame.draw.rect(my_surface, (40, 50, 40), (bx, sy, sw, sh), 1)

        # LCD — adjusted y and spacing
        lx, ly = 210, 11 # Lowered ly from 9 to 11
        lw = 205

        date_str = "SUN, MAR 15TH, 04:23 PM"
        txt = self.font_lcd.render(date_str, True, (80, 210, 80))
        my_surface.blit(txt, (lx + (lw - txt.get_width()) // 2, ly))

        # LOC: bottom-left of LCD
        loc_msg = f"LOC: {self.player.current_location[:18]}"
        loc_txt = self.font_tiny.render(loc_msg, True, (60, 170, 60))
        my_surface.blit(loc_txt, (lx + 4, ly + 26))

        # ── LCD: SPEED / TABLA DE VELOCIDAD ──────────────────────────────────
        # COMENTARIO PARA MODIFICAR: 
        # Esta sección formatea y colorea los kilómetros por hora.
        # Si la velocidad es > 100 pasa a rojo intenso (255, 60, 60), de normal verde claro (120, 255, 120).
        # Modificar esos RGB para cambiar el aspecto. Modificar `ly+21` para ajustar la posición de altura.
        spd_str = f"{speed_val:03d}"
        spd_col = (255, 60, 60) if speed_val > 100 else (120, 255, 120)
        spd_txt = self._font_digital.render(spd_str, True, spd_col)
        kmh_txt = self.font_tiny.render("KM/H", True, (60, 170, 60))
        sx2 = lx + lw - max(spd_txt.get_width(), kmh_txt.get_width()) - 8
        my_surface.blit(kmh_txt, (sx2, ly + 21)) # Lowered from 18 to 21
        my_surface.blit(spd_txt, (sx2, ly + 28)) # Lowered from 26 to 28

        
        # ── RIGHT PANEL  ─────────────────────────────────────────────────────
        # CAR: adjusted based on test27 (7 columns, 2 rows)
        cx, cy = 484, 24
        cw, ch, cg_x, cg_y = 5, 5, 3, 3
        cond_pct = self.car_manager.condition / 100.0
        for idx in range(14):
            filled = cond_pct >= (idx + 1) / 14.0
            col    = (50, 160, 220) if filled else (15, 30, 45)
            row, col_pos = divmod(idx, 7)
            bx = cx + col_pos * (cw + cg_x)
            by = cy + row     * (ch + cg_y)
            pygame.draw.rect(my_surface, col, (bx, by, cw, ch))

        # ── GAS NEEDLE / AGUJA DE COMBUSTIBLE ──────────────────────────────
        # COMENTARIO PARA MODIFICAR: 
        # Dibuja la aguja rotacional midiendo el centro 'pivot_x=523, pivot_y=64' del asset visual 640x90.
        # El consumo dicta 'fuel_pct', moviendo el ángulo entre 'angle_start' y 'angle_end'.
        # Color aguja: rojo oscurecido (230, 40, 40), de ancho 2. Color centro: negro (10, 10, 10).
        fuel_pct  = self.car_manager.fuel / 100.0
        pivot_x   = 523
        pivot_y   = 64
        needle_r  = 18 # Longitud de la aguja en píxeles.

        angle_start = math.pi * 1.17
        angle_end   = math.pi * 1.83
        curr_angle  = angle_start + (angle_end - angle_start) * fuel_pct
        ex2 = pivot_x + int(math.cos(curr_angle) * needle_r)
        ey2 = pivot_y + int(math.sin(curr_angle) * needle_r)

        pygame.draw.line(my_surface, (230, 40, 40), (pivot_x, pivot_y), (ex2, ey2), 2)
        pygame.draw.circle(my_surface, (10, 10, 10), (pivot_x, pivot_y), 3)

        # ── STATUS TEXT ──────────────────────────────────────────────────────
        st_txt = self.font_tiny.render("DRIVE" if speed_val > 0 else "IDLE",
                                       True, (160, 170, 180))
        # 60 pixels a la izquierda y 20 pixeles arriba de la original
        my_surface.blit(st_txt, (HUD_OFFSET_X + 4 - 60, DASH_H - 12 - 20))

        if music_manager and music_manager.now_playing:
            track = music_manager.now_playing
            m_txt = self.font_tiny.render(f"TAPE: {track['title']}", True, (130, 140, 150))
            surface.blit(m_txt, (W - m_txt.get_width() - 4, H - 12))

        # Paint the composed HUD onto the main canvas
        surface.blit(my_surface, (0, DASH_Y))

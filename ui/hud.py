"""
High-Fidelity Dashboard Interface — Keep Driving.
Uses dash_inferior.png scaled proportionally (497x90) centred in a 640x90
black strip. Left/right black bars are 71px each.
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
        p_path = os.path.join("assets", "sprites", "portraits", "agent.png")
        if os.path.exists(p_path):
            p_src = pygame.image.load(p_path).convert_alpha()
            # It's huge, scale to seat size (approx 24x24)
            self.player_sprite = pygame.transform.smoothscale(p_src, (24, 24))
        else:
            self.player_sprite = None

    def update_fuel(self, **_):    pass
    def update_sanity(self, **_):  pass

    def update(self, dt):
        """Update road scroll and pulse animations."""
        self._pulse = (self._pulse + dt * 4) % (2 * math.pi)
        
        # Scroll road based on car speed
        if self.car_manager:
            speed = self.car_manager.car.speed # km/h
            # Visual speed scaling: 100km/h = ~120px/sec scroll
            self.road_scroll += speed * dt * 1.2
            if self.road_img:
                self.road_scroll %= self.road_img.get_width()

    def render(self, surface, music_manager=None):
        my_surface = pygame.Surface((W, DASH_H))
        
        # ── ROAD SECTION (Behind dashboard gap) ──────────────────────────────
        rx, ry = 110, 67 # Raised ry higher to align perfectly behind the gap
        rw, rh = 370, 13 # road height. rw will be 380
        
        # Dashboard gap starts near x=110 and ends near x=490 -> rw = 380
        rw = 370
        
        # Draw road scrolling
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

        # ── RADAR ICONS (World Events) ─────────────────────────────────────
        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            radar_scale = rw / 5.0 # pixels per km
            dist_to_next = node.km_per_encounter - node.distance_since_last
            for i, enc in enumerate(node.encounters_remaining):
                dist = dist_to_next + i * node.km_per_encounter
                if dist < 5.0:
                    ex_pos = rx + int(dist * radar_scale)
                    color = (200, 100, 255) # Hitchhiker
                    if any(k in enc for k in ['fuel', 'gas', 'shop']): color = (255, 230, 100)
                    elif any(k in enc for k in ['accident', 'flat', 'rock', 'tree']): color = (255, 80, 50)
                    pygame.draw.circle(my_surface, color, (ex_pos, ry + 6), 3)
                    if dist < 0.2:
                        pygame.draw.circle(my_surface, (255, 255, 255), (ex_pos, ry + 6), 5, 1)

            dist_to_end = node.length_km - node.km_driven
            if dist_to_end < 5.0:
                sx_pos = rx + int(dist_to_end * radar_scale)
                pygame.draw.rect(my_surface, (255, 215, 70), (sx_pos - 2, ry + 1, 6, 11))
                pygame.draw.rect(my_surface, (50, 40, 0), (sx_pos - 2, ry + 1, 6, 11), 1)

        # ── DASHBOARD BACKGROUND (With potential transparent gap if asset allows, or blit normally) ─────
        # Note: If dash_inferior.png is fully opaque, we still blit it. 
        # If it has a central gap, the road will show through.
        my_surface.blit(self.bg_img, (0, 0))
        
        # ── PLAYER ICON ON RADAR ───────────────────────────────────────────
        pygame.draw.rect(my_surface, (100, 200, 255), (rx + 4, ry + 3, 10, 6))

        # ── TEXT LABELS (Left and Right of the Road Gap) ───────────────────
        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            dist_to_next = max(0.0, node.km_per_encounter - node.distance_since_last)
            next_km_str = f"NEXT POI: {dist_to_next:.1f} KM"
            driven_km_str = f"DRIVEN: {node.km_driven:.1f} KM"
        else:
            next_km_str = "NEXT POI: --"
            driven_km_str = "DRIVEN: --"
            
        txt_l = self.font_tiny.render(driven_km_str, True, (120, 130, 140))
        my_surface.blit(txt_l, (20, ry + 2))
        
        txt_r = self.font_tiny.render(next_km_str, True, (120, 130, 140))
        my_surface.blit(txt_r, (495, ry + 2))

        sanity_pct = self.player.sanity / MAX_SANITY
        speed_val  = int(self.car_manager.car.speed)

        # Render upper HUD if available
        if self.upper_img:
            surface.blit(self.upper_img, (0, 0))
            
            # ── UPPER HUD: PLAYER AVATAR (In-Seat) ──────────────────────────
            # Render player sprite in the front passenger seat (delantero superior)
            # Area in 640x90 asset is approx (115, 12, 24, 24)
            if self.player_sprite:
                surface.blit(self.player_sprite, (115, 12))
            else:
                # Fallback if image fails
                pygame.draw.rect(surface, (100, 150, 200), (115, 12, 24, 24), 2)

            # ── UPPER HUD: DIALOGUE / DESC ──────────────────────────────────
            # SITUATION REPORT: Central-Top
            diag_title = self.font_bold.render("SITUATION REPORT", True, (200, 210, 220))
            surface.blit(diag_title, (320 - diag_title.get_width() // 2, 5))
            
            # DESCRIPTION: Central-Bottom
            desc_dummy = "Scanning frequencies..." if speed_val > 100 else "Route stable. Maintaining cruise speed."
            desc_txt = self.font_tiny.render(desc_dummy, True, (100, 110, 120))
            surface.blit(desc_txt, (320 - desc_txt.get_width() // 2, 68))

            # ── UPPER HUD: SYSTEM INFO (Left Panel) ─────────────────────────
            info_txt = self.font_lcd.render("REAR VIEW", True, (100, 100, 120))
            surface.blit(info_txt, (15, 15))
            
            cond_str = f"SYSTEMS: {int(self.car_manager.condition)}%"
            cond_txt = self.font_tiny.render(cond_str, True, (80, 80, 90))
            surface.blit(cond_txt, (15, 35))

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

        # Speed: bottom-right of LCD
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

        # GAS needle — pivot measured directly on 640x90 asset
        fuel_pct  = self.car_manager.fuel / 100.0
        pivot_x   = 523
        pivot_y   = 64
        needle_r  = 18

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
        my_surface.blit(st_txt, (HUD_OFFSET_X + 4, DASH_H - 12))

        if music_manager and music_manager.now_playing:
            track = music_manager.now_playing
            m_txt = self.font_tiny.render(f"TAPE: {track['title']}", True, (130, 140, 150))
            surface.blit(m_txt, (W - m_txt.get_width() - 4, H - 12))

        # Paint the composed HUD onto the main canvas
        surface.blit(my_surface, (0, DASH_Y))

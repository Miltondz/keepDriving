"""
High-Fidelity Dashboard Interface — Keep Driving.
Uses dash_inferior.png scaled proportionally (497x90) centred in a 640x90
black strip. Left/right black bars are 71px each.
"""
import pygame
import math
import os
from core.config import BASE_RESOLUTION, MAX_FUEL, MAX_SANITY, MAX_PASSENGERS

W, H = BASE_RESOLUTION
DASH_H  = 90
DASH_Y  = H - DASH_H

HUD_ASSET_W  = 497
HUD_OFFSET_X = (W - HUD_ASSET_W) // 2   # 71

class HUD:
    def __init__(self, player, car_manager, world_map=None, inventory=None):
        self.player = player
        self.car_manager = car_manager
        self.world_map = world_map
        self.inventory = inventory
        self.font_lcd = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 14)
        self.font_bold = pygame.font.Font(None, 16)
        self._font_digital = pygame.font.Font(None, 24)
        self._pulse = 0.0

        self.bg_img = None
        self.upper_img = None
        self.road_img = None
        self.road_scroll = 0.0
        
        self.inventory_grid_rows = 4
        self.inventory_grid_cols = 2
        self.inventory_slot_size = 20
        self.inventory_grid_x = 25
        self.inventory_grid_y = 10
        self.inventory_grid_h_bonus = 15 # Requested elongation
        
        self.avatar_surfs = {}
        self._build_bg()

    def _build_bg(self):
        """Load UI assets and all character portraits."""
        src_path = os.path.join("assets", "ui", "dash_inferior.png")
        bg = pygame.Surface((W, DASH_H), pygame.SRCALPHA)
        if os.path.exists(src_path):
            src = pygame.image.load(src_path).convert_alpha()
            sw, sh = src.get_size()
            target_w = int(sw / sh * DASH_H)
            offset = (W - target_w) // 2
            scaled = pygame.transform.smoothscale(src, (target_w, DASH_H))
            bg.blit(scaled, (offset, 0))
        self.bg_img = bg

        upper_path = os.path.join("assets", "ui", "hud_upper.png")
        if os.path.exists(upper_path):
            self.upper_img = pygame.image.load(upper_path).convert_alpha()

        road_path = os.path.join("assets", "ui", "hud_road.png")
        if os.path.exists(road_path):
            self.road_img = pygame.image.load(road_path).convert_alpha()

        # Load and scale all character portraits
        portraits_dir = os.path.join("assets", "sprites", "portraits")
        if os.path.exists(portraits_dir):
            for f in os.listdir(portraits_dir):
                if f.endswith(".png"):
                    name = f.replace(".png", "")
                    try:
                        img = pygame.image.load(os.path.join(portraits_dir, f)).convert_alpha()
                        # Small version for seat indicators (25, 27, 32, 38)
                        s25 = pygame.transform.smoothscale(img, (25, 25))
                        s27 = pygame.transform.smoothscale(img, (27, 27))
                        s32 = pygame.transform.smoothscale(img, (32, 32))
                        s38 = pygame.transform.smoothscale(img, (38, 38))
                        self.avatar_surfs[name] = {"25": s25, "27": s27, "32": s32, "38": s38}
                    except: pass

    def update_fuel(self, **_): pass
    def update_sanity(self, **_): pass

    def _render_inventory_grid(self, surface):
        if not self.inventory: return
        grid_w = self.inventory_grid_cols * self.inventory_slot_size + 2
        grid_h = self.inventory_grid_rows * self.inventory_slot_size + 2 + self.inventory_grid_h_bonus
        bg_rect = pygame.Rect(self.inventory_grid_x - 1, self.inventory_grid_y - 1, grid_w, grid_h)
        pygame.draw.rect(surface, (15, 15, 20), bg_rect)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 1)
        
        items = self.inventory.items
        slot_idx = 0
        v_offset = (self.inventory_grid_h_bonus // 2) # Adjust internal slots
        for row in range(self.inventory_grid_rows):
            for col in range(self.inventory_grid_cols):
                sx = self.inventory_grid_x + col * self.inventory_slot_size
                sy = self.inventory_grid_y + row * self.inventory_slot_size + v_offset
                slot_rect = pygame.Rect(sx, sy, self.inventory_slot_size - 2, self.inventory_slot_size - 2)
                pygame.draw.rect(surface, (30, 30, 40), slot_rect)
                pygame.draw.rect(surface, (50, 50, 70), slot_rect, 1)
                if slot_idx < len(items):
                    item = items[slot_idx]
                    if not item.exhausted:
                        pygame.draw.rect(surface, item.icon_color, (sx + 4, sy + 4, 12, 12))
                        if 0 < item.uses < 3:
                            u_txt = self.font_tiny.render(str(item.uses), True, (255, 255, 255))
                            surface.blit(u_txt, (sx + 12, sy))
                slot_idx += 1

    def _render_passengers(self, surface):
        """Render hitchhikers in seats with their avatars."""
        passengers = getattr(self.player, 'passengers', {})
        col_x = 80
        col_y = 15  # Lowered +5px requested
        seat_size = 27
        gap = seat_size + 3
        
        for seat_idx in range(MAX_PASSENGERS):
            passenger = passengers.get(seat_idx)
            if seat_idx < 3:
                # First 3: Vertical column
                sx = col_x
                sy = col_y + seat_idx * gap
            else:
                # 4th seat: Moved +3px down
                sx = 125 
                sy = 78  # Adjusted as requested
            
            # Seat background
            pygame.draw.rect(surface, (30, 30, 40), (sx, sy, seat_size, seat_size))
            pygame.draw.rect(surface, (50, 50, 70), (sx, sy, seat_size, seat_size), 1)
            
            if passenger:
                avatar_key = getattr(passenger, 'avatar', None)
                if avatar_key and avatar_key in self.avatar_surfs:
                    surface.blit(self.avatar_surfs[avatar_key]["27"], (sx, sy))
                else:
                    # Fallback to initials
                    pygame.draw.rect(surface, getattr(passenger, 'color', (100,100,100)), (sx+2, sy+2, seat_size-4, seat_size-4))
                    ini = self.font_tiny.render(passenger.name[0], True, (255, 255, 255))
                    surface.blit(ini, (sx + 8, sy + 6))

    def update(self, dt):
        self._pulse = (self._pulse + dt * 4) % (2 * math.pi)
        if self.car_manager:
            speed = self.car_manager.car.speed
            self.road_scroll += speed * dt * 3.0
            if self.road_img:
                self.road_scroll %= self.road_img.get_width()

    def render(self, surface, music_manager, time_of_day, current_dialogue=None):
        my_surface = pygame.Surface((W, DASH_H))
        rx, ry = 110, 67 
        rw, rh = 370, 13
        
        if self.road_img:
            tw = self.road_img.get_width()
            start_x = -(self.road_scroll % tw)
            for ox in range(int(start_x), rw, tw):
                my_surface.blit(self.road_img, (rx + ox, ry))
        else:
            pygame.draw.rect(my_surface, (25, 25, 30), (rx, ry, rw, rh))
            
        car_x = rx + int(rw * 0.25)
        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            radar_scale = rw / 5.0
            dist_to_next = node.km_per_encounter - node.distance_since_last
            for i, enc in enumerate(node.encounters_remaining):
                dist = dist_to_next + i * node.km_per_encounter
                ex_pos = car_x + int(dist * radar_scale)
                if rx <= ex_pos <= rx + rw:
                    color = (200, 100, 255)
                    if any(k in enc for k in ['fuel', 'gas', 'shop']): color = (255, 230, 100)
                    elif any(k in enc for k in ['accident', 'flat', 'rock']): color = (255, 80, 50)
                    pygame.draw.circle(my_surface, color, (ex_pos, ry + 6), 3)

        my_surface.blit(self.bg_img, (0, 0))
        pygame.draw.rect(my_surface, (100, 200, 255), (car_x - 5, ry + 3, 10, 6))

        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            driven_km_str = f"{node.km_driven:.1f} KM"
            next_km_str = f"{max(0.0, node.km_per_encounter - node.distance_since_last):.1f} KM"
        else: driven_km_str, next_km_str = "--", "--"

        txt_l2 = self.font_tiny.render(driven_km_str, True, (120, 130, 140))
        my_surface.blit(txt_l2, (20, ry - 43))
        txt_r2 = self.font_tiny.render(next_km_str, True, (120, 130, 140))
        my_surface.blit(txt_r2, (580, ry - 43))

        if self.upper_img: surface.blit(self.upper_img, (0, 0))
        self._render_inventory_grid(surface)
        self._render_passengers(surface)

        # Player Avatar
        p_avatar = getattr(self.player, 'avatar', 'kid')
        if p_avatar in self.avatar_surfs:
            surface.blit(self.avatar_surfs[p_avatar]["38"], (125, 10))
        else:
            pygame.draw.rect(surface, (100, 150, 200), (125, 10, 38, 38), 2)

        sanity_pct = self.player.sanity / MAX_SANITY
        speed_val  = int(self.car_manager.car.speed)
        ex, ey = 180, 10
        for i in range(5):
            col = (200, 40, 40) if i >= 4 else (50, 160, 80)
            dim = (40, 10, 10)  if i >= 4 else (15, 30, 15)
            pygame.draw.rect(my_surface, col if sanity_pct >= (i+1)/5.0 else dim, (ex + i * 8, ey, 6, 8))

        lx, ly, lw = 210, 11, 205
        # Dynamic Time Calculation from time_of_day (0.0 to 1.0)
        total_hours = (time_of_day * 24.0 + 8.0) % 24.0  # Start at 8 AM
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        period = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12
        if display_hours == 0: display_hours = 12
        time_str = f"SUN, MAR 15TH, {display_hours:02d}:{minutes:02d} {period}"
        
        date_txt = self.font_lcd.render(time_str, True, (80, 210, 80))
        my_surface.blit(date_txt, (lx + (lw - date_txt.get_width()) // 2, ly))
        
        spd_col = (255, 60, 60) if speed_val > 100 else (120, 255, 120)
        spd_txt = self._font_digital.render(f"{speed_val:03d}", True, spd_col)
        my_surface.blit(spd_txt, (lx + lw - 50, ly + 28))

        # Dialogue overlay: under the rearview mirror (center area)
        active_line = current_dialogue
        if active_line:
            # Main text
            d_txt = self.font_tiny.render(f"{active_line.speaker}: {active_line.text}", True, (200, 220, 255))
            my_surface.blit(d_txt, (rx + (rw - d_txt.get_width()) // 2, 43))
            # Prompt hint if it's a multi-line story
            hint_txt = self.font_tiny.render("(Click to continue)", True, (100, 100, 150))
            my_surface.blit(hint_txt, (rx + (rw - hint_txt.get_width()) // 2, 54))
        fuel_pct = self.car_manager.fuel / 100.0
        pivot_x, pivot_y, needle_r = 523, 64, 18
        ang = 1.17 * math.pi + (1.83 * math.pi - 1.17 * math.pi) * fuel_pct
        pygame.draw.line(my_surface, (230, 40, 40), (pivot_x, pivot_y), 
                         (pivot_x + int(math.cos(ang)*needle_r), pivot_y + int(math.sin(ang)*needle_r)), 2)
        pygame.draw.circle(my_surface, (10, 10, 10), (pivot_x, pivot_y), 3)

        if music_manager and music_manager.now_playing:
            m_txt = self.font_tiny.render(f"TAPE: {music_manager.now_playing['title']}", True, (130, 140, 150))
            surface.blit(m_txt, (W - m_txt.get_width() - 4, H - 12))

        surface.blit(my_surface, (0, DASH_Y))

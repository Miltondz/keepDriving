"""
High-Fidelity Dashboard Interface — Keep Driving.
Layout: Radio unit (0-142) | Dashboard (143-639)
The dash_inferior.png is 640x90 with 71px black margins on each side.
We crop the 497px center and place it at x=143.
"""
import pygame
import math
import os
from core.config import BASE_RESOLUTION, MAX_FUEL, MAX_SANITY, MAX_PASSENGERS

W, H = BASE_RESOLUTION
DASH_H  = 90
DASH_Y  = H - DASH_H

# Layout zones
RADIO_W = 143          # Left panel: radio unit
DASH_X  = RADIO_W      # Dashboard starts here (143)
DASH_CONTENT_W = 497   # Width of dashboard content from asset

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
        self._font_radio = pygame.font.Font(None, 11)
        self._pulse = 0.0

        self.show_zoomed_cassette = False
        self.bg_img = None
        self.upper_img = None
        self.road_img = None
        self.radio_unit_img = None
        self.road_scroll = 0.0
        
        self.inventory_grid_rows = 4
        self.inventory_grid_cols = 2
        self.inventory_slot_size = 20
        self.inventory_grid_x = 25
        self.inventory_grid_y = 10
        self.inventory_grid_h_bonus = 15
        
        self.avatar_surfs = {}
        self.cassette_img = None
        self.tape_cache = {}
        self._build_bg()

    def _build_bg(self):
        """Load UI assets and all character portraits."""
        # --- Dashboard background ---
        src_path = os.path.join("assets", "ui", "dash_inferior.png")
        bg = pygame.Surface((W, DASH_H), pygame.SRCALPHA)
        if os.path.exists(src_path):
            src = pygame.image.load(src_path).convert_alpha()
            sw, sh = src.get_size()
            if sw >= 497 and sh >= DASH_H:
                # Crop center 497px from the 640px-wide asset
                margin = (sw - 497) // 2
                content_src = src.subsurface(pygame.Rect(margin, 0, 497, DASH_H))
                bg.blit(content_src, (DASH_X, 0))
            else:
                # Fallback: scale and place right-aligned
                scaled = pygame.transform.smoothscale(src, (497, DASH_H))
                bg.blit(scaled, (DASH_X, 0))
        self.bg_img = bg

        # --- Radio unit (use cropped version if available) ---
        radio_path = os.path.join("assets", "ui", "radio_cropped.png")
        if not os.path.exists(radio_path):
            radio_path = os.path.join("assets", "ui", "radio_unit.png")
        if os.path.exists(radio_path):
            self.radio_unit_img = pygame.image.load(radio_path).convert_alpha()
            self.radio_unit_img = pygame.transform.smoothscale(self.radio_unit_img, (RADIO_W, DASH_H))

        # --- Upper HUD ---
        upper_path = os.path.join("assets", "ui", "hud_upper.png")
        if os.path.exists(upper_path):
            self.upper_img = pygame.image.load(upper_path).convert_alpha()

        # --- Road tile ---
        road_path = os.path.join("assets", "ui", "hud_road.png")
        if os.path.exists(road_path):
            self.road_img = pygame.image.load(road_path).convert_alpha()

        # --- Character portraits ---
        portraits_dir = os.path.join("assets", "sprites", "portraits")
        if os.path.exists(portraits_dir):
            for f in os.listdir(portraits_dir):
                if f.endswith(".png"):
                    name = f.replace(".png", "")
                    try:
                        img = pygame.image.load(os.path.join(portraits_dir, f)).convert_alpha()
                        s25 = pygame.transform.smoothscale(img, (25, 25))
                        s27 = pygame.transform.smoothscale(img, (27, 27))
                        s32 = pygame.transform.smoothscale(img, (32, 32))
                        s38 = pygame.transform.smoothscale(img, (38, 38))
                        self.avatar_surfs[name] = {"25": s25, "27": s27, "32": s32, "38": s38}
                    except: pass

        # --- Cassette template ---
        cassette_path = os.path.join("assets", "ui", "cassette_template.png")
        if os.path.exists(cassette_path):
            self.cassette_img = pygame.image.load(cassette_path).convert_alpha()
            self.cassette_img = pygame.transform.smoothscale(self.cassette_img, (32, 20))

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
        v_offset = (self.inventory_grid_h_bonus // 2)
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
        col_y = 15
        seat_size = 27
        gap = seat_size + 3
        
        for seat_idx in range(MAX_PASSENGERS):
            passenger = passengers.get(seat_idx)
            if seat_idx < 3:
                sx = col_x
                sy = col_y + seat_idx * gap
            else:
                sx = 125
                sy = 78
            
            pygame.draw.rect(surface, (30, 30, 40), (sx, sy, seat_size, seat_size))
            pygame.draw.rect(surface, (50, 50, 70), (sx, sy, seat_size, seat_size), 1)
            
            if passenger:
                avatar_key = getattr(passenger, 'avatar', None)
                if avatar_key and avatar_key in self.avatar_surfs:
                    surface.blit(self.avatar_surfs[avatar_key]["27"], (sx, sy))
                else:
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
        my_surface = pygame.Surface((W, DASH_H), pygame.SRCALPHA)

        # ── Mini-road (relative to dashboard zone, not radio) ──────────
        # Original coords in 497px asset: road at ~x=39, y=67, w=370
        # Mapped to screen: DASH_X + 39 = 182
        rx, ry = DASH_X + 39, 67
        rw, rh = 370, 13
        
        if self.road_img:
            tw = self.road_img.get_width()
            start_x = -(self.road_scroll % tw)
            for ox in range(int(start_x), rw, tw):
                my_surface.blit(self.road_img, (rx + ox, ry))
        else:
            pygame.draw.rect(my_surface, (25, 25, 30), (rx, ry, rw, rh))

        # Car marker on mini-road
        car_x = rx + int(rw * 0.25)

        # Encounter dots on radar
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

        # ── Blit background assets ─────────────────────────────────────
        my_surface.blit(self.bg_img, (0, 0))
        if self.radio_unit_img:
            my_surface.blit(self.radio_unit_img, (0, 0))

        # Car blue dot on mini-road (over the asset)
        pygame.draw.rect(my_surface, (100, 200, 255), (car_x - 5, ry + 3, 10, 6))

        # ── KM labels ─────────────────────────────────────────────────
        if self.world_map and self.world_map.is_road:
            node = self.world_map.current_node
            driven_km_str = f"{node.km_driven:.1f} KM"
            next_km_str = f"{max(0.0, node.km_per_encounter - node.distance_since_last):.1f} KM"
        else:
            driven_km_str, next_km_str = "--", "--"

        txt_l2 = self.font_tiny.render(driven_km_str, True, (120, 130, 140))
        my_surface.blit(txt_l2, (DASH_X + 5, ry - 43))
        txt_r2 = self.font_tiny.render(next_km_str, True, (120, 130, 140))
        my_surface.blit(txt_r2, (W - 50, ry - 43))

        # ── Upper HUD (full screen) ───────────────────────────────────
        if self.upper_img: surface.blit(self.upper_img, (0, 0))
        self._render_inventory_grid(surface)
        self._render_passengers(surface)

        # Player Avatar
        p_avatar = getattr(self.player, 'avatar', 'kid')
        if p_avatar in self.avatar_surfs:
            surface.blit(self.avatar_surfs[p_avatar]["38"], (125, 10))
        else:
            pygame.draw.rect(surface, (100, 150, 200), (125, 10, 38, 38), 2)

        # ── Dashboard instruments (all relative to DASH_X) ────────────
        sanity_pct = self.player.sanity / MAX_SANITY
        speed_val  = int(self.car_manager.car.speed)

        # Energy bars: original x=109 in 497px asset → DASH_X+109 = 252
        ex, ey = DASH_X + 109, 10
        for i in range(5):
            col = (200, 40, 40) if i >= 4 else (50, 160, 80)
            dim = (40, 10, 10)  if i >= 4 else (15, 30, 15)
            pygame.draw.rect(my_surface, col if sanity_pct >= (i+1)/5.0 else dim, (ex + i * 8, ey, 6, 8))

        # LCD screen: original x=139 in 497px asset → DASH_X+139 = 282
        lx, ly, lw = DASH_X + 139, 11, 205

        # Date/Time
        total_hours = (time_of_day * 24.0 + 8.0) % 24.0
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        period = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12
        if display_hours == 0: display_hours = 12
        time_str = f"SUN, MAR 15TH, {display_hours:02d}:{minutes:02d} {period}"
        
        date_txt = self.font_lcd.render(time_str, True, (80, 210, 80))
        my_surface.blit(date_txt, (lx + (lw - date_txt.get_width()) // 2, ly))
        
        # Speed
        spd_col = (255, 60, 60) if speed_val > 100 else (120, 255, 120)
        spd_txt = self._font_digital.render(f"{speed_val:03d}", True, spd_col)
        my_surface.blit(spd_txt, (lx + lw - 50, ly + 28))

        # Dialogue overlay
        active_line = current_dialogue
        if active_line:
            d_txt = self.font_tiny.render(f"{active_line.speaker}: {active_line.text}", True, (200, 220, 255))
            my_surface.blit(d_txt, (rx + (rw - d_txt.get_width()) // 2, 43))
            hint_txt = self.font_tiny.render("(Click to continue)", True, (100, 100, 150))
            my_surface.blit(hint_txt, (rx + (rw - hint_txt.get_width()) // 2, 54))

        # Fuel gauge: original pivot x=452 in 497px asset → DASH_X+452 = 595
        fuel_pct = self.car_manager.fuel / 100.0
        pivot_x, pivot_y, needle_r = DASH_X + 452, 64, 18
        ang = 1.17 * math.pi + (1.83 * math.pi - 1.17 * math.pi) * fuel_pct
        pygame.draw.line(my_surface, (230, 40, 40), (pivot_x, pivot_y), 
                         (pivot_x + int(math.cos(ang)*needle_r), pivot_y + int(math.sin(ang)*needle_r)), 2)
        pygame.draw.circle(my_surface, (10, 10, 10), (pivot_x, pivot_y), 3)

        # ── Radio panel (left zone: 0 to RADIO_W) ─────────────────────
        # Cropped asset 530x324 scaled to 143x90
        # LCD area: x=18..101, y=8..75 (83x67 px)
        radio_surf = pygame.Surface((RADIO_W, DASH_H), pygame.SRCALPHA)
        lcd_x, lcd_y = 10, 8
        lcd_w, lcd_h = 100, 67
        # Create a clip surface for LCD text so nothing bleeds outside
        lcd_clip = pygame.Surface((lcd_w, lcd_h), pygame.SRCALPHA)

        if music_manager and music_manager.now_playing:
            tape_name = music_manager.now_playing.get('mixtape', 'RADIO')
            song_name = music_manager.now_playing.get('title', '...')
            col = (20, 80, 20)
            
            # MOVER TEXTO +5 PIX A LA IZQ Y REDUCIR -10 TOTAL (-5 LADO Y LADO)
            base_x = 12  # (+5px right offset from previous 7)
            usable_w = lcd_w - 24  # (-10px usable width from previous 14)

            # Word-wrap helper: split text into lines that fit usable_w
            def wrap_text(text, max_w):
                words = text.split(' ')
                lines, current = [], ''
                for w in words:
                    test = (current + ' ' + w).strip()
                    if self._font_radio.size(test)[0] <= max_w:
                        current = test
                    else:
                        if current: lines.append(current)
                        current = w
                if current: lines.append(current)
                return lines if lines else [text]

            # BAJA EL TEXTO DEL LED UNOS 2 PIXEL
            y_cursor = 13  # Start at 13 (was 11)

            # Tape name (multi-line if needed)
            for line in wrap_text(tape_name.upper(), usable_w):
                txt = self._font_radio.render(line, True, col)
                lcd_clip.blit(txt, (base_x + max(0, (usable_w - txt.get_width()) // 2), y_cursor))
                y_cursor += 10

            y_cursor += 2  # gap

            # Song name (multi-line if needed)
            for line in wrap_text(song_name, usable_w):
                txt = self._font_radio.render(line, True, col)
                lcd_clip.blit(txt, (base_x + max(0, (usable_w - txt.get_width()) // 2), y_cursor))
                y_cursor += 10

            y_cursor += 6  # gap before vol bar (since PLAYING was removed)

            # Volume bar only (reduced width by 30%)
            vol_pct = getattr(music_manager, 'volume', 0.5)
            vol_w = int(usable_w * 0.70)
            # Center the volume bar in the usable width
            bar_x = base_x + (usable_w - vol_w) // 2
            pygame.draw.rect(lcd_clip, (10, 50, 10), (bar_x, y_cursor, vol_w, 3))
            pygame.draw.rect(lcd_clip, (30, 140, 30), (bar_x, y_cursor, int(vol_w * vol_pct), 3))
        else:
            no_tape = self._font_radio.render("NO TAPE", True, (20, 80, 20))
            lcd_clip.blit(no_tape, ((lcd_w - no_tape.get_width()) // 2, 32))

        # Blit clipped LCD text onto radio surface, then onto main
        radio_surf.blit(lcd_clip, (lcd_x, lcd_y))
        my_surface.blit(radio_surf, (0, 0))

        # ── Cassette in dashboard black box ────────────────────────────
        # Dark box in asset on screen: DASH_X+2..DASH_X+90
        # SUBE EL CASSET 2 PIXEL (28)
        # REDUCE ANCHO 2 PIX DE DERECHA (86)
        # AUMENTA LARGO 4 PIX ABAJO (60)
        box_x, box_y = DASH_X + 4, 28
        box_w, box_h = 86, 60

        if music_manager and getattr(music_manager, 'now_playing', None):
            # Draw cassette image scaled to fill the entire black box
            cp = music_manager.now_playing.get('cover_path')
            img = self.cassette_img
            if cp:
                if cp not in self.tape_cache:
                    try:
                        loaded = pygame.image.load(cp).convert_alpha()
                        self.tape_cache[cp + "_orig"] = loaded
                        self.tape_cache[cp] = pygame.transform.smoothscale(loaded, (box_w, box_h))
                    except:
                        self.tape_cache[cp] = None
                        self.tape_cache[cp + "_orig"] = None
                img = self.tape_cache.get(cp, self.cassette_img)
            
            if img:
                # If it's a valid pygame surface (not None) it might be the unscaled cassette_img
                if img == self.cassette_img:
                    my_surface.blit(pygame.transform.smoothscale(img, (box_w, box_h)), (box_x, box_y))
                else:
                    my_surface.blit(img, (box_x, box_y))
                
        elif self.cassette_img:
            # No music playing: show static cassette
            scaled_cassette = pygame.transform.smoothscale(self.cassette_img, (box_w, box_h))
            my_surface.blit(scaled_cassette, (box_x, box_y))

        # ── Final composite ───────────────────────────────────────────
        surface.blit(my_surface, (0, DASH_Y))
        
        # ── Overlays ──────────────────────────────────────────────────
        if self.show_zoomed_cassette and music_manager and getattr(music_manager, 'now_playing', None):
            self._render_zoomed_cassette(surface, music_manager)

    def _render_zoomed_cassette(self, surface, music_manager):
        # Semi-transparent dark background
        dim_surf = pygame.Surface(BASE_RESOLUTION, pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))
        
        cp = music_manager.now_playing.get('cover_path')
        img = self.cassette_img
        if cp:
            if cp not in self.tape_cache:
                try:
                    loaded = pygame.image.load(cp).convert_alpha()
                    # Cache original surface to rescale better
                    self.tape_cache[cp + "_orig"] = loaded
                except:
                    pass
            # Retrieve original
            orig_img = self.tape_cache.get(cp + "_orig", self.cassette_img)
            img = orig_img
            
        if img:
            # Scale to large size, keeping aspect ratio somewhat
            # Original typical size might be wide
            zx, zy = BASE_RESOLUTION[0] // 2, BASE_RESOLUTION[1] // 2
            zw, zh = 260, 170
            zoom_surf = pygame.transform.smoothscale(img, (zw, zh))
            rect = zoom_surf.get_rect(center=(zx, zy))
            
            # Simple border
            pygame.draw.rect(surface, (40, 40, 50), rect.inflate(8, 8), border_radius=4)
            pygame.draw.rect(surface, (180, 180, 190), rect.inflate(4, 4), 2, border_radius=4)
            
            surface.blit(zoom_surf, rect)
            
            # Instruction text
            txt = self._font_digital.render("[ESC] OR CLICK TO RETURN", True, (200, 200, 200))
            txt_rect = txt.get_rect(center=(zx, rect.bottom + 20))
            surface.blit(txt, txt_rect)

    def _draw_spinning_tape(self, surface, x, y):
        """Draw two tiny spinning reels (small version for radio LCD)."""
        t = pygame.time.get_ticks() * 0.01
        for offset_x in [0, 16]:
            rx, ry = x + offset_x, y + 8
            pygame.draw.circle(surface, (60, 40, 20), (rx, ry), 5)
            for i in range(3):
                ang = t + i * (math.pi * 2 / 3)
                dx, dy = math.cos(ang) * 4, math.sin(ang) * 4
                pygame.draw.line(surface, (180, 180, 150), (rx, ry), (rx + dx, ry + dy), 1)

    def handle_click(self, pos, engine):
        """Handle interactions with HUD elements (Radio and Dashboard Cassette)."""
        # If clicked anywhere while zoomed cassette is visible, close it
        if self.show_zoomed_cassette:
            self.show_zoomed_cassette = False
            return True

        x, y = pos
        # Check if click is within dashboard area
        if y >= DASH_Y:
            dy = y - DASH_Y # relative Y to dashboard top
            
            # LCD Box (Pause/Unpause) -> x=10..110, y=8..75 (approx)
            if 10 <= x <= 110 and 8 <= dy <= 75:
                if engine.music_mgr:
                    if engine.music_mgr.playing:
                        engine.music_mgr.pause()
                    else:
                        engine.music_mgr.unpause()
                return True

            # Volume Knob (Top Knob on Radio) -> Center offset ~ x=126, y=25
            if 115 <= x <= 135 and 14 <= dy <= 36:
                if engine.music_mgr:
                    if dy < 25:  # Upper half
                        engine.music_mgr.volume_up()
                    else:        # Lower half
                        engine.music_mgr.volume_down()
                return True

            # Track Knob (Bottom Knob on Radio) -> Center offset ~ x=126, y=60
            if 115 <= x <= 135 and 49 <= dy <= 71:
                if engine.music_mgr:
                    if dy < 60:  # Upper half
                        engine.music_mgr.next_track()
                    else:        # Lower half
                        engine.music_mgr.prev_track()
                return True

            # Cassette Box in Dashboard -> DASH_X+4 to DASH_X+90, y=28..88
            box_x = DASH_X + 4
            box_y = 28 
            if box_x <= x <= box_x + 86 and box_y <= dy <= box_y + 60:
                if engine.music_mgr and getattr(engine.music_mgr, 'now_playing', None):
                    self.show_zoomed_cassette = True
                return True
                
        return False

    def _draw_spinning_tape_large(self, surface, x, y):
        """Draw smaller spinning reels for the dashboard cassette box."""
        t = pygame.time.get_ticks() * 0.008
        for offset_x in [0, 20]:
            rx, ry = x + offset_x, y
            # Hub
            pygame.draw.circle(surface, (80, 60, 30), (rx, ry), 6)
            pygame.draw.circle(surface, (50, 35, 15), (rx, ry), 3)
            # Spinning spokes
            for i in range(3):
                ang = t + i * (math.pi * 2 / 3)
                dx, dy = math.cos(ang) * 5, math.sin(ang) * 5
                pygame.draw.line(surface, (200, 190, 160), (rx, ry), (int(rx + dx), int(ry + dy)), 1)

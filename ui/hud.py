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

        self.bg_img = None
        self.upper_img = None
        self.road_img = None
        self.radio_unit_img = None
        self.glovebox_img = None
        self.cassette_img = None
        
        self.show_zoomed_cassette = False
        self.show_glovebox = False
        self.glovebox_idx = 0
        self.last_preview_idx = -1
        self.tape_cache = {}
        
        self.inventory_grid_rows = 4
        self.inventory_grid_cols = 2
        self.inventory_slot_size = 20
        self.inventory_grid_x = 25
        self.inventory_grid_y = 10
        self.inventory_grid_h_bonus = 15
        
        self.avatar_surfs = {}
        self.road_scroll = 0.0
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

        from core.config import ASSETS_DIR, SPRITES_DIR
        # --- Upper HUD ---
        upper_path = os.path.join(ASSETS_DIR, "ui", "hud_upper.png")
        if os.path.exists(upper_path):
            self.upper_img = pygame.image.load(upper_path).convert_alpha()

        # --- Road tile ---
        road_path = os.path.join(ASSETS_DIR, "ui", "hud_road.png")
        if os.path.exists(road_path):
            self.road_img = pygame.image.load(road_path).convert_alpha()

        # --- Character portraits ---
        portraits_dir = os.path.join(SPRITES_DIR, "portraits")
        if os.path.exists(portraits_dir):
            for f in os.listdir(portraits_dir):
                if f.endswith(".png"):
                    # Use lowercase keys for case-insensitive lookup
                    name = f.replace(".png", "").lower()
                    try:
                        img_path = os.path.join(portraits_dir, f)
                        img = pygame.image.load(img_path).convert_alpha()
                        s25 = pygame.transform.smoothscale(img, (25, 25))
                        s27 = pygame.transform.smoothscale(img, (27, 27))
                        s32 = pygame.transform.smoothscale(img, (32, 32))
                        s38 = pygame.transform.smoothscale(img, (38, 38))
                        s50 = pygame.transform.smoothscale(img, (50, 50))
                        self.avatar_surfs[name] = {"25": s25, "27": s27, "32": s32, "38": s38, "50": s50}
                    except Exception as e:
                        print(f"Error loading {f}: {e}")

        # --- Cassette and Glovebox ---
        cassette_path = os.path.join(ASSETS_DIR, "ui", "cassette_template.png")
        if os.path.exists(cassette_path):
            self.cassette_img = pygame.image.load(cassette_path).convert_alpha()
            # DON'T DOWNSCALE HERE, KEEP ORIGINAL TO SCALE BETTER LATER
            
        glove_path = os.path.join(ASSETS_DIR, "audio", "radio", "guantera.png")
        if os.path.exists(glove_path):
            self.glovebox_img = pygame.image.load(glove_path).convert_alpha()
            # Scale to fit nicely in the 640x360 internal res
            self.glovebox_img = pygame.transform.smoothscale(self.glovebox_img, (320, 240))

    def update_fuel(self, **_): pass
    def update_sanity(self, **_): pass

    def _scale_aspect(self, img, max_w, max_h):
        """Helper to scale a surface while maintaining aspect ratio."""
        if not img: return None
        sw, sh = img.get_size()
        ratio = min(max_w / sw, max_h / sh)
        new_w, new_h = int(sw * ratio), int(sh * ratio)
        return pygame.transform.smoothscale(img, (new_w, new_h))

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
            
            if passenger is not None:
                avatar_key = getattr(passenger, 'avatar', None)
                if avatar_key:
                    avatar_key = avatar_key.lower()
                
                if avatar_key and avatar_key in self.avatar_surfs:
                    surface.blit(self.avatar_surfs[avatar_key]["27"], (sx, sy))
                else:
                    # Fallback
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

        # KM labels blit moved to LCD section below

        # ── Upper HUD (full screen) ───────────────────────────────────
        if self.upper_img: surface.blit(self.upper_img, (0, 0))
        self._render_inventory_grid(surface)
        self._render_passengers(surface)

        # Player Avatar
        p_avatar = getattr(self.player, 'avatar', 'kid')
        if p_avatar: p_avatar = p_avatar.lower()
        
        if p_avatar in self.avatar_surfs:
            surface.blit(self.avatar_surfs[p_avatar]["38"], (125, 10))
        else:
            pygame.draw.rect(surface, (100, 150, 200), (125, 10, 38, 38), 2)

        # ── Dashboard instruments (all relative to DASH_X) ────────────
        sanity_pct = self.player.sanity / MAX_SANITY
        speed_val  = int(self.car_manager.car.speed)

        # Energy bars: refined (6x10, 2px gap, stride=8)
        ex, ey = DASH_X + 17, 23
        for i in range(5):
            col = (200, 40, 40) if i >= 4 else (50, 160, 80)
            dim = (40, 10, 10)  if i >= 4 else (15, 30, 15)
            pygame.draw.rect(my_surface, col if sanity_pct >= (i+1)/5.0 else dim, (ex + i * 8, ey, 6, 10))

        # LCD screen: original x=139 in 497px asset → DASH_X+139 = 282
        lx, ly, lw = DASH_X + 139, 11, 205

        # Date/Time (Synchronized with 24h day/night cycle: 0.5 = Noon)
        total_hours = (time_of_day * 24.0) % 24.0
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        period = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12
        if display_hours == 0: display_hours = 12
        time_str = f"SUN, MAR 15TH, {display_hours:02d}:{minutes:02d} {period}"
        
        date_txt = self.font_lcd.render(time_str, True, (80, 210, 80))
        my_surface.blit(date_txt, (lx + (lw - date_txt.get_width()) // 2, ly))
        
        # KM Indicators inside LCD
        txt_driven = self.font_tiny.render(f"DRIVEN: {driven_km_str}", True, (50, 180, 50))
        my_surface.blit(txt_driven, (lx + 8, ly + 22))
        txt_next = self.font_tiny.render(f"NEXT POI: {next_km_str}", True, (50, 180, 50))
        my_surface.blit(txt_next, (lx + 8, ly + 34))

        # Speed
        spd_col = (255, 60, 60) if speed_val > 100 else (120, 255, 120)
        spd_txt = self._font_digital.render(f"{speed_val:03d}", True, spd_col)
        my_surface.blit(spd_txt, (lx + lw - 50, ly + 28))

        # Gas percentage numeric display
        fuel_val = int(self.car_manager.fuel)
        fuel_col = (255, 100, 100) if fuel_val < 25 else (140, 200, 140)
        gas_txt = self.font_tiny.render(f"GAS: {fuel_val}%", True, fuel_col)
        my_surface.blit(gas_txt, (lx + lw - 50, ly + 20))

        # ── Dialogue overlay (Restricted to Red Boxes) ────────────────
        active_line = current_dialogue
        if active_line:
            # Large box for text: (165, 50, 190, 85)
            # Small box for avatar: (360, 50, 55, 85)
            lg_rect = pygame.Rect(165, 50, 190, 85)
            sm_rect = pygame.Rect(360, 50, 55, 85)
            
            # 1. Speaker & Text with Word Wrap
            full_txt = f"{active_line.speaker}: {active_line.text}"
            words = full_txt.split(' ')
            lines = []
            curr_line = ""
            for w in words:
                test = (curr_line + " " + w).strip()
                if self.font_tiny.size(test)[0] <= lg_rect.width - 10:
                    curr_line = test
                else:
                    if curr_line: lines.append(curr_line)
                    curr_line = w
            if curr_line: lines.append(curr_line)
            
            # Start drawing from top of lg_rect
            yh = lg_rect.y + 5
            for line in lines:
                txt_surf = self.font_tiny.render(line, True, (255, 255, 255))
                surface.blit(txt_surf, (lg_rect.x + 5, yh))
                yh += 12 # Line spacing
            
            # [Click to continue] below the last line
            hint_txt = self.font_tiny.render("(Click to continue)", True, (120, 120, 160))
            surface.blit(hint_txt, (lg_rect.x + 5, yh + 4))

            # 2. Speaker Avatar in SM_BOX
            if active_line.avatar:
                ak = active_line.avatar.lower()
                if ak in self.avatar_surfs:
                    # Safe fallback if 50 is not present
                    av_data = self.avatar_surfs[ak]
                    av_img = av_data.get("50") or av_data.get("38") or av_data.get("25")
                    if av_img:
                        # Center in sm_rect
                        ax = sm_rect.centerx - av_img.get_width() // 2
                        ay = sm_rect.centery - av_img.get_height() // 2
                        surface.blit(av_img, (ax, ay))

        # --- Glovebox / Cassette Selector ---
        if self.show_glovebox and music_manager:
            self._render_glovebox(surface, music_manager)
            
        # --- Footers / Status ---
        # Placeholder for _render_footers if it's meant to be a new method
        # self._render_footers(surface) 
        
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

        # ── Cassette in dashboard black box (MILIMETRIC RESTORE) ──────
        # Restaurado a la posición exacta previa: DASH_X + 4, 28
        # Tamaño: 86x60
        box_x, box_y = DASH_X + 4, 28
        mw, mh = 86, 60

        if music_manager and music_manager.now_playing:
            cp = music_manager.now_playing.get('cover_path')
            img = None  # No usamos el template de UI por defecto
            if cp:
                if cp not in self.tape_cache:
                    try:
                        loaded = pygame.image.load(cp).convert_alpha()
                        self.tape_cache[cp + "_orig"] = loaded
                        self.tape_cache[cp] = pygame.transform.smoothscale(loaded, (mw, mh))
                    except:
                        self.tape_cache[cp] = None
                img = self.tape_cache.get(cp)
            
            if img:
                # Forzar escalado al hueco exacto si es necesario
                if img.get_rect().width != mw:
                    final_img = pygame.transform.smoothscale(img, (mw, mh))
                else:
                    final_img = img
                my_surface.blit(final_img, (box_x, box_y))

        # ── Final composite ───────────────────────────────────────────
        surface.blit(my_surface, (0, DASH_Y))



    def _render_glovebox(self, surface, music_manager):
        # 1. Semi-transparent dark background
        dim_surf = pygame.Surface(BASE_RESOLUTION, pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        """Previsualiza el casset seleccionado en la guantera con su diseño real."""
        gb_rect = self.glovebox_img.get_rect(center=(W // 2, H // 2 - 50))
        surface.blit(self.glovebox_img, gb_rect)
        
        mixtapes = music_manager.mixtapes
        if not mixtapes:
            # Mensaje si no hay música
            msg = self.font_bold.render("NO CASSETTES FOUND", True, (255, 100, 100))
            surface.blit(msg, (gb_rect.centerx - msg.get_width() // 2, gb_rect.centery - 10))
            self._draw_btn(surface, "CLOSE", (gb_rect.centerx - 30, gb_rect.bottom - 45, 60, 25), (120, 60, 60))
            return

        m_idx = self.glovebox_idx % len(mixtapes)
        tape = mixtapes[m_idx]
        
        # RENDER CASSETTE PREVIEW (Reduce 30% -> 168x105)
        mw, mh = 168, 105
        img = None
        cp = tape.cover_path
        
        if cp:
            # Check if we already have the glovebox-sized version
            img = self.tape_cache.get(cp + "_glovebox")
            if not img:
                try:
                    # Reuse original if already loaded by lower HUD
                    orig = self.tape_cache.get(cp + "_orig")
                    if not orig:
                        orig = pygame.image.load(cp).convert_alpha()
                        self.tape_cache[cp + "_orig"] = orig
                    
                    img = pygame.transform.smoothscale(orig, (mw, mh))
                    self.tape_cache[cp + "_glovebox"] = img
                except Exception as e:
                    print(f"Error loading glovebox cover {cp}: {e}")
                    self.tape_cache[cp + "_glovebox"] = None

        # Centrar el casset final
        if img:
            fx = gb_rect.centerx - (mw // 2)
            fy = gb_rect.centery - (mh // 2 + 10) # Ligeramente más arriba
            surface.blit(img, (fx, fy))
            cx, cy, cw, ch = fx, fy, mw, mh
        else:
            # Hueco vacío si no hay imagen propia
            cx, cy, cw, ch = gb_rect.centerx - (mw // 2), gb_rect.centery - (mh // 2 + 10), mw, mh
            pygame.draw.rect(surface, (10, 10, 15), (cx, cy, cw, ch))
            pygame.draw.rect(surface, (30, 30, 40), (cx, cy, cw, ch), 1)
        
        # Título del mixtape
        title_txt = self.font_bold.render(tape.name, True, (255, 255, 255))
        surface.blit(title_txt, (gb_rect.centerx - title_txt.get_width() // 2, gb_rect.centery - 70))

        # Flechas de navegación (más separadas para evitar overlap)
        lx, ly = gb_rect.centerx - 120, gb_rect.centery
        pygame.draw.polygon(surface, (200, 200, 200), [(lx, ly), (lx + 20, ly - 15), (lx + 20, ly + 15)])
        rx, ry = gb_rect.centerx + 100, gb_rect.centery
        pygame.draw.polygon(surface, (200, 200, 200), [(rx + 20, ry), (rx, ry - 15), (rx, ry + 15)])

        # Botones
        self._draw_btn(surface, "SELECT", (gb_rect.centerx - 85, gb_rect.bottom - 45, 75, 25), (60, 120, 60))
        self._draw_btn(surface, "CLOSE", (gb_rect.centerx + 10, gb_rect.bottom - 45, 75, 25), (120, 60, 60))

        # 6. Preview indicator
        if music_manager.preview_mode:
            prev_txt = self.font_tiny.render("PREVIEW - 10s", True, (255, 255, 0))
            surface.blit(prev_txt, (gb_rect.centerx - prev_txt.get_width() // 2, cy + ch + 10))

    def _draw_btn(self, surface, text, rect_tupl, color):
        r = pygame.Rect(rect_tupl)
        pygame.draw.rect(surface, color, r)
        pygame.draw.rect(surface, (255, 255, 255), r, 1)
        txt = self.font_tiny.render(text, True, (255, 255, 255))
        surface.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

    def _handle_glovebox_click(self, pos, engine):
        mx, my = pos
        gb_rect = pygame.Rect(W // 2 - 160, H // 2 - 170, 320, 240)
        if hasattr(self, 'glovebox_img') and self.glovebox_img:
            gb_rect = self.glovebox_img.get_rect(center=(W // 2, H // 2 - 50))
        
        mixtapes = engine.music_mgr.mixtapes
        if not mixtapes:
            # If no mixtapes, only the close button is relevant
            if pygame.Rect(gb_rect.centerx - 30, gb_rect.bottom - 40, 60, 25).collidepoint(mx, my):
                self.show_glovebox = False
                return True
            return False

        # Center area for arrows
        cw, ch = 120, 80
        cx, cy = gb_rect.centerx - (cw // 2), gb_rect.centery - (ch // 2)

        # Left Arrow Click
        if pygame.Rect(cx - 55, cy - 20, 50, ch + 40).collidepoint(mx, my):
            self.glovebox_idx = (self.glovebox_idx - 1) % len(mixtapes)
            engine.music_mgr.play(mixtape_idx=self.glovebox_idx, is_preview=True)
            return True

        # Right Arrow Click
        if pygame.Rect(cx + cw + 10, cy, 50, ch).collidepoint(mx, my):
            self.glovebox_idx = (self.glovebox_idx + 1) % len(mixtapes)
            engine.music_mgr.play(mixtape_idx=self.glovebox_idx, is_preview=True)
            return True

        # SELECT Button Click
        if pygame.Rect(gb_rect.centerx - 85, gb_rect.bottom - 45, 75, 25).collidepoint(mx, my):
            engine.music_mgr.play(mixtape_idx=self.glovebox_idx, is_preview=False)
            self.show_glovebox = False
            return True

        # CLOSE Button Click
        if pygame.Rect(gb_rect.centerx + 10, gb_rect.bottom - 45, 75, 25).collidepoint(mx, my):
            # If we were previewing, stop it or return to original
            if engine.music_mgr.preview_mode:
                engine.music_mgr.stop()
            self.show_glovebox = False
            return True
        
        return False # Clicked inside glovebox but not on an interactive element

    def _draw_spinning_tape(self, surface, x, y):
        """Draw two tiny spinning reels (small version for radio LCD)."""
        t = pygame.time.get_ticks() * 0.01
        for i in range(2):
            rx = x + 15 + i * 25
            ry = y + 12
            pygame.draw.circle(surface, (50, 50, 50), (int(rx), int(ry)), 6)
            # Spokes
            for s in range(3):
                angle = t + s * (math.pi * 2 / 3)
                px = rx + math.cos(angle) * 5
                py = ry + math.sin(angle) * 5
                pygame.draw.line(surface, (150, 150, 150), (rx, ry), (px, py), 1)

    def handle_click(self, pos, engine):
        """Handle interactions with HUD elements (Radio and Dashboard Cassette)."""
        mx, my = pos
        
        # 0. If Glovebox is open, it captures all clicks
        if self.show_glovebox:
            return self._handle_glovebox_click(pos, engine)

        # 1. Check for dialogue click
        if engine.dialogue.is_active():
            # Dialogue box is roughly (gx-110, gy-12) to (gx+110, gy+12)
            # Center of dialogue is gx = 320, gy = 330
            # These coordinates are based on the render method's dialogue positioning
            mid_road_x = DASH_X + 39 + (370 // 2) # rx + rw // 2
            gx = mid_road_x - 112
            gy = DASH_Y + 43 - 240 # This is the gy for the dialogue text
            
            # Approximate dialogue box area based on text and avatar
            dialogue_rect = pygame.Rect(gx - 150, gy - 10, 300, 50) # A bit generous
            if dialogue_rect.collidepoint(mx, my):
                engine.dialogue.advance()
                return True

        # 2. Check for cassette click
        # Location (DASH_X + 4, DASH_Y + 28) with size (86, 60)
        cassette_rect = pygame.Rect(DASH_X + 4, DASH_Y + 28, 86, 60)
        if cassette_rect.collidepoint(mx, my):
            self.show_glovebox = True
            # Sync index with current mixtape
            if engine.music_mgr and engine.music_mgr.mixtapes:
                self.glovebox_idx = engine.music_mgr.current_mixtape_idx
            return True
        
        # If clicked anywhere while zoomed cassette is visible, close it
        if self.show_zoomed_cassette:
            self.show_zoomed_cassette = False
            return True

        # Check if click is within dashboard area
        if my >= DASH_Y:
            dy = my - DASH_Y # relative Y to dashboard top
            
            # 3. Check for LCD Box (Pause/Unpause) -> x=10..110, y=8..75 (approx)
            if DASH_X + 10 <= mx <= DASH_X + 110 and 8 <= dy <= 75:
                if engine.music_mgr:
                    if engine.music_mgr.playing:
                        engine.music_mgr.pause()
                    else:
                        engine.music_mgr.unpause()
                return True
                
            # Volume Knob (Top Knob on Radio) -> Center offset ~ x=126, y=25
            if 115 <= mx <= 135 and 14 <= dy <= 36:
                if engine.music_mgr:
                    if dy < 25:  # Upper half
                        engine.music_mgr.volume_up()
                    else:        # Lower half
                        engine.music_mgr.volume_down()
                return True

            # Track Knob (Bottom Knob on Radio) -> Center offset ~ x=126, y=60
            if 115 <= mx <= 135 and 49 <= dy <= 71:
                if engine.music_mgr:
                    if dy < 60:  # Upper half
                        engine.music_mgr.next_track()
                    else:        # Lower half
                        engine.music_mgr.prev_track()
                return True

            # Cassette Box in Dashboard -> Bajo ENERGY (x=245, y=53)
            box_x = 245
            box_y_rel = 53 
            if box_x <= mx <= box_x + 86 and box_y_rel <= dy <= box_y_rel + 32:
                # Open glovebox on click
                self.show_glovebox = True
                if engine.music_mgr:
                    self.glovebox_idx = engine.music_mgr.current_mixtape_idx
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

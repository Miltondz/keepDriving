"""
Main game engine — fully wired with all systems:
  WorldMap, CarManager, TurnEngine, EncounterUI, MusicManager,
  Hitchikers, Inventory, HUD, GameRenderer
"""
import pygame
import random
from enum import Enum, auto

from core.config import (BASE_RESOLUTION, SCREEN_WIDTH, SCREEN_HEIGHT,
                         TARGET_FPS, COLORS)
from core.events import events, EVENTS

from graphics.renderer import GameRenderer
from graphics.post_process import PostProcessor
from entities.player import Player
from entities.car import Car
from entities.hitchhiker import random_hitchhiker
from entities.inventory import GloveboxInventory
from systems.car_manager import CarManager
from systems.turn_engine import TurnEngine
from systems.music_manager import MusicManager
from systems.sound_manager import SoundManager
from systems.dialogue_system import DialogueSystem
from systems.weather import WeatherSystem
from systems.traffic import TrafficManager
from world.map import WorldMap
from world.locations import Settlement, RoadType
from ui.hud import HUD
from ui.encounter_ui import EncounterUI
from ui.menu_screens import MenuScreen, SettingsScreen, ShopScreen
from ui.mixtape_menu import MixtapeMenu

W, H = BASE_RESOLUTION

# ── Biome → road type string mapping ──────────────────────────────────────
ROAD_BIOMES = {
    RoadType.DESERT:  "desert",
    RoadType.FOREST:  "forest",
    RoadType.MOUNTAIN:"mountain",
    RoadType.HIGHWAY: "highway",
    RoadType.COASTAL: "coastal",
}


class GameState(Enum):
    MENU       = auto()
    SETTINGS   = auto()
    TRAVEL     = auto()
    PAUSED     = auto()
    ENCOUNTER  = auto()
    SETTLEMENT = auto()
    SHOP       = auto()
    GAME_OVER  = auto()
    WIN        = auto()
    MIXTAPE_SELECT = auto()


class KeepDrivingEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Pixel-art double-buffer
        self.canvas = pygame.Surface(BASE_RESOLUTION)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Keep Driving")

        self.clock   = pygame.time.Clock()
        self.state   = GameState.MENU
        self.running = True

        # Font for menus
        self._font_lg = pygame.font.Font(None, 48)
        self._font_md = pygame.font.Font(None, 24)
        self._font_sm = pygame.font.Font(None, 16)

        # Systems (wired in setup())
        self.player      = None
        self.car         = None
        self.car_manager = None
        self.inventory   = None
        self.world_map   = None
        self.turn_engine = None
        self.music_mgr   = None
        self.dialogue    = None
        self.renderer    = None
        self.hud         = None
        self.enc_ui      = None
        self.weather     = None

        # Pending encounter key (from WorldMap.advance_km)
        self._pending_encounter = None
        # Pending hitchhiker for preview
        self._pending_hitchhiker = None
        # Settlement info
        self._current_settlement = None
        # Menu animation
        # Menu screens
        self.menu_screen = MenuScreen(self._font_lg, self._font_md)
        self.settings_screen = SettingsScreen(self._font_md)
        self.shop_screen = None # Created per settlement
        self.mixtape_menu = MixtapeMenu(self._font_md)

        # Time of day: 0.0 (midnight) to 1.0 (midnight), 0.5 is noon
        self.time_of_day = 0.4
        self.current_biome = "desert"

        # Post-processing filter (F10 to cycle)
        self.post_proc = PostProcessor(*BASE_RESOLUTION)

    # ── Setup ─────────────────────────────────────────────────────────────
    def setup(self):
        self.player      = Player(name="Driver")
        self.car         = Car()
        self.car_manager = CarManager(self.player, self.car)
        self.inventory   = GloveboxInventory()
        self.world_map   = WorldMap(seed=None, num_segments=8)
        self.turn_engine = TurnEngine(self.player, self.car_manager)
        self.music_mgr   = MusicManager()
        self.sound_mgr   = SoundManager()
        self.dialogue    = DialogueSystem()
        self.renderer    = GameRenderer()
        self.hud         = HUD(self.player, self.car_manager, self.world_map, self.inventory)
        self.enc_ui      = EncounterUI()
        self.weather     = WeatherSystem()
        self.traffic     = TrafficManager()

        # Event wiring
        events.subscribe(EVENTS['FUEL_CHANGED'],    self.hud.update_fuel)
        events.subscribe(EVENTS['SANITY_CHANGED'],  self.hud.update_sanity)
        events.subscribe(EVENTS['ENCOUNTER_START'], self._on_encounter_start)
        events.subscribe(EVENTS['ENCOUNTER_END'],   self._on_encounter_end)

        # Start music
        self.music_mgr.play()
        print("✓ Keep Driving engine ready")

    # ── Event callbacks ────────────────────────────────────────────────────
    def _on_encounter_start(self, **_):
        pass  # enc_ui.show() called in _trigger_encounter

    def _on_encounter_end(self, **_):
        if self.state == GameState.ENCOUNTER:
            self.state = GameState.TRAVEL

    # ── Input ──────────────────────────────────────────────────────────────
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hud and self.hud.handle_click(
                    (int(event.pos[0] * (W / SCREEN_WIDTH)), int(event.pos[1] * (H / SCREEN_HEIGHT))), 
                    self
                ):
                    continue

            if event.type == pygame.KEYDOWN:
                if getattr(self, 'exit_confirm', False):
                    if event.key == pygame.K_y:
                        self.running = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        self.exit_confirm = False
                    continue

                if event.key == pygame.K_ESCAPE:
                    if self.hud and getattr(self.hud, 'show_zoomed_cassette', False):
                        self.hud.show_zoomed_cassette = False
                    elif self.state in (GameState.TRAVEL, GameState.PAUSED):
                        self.exit_confirm = True
                    else:
                        self.running = False

                if event.key == pygame.K_SPACE:
                    if self.state == GameState.TRAVEL:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.TRAVEL

                # Help overlay (F1)
                if event.key == pygame.K_F1:
                    self.show_help = not getattr(self, 'show_help', False)

                # View switch (F2, F3)
                elif event.key == pygame.K_F2:
                    self.renderer.switch_view('topdown')
                elif event.key == pygame.K_F3:
                    self.renderer.switch_view('side')
                
                # Debug Shortcuts (F4 - F9)
                elif event.key == pygame.K_F4: # Day / Night toggle
                    if 0.25 < self.time_of_day < 0.75:
                        self.time_of_day = 0.85 # Night
                    else:
                        self.time_of_day = 0.5 # Day
                elif event.key == pygame.K_F5: self.weather.state = "sunny"
                elif event.key == pygame.K_F6: self.weather.state = "rain"
                elif event.key == pygame.K_F7: self.weather.state = "storm"
                elif event.key == pygame.K_F8: self.weather.state = "sandstorm"
                elif event.key == pygame.K_F9: self.weather.state = "snow"
                elif event.key == pygame.K_F10: self.post_proc.cycle()
                
                # Radio & Audio controls
                elif event.key == pygame.K_LEFTBRACKET:  self.music_mgr.volume_down()
                elif event.key == pygame.K_RIGHTBRACKET: self.music_mgr.volume_up()
                elif event.key == pygame.K_n:            self.music_mgr.next_track()
                elif event.key == pygame.K_k:
                    if self.state in (GameState.TRAVEL, GameState.SETTLEMENT):
                        self.mixtape_menu.update_mixtapes(self.music_mgr.mixtapes)
                        self.state = GameState.MIXTAPE_SELECT

                # State-specific
                if self.state == GameState.MENU:
                    choice = self.menu_screen.handle_input(event)
                    if choice == "START JOURNEY":
                        self._start_game()
                    elif choice == "SETTINGS":
                        self.state = GameState.SETTINGS
                    elif choice == "EXIT":
                        self.running = False

                elif self.state == GameState.MIXTAPE_SELECT:
                    choice = self.mixtape_menu.handle_input(event)
                    if choice == "BACK":
                        self.state = GameState.TRAVEL
                    elif isinstance(choice, int):
                        self.music_mgr.play(mixtape_idx=choice)
                        self.state = GameState.TRAVEL

                elif self.state == GameState.SETTINGS:
                    choice = self.settings_screen.handle_input(event)
                    if choice == "BACK":
                        self.state = GameState.MENU
                    # Volume/Fullscreen logic could be added here

                elif self.state == GameState.ENCOUNTER:
                    chosen = self.enc_ui.handle_input(event)
                    if chosen is not None:
                        self._resolve_encounter(chosen)

                elif self.state == GameState.SETTLEMENT:
                    # L = leave settlement
                    if event.key == pygame.K_l:
                        self._leave_settlement()
                    # R = enter shop / interaction
                    elif event.key == pygame.K_r or event.key == pygame.K_s:
                        self.shop_screen = ShopScreen(self._font_md, self._current_settlement.name)
                        # Filter shop items dynamically based on settlement services
                        filtered = []
                        services = self._current_settlement.services
                        
                        all_items = self.shop_screen.items
                        for item in all_items:
                            name = item["name"].upper()
                            if "REFUEL" in name and 'fuel' in services:
                                filtered.append(item)
                            elif "REPAIR" in name and 'repair' in services:
                                filtered.append(item)
                            elif "SNACK" in name and 'shop' in services:
                                filtered.append(item)
                            elif "LEAVE" in name:
                                filtered.append(item)
                        
                        self.shop_screen.items = filtered
                        self.state = GameState.SHOP

                elif self.state == GameState.SHOP:
                    choice = self.shop_screen.handle_input(event)
                    if choice:
                        if choice["name"] == "LEAVE":
                            self.state = GameState.SETTLEMENT
                        elif self.player.spend(choice["price"]):
                            self.sound_mgr.play("purchase")
                            if "REFUEL" in choice["name"]:
                                self.car_manager.refuel(100)
                                self.sound_mgr.play("fueling")
                            elif "REPAIR" in choice["name"]:
                                self.car_manager.condition = min(100, self.car_manager.condition + 40)
                                self.sound_mgr.play("repair")
                            elif "SNACK" in choice["name"]:
                                self.player.modify_sanity(30)
                                self.sound_mgr.play("eat")
                            # Maybe refresh screen or play sound?

                elif self.state in (GameState.GAME_OVER, GameState.WIN):
                    if event.key == pygame.K_r:
                        self.setup()
                        self.state = GameState.MENU

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self, dt):
        self.time_of_day = (self.time_of_day + dt * 0.002) % 1.0
        self.car_manager.update(dt) 
        self.music_mgr.update(dt)
        self.hud.update(dt)
        self.enc_ui.update(dt)
        self.weather.update(dt, self.player, self.current_biome)
        self.traffic.update(dt, self.car.speed)

        if self.state == GameState.TRAVEL:
            self._maybe_trigger_conversation(dt)

    def _maybe_trigger_conversation(self, dt):
        """Randomly trigger dialogue with hitchhikers."""
        if self.dialogue.is_active(): return
        
        # 0.5% chance per second when moving
        if self.car.speed > 10 and random.random() < 0.005:
            # Filter None to avoid crash
            passengers = [p for p in self.player.passengers.values() if p is not None]
            if passengers:
                p = random.choice(passengers)
                story = p.get_next_story() 
                from systems.dialogue_system import DialogueTree, DialogueLine
                lines = []
                for i, text in enumerate(story):
                    next_id = i + 1 if i < len(story) - 1 else None
                    lines.append(DialogueLine(p.name, text, next_id))
                
                tree = DialogueTree(lines)
                self.dialogue.start(tree)

        if self.state == GameState.TRAVEL:
            # Continuous input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.car.accelerate(dt)
                self.sound_mgr.play("engine_rev")
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.car.brake(dt)
                self.sound_mgr.play("brake_squeal")

            # Physics + resources
            self.car.update(dt)
            self.car_manager.update(dt)

            # Distance and player update
            km_this_frame = (self.car.speed / 3600) * dt # speed in km/h, km per frame
            self.player.update_travel(km_this_frame)

            # Update biome based on distance
            d = self.player.distance_traveled
            if d < 200:      new_biome = "desert"
            elif d < 400:    new_biome = "village"
            elif d < 600:    new_biome = "forest"
            elif d < 800:    new_biome = "mountain"
            else:            new_biome = "city"
            
            self.current_biome = new_biome
            if self.renderer.parallax.biome != new_biome:
                self.renderer.set_biome(new_biome)

            # Renderer
            self.renderer.update(dt, self.car.speed, self.weather.state)

            # World advancement — check for encounters
            encounter_key = self.world_map.advance_km(km_this_frame)
            if encounter_key:
                self._trigger_encounter(encounter_key)

            # Check if we've reached a settlement
            if self.world_map.is_settlement and self.state == GameState.TRAVEL:
                self._enter_settlement(self.world_map.current_node)

            # Sync biome with parallax
            if self.world_map.is_road:
                biome = ROAD_BIOMES.get(self.world_map.current_node.road_type, "desert")
                self.renderer.set_biome(biome)

            # Check resource failures
            if self.car_manager.fuel <= 0:
                self.state = GameState.GAME_OVER
            if not self.player.is_sane:
                self.state = GameState.GAME_OVER
            
            # Fatigue risk (low sanity)
            if self.player.sanity < 25 and random.random() < 0.005:
                self._trigger_encounter("fatigue_blurred")

            # Speeding police risk (only when above 100km/h)
            if self.car.speed > 100 and self.state == GameState.TRAVEL and getattr(self.enc_ui, 'is_visible', False) == False:
                # Highest speed (170) = +70. Chance ~ 0.001 per frame (6% per second)
                over_speed = self.car.speed - 100
                if random.random() < over_speed * 0.000015:
                    if random.random() < 0.10:
                        self._trigger_encounter("speeding_busted")
                    else:
                        self._trigger_encounter("speeding_ticket")

            if self.world_map.at_end:
                self.state = GameState.WIN

    # ── Encounter flow ────────────────────────────────────────────────────
    def _trigger_encounter(self, key: str):
        encounter = self.turn_engine.trigger(key)
        if not encounter:
            return
        # Special: hitchhiker encounter → use HH logic if no slots
        if key == 'hitchhiker' and self.player.is_vehicle_full:
            events.emit(EVENTS['ENCOUNTER_END'])
            return

        options = self.turn_engine.get_available_options(self.inventory)
        # Get current hitchhiker for avatar display
        self._pending_hitchhiker = None
        if key == 'hitchhiker':
            self._pending_hitchhiker = random_hitchhiker()
            
        self.enc_ui.show(encounter, options, self._pending_hitchhiker)
        self.state = GameState.ENCOUNTER

    def _resolve_encounter(self, option_index: int):
        result = self.turn_engine.resolve(option_index, self.inventory)
        positive = sum(v for v in result.values() if isinstance(v, (int, float)) and v > 0) > 0

        # Special: hitchhiker → actually add one
        if self.turn_engine.current_encounter is None:
            if 'sanity' in result and result.get('option', '').startswith('Pick'):
                hh = self._pending_hitchhiker or random_hitchhiker()
                if self.player.add_passenger(hh):
                    result['_note'] = f"Picked up {hh.name}"
                self._pending_hitchhiker = None

        self.enc_ui.show_outcome(result, positive)
        
        if result.get('game_over'):
            self.state = GameState.GAME_OVER

    # ── Settlement flow ───────────────────────────────────────────────────
    def _enter_settlement(self, settlement: Settlement):
        self._current_settlement = settlement
        self.state = GameState.SETTLEMENT

    def _leave_settlement(self):
        self.world_map.leave_settlement()
        self._current_settlement = None
        self.state = GameState.TRAVEL

    def _recruit_hitchhiker(self):
        if not self.player.is_vehicle_full:
            hh = random_hitchhiker()
            self.player.add_passenger(hh)

    # ── Game creation ─────────────────────────────────────────────────────
    def _start_game(self):
        self.setup()
        self.state = GameState.TRAVEL

    # ── Render ────────────────────────────────────────────────────────────
    def _render(self):
        self.canvas.fill(COLORS['bg_night'])

        # Context-aware rendering
        active_state = self.state
        
        # If we are in a menu/overlay state, we might still want to see the "world" behind
        backdrop_states = (GameState.MENU, GameState.SETTINGS, GameState.SHOP, GameState.ENCOUNTER)
        
        if active_state == GameState.TRAVEL or active_state in backdrop_states:
            ox, oy = (0, 0)
            if self.weather:
                ox, oy = self.weather.shake_offset
            
            if self.renderer and self.weather:
                # Determine upcoming encounter for road visualization
                upcoming = None
                if self.world_map and self.world_map.is_road:
                    node = self.world_map.current_node
                    dist = node.km_per_encounter - node.distance_since_last
                    
                    if self.state in (GameState.TRAVEL, GameState.PAUSED):
                        if node.encounters_remaining and dist < 0.8: # Show if within 800m
                            upcoming = {
                                'key': node.encounters_remaining[0],
                                'dist': dist
                            }
                    elif self.state == GameState.ENCOUNTER:
                        # Draw the current encounter parked right at the car (dist=0)
                        curr_enc = getattr(self.turn_engine, 'current_encounter', None)
                        if curr_enc:
                            upcoming = {
                                'key': curr_enc.id if hasattr(curr_enc, 'id') else 'marker',
                                'dist': 0.0
                            }

                self.renderer.render(
                    self.canvas, self.car, self.car_manager, 
                    self.weather.state, self.weather, self.time_of_day, (ox, oy),
                    traffic=self.traffic,
                    upcoming_encounter=upcoming
                )
                
            # The HUD must ALWAYS be drawn LAST, over the weather and night filters
            if self.hud:
                self.hud.render(self.canvas, self.music_mgr, self.time_of_day, self.dialogue.get_current())

        if active_state == GameState.SETTLEMENT:
            self._render_settlement()
            # Mini-prompt for shop
            p_txt = self._font_sm.render("[S] ENTER SHOP   [L] LEAVE", True, (255, 255, 200))
            self.canvas.blit(p_txt, (W//2 - p_txt.get_width()//2, H - 40))

        elif active_state == GameState.SHOP:
            self._render_settlement()
            self.shop_screen.render(self.canvas, self.player.money)

        elif active_state == GameState.ENCOUNTER:
            self.enc_ui.render(self.canvas)

        elif active_state == GameState.MENU:
            self.menu_screen.render(self.canvas)

        elif active_state == GameState.SETTINGS:
            self.settings_screen.render(self.canvas)

        elif active_state == GameState.MIXTAPE_SELECT:
            self.mixtape_menu.render(self.canvas)

        elif active_state == GameState.GAME_OVER:
            self._render_end("STRANDED", "The road beat you.", "(R) Try Again")

        elif active_state == GameState.WIN:
            self._render_end("DESTINATION REACHED",
                             f"{int(self.player.distance_traveled)} km driven.",
                             "(R) Drive Again")

        # Outcome flash
        if self.enc_ui and self.enc_ui.outcome_timer > 0:
            self.enc_ui.render(self.canvas)

        # Pause overlay
        if active_state == GameState.PAUSED:
            p_txt = self._font_lg.render("PAUSED", True, (255, 255, 255))
            self.canvas.blit(p_txt, (W//2 - p_txt.get_width()//2, H//2 - p_txt.get_height()//2))

        # Exit confirmation overlay
        if getattr(self, 'exit_confirm', False):
            bw, bh = 220, 90
            bx, by = W//2 - bw//2, H//2 - bh//2
            pygame.draw.rect(self.canvas, (20, 20, 30), (bx, by, bw, bh))
            pygame.draw.rect(self.canvas, (200, 50, 50), (bx, by, bw, bh), 2)
            
            txt1 = self._font_md.render("QUIT GAME?", True, (255, 255, 255))
            txt2 = self._font_sm.render("Unsaved progress will be lost.", True, (150, 150, 150))
            txt3 = self._font_sm.render("[Y] YES   /   [N] NO", True, (200, 200, 100))
            
            self.canvas.blit(txt1, (W//2 - txt1.get_width()//2, by + 15))
            self.canvas.blit(txt2, (W//2 - txt2.get_width()//2, by + 40))
            self.canvas.blit(txt3, (W//2 - txt3.get_width()//2, by + 65))

        # F1 Help overlay
        if getattr(self, 'show_help', False):
            bw, bh = 280, 180
            bx, by = W//2 - bw//2, 40
            pygame.draw.rect(self.canvas, (10, 10, 15, 220), (bx, by, bw, bh))
            pygame.draw.rect(self.canvas, (100, 100, 120), (bx, by, bw, bh), 1)
            
            title = self._font_md.render("CONTROLS & SHORTCUTS", True, (255, 215, 70))
            self.canvas.blit(title, (bx + 15, by + 15))
            
            lines = [
                "W / UP : Accelerate",
                "S / DOWN : Brake",
                "SPACE : Pause Game",
                "F1 : Toggle Help",
                "[ , ] : Volume Down / Volume Up",
                "N : Next Track",
                "K : Tape Collection",
                "F4-F9 : Debug Weather/Time",
                "ESC : Quit Game"
            ]
            
            cy = by + 40
            for line in lines:
                txt = self._font_sm.render(line, True, (200, 200, 200))
                self.canvas.blit(txt, (bx + 20, cy))
                cy += 14

        # ── Post-processing filter (applied to canvas before upscale) ────────
        if self.post_proc.current != 0:
            self.post_proc.apply(self.canvas)
            # Show active filter name in corner
            _lbl = self._font_sm.render(f"FX: {self.post_proc.name()}", True, (200, 200, 200))
            self.canvas.blit(_lbl, (4, 124))

        # Upscale
        pygame.transform.scale(self.canvas, (SCREEN_WIDTH, SCREEN_HEIGHT), self.screen)
        pygame.display.flip()

    def _render_menu(self):
        self._menu_t += 0.02
        # Gradient sky
        for y in range(H):
            t = y / H
            r = int(20 + 40 * t)
            g = int(15 + 20 * t)
            b = int(40 + 60 * t)
            pygame.draw.line(self.canvas, (r, g, b), (0, y), (W, y))

        # Road at bottom
        pygame.draw.rect(self.canvas, (50, 50, 60), (0, H - 40, W, 40))
        pygame.draw.rect(self.canvas, (180, 160, 100), (0, H - 40, W, 3))
        import math
        road_off = int(self._menu_t * 60) % 36
        for i in range(-1, W // 36 + 2):
            x = i * 36 - road_off
            pygame.draw.rect(self.canvas, (220, 220, 180), (x, H - 22, 20, 4))

        # Stars
        import random as rnd
        rnd.seed(99)
        for _ in range(60):
            sx = rnd.randint(0, W)
            sy = rnd.randint(0, H // 2)
            pygame.draw.circle(self.canvas, (200, 200, 220), (sx, sy), 1)

        # Title
        title = self._font_lg.render("KEEP DRIVING", True, (255, 215, 70))
        shadow = self._font_lg.render("KEEP DRIVING", True, (80, 40, 0))
        tx = W // 2 - title.get_width() // 2
        self.canvas.blit(shadow, (tx + 2, 62))
        self.canvas.blit(title,  (tx, 60))

        sub = self._font_md.render("An atmospheric road trip RPG", True, (160, 140, 200))
        self.canvas.blit(sub, (W // 2 - sub.get_width() // 2, 88))

        prompt = self._font_md.render("Press any key to drive", True,
                                      (200, 200, 220) if int(self._menu_t * 3) % 2 == 0
                                      else (100, 100, 130))
        self.canvas.blit(prompt, (W // 2 - prompt.get_width() // 2, 150))

        controls = [
            "W / ↑  Accelerate     S / ↓  Brake",
            "F1 Interior  F2 Map  F3 Road  ESC Quit",
        ]
        for i, line in enumerate(controls):
            t = self._font_sm.render(line, True, (100, 90, 120))
            self.canvas.blit(t, (W // 2 - t.get_width() // 2, H - 38 + i * 14))

    def _render_settlement(self):
        s = self._current_settlement
        # Background
        pygame.draw.rect(self.canvas, (30, 22, 15), (0, 0, W, H))
        # Fake buildings
        colors = [(80, 60, 40), (70, 55, 35), (90, 65, 45)]
        for i, (bx, bw, bh, bc) in enumerate(
            [(20, 40, 60, 0), (70, 30, 45, 1), (110, 50, 70, 2),
             (220, 35, 50, 0), (260, 45, 65, 1), (150, 25, 40, 2)]
        ):
            by = H - 50 - bh
            pygame.draw.rect(self.canvas, colors[bc], (bx, by, bw, bh + 50))
            # Window
            pygame.draw.rect(self.canvas, (220, 200, 100), (bx + 8, by + 10, 10, 10))
        # Road
        pygame.draw.rect(self.canvas, (50, 50, 60), (0, H - 50, W, 50))

        # Name banner
        name_bg = pygame.Surface((W, 28))
        name_bg.fill((20, 15, 10))
        self.canvas.blit(name_bg, (0, 0))
        name_t = self._font_lg.render(s.name.upper(), True, (255, 215, 70))
        self.canvas.blit(name_t, (W // 2 - name_t.get_width() // 2, 2))

        services = s.services
        menu = []
        if 'fuel'   in services: menu.append("[R] Refuel — $20")
        if 'repair' in services: menu.append("[F] Repair Car — $30")
        menu.append("[H] Recruit Hitchhiker")
        menu.append("[L] Leave Town")

        for i, line in enumerate(menu):
            col = (200, 180, 230) if i < len(menu) - 1 else (255, 215, 70)
            t = self._font_md.render(line, True, col)
            self.canvas.blit(t, (W // 2 - t.get_width() // 2, 45 + i * 22))

        # Stats
        stats = [
            f"Fuel {int(self.car_manager.fuel)}%  Car {int(self.car_manager.condition)}%",
            f"Sanity {int(self.player.sanity)}%   Cash ${self.player.money}",
        ]
        for i, line in enumerate(stats):
            t = self._font_sm.render(line, True, (130, 120, 150))
            self.canvas.blit(t, (10, H - 44 + i * 14))

    def _render_end(self, headline, sub, prompt):
        for y in range(H):
            t = y / H
            pygame.draw.line(self.canvas, (int(10 + 20*t), int(5+10*t), int(20+30*t)), (0,y),(W,y))
        h = self._font_lg.render(headline, True, (255, 100, 80))
        self.canvas.blit(h, (W//2 - h.get_width()//2, 70))
        s = self._font_md.render(sub, True, (180, 160, 200))
        self.canvas.blit(s, (W//2 - s.get_width()//2, 110))
        p = self._font_md.render(prompt, True, (220, 210, 240))
        self.canvas.blit(p, (W//2 - p.get_width()//2, 150))

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        print("🚐 Keep Driving starting…")
        # Setup just the menu state first (full setup on key press)
        self._font_lg = pygame.font.Font(None, 48)
        self._font_md = pygame.font.Font(None, 24)
        self._font_sm = pygame.font.Font(None, 16)

        while self.running:
            dt = min(self.clock.tick(TARGET_FPS) / 1000.0, 0.05)  # cap dt
            self._handle_input()
            if self.state != GameState.MENU or self.player is not None:
                self._update(dt)
            self._render()

        pygame.quit()
        print("✓ Shutdown complete")

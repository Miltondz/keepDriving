"""
Menu and Overlay Screens — Main Menu, Settings, and Settlement Shop.
"""
import pygame
from core.config import BASE_RESOLUTION, COLORS

W, H = BASE_RESOLUTION

class MenuScreen:
    def __init__(self, font_title, font_main):
        self.font_title = font_title
        self.font_main = font_main
        self.selected_index = 0
        self.options = ["START JOURNEY", "SETTINGS", "EXIT"]
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index]
        return None

    def render(self, surface):
        # Overlay tint
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((10, 15, 20, 180))
        surface.blit(overlay, (0, 0))
        
        # Title
        title_txt = self.font_title.render("KEEP DRIVING", True, (255, 255, 255))
        surface.blit(title_txt, (W // 2 - title_txt.get_width() // 2, H // 4))
        
        # Subtitle
        sub_txt = self.font_main.render("A LONG ROAD AHEAD", True, (150, 160, 180))
        surface.blit(sub_txt, (W // 2 - sub_txt.get_width() // 2, H // 4 + 40))

        # Options
        for i, opt in enumerate(self.options):
            col = COLORS['ui_highlight'] if i == self.selected_index else (180, 180, 190)
            prefix = "> " if i == self.selected_index else "  "
            txt = self.font_main.render(prefix + opt, True, col)
            surface.blit(txt, (W // 2 - 60, H // 2 + i * 30))

class SettingsScreen:
    def __init__(self, font_main):
        self.font_main = font_main
        self.selected_index = 0
        self.options = ["MUSIC VOLUME: 80%", "SFX VOLUME: 100%", "FULLSCREEN: OFF", "BACK"]
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index]
        return None

    def render(self, surface):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((15, 20, 25, 220))
        surface.blit(overlay, (0, 0))
        
        title_txt = self.font_main.render("SETTINGS", True, COLORS['ui_highlight'])
        surface.blit(title_txt, (W // 2 - title_txt.get_width() // 2, H // 4))

        for i, opt in enumerate(self.options):
            col = (255, 215, 70) if i == self.selected_index else (180, 180, 190)
            prefix = "> " if i == self.selected_index else "  "
            txt = self.font_main.render(prefix + opt, True, col)
            surface.blit(txt, (W // 2 - 80, H // 2 - 20 + i * 25))

class ShopScreen:
    def __init__(self, font_main, settlement_name):
        self.font_main = font_main
        self.settlement_name = settlement_name
        self.selected_index = 0
        self.items = [
            {"name": "REFUEL (FULL)", "price": 20, "desc": "Top off the gas tank."},
            {"name": "QUICK REPAIR", "price": 30, "desc": "Fix major mechanical issues."},
            {"name": "ENERGY SNACK", "price": 10, "desc": "Restores some sanity."},
            {"name": "LEAVE", "price": 0, "desc": "Continue your journey."}
        ]
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.items[self.selected_index]
        return None

    def render(self, surface, player_money):
        # Draw Shop Panel
        panel_w, panel_h = 280, 220
        px, py = (W - panel_w) // 2, (H - panel_h) // 2
        
        # Border/Shadow
        pygame.draw.rect(surface, (5, 5, 8), (px+4, py+4, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, (25, 28, 35), (px, py, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, (60, 70, 80), (px, py, panel_w, panel_h), 2, border_radius=8)
        
        # Header
        title = self.font_main.render(self.settlement_name.upper(), True, (255, 255, 255))
        surface.blit(title, (px + 20, py + 15))
        
        cash_txt = self.font_main.render(f"CASH: ${player_money:.2f}", True, (160, 220, 160))
        surface.blit(cash_txt, (px + panel_w - cash_txt.get_width() - 20, py + 15))
        pygame.draw.line(surface, (60, 70, 80), (px + 10, py + 40), (px + panel_w - 10, py + 40), 1)

        # Items
        for i, item in enumerate(self.items):
            is_sel = (i == self.selected_index)
            col = (255, 215, 70) if is_sel else (180, 180, 190)
            
            # Selection bar
            if is_sel:
                pygame.draw.rect(surface, (40, 45, 60), (px + 10, py + 50 + i*35, panel_w - 20, 30), border_radius=4)
            
            name_txt = self.font_main.render(item["name"], True, col)
            surface.blit(name_txt, (px + 20, py + 58 + i*35))
            
            if item["price"] > 0:
                price_txt = self.font_main.render(f"${item['price']}", True, (200, 200, 210))
                surface.blit(price_txt, (px + panel_w - price_txt.get_width() - 25, py + 58 + i*35))

        # Bottom decription
        desc = self.items[self.selected_index]["desc"]
        desc_txt = self.font_main.render(desc, True, (140, 150, 160))
        surface.blit(desc_txt, (px + 20, py + panel_h - 35))

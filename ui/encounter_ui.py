"""
Encounter UI — renders the turn-based encounter panel over the game.
Handles keyboard navigation (1/2/3 to choose, ESC to wait).
"""
import pygame
import math
from core.config import BASE_RESOLUTION, COLORS

W, H = BASE_RESOLUTION

# UI colors
C_PANEL_BG   = (18, 15, 28)
C_PANEL_BRD  = (80, 60, 120)
C_TITLE_BG   = (40, 20, 60)
C_TEXT        = (220, 215, 235)
C_DIM         = (130, 120, 150)
C_HIGHLIGHT   = (255, 215,  70)
C_DISABLED    = ( 80,  70,  90)
C_OUTCOME_POS = ( 80, 200, 120)
C_OUTCOME_NEG = (200,  80,  80)


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
        self.font_title  = pygame.font.Font(None, 22)
        self.font_body   = pygame.font.Font(None, 15)
        self.font_key    = pygame.font.Font(None, 18)

        self.encounter   = None
        self.options_list = []       # list of (option, available)
        self.selected    = 0
        self.outcome_text = ""
        self.outcome_timer = 0.0     # seconds to show outcome flash
        self.outcome_positive = True

        # Animation
        self._slide_y = H           # slides up from bottom
        self._target_y = H - 175

    def show(self, encounter, options_list):
        self.encounter   = encounter
        self.options_list = options_list
        self.selected    = 0
        self.outcome_text = ""
        self.outcome_timer = 0.0
        self._slide_y = H

    def hide(self):
        self.encounter = None
        self.outcome_text = ""

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
        self.outcome_text = "  ·  ".join(parts) if parts else "Nothing changed."
        self.outcome_positive = positive
        self.outcome_timer = 2.5
        self.encounter = None

    def update(self, dt):
        # Slide animation
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

    def _render_panel(self, surface):
        panel_y = int(self._slide_y)
        panel_h = H - panel_y
        panel_w = W - 10

        # Semi-transparent overlay
        overlay = pygame.Surface((W, panel_y), pygame.SRCALPHA)
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
            bg  = (40, 30, 60) if is_sel and available else C_PANEL_BG
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
        hint = self.font_body.render("↑↓ navigate  · ENTER / 1 2 3 choose", True, C_DIM)
        surface.blit(hint, (10, H - 14))

    def _render_outcome(self, surface):
        # Flash banner
        alpha = min(255, int(self.outcome_timer / 2.5 * 255))
        col = C_OUTCOME_POS if self.outcome_positive else C_OUTCOME_NEG
        bar = pygame.Surface((W, 30), pygame.SRCALPHA)
        bar.fill((*col, 180))
        surface.blit(bar, (0, H // 2 - 15))
        txt = self.font_title.render(self.outcome_text, True, (255, 255, 255))
        surface.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 10))

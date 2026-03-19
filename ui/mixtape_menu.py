"""
Mixtape Selection Menu — Browse and select cassette tapes to play.
"""
import pygame
from core.config import BASE_RESOLUTION, COLORS

W, H = BASE_RESOLUTION

class MixtapeMenu:
    def __init__(self, font_main):
        self.font_main = font_main
        self.selected_index = 0
        self.mixtapes = []
        self.visible = False

    def update_mixtapes(self, mixtapes):
        self.mixtapes = mixtapes

    def handle_input(self, event):
        if not self.mixtapes: 
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_k or event.key == pygame.K_ESCAPE):
                return "BACK"
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP, pygame.K_a, pygame.K_LEFT):
                self.selected_index = (self.selected_index - 1) % len(self.mixtapes)
            elif event.key in (pygame.K_s, pygame.K_DOWN, pygame.K_d, pygame.K_RIGHT):
                self.selected_index = (self.selected_index + 1) % len(self.mixtapes)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.selected_index
            elif event.key == pygame.K_k or event.key == pygame.K_ESCAPE:
                return "BACK"
        return None

    def render(self, surface):
        # Draw background overlay (dark interior brown/orange)
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((30, 15, 10, 210)) 
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_main.render("THE BOX", True, (255, 215, 70))
        surface.blit(title, (W // 2 - title.get_width() // 2, 30))
        
        sub = self.font_main.render("Select a Tape to Insert", True, (180, 160, 140))
        surface.blit(sub, (W // 2 - sub.get_width() // 2, 55))

        if not self.mixtapes:
            empty = self.font_main.render("NO TAPES FOUND", True, (100, 100, 100))
            surface.blit(empty, (W // 2 - empty.get_width() // 2, H // 2))
        else:
            # Draw Tape Grid
            cols = 3
            cell_w, cell_h = 160, 70
            start_x = (W - (cols * cell_w)) // 2
            start_y = 90

            for i, tape in enumerate(self.mixtapes):
                row = i // cols
                col = i % cols
                x = start_x + col * cell_w
                y = start_y + row * cell_h

                is_sel = (i == self.selected_index)
                
                # Tape Body
                color = (45, 45, 50) if not is_sel else (60, 60, 70)
                pygame.draw.rect(surface, color, (x + 10, y + 10, cell_w - 20, cell_h - 20), border_radius=4)
                pygame.draw.rect(surface, (100, 100, 110), (x + 10, y + 10, cell_w - 20, cell_h - 20), 2, border_radius=4)
                
                # Selection Highlight
                if is_sel:
                    pygame.draw.rect(surface, (255, 215, 70), (x + 8, y + 8, cell_w - 16, cell_h - 16), 2, border_radius=6)

                # Tape Label
                lbl_color = (220, 220, 220) if is_sel else (140, 140, 140)
                name_txt = self.font_main.render(tape.name[:14], True, lbl_color)
                surface.blit(name_txt, (x + (cell_w - name_txt.get_width()) // 2, y + 22))
                
                count_txt = self.font_main.render(f"{len(tape.songs)} TRACKS", True, (100, 100, 110) if not is_sel else (130, 130, 200))
                surface.blit(count_txt, (x + (cell_w - count_txt.get_width()) // 2, y + 42))

        # Controls Hint
        help_txt = self.font_main.render("[ENTER] Play Tape    [K] Close Box", True, (150, 150, 150))
        surface.blit(help_txt, (W // 2 - help_txt.get_width() // 2, H - 45))

"""Sound manager — Plays SFX from the sfx folder."""
import os
import pygame


class SoundManager:
    """Manages playing sound effects (SFX) from assets/audio/sfx."""

    def __init__(self):
        self.sfx_dir = os.path.join("assets", "audio", "sfx")
        if not os.path.exists(self.sfx_dir):
            os.makedirs(self.sfx_dir, exist_ok=True)
            print(f"Created SFX directory: {self.sfx_dir}")

        self.sfx = {}
        self.volume = 0.5
        
        # We will scan the directory whenever we start playing or when refreshed
        self.refresh_library()

    def refresh_library(self):
        """Pre-loads all SFX files into memory."""
        if not os.path.exists(self.sfx_dir):
            return
            
        supported_exts = ('.mp3', '.ogg', '.wav')
        for f in os.listdir(self.sfx_dir):
            if f.casefold().endswith(supported_exts):
                name = f.rsplit('.', 1)[0] # Strip extension for easier ID
                full_path = os.path.join(self.sfx_dir, f)
                try:
                    self.sfx[name] = pygame.mixer.Sound(full_path)
                    self.sfx[name].set_volume(self.volume)
                except Exception as e:
                    print(f"Error loading SFX {f}: {e}")
        
        print(f"Loaded {len(self.sfx)} sound effects.")

    def play(self, sound_name: str, loops=0):
        """Play a pre-loaded sound effect."""
        if sound_name in self.sfx:
            try:
                self.sfx[sound_name].play(loops=loops)
            except Exception as e:
                print(f"Error playing SFX {sound_name}: {e}")
        else:
            # Silently fail if not found or try to load it specifically
            # print(f"Warning: SFX '{sound_name}' not found.")
            pass

    def stop(self, sound_name: str):
        """Stop a specific looping SFX."""
        if sound_name in self.sfx:
            self.sfx[sound_name].stop()

    def set_volume(self, volume: float):
        """Set SFX volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sfx.values():
            sound.set_volume(self.volume)

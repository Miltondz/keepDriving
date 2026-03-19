"""Music manager — Plays real MP3/OGG files organized as Mixtapes."""
import os
import random
import pygame


class Mixtape:
    """A collection of songs (usually a folder)."""
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory
        self.songs = []
        self.cover_path = None
        self.refresh()

    def refresh(self):
        """Scans the directory for audio files and covers."""
        if not os.path.exists(self.directory):
            return
        supported_exts = ('.mp3', '.ogg', '.wav')
        self.songs = [f for f in os.listdir(self.directory) if f.casefold().endswith(supported_exts)]
        
        # Check for local cover template
        cover_names = ["cassette.png", "cassette_template.png", "label.png"]
        for cn in cover_names:
            cp = os.path.join(self.directory, cn)
            if os.path.exists(cp):
                self.cover_path = cp
                break

    def get_song(self, index):
        if not self.songs: return None
        return self.songs[index % len(self.songs)]


class MusicManager:
    """Manages playing music organized into Mixtapes from subfolders in assets/audio/radio."""

    def __init__(self):
        self.radio_dir = os.path.join("assets", "audio", "radio")
        if not os.path.exists(self.radio_dir):
            os.makedirs(self.radio_dir, exist_ok=True)

        self.mixtapes = []
        self.current_mixtape = None
        self.current_mixtape_idx = 0
        self.song_index = 0
        
        self.now_playing = None
        self.playing = False
        self.volume = 0.5
        
        self.refresh_library()

    def refresh_library(self):
        """Scans the radio directory for subfolders (Mixtapes)."""
        self.mixtapes = []
        
        # 1. Check for files in root radio dir (General Mixtape)
        root_tape = Mixtape("General Mix", self.radio_dir)
        if root_tape.songs:
            self.mixtapes.append(root_tape)

        # 2. Check for subdirectories (Each is a Mixtape)
        if os.path.exists(self.radio_dir):
            for entry in os.scandir(self.radio_dir):
                if entry.is_dir():
                    tape = Mixtape(entry.name.replace('_', ' ').title(), entry.path)
                    if tape.songs:
                        self.mixtapes.append(tape)
        
        if not self.current_mixtape and self.mixtapes:
            self.current_mixtape = self.mixtapes[0]
            
        print(f"Loaded {len(self.mixtapes)} mixtapes.")

    def play(self, mixtape_idx=None, song_name=None):
        """Play a song from a specific mixtape or the current one."""
        if not self.mixtapes:
            self.refresh_library()
            if not self.mixtapes: return

        if mixtape_idx is not None and 0 <= mixtape_idx < len(self.mixtapes):
            self.current_mixtape = self.mixtapes[mixtape_idx]
            self.current_mixtape_idx = mixtape_idx
            self.song_index = 0

        if not self.current_mixtape:
            self.current_mixtape = self.mixtapes[0]
            self.current_mixtape_idx = 0

        if song_name is None:
            song_name = self.current_mixtape.get_song(self.song_index)
        
        if not song_name:
            self.playing = False
            return

        full_path = os.path.join(self.current_mixtape.directory, song_name)
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.now_playing = {
                "title": song_name.rsplit('.', 1)[0].replace('_', ' ').title(),
                "mixtape": self.current_mixtape.name,
                "cover_path": self.current_mixtape.cover_path
            }
            self.playing = True
        except Exception as e:
            print(f"Error playing {song_name}: {e}")
            self.playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.now_playing = None

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False

    def unpause(self):
        if self.now_playing and not self.playing:
            pygame.mixer.music.unpause()
            self.playing = True

    def update(self, dt: float):
        if self.playing and not pygame.mixer.music.get_busy():
            self.next_track()

    def next_track(self):
        if self.current_mixtape and self.current_mixtape.songs:
            self.song_index = (self.song_index + 1) % len(self.current_mixtape.songs)
        self.play()

    def prev_track(self):
        if self.current_mixtape and self.current_mixtape.songs:
            self.song_index = (self.song_index - 1) % len(self.current_mixtape.songs)
        self.play()

    def volume_up(self):
        self.volume = min(1.0, self.volume + 0.1)
        pygame.mixer.music.set_volume(self.volume)
        return self.volume

    def volume_down(self):
        self.volume = max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)
        return self.volume

    @property
    def mood(self) -> str:
        return "calm"

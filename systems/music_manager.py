"""Music manager — collect songs, build mix CDs, control atmosphere."""
import random


SONG_LIBRARY = [
    {"id": "s01", "title": "Desert Miles",        "artist": "The Low Suns",      "mood": "calm",    "bpm": 75},
    {"id": "s02", "title": "Cracked Asphalt",     "artist": "Road Ghosts",       "mood": "tense",   "bpm": 110},
    {"id": "s03", "title": "Golden Hour",         "artist": "Miriam Voss",       "mood": "uplifting","bpm": 90},
    {"id": "s04", "title": "Night Driving",       "artist": "Static Bloom",      "mood": "calm",    "bpm": 65},
    {"id": "s05", "title": "Strangers on the 40", "artist": "The Hitch",         "mood": "melancholy","bpm": 80},
    {"id": "s06", "title": "Fuel & Fire",         "artist": "Carla Renn",        "mood": "uplifting","bpm": 120},
    {"id": "s07", "title": "Empty Tank",          "artist": "Low Gear",          "mood": "tense",   "bpm": 95},
    {"id": "s08", "title": "Mountain Pass",       "artist": "Echo Plains",       "mood": "uplifting","bpm": 100},
    {"id": "s09", "title": "Rain on Glass",       "artist": "Soft Static",       "mood": "melancholy","bpm": 60},
    {"id": "s10", "title": "Last Exit",           "artist": "The Wanderers",     "mood": "tense",   "bpm": 130},
    {"id": "s11", "title": "Cowboy Drift",        "artist": "Dust & Twang",      "mood": "calm",    "bpm": 70},
    {"id": "s12", "title": "Coastal Haze",        "artist": "Bell & Shore",      "mood": "uplifting","bpm": 85},
]

MIX_CD_SIZE = 5   # max songs per mix CD


class MixCD:
    def __init__(self, name="Mix #1"):
        self.name = name
        self.tracks: list[dict] = []

    def add(self, song: dict):
        if len(self.tracks) < MIX_CD_SIZE:
            self.tracks.append(song)
            return True
        return False

    def is_full(self):
        return len(self.tracks) >= MIX_CD_SIZE

    def dominant_mood(self) -> str:
        if not self.tracks:
            return "calm"
        moods = [t['mood'] for t in self.tracks]
        return max(set(moods), key=moods.count)


class MusicManager:
    """Manages song collection, mix CDs, and current playback state."""

    def __init__(self):
        self.collected: list[dict] = []   # songs the player owns
        self.mix_cds: list[MixCD] = []
        self.current_cd: MixCD | None = None
        self.current_track_index: int = 0
        self.playing: bool = False
        self.track_timer: float = 0.0    # seconds of current track
        self.track_duration: float = 180.0  # default 3 min per track

        # Start with 2 random songs
        starters = random.sample(SONG_LIBRARY, 2)
        for s in starters:
            self.collect_song(s['id'])

        # Create first mix CD automatically
        cd = MixCD("Road Mix #1")
        for s in self.collected[:MIX_CD_SIZE]:
            cd.add(s)
        self.mix_cds.append(cd)
        self.current_cd = cd

    def collect_song(self, song_id: str) -> bool:
        """Add song to collection if not already owned."""
        song = next((s for s in SONG_LIBRARY if s['id'] == song_id), None)
        if song and song_id not in [s['id'] for s in self.collected]:
            self.collected.append(song)
            return True
        return False

    def collect_random(self) -> dict | None:
        """Collect a random uncollected song."""
        uncollected = [s for s in SONG_LIBRARY if s['id'] not in [c['id'] for c in self.collected]]
        if uncollected:
            song = random.choice(uncollected)
            self.collect_song(song['id'])
            return song
        return None

    def create_mix_cd(self, name=None) -> MixCD:
        name = name or f"Road Mix #{len(self.mix_cds)+1}"
        cd = MixCD(name)
        self.mix_cds.append(cd)
        return cd

    def play(self, cd: MixCD = None):
        self.current_cd = cd or self.current_cd
        self.current_track_index = 0
        self.playing = bool(self.current_cd and self.current_cd.tracks)
        self.track_timer = 0.0

    def stop(self):
        self.playing = False

    def update(self, dt: float):
        """Advance track timer, loop through CD."""
        if not self.playing or not self.current_cd:
            return
        self.track_timer += dt
        if self.track_timer >= self.track_duration:
            self.track_timer = 0.0
            self.current_track_index = (self.current_track_index + 1) % max(1, len(self.current_cd.tracks))

    @property
    def now_playing(self) -> dict | None:
        if self.playing and self.current_cd and self.current_cd.tracks:
            return self.current_cd.tracks[self.current_track_index]
        return None

    @property
    def mood(self) -> str:
        if self.current_cd:
            return self.current_cd.dominant_mood()
        return "calm"

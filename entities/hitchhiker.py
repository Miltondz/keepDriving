"""Hitchhiker entity with evolving relationship stages."""
from enum import Enum
import random


class RelationshipStage(Enum):
    NEW = 0           # Helpful abilities, minimal side effects
    BONDED = 1        # Powerful abilities unlocked
    COMPLICATED = 2   # Powerful BUT harmful side effects appear


class Ability:
    def __init__(self, name, description, encounter_tags, effect_key,
                 cost=None, drawback=None):
        self.name = name
        self.description = description
        self.encounter_tags = encounter_tags  # encounter types this helps
        self.effect_key = effect_key
        self.cost = cost or {}           # {'sanity': 5}
        self.drawback = drawback         # str description of the dark side
        self.usable_in_encounter = True


# ── Named Hitchhikers (inspired by Keep Driving archetypes) ──────────────────
HITCHHIKER_TEMPLATES = [
    {
        "name": "The Mechanic",
        "color": (200, 180, 150),
        "personality": "quiet",
        "destination": "Redrock Junction",
        "description": "Grease-stained hands. Doesn't say much. Fixes things.",
        "abilities": {
            RelationshipStage.NEW: [
                Ability("Quick Fix", "Repairs 15 car condition.", ['breakdown', 'flat_tire'], "repair_15"),
            ],
            RelationshipStage.BONDED: [
                Ability("Full Overhaul", "Repairs 40 car condition.", ['breakdown'], "repair_40"),
                Ability("Fuel Efficiency", "Reduces fuel burn by 30% for 10km.", [], "fuel_save"),
            ],
            RelationshipStage.COMPLICATED: [
                Ability("Full Overhaul", "Repairs 40 car condition.", ['breakdown'], "repair_40"),
                Ability("Fuel Efficiency", "Reduces fuel burn 30% for 10km.", [], "fuel_save"),
                Ability("Obsessive Tinkering", "Restores car but costs sanity.", [], "tinker",
                        drawback="Driver loses 15 sanity watching."),
            ],
        },
        "passive": {"sanity_per_km": 0},
        "km_bonded": 80,
        "km_complicated": 200,
    },
    {
        "name": "The Songwriter",
        "color": (150, 210, 200),
        "personality": "friendly",
        "destination": "Bayside",
        "description": "A guitar case and a notebook full of unfinished lyrics.",
        "abilities": {
            RelationshipStage.NEW: [
                Ability("Sing Along", "Restores 10 sanity.", ['fatigue'], "restore_sanity_10"),
            ],
            RelationshipStage.BONDED: [
                Ability("Road Song", "Restores 25 sanity + 10 fuel (morale boost).", ['fatigue', 'fog'], "restore_sanity_25_fuel"),
                Ability("Jam Session", "Collect a new song for the mix CD.", [], "collect_song"),
            ],
            RelationshipStage.COMPLICATED: [
                Ability("Road Song", "Restores 25 sanity + 10 fuel.", ['fatigue'], "restore_sanity_25_fuel"),
                Ability("Melancholy", "Powerful song but costs 20 sanity.", [], "melancholy_song",
                        drawback="Their sadness is infectious."),
            ],
        },
        "passive": {"sanity_per_km": 0.5},
        "km_bonded": 60,
        "km_complicated": 160,
    },
    {
        "name": "The Stranger",
        "color": (120, 120, 140),
        "personality": "unsettling",
        "destination": "Unknown",
        "description": "No destination given. Stares at the road.",
        "abilities": {
            RelationshipStage.NEW: [
                Ability("Eerie Calm", "Resolves any encounter, unknown method.", ['any'], "resolve_any"),
            ],
            RelationshipStage.BONDED: [
                Ability("Unsettling Presence", "Deters threats. Police leave.", ['police_check', 'tailgater'], "deter"),
                Ability("Know the Road", "Skip next 2 encounters entirely.", [], "skip_encounters"),
            ],
            RelationshipStage.COMPLICATED: [
                Ability("Unsettling Presence", "Deters Police.", ['police_check'], "deter"),
                Ability("The Weight", "Removes encounter but drains 30 sanity.", [], "resolve_any",
                        drawback="You don't want to know how they did it."),
            ],
        },
        "passive": {"sanity_per_km": -1.0},
        "km_bonded": 50,
        "km_complicated": 100,
    },
    {
        "name": "The Hiker",
        "color": (160, 200, 140),
        "personality": "friendly",
        "destination": "Coldwater Pass",
        "description": "Backpack, hiking boots, looks at everything with wonder.",
        "abilities": {
            RelationshipStage.NEW: [
                Ability("Fresh Air!", "Open windows — restores 15 sanity.", ['fatigue'], "restore_sanity_15"),
                Ability("Take in Nature", "Scenic break restores 10 sanity + skips encounter.", ['scenic_view'], "scenic_skip"),
            ],
            RelationshipStage.BONDED: [
                Ability("Trail Knowledge", "Avoid rocky terrain incidents.", ['rockslide', 'muddy_road'], "avoid_terrain"),
                Ability("Foraging", "Finds provisions — restores $10 worth of items.", [], "forage"),
            ],
            RelationshipStage.COMPLICATED: [
                Ability("Trial Knowledge", "Avoid terrain incidents.", ['rockslide'], "avoid_terrain"),
                Ability("Nature Over Everything", "Insists on detours, adds 15km.", [], "detour",
                        drawback="Costs extra fuel for the 'scenic' route."),
            ],
        },
        "passive": {"sanity_per_km": 0.3},
        "km_bonded": 70,
        "km_complicated": 180,
    },
    {
        "name": "The Kid",
        "color": (220, 160, 160),
        "personality": "friendly",
        "destination": "Las Piedras",
        "description": "Way too young to be hitchhiking. Full of questions.",
        "abilities": {
            RelationshipStage.NEW: [
                Ability("Are we there yet?", "Annoyingly effective at spotting shortcuts.", ['detour'], "shortcut"),
            ],
            RelationshipStage.BONDED: [
                Ability("Innocent Appeal", "Police let you go no questions asked.", ['police_check'], "police_dismiss"),
                Ability("Endless Energy", "Keeps driver awake — prevents fatigue encounters.", ['fatigue'], "prevent_fatigue"),
            ],
            RelationshipStage.COMPLICATED: [
                Ability("Innocent Appeal", "Police dismiss encounter.", ['police_check'], "police_dismiss"),
                Ability("Meltdown", "Tantrum costs 25 sanity but ends any encounter.", [], "tantrum",
                        drawback="Screaming for 10 minutes is... a lot."),
            ],
        },
        "passive": {"sanity_per_km": -0.2},
        "km_bonded": 50,
        "km_complicated": 120,
    },
]


class Hitchhiker:
    def __init__(self, template: dict):
        self.name = template['name']
        self.color = template.get('color', (180, 180, 180))
        self.personality = template['personality']
        self.destination = template['destination']
        self.description = template['description']
        self.abilities_by_stage = template['abilities']
        self.passive = template.get('passive', {})
        self.km_bonded = template['km_bonded']
        self.km_complicated = template['km_complicated']

        self.stage = RelationshipStage.NEW
        self.km_traveled = 0.0
        self.dialogue_index = 0

    def travel(self, km: float):
        """Advance relationship based on km traveled together."""
        self.km_traveled += km
        if self.stage == RelationshipStage.NEW and self.km_traveled >= self.km_bonded:
            self.stage = RelationshipStage.BONDED
        elif self.stage == RelationshipStage.BONDED and self.km_traveled >= self.km_complicated:
            self.stage = RelationshipStage.COMPLICATED

    def get_active_abilities(self) -> list[Ability]:
        """All abilities available at current stage (cumulative)."""
        abilities = []
        for stage in RelationshipStage:
            if stage.value <= self.stage.value:
                abilities.extend(self.abilities_by_stage.get(stage, []))
        return abilities

    def apply_passive(self, player, km: float):
        """Apply passive per-km effects to player."""
        sanity_mod = self.passive.get('sanity_per_km', 0) * km
        if sanity_mod != 0:
            player.modify_sanity(sanity_mod)

    def get_greeting(self) -> str:
        greetings = {
            'friendly': f"Hey! I'm {self.name}. Thanks for the ride!",
            'quiet':    f"...{self.name}. Thanks.",
            'unsettling': f"I knew you'd stop. I'm {self.name}.",
            'weird':    f"The road chose you to find me. {self.name}.",
        }
        return greetings.get(self.personality, f"Hi, {self.name} here.")

    def stage_label(self) -> str:
        return {
            RelationshipStage.NEW: "★",
            RelationshipStage.BONDED: "★★",
            RelationshipStage.COMPLICATED: "★★✦",
        }[self.stage]

    def __repr__(self):
        return f"Hitchhiker({self.name} [{self.stage.name}] {self.km_traveled:.0f}km)"


def random_hitchhiker() -> Hitchhiker:
    """Spawn a random hitchhiker from the template pool."""
    return Hitchhiker(random.choice(HITCHHIKER_TEMPLATES))

from enum import Enum
import random
from systems.narrative_loader import narrative


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


class Hitchhiker:
    def __init__(self, template: dict):
        self.name = template['name']
        self.color = template.get('color', (180, 180, 180))
        self.personality = template['personality']
        self.destination = template['destination']
        self.description = template['description']
        self.passive = template.get('passive', {})
        self.km_bonded = template['km_bonded']
        self.km_complicated = template['km_complicated']
        
        # Avatar (referencia al archivo de imagen)
        self.avatar = template.get('avatar', 'portrait')
        
        # Lista de conversaciones
        self.conversations = template.get('conversations', [
            "Nice weather today.",
            "How much further?",
            "I like this song.",
        ])

        # Convertir habilidades de dict (json) a objetos Ability
        self.abilities_by_stage = {}
        json_abs = template.get('abilities', {})
        
        # Mapeo manual de strings del JSON a Enums
        mapping = {
            "NEW": RelationshipStage.NEW,
            "BONDED": RelationshipStage.BONDED,
            "COMPLICATED": RelationshipStage.COMPLICATED
        }
        
        for stage_str, stage_enum in mapping.items():
            abs_list = []
            for a in json_abs.get(stage_str, []):
                abs_list.append(Ability(
                    name=a['name'],
                    description=a['description'],
                    encounter_tags=a.get('tags', []),
                    effect_key=a['effect'],
                    drawback=a.get('drawback')
                ))
            self.abilities_by_stage[stage_enum] = abs_list

        self.stage = RelationshipStage.NEW
        self.km_traveled = 0.0
        self.dialogue_index = 0
        
        # Asiento en el vehículo (0 = front, 1-3 = back)
        self.seat_position = None

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

    def get_next_story(self) -> list[str]:
        """Returns a list of strings for a dialogue encounter."""
        if not self.conversations:
            return ["..."]
        
        story = self.conversations[self.dialogue_index % len(self.conversations)]
        self.dialogue_index += 1
        
        # If it's a single string, wrap it in a list
        if isinstance(story, str):
            return [story]
        return story  # already a list of strings


    def __repr__(self):
        return f"Hitchhiker({self.name} [{self.stage.name}] {self.km_traveled:.0f}km)"


def random_hitchhiker() -> Hitchhiker:
    """Spawn a random hitchhiker from the template pool."""
    templates = narrative.hitchhiker_templates
    if not templates:
        # Fallback if loader fails
        return Hitchhiker({
            "name": "Ghost Driver", "personality": "quiet", "destination": "???", 
            "description": "...", "abilities": {}, "km_bonded": 100, "km_complicated": 200,
            "avatar": "agent"
        })
    return Hitchhiker(random.choice(templates))

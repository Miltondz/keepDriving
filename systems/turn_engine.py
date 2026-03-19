import random
from core.events import events, EVENTS
from systems.narrative_loader import narrative


class EncounterOption:
    def __init__(self, text, description, effects, item_required=None,
                 hitchhiker_ability=None, icon_color=(150, 150, 200)):
        self.text = text
        self.description = description
        self.effects = effects          # dict: fuel/sanity/money/condition/skip
        self.item_required = item_required
        self.hitchhiker_ability = hitchhiker_ability
        self.icon_color = icon_color


class Encounter:
    def __init__(self, key, data):
        self.key = key
        self.title = data.get('title', key.upper())
        self.description = data.get('description', "...")
        self.flavour = data.get('flavour', "")
        self.tags = data.get('tags', [])
        self.difficulty = data.get('difficulty', 1)
        self.avatar = data.get('avatar')
        
        self.options = []
        for opt in data.get('options', []):
            self.options.append(EncounterOption(
                text=opt['text'],
                description=opt.get('description', ""),
                effects=opt.get('effects', {}),
                item_required=opt.get('item_required'),
                icon_color=tuple(opt.get('icon_color', [150, 150, 200]))
            ))


class TurnEngine:
    def __init__(self, player, car_manager):
        self.player = player
        self.car_manager = car_manager
        self.current_encounter = None

    def trigger(self, encounter_key: str) -> Encounter | None:
        """Trigger an encounter from JSON data."""
        data = narrative.get_encounter(encounter_key)
        if not data:
            # Fallback random among all encounters in narrative
            all_keys = list(narrative.encounters.keys())
            if all_keys:
                encounter_key = random.choice(all_keys)
                data = narrative.get_encounter(encounter_key)
            
        if not data:
            return None

        self.current_encounter = Encounter(encounter_key, data)
        events.emit(EVENTS['ENCOUNTER_START'])
        return self.current_encounter

    def get_available_options(self, inventory) -> list[tuple]:
        """Returns list of (option, available: bool) for UI."""
        if not self.current_encounter:
            return []
        result = []
        for opt in self.current_encounter.options:
            if opt.item_required:
                has_item = any(i.id == opt.item_required and not i.exhausted
                               for i in inventory.items)
                result.append((opt, has_item))
            else:
                result.append((opt, True))
        return result

    def resolve(self, option_index: int, inventory) -> dict:
        """Apply option effects. Returns result dict."""
        if not self.current_encounter:
            return {}
        
        if option_index >= len(self.current_encounter.options):
            return {}

        opt = self.current_encounter.options[option_index]
        effects = opt.effects

        if opt.item_required:
            item = next((i for i in inventory.items if i.id == opt.item_required), None)
            if item:
                item.use()
                inventory.remove_exhausted()

        # Apply effects
        if 'fuel' in effects:
            if effects['fuel'] < 0:
                self.car_manager.spend_fuel(abs(effects['fuel']))
            else:
                self.car_manager.refuel(effects['fuel'])
        if 'sanity' in effects:
            self.player.modify_sanity(effects['sanity'])
            events.emit(EVENTS['SANITY_CHANGED'])
        if 'money' in effects:
            self.player.money = max(0, self.player.money + effects['money'])
        if 'condition' in effects:
            self.car_manager.condition = max(
                0, min(100, self.car_manager.condition + effects['condition']))

        result = {**effects, 'option': opt.text}
        self.current_encounter = None
        events.emit(EVENTS['ENCOUNTER_END'])
        return result

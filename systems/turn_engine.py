"""Turn-based encounter resolver with 15+ encounter types."""
import random
from core.events import events, EVENTS


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
    def __init__(self, key, title, description, flavour, options,
                 tags=None, difficulty=1):
        self.key = key
        self.title = title
        self.description = description
        self.flavour = flavour
        self.options = options
        self.tags = tags or []
        self.difficulty = difficulty


# ── Master encounter pool ─────────────────────────────────────────────────────
ENCOUNTER_DATABASE = {

    "flat_tire": Encounter(
        key="flat_tire",
        title="FLAT TIRE",
        description="A loud bang. The van pulls sharply to the shoulder.",
        flavour="The rubber is shredded. Classic.",
        options=[
            EncounterOption("Change the Spare",    "Takes time but safe.",
                            {'condition': +10, 'sanity': -5}, icon_color=(100, 200, 100)),
            EncounterOption("Limp to the Next Town","Risky. Very risky.",
                            {'condition': -25, 'fuel': -8},  icon_color=(220, 100, 80)),
            EncounterOption("Use Spare Tire [item]","Instant fix.",
                            {'condition': +15},               item_required="spare_tire",
                            icon_color=(80, 160, 220)),
        ], tags=['flat_tire', 'breakdown'], difficulty=1,
    ),

    "hitchhiker": Encounter(
        key="hitchhiker",
        title="HITCHHIKER",
        description="A figure at the roadside, thumb raised into the heat.",
        flavour="Everyone has a reason to be somewhere.",
        options=[
            EncounterOption("Pick Them Up",  "Gain a companion.",
                            {'sanity': -5}, icon_color=(100, 200, 100)),
            EncounterOption("Drive Past",    "You already have enough problems.",
                            {'sanity': -10}, icon_color=(200, 150, 80)),
        ], tags=['hitchhiker'], difficulty=0,
    ),

    "traffic_jam": Encounter(
        key="traffic_jam",
        title="TRAFFIC JAM",
        description="Cars as far as you can see. Nothing moves.",
        flavour="Someone up ahead made a decision. You're living with it.",
        options=[
            EncounterOption("Wait It Out",   "Burns fuel. Drains will to live.",
                            {'fuel': -12, 'sanity': -8},  icon_color=(180, 150, 80)),
            EncounterOption("Side Road Detour","Adds distance but keeps moving.",
                            {'fuel': -18, 'condition': -5}, icon_color=(100, 180, 220)),
            EncounterOption("Use Road Atlas", "Find a shortcut.",
                            {'fuel': -5},                  item_required="road_atlas",
                            icon_color=(80, 160, 220)),
        ], tags=['traffic_jam'], difficulty=1,
    ),

    "police_check": Encounter(
        key="police_check",
        title="POLICE CHECKPOINT",
        description="Blues and twos. An officer waves you down.",
        flavour="They're not unfriendly. Just... thorough.",
        options=[
            EncounterOption("Comply Politely", "Time lost. Nothing gained.",
                            {'sanity': -5, 'fuel': -5},   icon_color=(180, 180, 200)),
            EncounterOption("Talk Your Way Out","Risky charm.",
                            {'sanity': +5, 'money': -10}, icon_color=(220, 200, 80)),
            EncounterOption("Small Bribe [item]","Money talks.",
                            {'sanity': +10},               item_required="bribe_cash",
                            icon_color=(255, 215, 0)),
        ], tags=['police_check'], difficulty=2,
    ),

    "sandstorm": Encounter(
        key="sandstorm",
        title="SANDSTORM",
        description="A wall of orange dust moves toward you at speed.",
        flavour="The horizon has teeth.",
        options=[
            EncounterOption("Pull Over and Wait","Safer. Loses time.",
                            {'fuel': -4, 'sanity': -10},  icon_color=(180, 150, 80)),
            EncounterOption("Push Through",     "Fast but hard on the van.",
                            {'condition': -20, 'sanity': -15}, icon_color=(200, 80, 60)),
        ], tags=['sandstorm', 'fog'], difficulty=2,
    ),

    "aggressive_tailgater": Encounter(
        key="aggressive_tailgater",
        title="AGGRESSIVE TAILGATER",
        description="The SUV behind you is two inches from your bumper.",
        flavour="Some people treat the road like an extension of their ego.",
        options=[
            EncounterOption("Speed Up",        "Match their aggression.",
                            {'fuel': -15, 'condition': -5}, icon_color=(220, 100, 80)),
            EncounterOption("Pull Over, Let Pass","The dignified option.",
                            {'sanity': -5},                icon_color=(100, 180, 120)),
            EncounterOption("Slow Right Down", "A power move. Risky.",
                            {'sanity': +10, 'condition': -15}, icon_color=(180, 100, 200)),
        ], tags=['tailgater'], difficulty=2,
    ),

    "deer_crossing": Encounter(
        key="deer_crossing",
        title="DEER CROSSING",
        description="Three deer stand in the road. They stare. You stare.",
        flavour="A standoff neither party signed up for.",
        options=[
            EncounterOption("Wait Patiently",  "Serene moment. Costs time.",
                            {'sanity': +5, 'fuel': -3},   icon_color=(100, 200, 100)),
            EncounterOption("Honk",            "Works. Startles everyone.",
                            {'sanity': -5},               icon_color=(200, 180, 80)),
        ], tags=['wildlife_crossing'], difficulty=0,
    ),

    "fallen_tree": Encounter(
        key="fallen_tree",
        title="FALLEN TREE",
        description="A massive pine has come down across both lanes.",
        flavour="The forest doesn't negotiate.",
        options=[
            EncounterOption("Clear It Together","Everyone helps. Takes time.",
                            {'sanity': +5, 'condition': -5}, icon_color=(100, 180, 120)),
            EncounterOption("Find Another Route","Adds 15km.",
                            {'fuel': -20},                icon_color=(180, 140, 80)),
            EncounterOption("Use Duct Tape [item]","Creative solution.",
                            {'condition': -10},           item_required="duct_tape",
                            icon_color=(100, 100, 200)),
        ], tags=['muddy_road', 'fallen_tree'], difficulty=2,
    ),

    "scenic_overlook": Encounter(
        key="scenic_overlook",
        title="SCENIC OVERLOOK",
        description="A pull-off with a view that goes on forever.",
        flavour="You forget, sometimes, why you're out here.",
        options=[
            EncounterOption("Stop and Breathe", "Costs fuel. Restores soul.",
                            {'sanity': +25, 'fuel': -5}, icon_color=(100, 200, 220)),
            EncounterOption("Press On",         "There's always another view.",
                            {},                          icon_color=(150, 150, 180)),
        ], tags=['scenic_view'], difficulty=0,
    ),

    "heat_shimmer": Encounter(
        key="heat_shimmer",
        title="HEAT EXHAUSTION",
        description="The van's temperature gauge creeps into the red.",
        flavour="The desert is reminding you who's in charge.",
        options=[
            EncounterOption("Pull Over, Let Cool", "Safe stop.",
                            {'condition': +5, 'fuel': -3, 'sanity': -5}, icon_color=(180, 130, 80)),
            EncounterOption("Nurse It Forward",    "Risky.",
                            {'condition': -20},           icon_color=(220, 80, 60)),
            EncounterOption("Thermos Coffee [item]","Drink and focus.",
                            {'sanity': +10},               item_required="coffee",
                            icon_color=(200, 140, 80)),
        ], tags=['heat_shimmer', 'fatigue'], difficulty=2,
    ),

    "fog": Encounter(
        key="fog",
        title="THICK FOG",
        description="Visibility drops to ten feet. Sounds become strange.",
        flavour="The road decides where it goes. Not you.",
        options=[
            EncounterOption("Drive Slowly",    "Safe. Drains patience.",
                            {'sanity': -8, 'fuel': -5},  icon_color=(180, 180, 200)),
            EncounterOption("Use Binoculars [item]","Find a gap.",
                            {'sanity': -2},               item_required="binoculars",
                            icon_color=(80, 150, 220)),
        ], tags=['fog'], difficulty=2,
    ),

    "broken_down_car": Encounter(
        key="broken_down_car",
        title="STRANDED MOTORIST",
        description="Someone's pulled over with hazards on, hood up.",
        flavour="You know that feeling.",
        options=[
            EncounterOption("Stop and Help",   "Good karma. Costs time.",
                            {'sanity': +10, 'fuel': -5, 'money': +15}, icon_color=(100, 200, 120)),
            EncounterOption("Keep Driving",    "You have your own problems.",
                            {'sanity': -8},               icon_color=(200, 100, 80)),
            EncounterOption("Use Duct Tape [item]","Share your repair kit.",
                            {'sanity': +15, 'money': +25},item_required="duct_tape",
                            icon_color=(100, 100, 200)),
        ], tags=['breakdown'], difficulty=1,
    ),

    "rockslide": Encounter(
        key="rockslide",
        title="ROCKSLIDE",
        description="Boulders have spilled across the road. Fresh — still moving.",
        flavour="Mountains don't care about your timeline.",
        options=[
            EncounterOption("Wait for Clearance","Safe but long.",
                            {'fuel': -8, 'sanity': -12}, icon_color=(180, 150, 80)),
            EncounterOption("Drive Through Gaps","Daring.",
                            {'condition': -20, 'sanity': -5}, icon_color=(220, 100, 60)),
        ], tags=['rockslide'], difficulty=3,
    ),

    "rest_stop": Encounter(
        key="rest_stop",
        title="REST STOP",
        description="Vending machines, restrooms, and a spectacular lack of soul.",
        flavour="Even mundane places feel important out here.",
        options=[
            EncounterOption("Stretch and Rest",  "Restore energy.",
                            {'sanity': +20},              icon_color=(100, 200, 120)),
            EncounterOption("Vending Machine",   "Spend $5, get snacks.",
                            {'sanity': +10, 'money': -5}, icon_color=(180, 160, 80)),
            EncounterOption("Keep Driving",      "No time.",
                            {},                           icon_color=(150, 150, 180)),
        ], tags=['rest_stop'], difficulty=0,
    ),

    "radio_signal": Encounter(
        key="radio_signal",
        title="STRANGE RADIO SIGNAL",
        description="Between stations — a voice. Clear as day. Says your name.",
        flavour="Static has never been this specific.",
        options=[
            EncounterOption("Listen",   "Unsettling. Compelling.",
                            {'sanity': -5},               icon_color=(150, 100, 200)),
            EncounterOption("Turn It Off","Probably for the best.",
                            {'sanity': +5},               icon_color=(180, 180, 200)),
        ], tags=['radio_signal'], difficulty=1,
    ),

    # ── Biome Specific expansion ───────────────────────────────────
    "mirage": Encounter(
        key="mirage", title="DESERT MIRAGE",
        description="Wait. Is that... a lake? Right there in the middle of the blacktop.",
        flavour="The heat is a powerful storyteller.",
        options=[
            EncounterOption("Blink and Drive", "Stay focused.", {'sanity': -5}),
            EncounterOption("Stop and Check", "You know it's not real, but...", {'sanity': -15, 'fuel': -5}),
        ], tags=['desert', 'mirage'], difficulty=1,
    ),

    "neon_distraction": Encounter(
        key="neon_distraction", title="NEON GLARE",
        description="The city lights are blinding. It's hard to tell where the lane ends.",
        flavour="Light can be just as blinding as shadow.",
        options=[
            EncounterOption("Focus on the Lines", "Drains sanity but stays safe.", {'sanity': -12}),
            EncounterOption("Follow Tail-lights", "Trust someone else.", {'condition': -10, 'sanity': -5}),
        ], tags=['city'], difficulty=2
    ),

    "seagull_attack": Encounter(
        key="seagull_attack", title="SEAGULL SWARM",
        description="Dozens of gulls are dive-bombing the windshield.",
        flavour="The ocean has a weird way of welcoming you.",
        options=[
            EncounterOption("Keep Wipers On", "Noisy. Distracting.", {'sanity': -8, 'condition': -2}),
            EncounterOption("Speed Through", "Aggressive move.", {'fuel': -10}),
        ], tags=['coastal'], difficulty=1
    ),

    "altitude_trouble": Encounter(
        key="altitude_trouble", title="ALTITUDE SICKNESS",
        description="The air is thin. Your head is pounding and the engine is wheezing.",
        flavour="Oxygen is a luxury at 8,000 feet.",
        options=[
            EncounterOption("Take a Breath", "Slow down.", {'fuel': -10, 'sanity': +5}),
            EncounterOption("Push High", "Get over the pass fast.", {'condition': -15, 'sanity': -10}),
        ], tags=['mountain'], difficulty=3
    ),

    # ── Condition Triggers ──────────────────────────────────────────
    "fatigue_blurred": Encounter(
        key="fatigue_blurred", title="EYES CLOSING",
        description="Your eyelids weigh a hundred pounds each. The road is a blur.",
        flavour="Sleep is coming, whether you want it or not.",
        options=[
            EncounterOption("Slap Yourself Awake", "Painful but works.", {'sanity': -15}),
            EncounterOption("Micro-sleep", "Terrifyingly risky.", {'condition': -40}, icon_color=(255, 0, 0)),
            EncounterOption("Drink Coffee [item]", "The only way.", {'sanity': +20}, item_required="coffee"),
        ], tags=['fatigue'], difficulty=4
    ),
}


class TurnEngine:
    def __init__(self, player, car_manager):
        self.player = player
        self.car_manager = car_manager
        self.current_encounter = None

    def trigger(self, encounter_key: str) -> Encounter | None:
        enc = ENCOUNTER_DATABASE.get(encounter_key)
        if not enc:
            # fallback random
            enc = random.choice(list(ENCOUNTER_DATABASE.values()))
        self.current_encounter = enc
        events.emit(EVENTS['ENCOUNTER_START'])
        return enc

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

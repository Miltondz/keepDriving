"""Inventory system — glovebox items used as encounter actions."""
import random
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Item:
    id: str
    name: str
    description: str
    uses: int                          # -1 = infinite
    encounter_tags: list               # which encounter types this helps with
    icon_color: tuple = (200, 200, 200)
    effect_key: str = ""               # key for TurnEngine to resolve

    def use(self):
        if self.uses > 0:
            self.uses -= 1
        return self.uses != 0

    @property
    def exhausted(self):
        return self.uses == 0


# ── Item definitions ─────────────────────────────────────────────────────────
ALL_ITEMS = [
    Item("spare_tire",    "Spare Tire",     "Fix a flat instantly.",          1,  ['flat_tire'],          (180,  80,  80), "fix_flat"),
    Item("jerry_can",     "Jerry Can",      "5L of emergency fuel.",          1,  ['empty_tank'],         (220, 160,  40), "add_fuel"),
    Item("duct_tape",     "Duct Tape",      "Temporary repair for anything.", 3,  ['breakdown','muddy'],  (100, 100, 160), "temp_repair"),
    Item("road_atlas",    "Road Atlas",     "Navigate around an obstacle.",   2,  ['detour','rockslide'], (120, 200, 120), "reroute"),
    Item("coffee",        "Thermos Coffee", "Restore 20 driver energy.",      2,  ['fatigue','fog'],      (200, 140,  80), "restore_energy"),
    Item("bribe_cash",    "Bribe Cash",     "Negotiate your way free.",       1,  ['police_check'],       (255, 215,   0), "bribe"),
    Item("air_freshener", "Air Freshener",  "Calm tense passengers.",         3,  ['passenger_conflict'], (180, 220, 240), "calm_passenger"),
    Item("first_aid",     "First Aid Kit",  "Treat minor injuries.",          1,  ['wildlife','accident'],(220,  80,  80), "heal"),
    Item("binoculars",    "Binoculars",     "Scout ahead, avoid trouble.",    5,  ['ambush','fog'],       (100, 160, 200), "scout"),
    Item("candy",         "Bag of Candy",   "Cheer up any companion.",        5,  [],                    (255, 140, 180), "cheer_up"),
]


class GloveboxInventory:
    """Player's item inventory — the 'hand of cards' for encounters."""

    def __init__(self):
        self.items: list[Item] = []
        self._add_starting_items()

    def _add_starting_items(self):
        starters = ["spare_tire", "coffee", "duct_tape", "road_atlas"]
        for iid in starters:
            item = next((i for i in ALL_ITEMS if i.id == iid), None)
            if item:
                import copy
                self.items.append(copy.copy(item))

    def add_item(self, item_id: str):
        match = next((i for i in ALL_ITEMS if i.id == item_id), None)
        if match:
            import copy
            self.items.append(copy.copy(match))

    def remove_exhausted(self):
        self.items = [i for i in self.items if not i.exhausted]

    def get_usable(self, encounter_tags: list = None) -> list[Item]:
        available = [i for i in self.items if not i.exhausted]
        if encounter_tags:
            relevant = [i for i in available if any(t in i.encounter_tags for t in encounter_tags)]
            # Always include universal items
            universal = [i for i in available if not i.encounter_tags and i not in relevant]
            return relevant + universal[:2]
        return available

    def __len__(self):
        return len(self.items)

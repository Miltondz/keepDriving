"""Event bus for decoupled system communication."""
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
    
    def subscribe(self, event_type, callback):
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type, **data):
        for callback in self._subscribers.get(event_type, []):
            callback(**data)

# Global event bus
events = EventBus()

# Event types
EVENTS = {
    'ENCOUNTER_START': 'encounter_start',
    'ENCOUNTER_END': 'encounter_end',
    'FUEL_CHANGED': 'fuel_changed',
    'SANITY_CHANGED': 'sanity_changed',
    'LOCATION_REACHED': 'location_reached',
}

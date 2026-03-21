"""
Player character — stats, inventory, passengers (hitchhikers).
Sistema de asientos, conversaciones y bajarse en ubicaciones.
"""
from core.config import MAX_SANITY, MAX_PASSENGERS, ROAD_Y
from entities.hitchhiker import Hitchhiker, random_hitchhiker
import random

# ============================================================================
# CONSTANTES DE PASAJEROS
# ============================================================================
# Positions in the vehicle: 0=front passenger, 1-3=back seats
PASSENGER_SEAT_FRONT = 0
PASSENGER_SEAT_BACK_1 = 1
PASSENGER_SEAT_BACK_2 = 2
PASSENGER_SEAT_BACK_3 = 3

SEAT_NAMES = {
    PASSENGER_SEAT_FRONT: "Front Seat",
    PASSENGER_SEAT_BACK_1: "Back Seat 1",
    PASSENGER_SEAT_BACK_2: "Back Seat 2",
    PASSENGER_SEAT_BACK_3: "Back Seat 3",
}

# Distancia mínima para que un pasajero se baje (km)
MIN_DISTANCE_BETWEEN_DROPOFF = 30

# Probabilidad de que un pasajero quiera bajarse cuando se acerca a su destino
DROPOFF_PROXIMITY_THRESHOLD = 15  # km


class Player:
    def __init__(self, name="Driver"):
        self.name = name
        self.sanity = MAX_SANITY
        self.money = 50
        self.distance_traveled = 0.0 # total km driven this run
        self.current_location = "START"
        
        # Avatar del jugador (kid.png)
        self.avatar = "kid"
        
        # Sistema de pasajeros: diccionario {seat_index: Hitchhiker or None}
        # 4 asientos: índice 0 = asiento frontal, 1-3 = asientos traseros
        self.passengers = {i: None for i in range(MAX_PASSENGERS)}
        
        # Historial de conversaciones para evitar repeticiones inmediatas
        self.conversation_history = []
        self.max_conversation_history = 10
        
        # última vez que un pasajero habló (para controlar frecuencia)
        self.last_conversation_km = 0.0
        self.conversation_interval_km = 5.0  # km entre conversaciones
        
        # Seguimiento de eventos para el sistema de cordura
        self.recent_events = []  # últimos eventos para determinar estado
        self.max_recent_events = 5
        
        # Efectos activos de eventos (para sanity lógico)
        self.sanity_events_stack = []  # [[event_type, km_remaining], ...]

    # ── Stats ──────────────────────────────────────────────────────────────
    def modify_sanity(self, delta: float):
        """Modifica la cordura con límites."""
        self.sanity = max(0.0, min(float(MAX_SANITY), self.sanity + delta))
        
        # Registrar evento para lógica de cordura
        if delta != 0:
            event_type = "good" if delta > 0 else "bad"
            self._add_sanity_event(event_type)

    def _add_sanity_event(self, event_type: str):
        """Agrega un evento al historial para calcular estado de cordura."""
        self.recent_events.append(event_type)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop(0)
    
    @property
    def sanity_trend(self) -> str:
        """Retorna la tendencia de cordura basado en eventos recientes."""
        if not self.recent_events:
            return "neutral"
        
        good_count = self.recent_events.count("good")
        bad_count = self.recent_events.count("bad")
        
        if good_count > bad_count + 1:
            return "improving"
        elif bad_count > good_count + 1:
            return "declining"
        elif bad_count > 0:
            return "mixed"
        return "stable"

    def earn(self, amount: int):
        self.money = max(0, self.money + amount)
        # Ganar dinero es un evento positivo
        if amount > 0:
            self._add_sanity_event("good")

    def spend(self, amount: int) -> bool:
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    # ── Pasajeros: Gestión de asientos ─────────────────────────────────────
    def add_passenger(self, hitchhiker: Hitchhiker) -> bool:
        """Agrega un pasajero al primer asiento disponible."""
        for seat in range(MAX_PASSENGERS):
            if self.passengers[seat] is None:
                self.passengers[seat] = hitchhiker
                hitchhiker.seat_position = seat
                return True
        return False
    
    def add_passenger_to_seat(self, hitchhiker: Hitchhiker, seat: int) -> bool:
        """Agrega un pasajero a un asiento específico."""
        if 0 <= seat < MAX_PASSENGERS and self.passengers[seat] is None:
            self.passengers[seat] = hitchhiker
            hitchhiker.seat_position = seat
            return True
        return False
    
    def remove_passenger(self, seat: int) -> Hitchhiker | None:
        """Remueve un pasajero de un asiento específico."""
        if 0 <= seat < MAX_PASSENGERS:
            passenger = self.passengers[seat]
            self.passengers[seat] = None
            return passenger
        return None
    
    def remove_passenger_by_name(self, name: str) -> Hitchhiker | None:
        """Remueve un pasajero por nombre."""
        for seat, passenger in self.passengers.items():
            if passenger and passenger.name == name:
                self.passengers[seat] = None
                return passenger
        return None
    
    def get_passenger_at_seat(self, seat: int) -> Hitchhiker | None:
        """Obtiene el pasajero en un asiento específico."""
        return self.passengers.get(seat)

    @property
    def passenger_count(self) -> int:
        """Cantidad de pasajeros actual."""
        return sum(1 for p in self.passengers.values() if p is not None)
    
    @property
    def is_vehicle_full(self) -> bool:
        """Verifica si el vehículo está lleno."""
        return self.passenger_count >= MAX_PASSENGERS
    
    @property
    def available_seats(self) -> list:
        """Lista de asientos disponibles."""
        return [seat for seat, p in self.passengers.items() if p is None]

    # ── Pasajero en asiento frontal (para UI) ───────────────────────────────
    @property
    def front_passenger(self) -> Hitchhiker | None:
        """Retorna el pasajero del asiento frontal."""
        return self.passengers.get(0)
    
    @property
    def back_passengers(self) -> list:
        """Retorna lista de pasajeros traseros."""
        return [self.passengers[i] for i in range(1, MAX_PASSENGERS) if self.passengers[i]]

    # ── Sistema de conversaciones ─────────────────────────────────────────
    def get_random_conversation(self) -> str | None:
        """Obtiene una conversación aleatoria de un pasajero."""
        active_passengers = [p for p in self.passengers.values() if p is not None]
        if not active_passengers:
            return None
        
        # Seleccionar pasajero aleatorio
        passenger = random.choice(active_passengers)
        
        # Obtener conversación aleatoria
        if hasattr(passenger, 'conversations') and passenger.conversations:
            return random.choice(passenger.conversations)
        
        # Fallback al método original
        greeting = passenger.get_greeting()
        if hasattr(passenger, 'km_traveled'):
            greeting += f" ({passenger.km_traveled:.0f}km together)"
        return greeting
    
    def should_show_conversation(self, km_since_last: float) -> bool:
        """Determina si debe mostrarse una conversación."""
        if self.passenger_count == 0:
            return False
        return km_since_last >= self.conversation_interval_km

    # ── Sistema de bajarse en ubicaciones ─────────────────────────────────
    def check_dropoff(self, current_location_name: str, distance_to_settlement: float) -> list:
        """
        Verifica si algún pasajero quiere bajarse.
        Retorna lista de diccionarios con info del pasajero que quiere bajarse.
        """
        dropoff_candidates = []
        
        for seat, passenger in self.passengers.items():
            if passenger is None:
                continue
            
            # Verificar si está cerca de su destino
            destination = getattr(passenger, 'destination', '')
            wants_to_leave = False
            reason = ""
            
            # Si está en su destino o cerca
            if destination and current_location_name:
                if destination.lower() in current_location_name.lower():
                    wants_to_leave = True
                    reason = f"Has arrived at {destination}"
                elif distance_to_settlement < DROPOFF_PROXIMITY_THRESHOLD:
                    # Aleatorio cerca del destino
                    if random.random() < 0.1:  # 10% probabilidad por km cerca
                        wants_to_leave = True
                        reason = f"Near destination: {destination}"
            
            # También puede bajarse aleatoriamente después de mucho viaje
            if not wants_to_leave and hasattr(passenger, 'km_traveled'):
                if passenger.km_traveled > 100 and random.random() < 0.01:  # 1% por km después de 100km
                    wants_to_leave = True
                    reason = "Ready to leave"
            
            if wants_to_leave:
                dropoff_candidates.append({
                    'seat': seat,
                    'passenger': passenger,
                    'reason': reason,
                    'destination': getattr(passenger, 'destination', 'Unknown')
                })
        
        return dropoff_candidates

    # ── Per-frame update ───────────────────────────────────────────────────
    def update_travel(self, km: float):
        """Call every tick while in TRAVEL state."""
        self.distance_traveled += km
        
        # Base sanity drain (mental fatigue): 1 per 0.5 km (significantly more visible)
        base_drain = km / 0.5
        self.modify_sanity(-base_drain)
        
        # Procesar cada pasajero
        for passenger in list(self.passengers.values()):
            if passenger:
                passenger.travel(km)
                passenger.apply_passive(self, km)
        
        # Procesar eventos de cordura activos
        self._update_sanity_events(km)

    def _update_sanity_events(self, km: float):
        """Actualiza los eventos de cordura activos."""
        # Reducir duración de eventos activos
        for event in self.sanity_events_stack[:]:
            event_type, km_left = event
            km_left -= km
            if km_left <= 0:
                self.sanity_events_stack.remove(event)
            else:
                event[1] = km_left

    # ── Checks ─────────────────────────────────────────────────────────────
    @property
    def is_sane(self):
        return self.sanity > 0

    @property
    def hitchhiker_count(self):
        """Compatibilidad con código anterior."""
        return self.passenger_count
    
    @property
    def hitchhikers(self):
        """Compatibilidad con código anterior - retorna lista de pasajeros."""
        return [p for p in self.passengers.values() if p is not None]


# Alias para compatibilidad
MAX_HITCHHIKERS = MAX_PASSENGERS
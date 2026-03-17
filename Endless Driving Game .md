
**Game Design Document: Endless Driving Game (Keep Driving Style)**

**Proyecto:** Juego endless driving con sistema de hitchhikers, eventos y gestión de recursos  
**Motor:** Pygame (Python)  
**Estilo visual:** Pixel art low‑res con parallax scrolling  
**Inspiración principal:** Keep Driving  
**Autor:** Milton Diaz  
**Fecha:** 15 de marzo de 2026

**1\. Visión General del Juego**

**1.1 Concepto Core**

El jugador conduce por una carretera infinita en vista lateral, gestionando combustible, estado del vehículo y recursos mientras recoge hitchhikers (autoestopistas) que generan eventos narrativos. El objetivo es avanzar la mayor distancia posible, experimentando historias emergentes a través de encuentros aleatorios, puntos de descanso y tiendas.

**1.2 Mecánicas Principales**

- Conducción con carriles: el jugador cambia entre 2-3 carriles evitando tráfico
- Sistema de recursos: combustible, dinero, condición del auto, estado del conductor
- Hitchhikers: personajes que suben al auto y generan eventos/diálogos
- Puntos de descanso: estaciones de servicio, moteles, tiendas de conveniencia
- Progresión por distancia: cada kilómetro avanzado desbloquea nuevos biomas/eventos

**2\. Interfaz de Usuario (UI/UX)**

**2.1 Filosofía de Diseño UI**

**Principio clave:** Interfaz "analógica" integrada al mundo del juego. Los elementos UI deben sentirse como objetos físicos dentro del coche, no como menús abstractos superpuestos.

**Referencias visuales:**

- Keep Driving: objetos interactivos (guantera, radio, mapa) como UI diegética
- Papers Please: interfaz como espacio de trabajo físico
- A Short Hike: UI minimal que no rompe inmersión

**2.2 HUD Principal (Durante Conducción)**

**Layout recomendado (resolución base 320x180 px, escalado x4):**

| Zona               | Elementos                    | Especificaciones técnicas                |
| ------------------ | ---------------------------- | ---------------------------------------- |
| Superior izquierda | Combustible, Dinero          | Barra 60x6 px, texto 8px font            |
| Superior derecha   | Día/Hora, KM recorridos      | Texto compacto, reloj analógico opcional |
| Centro             | Carretera + vehículo jugador | 80% del espacio vertical                 |
| Inferior           | Velocímetro, Estado auto     | Dial simplificado 32x32 px               |
| Lateral derecho    | Retrato hitchhiker actual    | 48x48 px portrait + nombre               |

Table 1: Distribución del HUD principal

**Assets gráficos necesarios para HUD:**

- hud_fuel_bar.png - Barra de combustible vacía (marco)
- hud_fuel_fill.png - Relleno de combustible (se escala en X)
- hud_speedometer.png - Dial de velocímetro base
- hud_speedometer_needle.png - Aguja rotable
- hud_car_condition_icons.png - Sprite sheet: bueno, medio, dañado, crítico (16x16 px cada uno)
- hud_day_night_icons.png - Iconos sol/luna para indicador de tiempo
- hud_money_icon.png - Ícono de moneda 8x8 px

**Código de referencia (estructura básica):**

class HUD:  
def **init**(self, game_surface):  
self.surface = game_surface  
self.fuel_bar = load_image("hud_fuel_bar.png")  
self.fuel_fill = load_image("hud_fuel_fill.png")  
self.speedometer = load_image("hud_speedometer.png")  
self.font = load_pixel_font(8)

def draw(self, fuel_pct, money, km, day_time, car_state):  
\# Combustible (superior izquierda)  
self.surface.blit(self.fuel_bar, (8, 8))  
fill_width = int(60 \* fuel_pct)  
self.surface.blit(self.fuel_fill, (8, 8),  
(0, 0, fill_width, 6))  
<br/>\# Dinero  
draw_text(self.surface, f"\${money}", (8, 18), self.font)  
<br/>\# Kilómetros (superior derecha)  
draw_text(self.surface, f"{km} km", (260, 8), self.font)  
<br/>\# Velocímetro (inferior centro)  
self.surface.blit(self.speedometer, (144, 150))

**2.3 Pantallas de Eventos y Personajes**

**Escenario:** Cuando el jugador recoge un hitchhiker o llega a un punto de descanso, la UI cambia a modo "evento".

**Layout pantalla de evento:**

- Fondo difuminado de la carretera (seguir scroll lento para mantener sensación de movimiento)
- Panel central 240x140 px con borde estilo ventana/diálogo
- Retrato del personaje: 64x64 px, lado izquierdo del panel
- Texto del evento: máximo 3 líneas de 28 caracteres (fuente 8px)
- Opciones de decisión: 2-4 botones tipo "analógico" (rectangulares con ícono + texto corto)

**Assets gráficos necesarios:**

- event_panel_bg.png - Marco del panel de diálogo (240x140 px)
- event_button_normal.png - Botón de opción estado normal (80x20 px)
- event_button_hover.png - Botón estado hover
- event_button_pressed.png - Botón estado presionado
- event_icons/ - Carpeta con iconos 16x16 px: hablar, dar objeto, rechazar, aceptar, etc.

**Código de referencia:**

class EventScreen:  
def **init**(self):  
self.panel = load_image("event_panel_bg.png")  
self.buttons = {  
"normal": load_image("event_button_normal.png"),  
"hover": load_image("event_button_hover.png"),  
"pressed": load_image("event_button_pressed.png")  
}

def show_event(self, character, text, options):  
\# character: objeto con .portrait (Surface 64x64)  
\# text: string del evento  
\# options: lista de dict {"text": "Ayudar", "icon": "help", "callback": func}  
<br/>self.surface.blit(self.panel, (40, 20))  
self.surface.blit(character.portrait, (48, 28))  
<br/>draw_wrapped_text(self.surface, text, (120, 30), max_width=28)  
<br/>y = 100  
for i, opt in enumerate(options):  
btn_state = self.get_button_state(i) # normal/hover/pressed  
self.surface.blit(self.buttons\[btn_state\], (50, y))  
draw_text(self.surface, opt\["text"\], (58, y + 6))  
y += 24

**2.4 UI de Puntos de Descanso (Tiendas/Gasolineras)**

**Concepto:** Menú tipo "escaparate" horizontal donde los ítems son sprites físicos que el jugador puede inspeccionar y comprar.

**Layout:**

- Fondo específico del lugar (interior de tienda, bomba de gasolina, motel)
- Contador superior mostrando dinero actual del jugador
- 3-6 ítems dispuestos horizontalmente en "estantes" o "mostrador"
- Cursor/indicador sobre ítem seleccionado
- Panel inferior con descripción del ítem + precio + botón comprar

**Assets gráficos necesarios por tipo de punto:**

**Gasolinera:**

- location_gas_station_bg.png - Fondo de estación de servicio (320x180 px)
- items/fuel_can.png - Bidón de combustible (32x32 px)
- items/snack.png - Snack genérico
- items/map.png - Mapa plegable
- items/tire.png - Neumático de repuesto

**Tienda de conveniencia:**

- location_store_bg.png - Interior de tienda (estantes, refrigerador)
- items/coffee.png - Café (recupera "estado conductor")
- items/first_aid.png - Botiquín
- items/magazine.png - Revista (entretenimiento para hitchhikers)
- items/cigarettes.png - Cigarros (ítem social para eventos)

**Motel:**

- location_motel_bg.png - Habitación de motel
- items/bed_icon.png - Ícono de descanso
- items/shower_icon.png - Ícono de ducha (mejora estado)
- items/phone_icon.png - Llamada telefónica (desbloquea evento especial)

**Mecánica de compra:**

class Shop:  
def **init**(self, location*type):  
[self.bg](http://self.bg) = load_image(f"location*{location_type}\_bg.png")  
self.items = self.load_shop_inventory(location_type)  
self.selected_index = 0

def load_shop_inventory(self, loc_type):  
\# Retorna lista de objetos Item  
inventories = {  
"gas_station": \[  
Item("Combustible", 20, "fuel_can.png", effect="fuel+50"),  
Item("Snack", 5, "snack.png", effect="hunger-10"),  
Item("Neumático", 50, "tire.png", effect="repair+25")  
\],  
"store": \[  
Item("Café", 3, "coffee.png", effect="energy+20"),  
Item("Botiquín", 15, "first_aid.png", effect="health+30")  
\]  
}  
return inventories.get(loc_type, \[\])  
<br/>def draw(self):  
self.surface.blit(self.bg, (0, 0))  
x = 40  
for i, item in enumerate(self.items):  
self.surface.blit(item.sprite, (x, 80))  
if i == self.selected_index:  
draw_rect_outline(self.surface, (x-2, 78, 36, 36), color=(255, 255, 0))  
x += 48  
<br/>\# Panel de info del ítem seleccionado  
selected = self.items\[self.selected_index\]  
draw_text(self.surface, f"{selected.name} - \${selected.price}", (10, 150))

**3\. Sistema de Hitchhikers (Autoestopistas)**

**3.1 Concepto y Propósito**

Los hitchhikers son personajes procedurales que suben al auto del jugador en puntos aleatorios de la carretera. Cada uno tiene:

- Retrato único (generado por IA o sprite pre-diseñado)
- Nombre generado
- Personalidad (arquetipo narrativo)
- 1-3 eventos asociados que se disparan durante el viaje
- Posible recompensa o penalización al despedirse

**3.2 Arquetipos de Personajes**

**Tabla de arquetipos recomendados:**

| Arquetipo  | Descripción             | Tipo de eventos                             |
| ---------- | ----------------------- | ------------------------------------------- |
| Vagabundo  | Sin rumbo, filosófico   | Conversaciones reflexivas, pide comida      |
| Fugitivo   | Huyendo de algo/alguien | Eventos de tensión, riesgo vs recompensa    |
| Músico     | Artista en gira         | Ofrece música (buff temporal), historias    |
| Anciano    | Sabiduría, nostalgia    | Consejos útiles, historias del pasado       |
| Estudiante | Joven enérgico          | Diálogos alegres, puede ayudar con mecánica |
| Misterioso | Ambiguo, inquietante    | Eventos extraños, recompensas raras         |

Table 2: Arquetipos de hitchhikers

**3.3 Assets Gráficos Necesarios**

**Retratos de personajes (generación con IA):**

Cada personaje requiere un retrato pixel art de 64x64 px. Se recomienda generar variaciones con Pollinations u otro generador siguiendo estos **prompts base**:

**Prompts para generación de retratos:**

- **Vagabundo:** "pixel art portrait, 64x64, weathered homeless man, beard, tired eyes, worn cap, muted colors, side profile, indie game character"
- **Fugitivo:** "pixel art portrait, 64x64, nervous young person, hoodie, looking over shoulder, dark colors, tense expression, indie game style"
- **Músico:** "pixel art portrait, 64x64, cheerful musician with guitar case, headphones, colorful jacket, confident smile, indie game character"
- **Anciano:** "pixel art portrait, 64x64, elderly person, glasses, kind wrinkled face, gray hair, warm expression, side profile, retro game style"
- **Estudiante:** "pixel art portrait, 64x64, young college student, backpack, energetic expression, casual clothes, bright colors, indie game art"
- **Misterioso:** "pixel art portrait, 64x64, mysterious figure, shadowy face, hat obscuring features, ambiguous gender, dark palette, eerie vibe"

**Consideraciones técnicas para assets de personajes:**

- Todos los retratos deben usar la misma paleta de colores (16-32 colores máximo)
- Ángulo consistente: perfil lateral o 3/4 view
- Fondo transparente (PNG con alpha channel)
- Carpeta de organización: assets/characters/portraits/
- Nomenclatura: hitchhiker\_\[arquetipo\]\_\[variante\].png (ej: hitchhiker_vagabond_01.png)

**Sprites adicionales de personajes:**

- hitchhiker_roadside_waiting.png - Sprite del autoestopista esperando en la carretera (16x24 px, brazo levantado)
- hitchhiker_entering_car.png - Animación de subir al auto (2-3 frames)
- hitchhiker_leaving_car.png - Animación de bajar del auto (2-3 frames)

**3.4 Sistema de Eventos de Hitchhikers**

**Estructura de un evento:**

class HitchhikerEvent:  
def **init**(self, event_id, character, text, options):  
[self.id](http://self.id) = event_id  
self.character = character # Referencia al objeto Hitchhiker  
self.text = text # Texto del diálogo/situación  
self.options = options # Lista de opciones de decisión

def trigger(self, game_state):  
\# Muestra pantalla de evento  
\# Pausa la conducción o mantiene scroll lento  
\# Espera decisión del jugador  
pass

**Ejemplo de evento definido:**

vagabond_event_1 = HitchhikerEvent(  
event_id="vagabond_hunger",  
character=vagabond_npc,  
text="El autoestopista mira por la ventana. 'Hace dos días que no como', dice con voz ronca.",  
options=\[  
{  
"text": "Darle snack",  
"icon": "give",  
"condition": lambda gs: gs.inventory.has("snack"),  
"effect": lambda gs: \[gs.inventory.remove("snack"),  
gs.current_hitchhiker.mood += 20,  
gs.show_message("El vagabundo sonríe. 'Eres buena gente'.")\]  
},  
{  
"text": "Ignorar",  
"icon": "neutral",  
"effect": lambda gs: gs.current_hitchhiker.mood -= 10  
},  
{  
"text": "Ofrecer parar en próxima tienda",  
"icon": "help",  
"effect": lambda gs: \[gs.mark_next_stop("store"),  
gs.current_hitchhiker.mood += 5\]  
}  
\]  
)

**Timing de eventos:**

- Primer evento: 30-60 segundos después de recoger hitchhiker
- Eventos subsecuentes: cada 2-4 minutos de viaje o al pasar ciertos hitos (checkpoints de km)
- Evento final: al despedirse (cuando hitchhiker baja en su destino)

**3.5 Sistema de Spawn de Hitchhikers**

**Mecánica:**

El jugador ve un sprite de persona al costado de la carretera. Tiene 2-3 segundos para decidir si frena o pasa de largo.

**Assets necesarios:**

- hitchhiker_spawn_indicator.png - Flecha o ícono que aparece sobre la figura (8x8 px)
- road_shoulder.png - Tile de banquina donde aparecen (16x16 px)

**Código de referencia:**

class HitchhikerSpawnSystem:  
def **init**(self):  
self.spawn_cooldown = 0  
self.min_distance_between_spawns = 500 # metros

def update(self, game_state):  
if game_state.current_hitchhiker is not None:  
return # Ya hay alguien en el auto  
<br/>self.spawn_cooldown += game_state.delta_distance  
<br/>if self.spawn_cooldown >= self.min_distance_between_spawns:  
if random.random() < 0.3: # 30% probabilidad  
self.spawn_hitchhiker(game_state)  
self.spawn_cooldown = 0  
<br/>def spawn_hitchhiker(self, game_state):  
archetype = random.choice(\["vagabond", "musician", "student", "elder"\])  
hitchhiker = Hitchhiker.create_random(archetype)  
<br/>\# Crear entidad en carretera  
spawn_x = game_state.road_right_edge + 10  
spawn_y = game_state.road_baseline - 24  
<br/>game_state.entities.append(  
HitchhikerRoadEntity(hitchhiker, spawn_x, spawn_y)  
)

class HitchhikerRoadEntity:  
def **init**(self, hitchhiker_data, x, y):  
self.data = hitchhiker_data  
self.x = x  
self.y = y  
self.sprite = load_image("hitchhiker_roadside_waiting.png")  
self.active = True  
self.pickup_zone = pygame.Rect(x - 30, y - 10, 60, 40)

def update(self, game_state):  
\# Se mueve con el parallax de la carretera  
self.x -= game_state.road_scroll_speed  
<br/>if self.x < -50:  
self.active = False # Salió de pantalla, se perdió  
<br/>\# Detectar si jugador frenó cerca  
if self.pickup_zone.colliderect(game_state.player_car.rect):  
if game_state.player_speed < 2: # Está frenando  
game_state.pickup_hitchhiker(self.data)  
self.active = False

**4\. Puntos de Descanso y Locaciones**

**4.1 Tipos de Puntos de Descanso**

| Tipo            | Función principal                             | Frecuencia (km) |
| --------------- | --------------------------------------------- | --------------- |
| Gasolinera      | Recargar combustible, comprar reparaciones    | 80-150          |
| Tienda 24h      | Comprar consumibles, descanso breve           | 100-200         |
| Motel           | Descanso largo (avanza tiempo, restaura todo) | 200-350         |
| Taller mecánico | Reparación completa del auto                  | 150-300         |
| Restaurante     | Comida (recupera hambre conductor/hitchhiker) | 120-250         |

Table 3: Tipos de puntos de descanso

**4.2 Sistema de Aparición**

**Mecánica:**

- Los puntos de descanso aparecen en el horizonte con un cartel anunciador (50-100 metros antes)
- El jugador puede optar por detenerse (cambiar a carril de salida) o continuar
- Al detenerse, la vista cambia a la locación específica con su UI de menú

**Assets gráficos por locación:**

**Carteles anunciadores (roadside signs):**

- sign_gas_station.png - Cartel de gasolinera (32x16 px)
- sign_motel.png - Cartel de motel
- sign_store.png - Cartel de tienda
- sign_restaurant.png - Cartel de restaurante
- sign_mechanic.png - Cartel de taller

**Fondos de locaciones:**

- location_gas_station_bg.png - Vista de surtidor + tienda (320x180 px)
- location_motel_bg.png - Habitación de motel interior
- location_store_bg.png - Interior de convenience store
- location_restaurant_bg.png - Mesa de diner/restaurante
- location_mechanic_bg.png - Interior de taller con auto en elevador

**Props interactivos (por locación):**

**Gasolinera:**

- prop_fuel_pump.png - Bomba de combustible (sprite animado, 2 frames)
- prop_air_pump.png - Inflador de neumáticos
- prop_vending_machine.png - Máquina expendedora

**Motel:**

- prop_bed.png - Cama (clickable para descansar)
- prop_tv.png - TV retro (puede disparar mini-evento)
- prop_phone.png - Teléfono de habitación

**Tienda:**

- prop_shelf.png - Estante con productos
- prop_counter.png - Mostrador con cajero NPC
- prop_fridge.png - Refrigerador de bebidas

**4.3 Código de Sistema de Locaciones**

class RestStop:  
def **init**(self, stop*type, position_km):  
self.type = stop_type # "gas_station", "motel", etc.  
self.position_km = position_km  
self.background = load_image(f"location*{stop_type}\_bg.png")  
[self.shop](http://self.shop) = Shop(stop_type)  
self.services = self.get_available_services()

def get_available_services(self):  
services = {  
"gas_station": \["refuel", "shop", "air_tires"\],  
"motel": \["sleep", "shower", "phone"\],  
"store": \["shop"\],  
"restaurant": \["eat"\],  
"mechanic": \["repair_full", "repair_partial", "upgrade"\]  
}  
return services.get(self.type, \[\])  
<br/>def enter(self, game_state):  
game_state.pause_driving()  
game_state.current_screen = LocationScreen(self, game_state)  
<br/>def exit(self, game_state):  
game_state.resume_driving()  
game_state.current_screen = DrivingScreen(game_state)

class LocationScreen:  
def **init**(self, rest_stop, game_state):  
self.rest_stop = rest_stop  
self.game_state = game_state  
self.menu_items = self.build_menu()

def build_menu(self):  
menu = \[\]  
if "refuel" in self.rest_stop.services:  
menu.append(MenuItem("Llenar tanque", price=30, action="refuel_full"))  
if "shop" in self.rest_stop.services:  
menu.append(MenuItem("Comprar items", action="open_shop"))  
if "sleep" in self.rest_stop.services:  
menu.append(MenuItem("Descansar (6 horas)", price=25, action="sleep"))  
menu.append(MenuItem("Salir", action="exit"))  
return menu  
<br/>def draw(self, surface):  
surface.blit(self.rest_stop.background, (0, 0))  
<br/>y = 60  
for i, item in enumerate(self.menu_items):  
color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)  
draw_text(surface, f"{item.name} - \${item.price}", (40, y), color=color)  
y += 16

**4.4 Eventos Especiales en Locaciones**

Algunos puntos de descanso pueden disparar eventos únicos si se cumplen condiciones:

**Ejemplos:**

- **Motel - Evento "Llamada misteriosa":** Si el jugador usa el teléfono de la habitación, puede recibir una llamada que desbloquea un evento de hitchhiker especial o da una pista sobre un secreto del juego.
- **Gasolinera - Evento "Encuentro nocturno":** Si es de noche (hora del juego 22:00-05:00), hay probabilidad de encontrar un NPC especial que vende ítems raros.
- **Restaurante - Evento "Conversación en la barra":** El jugador puede hablar con otros viajeros NPCs y obtener rumores sobre la carretera adelante (warnings de tormentas, accidentes, etc.).

**Assets para eventos especiales:**

- npc_gas_attendant.png - Empleado de gasolinera (32x48 px)
- npc_motel_clerk.png - Recepcionista de motel
- npc_mechanic.png - Mecánico
- npc_waitress.png - Mesera de restaurante
- npc_mysterious_trader.png - Comerciante raro nocturno

**5\. Sistema de Recursos y Progresión**

**5.1 Recursos del Jugador**

| Recurso           | Rango | Consumo       | Consecuencia si llega a 0           |
| ----------------- | ----- | ------------- | ----------------------------------- |
| Combustible       | 0-100 | 1 por 5 km    | Auto se detiene, game over          |
| Dinero            | 0-999 | Variable      | No puede comprar, limita opciones   |
| Estado del auto   | 0-100 | 0.5 por 10 km | Velocidad reducida, game over en 0  |
| Energía conductor | 0-100 | 1 por 8 km    | Penalización en control, accidentes |

Table 4: Sistema de recursos

**5.2 Progresión por Distancia**

**Biomas y cambios visuales:**

| Distancia (km) | Bioma           | Assets de parallax necesarios    |
| -------------- | --------------- | -------------------------------- |
| 0-200          | Desierto día    | bg_desert_day_far/mid/near.png   |
| 200-400        | Desierto noche  | bg_desert_night_far/mid/near.png |
| 400-600        | Montañas        | bg_mountains_far/mid/near.png    |
| 600-800        | Bosque          | bg_forest_far/mid/near.png       |
| 800-1000       | Costa           | bg_coast_far/mid/near.png        |
| 1000+          | Ciudad nocturna | bg_city_night_far/mid/near.png   |

Table 5: Progresión de biomas

**Assets de carretera por bioma:**

- road_desert.png - Carretera de asfalto agrietado
- road_mountain.png - Carretera de montaña con líneas blancas
- road_forest.png - Carretera húmeda con hojas
- road_coast.png - Carretera costera con arena
- road_city.png - Carretera urbana con marcas de ciudad

**5.3 Sistema de Logros y Objetivos**

**Objetivos de corto plazo (por sesión):**

- Alcanzar cierta distancia (ej: 500 km)
- Recoger 3 hitchhikers diferentes
- Completar un evento especial
- Llegar a un motel antes de quedarse sin energía

**Objetivos de largo plazo (meta-progresión):**

- Desbloquear todos los arquetipos de hitchhikers
- Descubrir todos los eventos secretos
- Alcanzar la ciudad final (km 1500+)
- Coleccionar todos los ítems raros

**6\. Especificaciones Técnicas de Assets**

**6.1 Paleta de Colores Global**

**Recomendación:** Usar una paleta limitada de 32 colores para mantener coherencia visual pixel art.

**Paleta sugerida (valores hex):**

- Cielos: #87CEEB, #4682B4, #191970 (día a noche)
- Carretera: #2F2F2F, #404040, #FFFFFF (asfalto y líneas)
- Vegetación: #228B22, #6B8E23, #8B4513 (verde, marrón)
- UI: #F5DEB3, #D2691E, #8B4513 (tonos tierra/madera)
- Alertas: #FF4500 (peligro), #FFD700 (warning), #32CD32 (ok)

**6.2 Resolución y Escalado**

**Configuración recomendada:**

- Resolución interna del juego: 320x180 px (16:9 low-res)
- Factor de escalado: x4 (output final 1280x720 px)
- Método de escalado: Nearest neighbor (sin suavizado, mantiene píxeles nítidos)
- Todos los sprites deben diseñarse en múltiplos de 8 px para alineación perfecta

**6.3 Organización de Carpetas de Assets**

assets/  
├── backgrounds/  
│ ├── parallax/  
│ │ ├── desert_day_far.png  
│ │ ├── desert_day_mid.png  
│ │ ├── desert_day_near.png  
│ │ ├── desert_night_far.png  
│ │ └── ... (otros biomas)  
│ └── locations/  
│ ├── location_gas_station_bg.png  
│ └── ... (otros fondos de locaciones)  
├── characters/  
│ ├── portraits/  
│ │ ├── hitchhiker_vagabond_01.png  
│ │ └── ... (otros retratos)  
│ └── sprites/  
│ ├── hitchhiker_roadside_waiting.png  
│ └── ... (sprites de personajes)  
├── ui/  
│ ├── hud_fuel_bar.png  
│ ├── event_panel_bg.png  
│ └── ... (elementos de interfaz)  
├── vehicles/  
│ ├── player_car.png  
│ ├── npc_car_01.png  
│ └── ... (otros vehículos)  
├── items/  
│ ├── fuel_can.png  
│ └── ... (ítems del juego)  
├── props/  
│ ├── prop_fuel_pump.png  
│ └── ... (objetos interactivos)  
└── signs/  
├── sign_gas_station.png  
└── ... (carteles de carretera)

**6.4 Convenciones de Nomenclatura**

**Formato:** \[categoría\]\_\[nombre\]\_\[variante\].png

**Ejemplos:**

- bg_desert_day_far.png - Background, desierto, día, capa lejana
- hitchhiker_musician_02.png - Personaje, músico, variante 2
- item_coffee_hot.png - Ítem, café, versión caliente
- prop_vending_machine_lit.png - Prop, máquina expendedora, iluminada

**7\. Prompts Detallados para Generación de Assets con IA**

**7.1 Fondos de Parallax**

**Template de prompt:**  
"pixel art background layer, \[biome\] \[time\], \[depth layer\], side-scrolling game, \[resolution\], indie game style, muted colors, no characters"

**Ejemplos específicos:**

**Desierto día - Capa lejana:**  
"pixel art background layer, desert landscape day time, distant mountains and sky, side-scrolling game, 320x180, indie game style, warm muted colors, no characters, minimal detail"

**Desierto día - Capa media:**  
"pixel art background layer, desert landscape day time, mid-distance cacti and rocks, side-scrolling game, 320x180, indie game style, warm earth tones, no characters, medium detail"

**Desierto día - Capa cercana:**  
"pixel art background layer, desert landscape day time, foreground desert shrubs and fence posts, side-scrolling game, 320x180, indie game style, detailed vegetation, no characters"

**Bosque - Capa lejana:**  
"pixel art background layer, forest landscape, distant pine trees silhouette, side-scrolling game, 320x180, indie game style, dark green and blue tones, misty atmosphere"

**Costa - Capa media:**  
"pixel art background layer, coastal highway, ocean waves and beach in mid-distance, side-scrolling game, 320x180, indie game style, blue and sandy tones, seagulls optional"

**7.2 Vehículos**

**Coche del jugador:**  
"pixel art vehicle, side view, compact sedan, retro 1980s style, 48x24 pixels, simple clean design, red color, indie game sprite, transparent background"

**Tráfico NPC (variaciones):**

- "pixel art vehicle, side view, old pickup truck, weathered blue paint, 52x28 pixels, indie game traffic sprite, transparent background"
- "pixel art vehicle, side view, modern SUV, dark gray, 56x30 pixels, clean design, indie game sprite"
- "pixel art vehicle, side view, vintage van, yellow with rust spots, 50x26 pixels, retro indie game style"

**7.3 Props y Objetos**

**Bomba de gasolina:**  
"pixel art object, vintage gas pump, red and white, front view, 16x32 pixels, indie game prop, simple design, transparent background"

**Máquina expendedora:**  
"pixel art object, vending machine, colorful front panel with drinks, 24x48 pixels, indie game prop, pixel perfect, transparent background"

**Cama de motel:**  
"pixel art furniture, motel bed with blanket, side view, 64x32 pixels, simple retro design, warm colors, indie game interior prop"

**7.4 Ítems de Inventario**

**Template:**  
"pixel art item icon, \[object name\], \[view angle\], 16x16 pixels OR 32x32 pixels, simple clean design, indie game inventory sprite, transparent background"

**Ejemplos:**

- "pixel art item icon, fuel canister, isometric view, 16x16 pixels, red and yellow, simple clean design, indie game inventory sprite, transparent background"
- "pixel art item icon, coffee cup steaming, front view, 16x16 pixels, brown and white, simple design, indie game inventory sprite"
- "pixel art item icon, first aid kit, top-down view, 16x16 pixels, white box with red cross, clean pixel art, transparent background"
- "pixel art item icon, tire/wheel, side view, 16x16 pixels, black rubber with metal rim, simple design, indie game sprite"

**7.5 Carteles de Carretera**

**Template:**  
"pixel art road sign, \[location type\], weathered metal, side view, 32x16 pixels, simple iconic design, muted colors, indie game roadside sprite"

**Ejemplos:**

- "pixel art road sign, gas station symbol, weathered blue metal, side view, 32x16 pixels, simple pump icon, indie game roadside sprite, transparent background"
- "pixel art road sign, motel bed symbol, faded red sign, side view, 32x16 pixels, simple bed icon, retro indie game style"
- "pixel art road sign, food/restaurant fork and knife, yellow sign, 32x16 pixels, simple iconic design, indie game sprite"

**7.6 Personajes Hitchhiker (Detallado)**

**Consideraciones para prompts de personajes:**

- Especificar siempre "64x64 pixels" o "48x48 pixels" según necesidad
- Incluir "portrait" o "bust" para indicar que es retrato, no cuerpo completo
- Especificar ángulo: "side profile", "3/4 view", o "front view"
- Mencionar paleta: "muted colors", "16-color palette", "limited palette"
- Agregar "transparent background" o "alpha channel"

**Prompts específicos por arquetipo (versión extendida):**

**Vagabundo (3 variantes):**

- "pixel art portrait, weathered homeless man with gray beard, tired eyes, worn baseball cap, side profile, 64x64 pixels, muted earth tones, 16-color palette, indie game character, transparent background"
- "pixel art portrait, female vagabond with messy hair, dirt on face, determined expression, hoodie, side profile, 64x64 pixels, muted colors, indie game character sprite, alpha channel"
- "pixel art portrait, elderly homeless person, kind wrinkled face, knit cap, scarf, 3/4 view, 64x64 pixels, warm muted palette, retro game style, transparent background"

**Músico (3 variantes):**

- "pixel art portrait, young musician with headphones around neck, confident smile, colorful jacket, side profile, 64x64 pixels, vibrant limited palette, indie game character, transparent background"
- "pixel art portrait, street guitarist with long hair, bandana, peaceful expression, 3/4 view, 64x64 pixels, warm colors, indie game sprite, alpha channel"
- "pixel art portrait, jazz musician with fedora hat, sunglasses, cool demeanor, side profile, 64x64 pixels, noir color palette, retro game character"

**Fugitivo (3 variantes):**

- "pixel art portrait, nervous young person in dark hoodie, looking over shoulder, tense eyes, side profile, 64x64 pixels, dark muted palette, indie game character, transparent background"
- "pixel art portrait, woman on the run, cap low over eyes, bandage on cheek, determined look, 3/4 view, 64x64 pixels, desaturated colors, indie game sprite"
- "pixel art portrait, mysterious fugitive with scarf covering lower face, intense stare, side profile, 64x64 pixels, shadowy palette, noir indie game style"

**Estudiante (3 variantes):**

- "pixel art portrait, cheerful college student, backpack straps visible, bright smile, messy hair, side profile, 64x64 pixels, vibrant colors, indie game character, transparent background"
- "pixel art portrait, tired grad student with glasses, coffee in hand, exhausted but friendly, 3/4 view, 64x64 pixels, muted warm palette, indie game sprite"
- "pixel art portrait, energetic young traveler, camera around neck, excited expression, side profile, 64x64 pixels, bright saturated colors, retro game character"

**Anciano (3 variantes):**

- "pixel art portrait, kind elderly person with wrinkles, round glasses, gray hair, warm smile, side profile, 64x64 pixels, soft muted palette, indie game character, transparent background"
- "pixel art portrait, wise old traveler with white beard, sun hat, peaceful expression, 3/4 view, 64x64 pixels, earthy tones, indie game sprite"
- "pixel art portrait, elderly woman with silver hair in bun, gentle eyes, knitted shawl, side profile, 64x64 pixels, warm vintage palette, retro game character"

**Misterioso (3 variantes):**

- "pixel art portrait, mysterious figure with wide-brimmed hat obscuring face, shadowy features, side profile, 64x64 pixels, dark noir palette, eerie indie game character, transparent background"
- "pixel art portrait, enigmatic stranger with sunglasses at night, ambiguous gender, collar up, 3/4 view, 64x64 pixels, desaturated cool tones, indie game sprite"
- "pixel art portrait, hooded mysterious person, face in shadow, faint glow from eyes, side profile, 64x64 pixels, dark atmospheric palette, supernatural indie game style"

**8\. Implementación de Parallax Scrolling**

**8.1 Concepto Técnico**

El parallax scrolling crea sensación de profundidad moviendo capas de fondo a diferentes velocidades. Capas lejanas se mueven lento, capas cercanas rápido.

**Fórmula de velocidad por capa:**

Donde:

- \= velocidad de scroll de referencia (ej: 4 píxeles/frame)
- \= multiplicador (ej: 0.2 para lejano, 1.5 para cercano)

**8.2 Código de Implementación**

class ParallaxBackground:  
def **init**(self, biome):  
self.layers = \[  
ParallaxLayer(f"bg*{biome}  
\_far.png", speed_factor=0.2),ParallaxLayer(f"bg*{biome}  
_mid.png", speed_factor=0.5),ParallaxLayer(f"bg_{biome}  
<br/>_near.png", speed_factor=0.8)\]self.road_layer = ParallaxLayer(f"road_{biome}.png", speed_factor=1.2)

def update(self, base_speed, dt):  
for layer in self.layers:  
layer.update(base_speed, dt)  
self.road_layer.update(base_speed, dt)  
<br/>def draw(self, surface):  
for layer in self.layers:  
layer.draw(surface)  
self.road_layer.draw(surface, y_offset=120) # Carretera en parte baja

class ParallaxLayer:  
def **init**(self, image_path, speed_factor):  
self.image = load_image(image_path)  
self.width = self.image.get_width()  
self.speed_factor = speed_factor  
self.scroll_x = 0

def update(self, base_speed, dt):  
self.scroll_x += base_speed \* self.speed_factor \* dt  
self.scroll_x %= self.width # Loop infinito  
<br/>def draw(self, surface, y_offset=0):  
\# Dibuja dos copias de la imagen para loop sin costuras  
x1 = -self.scroll_x  
x2 = x1 + self.width  
<br/>surface.blit(self.image, (x1, y_offset))  
surface.blit(self.image, (x2, y_offset))

**8.3 Optimización de Performance**

- Pre-cargar todas las imágenes de parallax al inicio del juego
- Usar convert() o convert_alpha() en Pygame para optimizar blitting
- Limitar capas de parallax a 3-4 máximo
- Si FPS baja, reducir resolución interna o factor de escalado

**9\. Sistema de Eventos de Juego (Game Events)**

**9.1 Tipos de Eventos**

Además de eventos de hitchhikers, el juego puede tener eventos ambientales y situacionales:

| Tipo de evento | Trigger                     | Ejemplo                     |
| -------------- | --------------------------- | --------------------------- |
| Climático      | Aleatorio cada 200 km       | Tormenta reduce visibilidad |
| Mecánico       | Aleatorio si auto <50%      | Pinchazo de neumático       |
| Policial       | Aleatorio si velocidad >80% | Control de velocidad, multa |
| Encuentro      | Aleatorio día/noche         | Otro conductor pide ayuda   |
| Secreto        | Condiciones específicas     | Camino oculto desbloqueado  |

Table 6: Tipos de eventos del juego

**9.2 Assets para Eventos Ambientales**

**Efectos visuales:**

- fx_rain_overlay.png - Overlay de lluvia semi-transparente (320x180 px, alpha 0.3)
- fx_fog.png - Niebla densa (reduce visibilidad)
- fx_lightning.png - Flash de relámpago (frame único, alta opacidad)
- fx_dust_storm.png - Tormenta de arena para bioma desierto

**Sprites de encuentros:**

- event_broken_car.png - Auto averiado al costado (48x24 px)
- event_police_car.png - Patrulla policial con luces (52x26 px)
- event_roadblock.png - Barricada o control (64x32 px)
- event_deer.png - Animal cruzando carretera (16x24 px)

**9.3 Sistema de Clima Dinámico**

class WeatherSystem:  
def **init**(self):  
self.current_weather = "clear"  
self.weather_duration = 0  
self.effects = {  
"rain": load_image("fx_rain_overlay.png"),  
"fog": load_image("fx_fog.png"),  
"storm": load_image("fx_dust_storm.png")  
}

def update(self, game_state):  
self.weather_duration -= game_state.dt  
<br/>if self.weather_duration <= 0:  
\# Cambio de clima aleatorio  
if random.random() < 0.2:  
self.current_weather = random.choice(\["clear", "rain", "fog"\])  
self.weather_duration = random.randint(300, 600) # 5-10 minutos  
else:  
self.current_weather = "clear"  
<br/>def draw(self, surface):  
if self.current_weather != "clear":  
effect = self.effects\[self.current_weather\]  
surface.blit(effect, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)  
<br/>def get_visibility_modifier(self):  
modifiers = {"clear": 1.0, "rain": 0.8, "fog": 0.5, "storm": 0.3}  
return modifiers.get(self.current_weather, 1.0)

**10\. Ciclo de Juego y Game Loop Principal**

**10.1 Estructura de Estados del Juego**

class GameState(Enum):  
MENU = "menu"  
DRIVING = "driving"  
EVENT = "event"  
LOCATION = "location"  
GAME_OVER = "game_over"  
PAUSE = "pause"

class Game:  
def **init**(self):  
self.state = GameState.MENU  
self.screens = {  
GameState.MENU: MenuScreen(),  
GameState.DRIVING: DrivingScreen(),  
GameState.EVENT: EventScreen(),  
GameState.LOCATION: None, # Se crea dinámicamente  
GameState.GAME_OVER: GameOverScreen()  
}  
self.player_data = PlayerData()  
self.world = World()

def run(self):  
clock = pygame.time.Clock()  
while True:  
dt = clock.tick(60) / 1000.0 # Delta time en segundos  
<br/>events = pygame.event.get()  
for event in events:  
if event.type == pygame.QUIT:  
return  
<br/>current_screen = self.screens\[self.state\]  
current_screen.update(events, dt, self.player_data, self.world)  
current_screen.draw(self.surface)  
<br/>\# Escalado y render final  
scaled = pygame.transform.scale(self.surface, WINDOW_SIZE)  
self.display.blit(scaled, (0, 0))  
pygame.display.flip()

**10.2 Flujo de Sesión de Juego**

Inicio  
↓  
Menú principal  
↓  
\[Jugador presiona "Nueva partida"\]  
↓  
Estado: DRIVING  
↓  
Loop de conducción (parallax, tráfico, recursos)  
↓  
\[Aparece hitchhiker\] → Estado: EVENT  
↓  
Evento de recogida → vuelve a DRIVING con hitchhiker a bordo  
↓  
\[Pasan 60 segundos\] → Estado: EVENT (evento de diálogo)  
↓  
Jugador decide opción → vuelve a DRIVING  
↓  
\[Jugador ve cartel de gasolinera\] → Decide detenerse  
↓  
Estado: LOCATION (gasolinera)  
↓  
Jugador compra combustible/ítems → vuelve a DRIVING  
↓  
\[Combustible llega a 0\] → Estado: GAME_OVER  
↓  
Pantalla de estadísticas finales  
↓  
Opción: volver a menú o reintentar

**11\. Checklist de Assets Completos**

**11.1 Assets de Prioridad Alta (MVP)**

**Backgrounds (parallax):**

- \[ \] Desert day: far, mid, near (3 archivos)
- \[ \] Desert night: far, mid, near (3 archivos)
- \[ \] Road desert (1 archivo)

**UI/HUD:**

- \[ \] Fuel bar frame + fill (2 archivos)
- \[ \] Speedometer base + needle (2 archivos)
- \[ \] Money icon (1 archivo)
- \[ \] Event panel background (1 archivo)
- \[ \] Button states: normal, hover, pressed (3 archivos)

**Vehículos:**

- \[ \] Player car (1 archivo)
- \[ \] NPC car variant 1 (1 archivo)

**Personajes (mínimo 2 arquetipos):**

- \[ \] Hitchhiker vagabond portrait (1 archivo)
- \[ \] Hitchhiker musician portrait (1 archivo)
- \[ \] Hitchhiker roadside waiting sprite (1 archivo)

**Locaciones (mínimo 1):**

- \[ \] Gas station background (1 archivo)
- \[ \] Gas station sign (1 archivo)

**Ítems básicos:**

- \[ \] Fuel can (1 archivo)
- \[ \] Snack (1 archivo)

**Total archivos MVP: ~25-30**

**11.2 Assets de Prioridad Media (Expansión)**

- \[ \] Biomas adicionales: mountains, forest (6 archivos parallax cada uno)
- \[ \] 3 arquetipos más de hitchhikers (3 portraits + variantes)
- \[ \] 2 locaciones más: motel, store (2 backgrounds + signs)
- \[ \] 6 ítems adicionales
- \[ \] Props interactivos: fuel pump, vending machine (2 archivos)
- \[ \] Efectos climáticos: rain, fog (2 archivos)

**Total archivos expansión: ~30-40**

**11.3 Assets de Prioridad Baja (Polish)**

- \[ \] Sprites animados de personajes (entrada/salida coche)
- \[ \] Variantes de NPCs de locaciones (clerk, mechanic)
- \[ \] Eventos especiales sprites
- \[ \] Efectos de partículas (polvo, lluvia animada)
- \[ \] Biomas finales: coast, city

**12\. Guía de Generación con Pollinations (Workflow)**

**12.1 Proceso Paso a Paso**

**Paso 1: Preparar lista de prompts**

Usar la sección 7 de este documento, copiar prompts específicos a un archivo de texto o spreadsheet con columnas:

| Nombre de archivo          | Prompt                          | Prioridad |
| -------------------------- | ------------------------------- | --------- |
| bg_desert_day_far.png      | "pixel art background layer..." | Alta      |
| hitchhiker_vagabond_01.png | "pixel art portrait..."         | Alta      |

Table 7: Template de lista de assets

**Paso 2: Configurar script de generación**

Usar requests Python o curl para llamar a Pollinations API:

import requests  
import time

API_KEY = "TU_CLAVE_AQUI"  
PROMPTS = \[  
("bg_desert_day_far.png", "pixel art background layer, desert..."),  
\# ... resto de prompts  
\]

for filename, prompt in PROMPTS:  
response = requests.post(  
"<https://image.pollinations.ai/prompt/>" + prompt,  
headers={"Authorization": f"Bearer {API_KEY}"}  
)

if response.status_code == 200:  
with open(f"assets/raw/{filename}", "wb") as f:  
f.write(response.content)  
print(f"✓ {filename} generado")  
time.sleep(2) # Rate limiting  
else:  
print(f"✗ Error en {filename}: {response.status_code}")

**Paso 3: Post-procesamiento**

Después de generar con IA:

- Revisar cada imagen en editor pixel art (Aseprite, LibreSprite, GIMP)
- Ajustar tamaños exactos si la IA no respetó las dimensiones
- Unificar paleta de colores (reducir a 16-32 colores si hay más)
- Limpiar bordes y alinear a grid de 8x8 px
- Exportar con transparencia (PNG con alpha channel) donde aplique

**Paso 4: Integración en Pygame**

Organizar en carpetas según estructura definida en sección 6.3 y cargar en el código con paths relativos.

**12.2 Consideraciones de la API de Pollinations**

- Verificar límites de rate (requests por minuto) en la documentación actual
- Guardar archivos raw generados en carpeta separada antes de editar
- Hacer backup de prompts exitosos para regenerar si es necesario
- Si un asset no sale bien, refinar el prompt agregando más detalles específicos

**13\. Conclusión y Próximos Pasos**

**13.1 Resumen de Sistemas Clave**

Este documento define:

- UI analógica integrada al mundo (HUD, pantallas de eventos, locaciones)
- Sistema de hitchhikers con arquetipos, eventos y spawn procedural
- Puntos de descanso (gasolineras, moteles, tiendas) con mecánicas de compra
- Parallax scrolling con biomas progresivos
- Sistema de recursos (combustible, dinero, estado auto/conductor)
- Eventos ambientales y climáticos
- Especificaciones técnicas completas de assets
- Prompts detallados para generación con IA

**13.2 Orden de Implementación Sugerido**

**Fase 1 (Core MVP - 2-3 semanas):**

- Implementar parallax scrolling básico con 1 bioma
- Sistema de conducción (carriles, movimiento jugador, tráfico simple)
- HUD mínimo (combustible, dinero, km)
- Sistema de recursos básico
- 1 punto de descanso (gasolinera) funcional

**Fase 2 (Hitchhikers - 2 semanas):**

- Sistema de spawn de hitchhikers
- 2 arquetipos con 2 eventos cada uno
- Pantalla de eventos con decisiones funcional
- Sistema de mood/relación con personajes

**Fase 3 (Expansión - 3 semanas):**

- 2 biomas adicionales con transiciones
- 3 arquetipos más de hitchhikers
- 2 locaciones adicionales (motel, tienda)
- Sistema de clima dinámico
- Eventos especiales y secretos

**Fase 4 (Polish - 1-2 semanas):**

- Animaciones de personajes
- Efectos de sonido y música
- Menú principal y game over pulidos
- Balanceo de dificultad
- Testing y bugfixing

**13.3 Referencias Adicionales**

Para inspiración adicional de diseño y mecánicas, revisar:

- Keep Driving (Steam) - Referencia principal de UI y feel
- Desert Bus - Concepto de conducción minimalista
- A Short Hike - UI diegética y narrativa emergente
- Papers Please - Interfaz como espacio de trabajo físico
- Reigns - Sistema de decisiones binarias con consecuencias

**Documento preparado para agente de IA generador de assets.**  
**Versión 1.0 - Marzo 2026**
Rendered
Game Design Document: Endless Driving Game (Keep Driving Style)

Proyecto: Juego endless driving con sistema de hitchhikers, eventos y gestión de recursos
Motor: Pygame (Python)
Estilo visual: Pixel art low‑res con parallax scrolling
Inspiración principal: Keep Driving
Autor: Milton Diaz
Fecha: 15 de marzo de 2026

1. Visión General del Juego

1.1 Concepto Core

El jugador conduce por una carretera infinita en vista lateral, gestionando combustible, estado del vehículo y recursos mientras recoge hitchhikers (autoestopistas) que generan eventos narrativos. El objetivo es avanzar la mayor distancia posible, experimentando historias emergentes a través de encuentros aleatorios, puntos de descanso y tiendas.

1.2 Mecánicas Principales

Conducción con carriles: el jugador cambia entre 2-3 carriles evitando tráfico
Sistema de recursos: combustible, dinero, condición del auto, estado del conductor
Hitchhikers: personajes que suben al auto y generan eventos/diálogos
Puntos de descanso: estaciones de servicio, moteles, tiendas de conveniencia
Progresión por distancia: cada kilómetro avanzado desbloquea nuevos biomas/eventos
2. Interfaz de Usuario (UI/UX)

2.1 Filosofía de Diseño UI

Principio clave: Interfaz "analógica" integrada al mundo del juego. Los elementos UI deben sentirse como objetos físicos dentro del coche, no como menús abstractos superpuestos.

Referencias visuales:

Keep Driving: objetos interactivos (guantera, radio, mapa) como UI diegética
Papers Please: interfaz como espacio de trabajo físico
A Short Hike: UI minimal que no rompe inmersión
2.2 HUD Principal (Durante Conducción)

Layout recomendado (resolución base 320x180 px, escalado x4):

Zona	Elementos	Especificaciones técnicas
Superior izquierda	Combustible, Dinero	Barra 60x6 px, texto 8px font
Superior derecha	Día/Hora, KM recorridos	Texto compacto, reloj analógico opcional
Centro	Carretera + vehículo jugador	80% del espacio vertical
Inferior	Velocímetro, Estado auto	Dial simplificado 32x32 px
Lateral derecho	Retrato hitchhiker actual	48x48 px portrait + nombre
Table 1: Distribución del HUD principal

Assets gráficos necesarios para HUD:

hud_fuel_bar.png - Barra de combustible vacía (marco)
hud_fuel_fill.png - Relleno de combustible (se escala en X)
hud_speedometer.png - Dial de velocímetro base
hud_speedometer_needle.png - Aguja rotable
hud_car_condition_icons.png - Sprite sheet: bueno, medio, dañado, crítico (16x16 px cada uno)
hud_day_night_icons.png - Iconos sol/luna para indicador de tiempo
hud_money_icon.png - Ícono de moneda 8x8 px
Código de referencia (estructura básica):

class HUD:
def init(self, game_surface):
self.surface = game_surface
self.fuel_bar = load_image("hud_fuel_bar.png")
self.fuel_fill = load_image("hud_fuel_fill.png")
self.speedometer = load_image("hud_speedometer.png")
self.font = load_pixel_font(8)

def draw(self, fuel_pct, money, km, day_time, car_state):
# Combustible (superior izquierda)
self.surface.blit(self.fuel_bar, (8, 8))
fill_width = int(60 * fuel_pct)
self.surface.blit(self.fuel_fill, (8, 8),
(0, 0, fill_width, 6))
# Dinero
draw_text(self.surface, f"${money}", (8, 18), self.font)
# Kilómetros (superior derecha)
draw_text(self.surface, f"{km} km", (260, 8), self.font)
# Velocímetro (inferior centro)
self.surface.blit(self.speedometer, (144, 150))

2.3 Pantallas de Eventos y Personajes

Escenario: Cuando el jugador recoge un hitchhiker o llega a un punto de descanso, la UI cambia a modo "evento".

Layout pantalla de evento:

Fondo difuminado de la carretera (seguir scroll lento para mantener sensación de movimiento)
Panel central 240x140 px con borde estilo ventana/diálogo
Retrato del personaje: 64x64 px, lado izquierdo del panel
Texto del evento: máximo 3 líneas de 28 caracteres (fuente 8px)
Opciones de decisión: 2-4 botones tipo "analógico" (rectangulares con ícono + texto corto)
Assets gráficos necesarios:

event_panel_bg.png - Marco del panel de diálogo (240x140 px)
event_button_normal.png - Botón de opción estado normal (80x20 px)
event_button_hover.png - Botón estado hover
event_button_pressed.png - Botón estado presionado
event_icons/ - Carpeta con iconos 16x16 px: hablar, dar objeto, rechazar, aceptar, etc.
Código de referencia:

class EventScreen:
def init(self):
self.panel = load_image("event_panel_bg.png")
self.buttons = {
"normal": load_image("event_button_normal.png"),
"hover": load_image("event_button_hover.png"),
"pressed": load_image("event_button_pressed.png")
}

def show_event(self, character, text, options):
# character: objeto con .portrait (Surface 64x64)
# text: string del evento
# options: lista de dict {"text": "Ayudar", "icon": "help", "callback": func}
self.surface.blit(self.panel, (40, 20))
self.surface.blit(character.portrait, (48, 28))
draw_wrapped_text(self.surface, text, (120, 30), max_width=28)
y = 100
for i, opt in enumerate(options):
btn_state = self.get_button_state(i) # normal/hover/pressed
self.surface.blit(self.buttons[btn_state], (50, y))
draw_text(self.surface, opt["text"], (58, y + 6))
y += 24

2.4 UI de Puntos de Descanso (Tiendas/Gasolineras)

Concepto: Menú tipo "escaparate" horizontal donde los ítems son sprites físicos que el jugador puede inspeccionar y comprar.

Layout:

Fondo específico del lugar (interior de tienda, bomba de gasolina, motel)
Contador superior mostrando dinero actual del jugador
3-6 ítems dispuestos horizontalmente en "estantes" o "mostrador"
Cursor/indicador sobre ítem seleccionado
Panel inferior con descripción del ítem + precio + botón comprar
Assets gráficos necesarios por tipo de punto:

Gasolinera:

location_gas_station_bg.png - Fondo de estación de servicio (320x180 px)
items/fuel_can.png - Bidón de combustible (32x32 px)
items/snack.png - Snack genérico
items/map.png - Mapa plegable
items/tire.png - Neumático de repuesto
Tienda de conveniencia:

location_store_bg.png - Interior de tienda (estantes, refrigerador)
items/coffee.png - Café (recupera "estado conductor")
items/first_aid.png - Botiquín
items/magazine.png - Revista (entretenimiento para hitchhikers)
items/cigarettes.png - Cigarros (ítem social para eventos)
Motel:

location_motel_bg.png - Habitación de motel
items/bed_icon.png - Ícono de descanso
items/shower_icon.png - Ícono de ducha (mejora estado)
items/phone_icon.png - Llamada telefónica (desbloquea evento especial)
Mecánica de compra:

class Shop:
def init(self, locationtype):
self.bg = load_image(f"location{location_type}_bg.png")
self.items = self.load_shop_inventory(location_type)
self.selected_index = 0

def load_shop_inventory(self, loc_type):
# Retorna lista de objetos Item
inventories = {
"gas_station": [
Item("Combustible", 20, "fuel_can.png", effect="fuel+50"),
Item("Snack", 5, "snack.png", effect="hunger-10"),
Item("Neumático", 50, "tire.png", effect="repair+25")
],
"store": [
Item("Café", 3, "coffee.png", effect="energy+20"),
Item("Botiquín", 15, "first_aid.png", effect="health+30")
]
}
return inventories.get(loc_type, [])
def draw(self):
self.surface.blit(self.bg, (0, 0))
x = 40
for i, item in enumerate(self.items):
self.surface.blit(item.sprite, (x, 80))
if i == self.selected_index:
draw_rect_outline(self.surface, (x-2, 78, 36, 36), color=(255, 255, 0))
x += 48
# Panel de info del ítem seleccionado
selected = self.items[self.selected_index]
draw_text(self.surface, f"{selected.name} - ${selected.price}", (10, 150))

3. Sistema de Hitchhikers (Autoestopistas)

3.1 Concepto y Propósito

Los hitchhikers son personajes procedurales que suben al auto del jugador en puntos aleatorios de la carretera. Cada uno tiene:

Retrato único (generado por IA o sprite pre-diseñado)
Nombre generado
Personalidad (arquetipo narrativo)
1-3 eventos asociados que se disparan durante el viaje
Posible recompensa o penalización al despedirse
3.2 Arquetipos de Personajes

Tabla de arquetipos recomendados:

Arquetipo	Descripción	Tipo de eventos
Vagabundo	Sin rumbo, filosófico	Conversaciones reflexivas, pide comida
Fugitivo	Huyendo de algo/alguien	Eventos de tensión, riesgo vs recompensa
Músico	Artista en gira	Ofrece música (buff temporal), historias
Anciano	Sabiduría, nostalgia	Consejos útiles, historias del pasado
Estudiante	Joven enérgico	Diálogos alegres, puede ayudar con mecánica
Misterioso	Ambiguo, inquietante	Eventos extraños, recompensas raras
Table 2: Arquetipos de hitchhikers

3.3 Assets Gráficos Necesarios

Retratos de personajes (generación con IA):

Cada personaje requiere un retrato pixel art de 64x64 px. Se recomienda generar variaciones con Pollinations u otro generador siguiendo estos prompts base:

Prompts para generación de retratos:

Vagabundo: "pixel art portrait, 64x64, weathered homeless man, beard, tired eyes, worn cap, muted colors, side profile, indie game character"
Fugitivo: "pixel art portrait, 64x64, nervous young person, hoodie, looking over shoulder, dark colors, tense expression, indie game style"
Músico: "pixel art portrait, 64x64, cheerful musician with guitar case, headphones, colorful jacket, confident smile, indie game character"
Anciano: "pixel art portrait, 64x64, elderly person, glasses, kind wrinkled face, gray hair, warm expression, side profile, retro game style"
Estudiante: "pixel art portrait, 64x64, young college student, backpack, energetic expression, casual clothes, bright colors, indie game art"
Misterioso: "pixel art portrait, 64x64, mysterious figure, shadowy face, hat obscuring features, ambiguous gender, dark palette, eerie vibe"
Consideraciones técnicas para assets de personajes:

Todos los retratos deben usar la misma paleta de colores (16-32 colores máximo)
Ángulo consistente: perfil lateral o 3/4 view
Fondo transparente (PNG con alpha channel)
Carpeta de organización: assets/characters/portraits/
Nomenclatura: hitchhiker_[arquetipo]_[variante].png (ej: hitchhiker_vagabond_01.png)
Sprites adicionales de personajes:

hitchhiker_roadside_waiting.png - Sprite del autoestopista esperando en la carretera (16x24 px, brazo levantado)
hitchhiker_entering_car.png - Animación de subir al auto (2-3 frames)
hitchhiker_leaving_car.png - Animación de bajar del auto (2-3 frames)
3.4 Sistema de Eventos de Hitchhikers

Estructura de un evento:

class HitchhikerEvent:
def init(self, event_id, character, text, options):
self.id = event_id
self.character = character # Referencia al objeto Hitchhiker
self.text = text # Texto del diálogo/situación
self.options = options # Lista de opciones de decisión

def trigger(self, game_state):
# Muestra pantalla de evento
# Pausa la conducción o mantiene scroll lento
# Espera decisión del jugador
pass

Ejemplo de evento definido:

vagabond_event_1 = HitchhikerEvent(
event_id="vagabond_hunger",
character=vagabond_npc,
text="El autoestopista mira por la ventana. 'Hace dos días que no como', dice con voz ronca.",
options=[
{
"text": "Darle snack",
"icon": "give",
"condition": lambda gs: gs.inventory.has("snack"),
"effect": lambda gs: [gs.inventory.remove("snack"),
gs.current_hitchhiker.mood += 20,
gs.show_message("El vagabundo sonríe. 'Eres buena gente'.")]
},
{
"text": "Ignorar",
"icon": "neutral",
"effect": lambda gs: gs.current_hitchhiker.mood -= 10
},
{
"text": "Ofrecer parar en próxima tienda",
"icon": "help",
"effect": lambda gs: [gs.mark_next_stop("store"),
gs.current_hitchhiker.mood += 5]
}
]
)

Timing de eventos:

Primer evento: 30-60 segundos después de recoger hitchhiker
Eventos subsecuentes: cada 2-4 minutos de viaje o al pasar ciertos hitos (checkpoints de km)
Evento final: al despedirse (cuando hitchhiker baja en su destino)
3.5 Sistema de Spawn de Hitchhikers

Mecánica:

El jugador ve un sprite de persona al costado de la carretera. Tiene 2-3 segundos para decidir si frena o pasa de largo.

Assets necesarios:

hitchhiker_spawn_indicator.png - Flecha o ícono que aparece sobre la figura (8x8 px)
road_shoulder.png - Tile de banquina donde aparecen (16x16 px)
Código de referencia:

class HitchhikerSpawnSystem:
def init(self):
self.spawn_cooldown = 0
self.min_distance_between_spawns = 500 # metros

def update(self, game_state):
if game_state.current_hitchhiker is not None:
return # Ya hay alguien en el auto
self.spawn_cooldown += game_state.delta_distance
if self.spawn_cooldown >= self.min_distance_between_spawns:
if random.random() < 0.3: # 30% probabilidad
self.spawn_hitchhiker(game_state)
self.spawn_cooldown = 0
def spawn_hitchhiker(self, game_state):
archetype = random.choice(["vagabond", "musician", "student", "elder"])
hitchhiker = Hitchhiker.create_random(archetype)
# Crear entidad en carretera
spawn_x = game_state.road_right_edge + 10
spawn_y = game_state.road_baseline - 24
game_state.entities.append(
HitchhikerRoadEntity(hitchhiker, spawn_x, spawn_y)
)

class HitchhikerRoadEntity:
def init(self, hitchhiker_data, x, y):
self.data = hitchhiker_data
self.x = x
self.y = y
self.sprite = load_image("hitchhiker_roadside_waiting.png")
self.active = True
self.pickup_zone = pygame.Rect(x - 30, y - 10, 60, 40)

def update(self, game_state):
# Se mueve con el parallax de la carretera
self.x -= game_state.road_scroll_speed
if self.x < -50:
self.active = False # Salió de pantalla, se perdió
# Detectar si jugador frenó cerca
if self.pickup_zone.colliderect(game_state.player_car.rect):
if game_state.player_speed < 2: # Está frenando
game_state.pickup_hitchhiker(self.data)
self.active = False

4. Puntos de Descanso y Locaciones

4.1 Tipos de Puntos de Descanso

Tipo	Función principal	Frecuencia (km)
Gasolinera	Recargar combustible, comprar reparaciones	80-150
Tienda 24h	Comprar consumibles, descanso breve	100-200
Motel	Descanso largo (avanza tiempo, restaura todo)	200-350
Taller mecánico	Reparación completa del auto	150-300
Restaurante	Comida (recupera hambre conductor/hitchhiker)	120-250
Table 3: Tipos de puntos de descanso

4.2 Sistema de Aparición

Mecánica:

Los puntos de descanso aparecen en el horizonte con un cartel anunciador (50-100 metros antes)
El jugador puede optar por detenerse (cambiar a carril de salida) o continuar
Al detenerse, la vista cambia a la locación específica con su UI de menú
Assets gráficos por locación:

Carteles anunciadores (roadside signs):

sign_gas_station.png - Cartel de gasolinera (32x16 px)
sign_motel.png - Cartel de motel
sign_store.png - Cartel de tienda
sign_restaurant.png - Cartel de restaurante
sign_mechanic.png - Cartel de taller
Fondos de locaciones:

location_gas_station_bg.png - Vista de surtidor + tienda (320x180 px)
location_motel_bg.png - Habitación de motel interior
location_store_bg.png - Interior de convenience store
location_restaurant_bg.png - Mesa de diner/restaurante
location_mechanic_bg.png - Interior de taller con auto en elevador
Props interactivos (por locación):

Gasolinera:

prop_fuel_pump.png - Bomba de combustible (sprite animado, 2 frames)
prop_air_pump.png - Inflador de neumáticos
prop_vending_machine.png - Máquina expendedora
Motel:

prop_bed.png - Cama (clickable para descansar)
prop_tv.png - TV retro (puede disparar mini-evento)
prop_phone.png - Teléfono de habitación
Tienda:

prop_shelf.png - Estante con productos
prop_counter.png - Mostrador con cajero NPC
prop_fridge.png - Refrigerador de bebidas
4.3 Código de Sistema de Locaciones

class RestStop:
def init(self, stoptype, position_km):
self.type = stop_type # "gas_station", "motel", etc.
self.position_km = position_km
self.background = load_image(f"location{stop_type}_bg.png")
self.shop = Shop(stop_type)
self.services = self.get_available_services()

def get_available_services(self):
services = {
"gas_station": ["refuel", "shop", "air_tires"],
"motel": ["sleep", "shower", "phone"],
"store": ["shop"],
"restaurant": ["eat"],
"mechanic": ["repair_full", "repair_partial", "upgrade"]
}
return services.get(self.type, [])
def enter(self, game_state):
game_state.pause_driving()
game_state.current_screen = LocationScreen(self, game_state)
def exit(self, game_state):
game_state.resume_driving()
game_state.current_screen = DrivingScreen(game_state)

class LocationScreen:
def init(self, rest_stop, game_state):
self.rest_stop = rest_stop
self.game_state = game_state
self.menu_items = self.build_menu()

def build_menu(self):
menu = []
if "refuel" in self.rest_stop.services:
menu.append(MenuItem("Llenar tanque", price=30, action="refuel_full"))
if "shop" in self.rest_stop.services:
menu.append(MenuItem("Comprar items", action="open_shop"))
if "sleep" in self.rest_stop.services:
menu.append(MenuItem("Descansar (6 horas)", price=25, action="sleep"))
menu.append(MenuItem("Salir", action="exit"))
return menu
def draw(self, surface):
surface.blit(self.rest_stop.background, (0, 0))
y = 60
for i, item in enumerate(self.menu_items):
color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)
draw_text(surface, f"{item.name} - ${item.price}", (40, y), color=color)
y += 16

4.4 Eventos Especiales en Locaciones

Algunos puntos de descanso pueden disparar eventos únicos si se cumplen condiciones:

Ejemplos:

Motel - Evento "Llamada misteriosa": Si el jugador usa el teléfono de la habitación, puede recibir una llamada que desbloquea un evento de hitchhiker especial o da una pista sobre un secreto del juego.
Gasolinera - Evento "Encuentro nocturno": Si es de noche (hora del juego 22:00-05:00), hay probabilidad de encontrar un NPC especial que vende ítems raros.
Restaurante - Evento "Conversación en la barra": El jugador puede hablar con otros viajeros NPCs y obtener rumores sobre la carretera adelante (warnings de tormentas, accidentes, etc.).
Assets para eventos especiales:

npc_gas_attendant.png - Empleado de gasolinera (32x48 px)
npc_motel_clerk.png - Recepcionista de motel
npc_mechanic.png - Mecánico
npc_waitress.png - Mesera de restaurante
npc_mysterious_trader.png - Comerciante raro nocturno
5. Sistema de Recursos y Progresión

5.1 Recursos del Jugador

Recurso	Rango	Consumo	Consecuencia si llega a 0
Combustible	0-100	1 por 5 km	Auto se detiene, game over
Dinero	0-999	Variable	No puede comprar, limita opciones
Estado del auto	0-100	0.5 por 10 km	Velocidad reducida, game over en 0
Energía conductor	0-100	1 por 8 km	Penalización en control, accidentes
Table 4: Sistema de recursos

5.2 Progresión por Distancia

Biomas y cambios visuales:

Distancia (km)	Bioma	Assets de parallax necesarios
0-200	Desierto día	bg_desert_day_far/mid/near.png
200-400	Desierto noche	bg_desert_night_far/mid/near.png
400-600	Montañas	bg_mountains_far/mid/near.png
600-800	Bosque	bg_forest_far/mid/near.png
800-1000	Costa	bg_coast_far/mid/near.png
1000+	Ciudad nocturna	bg_city_night_far/mid/near.png
Table 5: Progresión de biomas

Assets de carretera por bioma:

road_desert.png - Carretera de asfalto agrietado
road_mountain.png - Carretera de montaña con líneas blancas
road_forest.png - Carretera húmeda con hojas
road_coast.png - Carretera costera con arena
road_city.png - Carretera urbana con marcas de ciudad
5.3 Sistema de Logros y Objetivos

Objetivos de corto plazo (por sesión):

Alcanzar cierta distancia (ej: 500 km)
Recoger 3 hitchhikers diferentes
Completar un evento especial
Llegar a un motel antes de quedarse sin energía
Objetivos de largo plazo (meta-progresión):

Desbloquear todos los arquetipos de hitchhikers
Descubrir todos los eventos secretos
Alcanzar la ciudad final (km 1500+)
Coleccionar todos los ítems raros
6. Especificaciones Técnicas de Assets

6.1 Paleta de Colores Global

Recomendación: Usar una paleta limitada de 32 colores para mantener coherencia visual pixel art.

Paleta sugerida (valores hex):

Cielos: #87CEEB, #4682B4, #191970 (día a noche)
Carretera: #2F2F2F, #404040, #FFFFFF (asfalto y líneas)
Vegetación: #228B22, #6B8E23, #8B4513 (verde, marrón)
UI: #F5DEB3, #D2691E, #8B4513 (tonos tierra/madera)
Alertas: #FF4500 (peligro), #FFD700 (warning), #32CD32 (ok)
6.2 Resolución y Escalado

Configuración recomendada:

Resolución interna del juego: 320x180 px (16:9 low-res)
Factor de escalado: x4 (output final 1280x720 px)
Método de escalado: Nearest neighbor (sin suavizado, mantiene píxeles nítidos)
Todos los sprites deben diseñarse en múltiplos de 8 px para alineación perfecta
6.3 Organización de Carpetas de Assets

assets/
├── backgrounds/
│ ├── parallax/
│ │ ├── desert_day_far.png
│ │ ├── desert_day_mid.png
│ │ ├── desert_day_near.png
│ │ ├── desert_night_far.png
│ │ └── ... (otros biomas)
│ └── locations/
│ ├── location_gas_station_bg.png
│ └── ... (otros fondos de locaciones)
├── characters/
│ ├── portraits/
│ │ ├── hitchhiker_vagabond_01.png
│ │ └── ... (otros retratos)
│ └── sprites/
│ ├── hitchhiker_roadside_waiting.png
│ └── ... (sprites de personajes)
├── ui/
│ ├── hud_fuel_bar.png
│ ├── event_panel_bg.png
│ └── ... (elementos de interfaz)
├── vehicles/
│ ├── player_car.png
│ ├── npc_car_01.png
│ └── ... (otros vehículos)
├── items/
│ ├── fuel_can.png
│ └── ... (ítems del juego)
├── props/
│ ├── prop_fuel_pump.png
│ └── ... (objetos interactivos)
└── signs/
├── sign_gas_station.png
└── ... (carteles de carretera)

6.4 Convenciones de Nomenclatura

Formato: [categoría]_[nombre]_[variante].png

Ejemplos:

bg_desert_day_far.png - Background, desierto, día, capa lejana
hitchhiker_musician_02.png - Personaje, músico, variante 2
item_coffee_hot.png - Ítem, café, versión caliente
prop_vending_machine_lit.png - Prop, máquina expendedora, iluminada
7. Prompts Detallados para Generación de Assets con IA

7.1 Fondos de Parallax

Template de prompt:
"pixel art background layer, [biome] [time], [depth layer], side-scrolling game, [resolution], indie game style, muted colors, no characters"

Ejemplos específicos:

Desierto día - Capa lejana:
"pixel art background layer, desert landscape day time, distant mountains and sky, side-scrolling game, 320x180, indie game style, warm muted colors, no characters, minimal detail"

Desierto día - Capa media:
"pixel art background layer, desert landscape day time, mid-distance cacti and rocks, side-scrolling game, 320x180, indie game style, warm earth tones, no characters, medium detail"

Desierto día - Capa cercana:
"pixel art background layer, desert landscape day time, foreground desert shrubs and fence posts, side-scrolling game, 320x180, indie game style, detailed vegetation, no characters"

Bosque - Capa lejana:
"pixel art background layer, forest landscape, distant pine trees silhouette, side-scrolling game, 320x180, indie game style, dark green and blue tones, misty atmosphere"

Costa - Capa media:
"pixel art background layer, coastal highway, ocean waves and beach in mid-distance, side-scrolling game, 320x180, indie game style, blue and sandy tones, seagulls optional"

7.2 Vehículos

Coche del jugador:
"pixel art vehicle, side view, compact sedan, retro 1980s style, 48x24 pixels, simple clean design, red color, indie game sprite, transparent background"

Tráfico NPC (variaciones):

"pixel art vehicle, side view, old pickup truck, weathered blue paint, 52x28 pixels, indie game traffic sprite, transparent background"
"pixel art vehicle, side view, modern SUV, dark gray, 56x30 pixels, clean design, indie game sprite"
"pixel art vehicle, side view, vintage van, yellow with rust spots, 50x26 pixels, retro indie game style"
7.3 Props y Objetos

Bomba de gasolina:
"pixel art object, vintage gas pump, red and white, front view, 16x32 pixels, indie game prop, simple design, transparent background"

Máquina expendedora:
"pixel art object, vending machine, colorful front panel with drinks, 24x48 pixels, indie game prop, pixel perfect, transparent background"

Cama de motel:
"pixel art furniture, motel bed with blanket, side view, 64x32 pixels, simple retro design, warm colors, indie game interior prop"

7.4 Ítems de Inventario

Template:
"pixel art item icon, [object name], [view angle], 16x16 pixels OR 32x32 pixels, simple clean design, indie game inventory sprite, transparent background"

Ejemplos:

"pixel art item icon, fuel canister, isometric view, 16x16 pixels, red and yellow, simple clean design, indie game inventory sprite, transparent background"
"pixel art item icon, coffee cup steaming, front view, 16x16 pixels, brown and white, simple design, indie game inventory sprite"
"pixel art item icon, first aid kit, top-down view, 16x16 pixels, white box with red cross, clean pixel art, transparent background"
"pixel art item icon, tire/wheel, side view, 16x16 pixels, black rubber with metal rim, simple design, indie game sprite"
7.5 Carteles de Carretera

Template:
"pixel art road sign, [location type], weathered metal, side view, 32x16 pixels, simple iconic design, muted colors, indie game roadside sprite"

Ejemplos:

"pixel art road sign, gas station symbol, weathered blue metal, side view, 32x16 pixels, simple pump icon, indie game roadside sprite, transparent background"
"pixel art road sign, motel bed symbol, faded red sign, side view, 32x16 pixels, simple bed icon, retro indie game style"
"pixel art road sign, food/restaurant fork and knife, yellow sign, 32x16 pixels, simple iconic design, indie game sprite"
7.6 Personajes Hitchhiker (Detallado)

Consideraciones para prompts de personajes:

Especificar siempre "64x64 pixels" o "48x48 pixels" según necesidad
Incluir "portrait" o "bust" para indicar que es retrato, no cuerpo completo
Especificar ángulo: "side profile", "3/4 view", o "front view"
Mencionar paleta: "muted colors", "16-color palette", "limited palette"
Agregar "transparent background" o "alpha channel"
Prompts específicos por arquetipo (versión extendida):

Vagabundo (3 variantes):

"pixel art portrait, weathered homeless man with gray beard, tired eyes, worn baseball cap, side profile, 64x64 pixels, muted earth tones, 16-color palette, indie game character, transparent background"
"pixel art portrait, female vagabond with messy hair, dirt on face, determined expression, hoodie, side profile, 64x64 pixels, muted colors, indie game character sprite, alpha channel"
"pixel art portrait, elderly homeless person, kind wrinkled face, knit cap, scarf, 3/4 view, 64x64 pixels, warm muted palette, retro game style, transparent background"
Músico (3 variantes):

"pixel art portrait, young musician with headphones around neck, confident smile, colorful jacket, side profile, 64x64 pixels, vibrant limited palette, indie game character, transparent background"
"pixel art portrait, street guitarist with long hair, bandana, peaceful expression, 3/4 view, 64x64 pixels, warm colors, indie game sprite, alpha channel"
"pixel art portrait, jazz musician with fedora hat, sunglasses, cool demeanor, side profile, 64x64 pixels, noir color palette, retro game character"
Fugitivo (3 variantes):

"pixel art portrait, nervous young person in dark hoodie, looking over shoulder, tense eyes, side profile, 64x64 pixels, dark muted palette, indie game character, transparent background"
"pixel art portrait, woman on the run, cap low over eyes, bandage on cheek, determined look, 3/4 view, 64x64 pixels, desaturated colors, indie game sprite"
"pixel art portrait, mysterious fugitive with scarf covering lower face, intense stare, side profile, 64x64 pixels, shadowy palette, noir indie game style"
Estudiante (3 variantes):

"pixel art portrait, cheerful college student, backpack straps visible, bright smile, messy hair, side profile, 64x64 pixels, vibrant colors, indie game character, transparent background"
"pixel art portrait, tired grad student with glasses, coffee in hand, exhausted but friendly, 3/4 view, 64x64 pixels, muted warm palette, indie game sprite"
"pixel art portrait, energetic young traveler, camera around neck, excited expression, side profile, 64x64 pixels, bright saturated colors, retro game character"
Anciano (3 variantes):

"pixel art portrait, kind elderly person with wrinkles, round glasses, gray hair, warm smile, side profile, 64x64 pixels, soft muted palette, indie game character, transparent background"
"pixel art portrait, wise old traveler with white beard, sun hat, peaceful expression, 3/4 view, 64x64 pixels, earthy tones, indie game sprite"
"pixel art portrait, elderly woman with silver hair in bun, gentle eyes, knitted shawl, side profile, 64x64 pixels, warm vintage palette, retro game character"
Misterioso (3 variantes):

"pixel art portrait, mysterious figure with wide-brimmed hat obscuring face, shadowy features, side profile, 64x64 pixels, dark noir palette, eerie indie game character, transparent background"
"pixel art portrait, enigmatic stranger with sunglasses at night, ambiguous gender, collar up, 3/4 view, 64x64 pixels, desaturated cool tones, indie game sprite"
"pixel art portrait, hooded mysterious person, face in shadow, faint glow from eyes, side profile, 64x64 pixels, dark atmospheric palette, supernatural indie game style"
8. Implementación de Parallax Scrolling

8.1 Concepto Técnico

El parallax scrolling crea sensación de profundidad moviendo capas de fondo a diferentes velocidades. Capas lejanas se mueven lento, capas cercanas rápido.

Fórmula de velocidad por capa:

Donde:

= velocidad de scroll de referencia (ej: 4 píxeles/frame)
= multiplicador (ej: 0.2 para lejano, 1.5 para cercano)
8.2 Código de Implementación

class ParallaxBackground:
def init(self, biome):
self.layers = [
ParallaxLayer(f"bg*{biome}
_far.png", speed_factor=0.2),ParallaxLayer(f"bg*{biome}
mid.png", speed_factor=0.5),ParallaxLayer(f"bg{biome}
near.png", speed_factor=0.8)]self.road_layer = ParallaxLayer(f"road{biome}.png", speed_factor=1.2)

def update(self, base_speed, dt):
for layer in self.layers:
layer.update(base_speed, dt)
self.road_layer.update(base_speed, dt)
def draw(self, surface):
for layer in self.layers:
layer.draw(surface)
self.road_layer.draw(surface, y_offset=120) # Carretera en parte baja

class ParallaxLayer:
def init(self, image_path, speed_factor):
self.image = load_image(image_path)
self.width = self.image.get_width()
self.speed_factor = speed_factor
self.scroll_x = 0

def update(self, base_speed, dt):
self.scroll_x += base_speed * self.speed_factor * dt
self.scroll_x %= self.width # Loop infinito
def draw(self, surface, y_offset=0):
# Dibuja dos copias de la imagen para loop sin costuras
x1 = -self.scroll_x
x2 = x1 + self.width
surface.blit(self.image, (x1, y_offset))
surface.blit(self.image, (x2, y_offset))

8.3 Optimización de Performance

Pre-cargar todas las imágenes de parallax al inicio del juego
Usar convert() o convert_alpha() en Pygame para optimizar blitting
Limitar capas de parallax a 3-4 máximo
Si FPS baja, reducir resolución interna o factor de escalado
9. Sistema de Eventos de Juego (Game Events)

9.1 Tipos de Eventos

Además de eventos de hitchhikers, el juego puede tener eventos ambientales y situacionales:

Tipo de evento	Trigger	Ejemplo
Climático	Aleatorio cada 200 km	Tormenta reduce visibilidad
Mecánico	Aleatorio si auto <50%	Pinchazo de neumático
Policial	Aleatorio si velocidad >80%	Control de velocidad, multa
Encuentro	Aleatorio día/noche	Otro conductor pide ayuda
Secreto	Condiciones específicas	Camino oculto desbloqueado
Table 6: Tipos de eventos del juego

9.2 Assets para Eventos Ambientales

Efectos visuales:

fx_rain_overlay.png - Overlay de lluvia semi-transparente (320x180 px, alpha 0.3)
fx_fog.png - Niebla densa (reduce visibilidad)
fx_lightning.png - Flash de relámpago (frame único, alta opacidad)
fx_dust_storm.png - Tormenta de arena para bioma desierto
Sprites de encuentros:

event_broken_car.png - Auto averiado al costado (48x24 px)
event_police_car.png - Patrulla policial con luces (52x26 px)
event_roadblock.png - Barricada o control (64x32 px)
event_deer.png - Animal cruzando carretera (16x24 px)
9.3 Sistema de Clima Dinámico

class WeatherSystem:
def init(self):
self.current_weather = "clear"
self.weather_duration = 0
self.effects = {
"rain": load_image("fx_rain_overlay.png"),
"fog": load_image("fx_fog.png"),
"storm": load_image("fx_dust_storm.png")
}

def update(self, game_state):
self.weather_duration -= game_state.dt
if self.weather_duration <= 0:
# Cambio de clima aleatorio
if random.random() < 0.2:
self.current_weather = random.choice(["clear", "rain", "fog"])
self.weather_duration = random.randint(300, 600) # 5-10 minutos
else:
self.current_weather = "clear"
def draw(self, surface):
if self.current_weather != "clear":
effect = self.effects[self.current_weather]
surface.blit(effect, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
def get_visibility_modifier(self):
modifiers = {"clear": 1.0, "rain": 0.8, "fog": 0.5, "storm": 0.3}
return modifiers.get(self.current_weather, 1.0)

10. Ciclo de Juego y Game Loop Principal

10.1 Estructura de Estados del Juego

class GameState(Enum):
MENU = "menu"
DRIVING = "driving"
EVENT = "event"
LOCATION = "location"
GAME_OVER = "game_over"
PAUSE = "pause"

class Game:
def init(self):
self.state = GameState.MENU
self.screens = {
GameState.MENU: MenuScreen(),
GameState.DRIVING: DrivingScreen(),
GameState.EVENT: EventScreen(),
GameState.LOCATION: None, # Se crea dinámicamente
GameState.GAME_OVER: GameOverScreen()
}
self.player_data = PlayerData()
self.world = World()

def run(self):
clock = pygame.time.Clock()
while True:
dt = clock.tick(60) / 1000.0 # Delta time en segundos
events = pygame.event.get()
for event in events:
if event.type == pygame.QUIT:
return
current_screen = self.screens[self.state]
current_screen.update(events, dt, self.player_data, self.world)
current_screen.draw(self.surface)
# Escalado y render final
scaled = pygame.transform.scale(self.surface, WINDOW_SIZE)
self.display.blit(scaled, (0, 0))
pygame.display.flip()

10.2 Flujo de Sesión de Juego

Inicio
↓
Menú principal
↓
[Jugador presiona "Nueva partida"]
↓
Estado: DRIVING
↓
Loop de conducción (parallax, tráfico, recursos)
↓
[Aparece hitchhiker] → Estado: EVENT
↓
Evento de recogida → vuelve a DRIVING con hitchhiker a bordo
↓
[Pasan 60 segundos] → Estado: EVENT (evento de diálogo)
↓
Jugador decide opción → vuelve a DRIVING
↓
[Jugador ve cartel de gasolinera] → Decide detenerse
↓
Estado: LOCATION (gasolinera)
↓
Jugador compra combustible/ítems → vuelve a DRIVING
↓
[Combustible llega a 0] → Estado: GAME_OVER
↓
Pantalla de estadísticas finales
↓
Opción: volver a menú o reintentar

11. Checklist de Assets Completos

11.1 Assets de Prioridad Alta (MVP)

Backgrounds (parallax):

[ ] Desert day: far, mid, near (3 archivos)
[ ] Desert night: far, mid, near (3 archivos)
[ ] Road desert (1 archivo)
UI/HUD:

[ ] Fuel bar frame + fill (2 archivos)
[ ] Speedometer base + needle (2 archivos)
[ ] Money icon (1 archivo)
[ ] Event panel background (1 archivo)
[ ] Button states: normal, hover, pressed (3 archivos)
Vehículos:

[ ] Player car (1 archivo)
[ ] NPC car variant 1 (1 archivo)
Personajes (mínimo 2 arquetipos):

[ ] Hitchhiker vagabond portrait (1 archivo)
[ ] Hitchhiker musician portrait (1 archivo)
[ ] Hitchhiker roadside waiting sprite (1 archivo)
Locaciones (mínimo 1):

[ ] Gas station background (1 archivo)
[ ] Gas station sign (1 archivo)
Ítems básicos:

[ ] Fuel can (1 archivo)
[ ] Snack (1 archivo)
Total archivos MVP: ~25-30

11.2 Assets de Prioridad Media (Expansión)

[ ] Biomas adicionales: mountains, forest (6 archivos parallax cada uno)
[ ] 3 arquetipos más de hitchhikers (3 portraits + variantes)
[ ] 2 locaciones más: motel, store (2 backgrounds + signs)
[ ] 6 ítems adicionales
[ ] Props interactivos: fuel pump, vending machine (2 archivos)
[ ] Efectos climáticos: rain, fog (2 archivos)
Total archivos expansión: ~30-40

11.3 Assets de Prioridad Baja (Polish)

[ ] Sprites animados de personajes (entrada/salida coche)
[ ] Variantes de NPCs de locaciones (clerk, mechanic)
[ ] Eventos especiales sprites
[ ] Efectos de partículas (polvo, lluvia animada)
[ ] Biomas finales: coast, city
12. Guía de Generación con Pollinations (Workflow)

12.1 Proceso Paso a Paso

Paso 1: Preparar lista de prompts

Usar la sección 7 de este documento, copiar prompts específicos a un archivo de texto o spreadsheet con columnas:

Nombre de archivo	Prompt	Prioridad
bg_desert_day_far.png	"pixel art background layer..."	Alta
hitchhiker_vagabond_01.png	"pixel art portrait..."	Alta
Table 7: Template de lista de assets

Paso 2: Configurar script de generación

Usar requests Python o curl para llamar a Pollinations API:

import requests
import time

API_KEY = "TU_CLAVE_AQUI"
PROMPTS = [
("bg_desert_day_far.png", "pixel art background layer, desert..."),
# ... resto de prompts
]

for filename, prompt in PROMPTS:
response = requests.post(
"https://image.pollinations.ai/prompt/" + prompt,
headers={"Authorization": f"Bearer {API_KEY}"}
)

if response.status_code == 200:
with open(f"assets/raw/{filename}", "wb") as f:
f.write(response.content)
print(f"✓ {filename} generado")
time.sleep(2) # Rate limiting
else:
print(f"✗ Error en {filename}: {response.status_code}")

Paso 3: Post-procesamiento

Después de generar con IA:

Revisar cada imagen en editor pixel art (Aseprite, LibreSprite, GIMP)
Ajustar tamaños exactos si la IA no respetó las dimensiones
Unificar paleta de colores (reducir a 16-32 colores si hay más)
Limpiar bordes y alinear a grid de 8x8 px
Exportar con transparencia (PNG con alpha channel) donde aplique
Paso 4: Integración en Pygame

Organizar en carpetas según estructura definida en sección 6.3 y cargar en el código con paths relativos.

12.2 Consideraciones de la API de Pollinations

Verificar límites de rate (requests por minuto) en la documentación actual
Guardar archivos raw generados en carpeta separada antes de editar
Hacer backup de prompts exitosos para regenerar si es necesario
Si un asset no sale bien, refinar el prompt agregando más detalles específicos
13. Conclusión y Próximos Pasos

13.1 Resumen de Sistemas Clave

Este documento define:

UI analógica integrada al mundo (HUD, pantallas de eventos, locaciones)
Sistema de hitchhikers con arquetipos, eventos y spawn procedural
Puntos de descanso (gasolineras, moteles, tiendas) con mecánicas de compra
Parallax scrolling con biomas progresivos
Sistema de recursos (combustible, dinero, estado auto/conductor)
Eventos ambientales y climáticos
Especificaciones técnicas completas de assets
Prompts detallados para generación con IA
13.2 Orden de Implementación Sugerido

Fase 1 (Core MVP - 2-3 semanas):

Implementar parallax scrolling básico con 1 bioma
Sistema de conducción (carriles, movimiento jugador, tráfico simple)
HUD mínimo (combustible, dinero, km)
Sistema de recursos básico
1 punto de descanso (gasolinera) funcional
Fase 2 (Hitchhikers - 2 semanas):

Sistema de spawn de hitchhikers
2 arquetipos con 2 eventos cada uno
Pantalla de eventos con decisiones funcional
Sistema de mood/relación con personajes
Fase 3 (Expansión - 3 semanas):

2 biomas adicionales con transiciones
3 arquetipos más de hitchhikers
2 locaciones adicionales (motel, tienda)
Sistema de clima dinámico
Eventos especiales y secretos
Fase 4 (Polish - 1-2 semanas):

Animaciones de personajes
Efectos de sonido y música
Menú principal y game over pulidos
Balanceo de dificultad
Testing y bugfixing
13.3 Referencias Adicionales

Para inspiración adicional de diseño y mecánicas, revisar:

Keep Driving (Steam) - Referencia principal de UI y feel
Desert Bus - Concepto de conducción minimalista
A Short Hike - UI diegética y narrativa emergente
Papers Please - Interfaz como espacio de trabajo físico
Reigns - Sistema de decisiones binarias con consecuencias
Documento preparado para agente de IA generador de assets.
Versión 1.0 - Marzo 2026

Feed
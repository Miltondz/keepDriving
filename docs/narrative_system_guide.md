# Guía del Sistema de Narrativa JSON — Keep Driving

El juego **Keep Driving** utiliza un sistema basado en datos para manejar gran parte de su lógica narrativa, encuentros y personajes. Toda esta configuración se encuentra en `data/narrative.json`.

---

## Estructura General del Archivo

El archivo `narrative.json` se divide en tres secciones principales:

1.  **`encounters`**: Define los eventos que ocurren en la carretera.
2.  **`hitchhiker_templates`**: Define los personajes que puedes recoger.
3.  **`locations`**: Define los biomas, ciudades y qué encuentros ocurren en cada lugar.

---

## 1. Crear un Nuevo Encuentro (`encounters`)

Cada entrada en el diccionario `encounters` representa un evento único.

```json
"nombre_del_evento": {
  "title": "TÍTULO EN MAYÚSCULAS",
  "description": "Lo que el jugador ve inicialmente.",
  "flavour": "Texto de ambientación (opcional).",
  "avatar": "nombre_del_portrait",
  "difficulty": 1,
  "tags": ["mi_tag"],
  "options": [
    {
      "text": "Texto de la opción",
      "description": "Lo que pasará si la eliges.",
      "effects": {
        "sanity": -5,
        "fuel": -10,
        "condition": -15,
        "money": 20
      },
      "icon_color": [255, 100, 100]
    }
  ]
}
```

### Campos Clave:
- **`avatar`**: Referencia al nombre del archivo en `assets/sprites/portraits/` (sin el `.png`).
- **`effects`**: Diccionario con los cambios en las estadísticas del jugador.
- **`item_required`**: (Opcional) Si la opción requiere un ítem específico del inventario (ej: `"coffee"`).

---

## 2. Crear un Nuevo Mochilero (`hitchhiker_templates`)

Los mochileros son personajes complejos con habilidades que evolucionan.

```json
{
  "name": "El Mecánico",
  "avatar": "mechanic",
  "color": [200, 180, 150],
  "personality": "quiet",
  "destination": "Redrock Junction",
  "description": "Una breve descripción del personaje.",
  "km_bonded": 80,
  "km_complicated": 200,
  "abilities": {
    "NEW": [
      {
        "name": "Arreglo Rápido",
        "description": "Repara 15 de condición.",
        "tags": ["breakdown"],
        "effect": "repair_15"
      }
    ],
    "BONDED": [...],
    "COMPLICATED": [...]
  },
  "passive": { "sanity_per_km": 0.5 },
  "conversations": [
    "Diálogo 1",
    "Diálogo 2"
  ]
}
```

### Notas sobre Habilidades:
- **`NEW`**: Habilidades disponibles apenas suben al auto.
- **`BONDED`**: Se desbloquean tras recorrer `km_bonded`.
- **`COMPLICATED`**: Se desbloquean tras recorrer `km_complicated` (pueden tener efectos negativos).
- **`effect`**: La clave que el código debe reconocer para ejecutar la lógica (ej: `repair_15`, `restore_sanity_10`).

---

## 3. Configurar Biomas e Inclusión (`locations`)

Para que un encuentro aparezca en el juego, debe estar incluido en la lista de `encounters` de un bioma específico.

```json
"biomes": {
  "desert": {
    "encounters": [
      "flat_tire",
      "hitchhiker",
      "mi_nuevo_evento"
    ],
    "color": [200, 150, 80]
  }
}
```

---

## Mejores Prácticas y Consejos

1.  **Avatares**: Asegúrate de que el nombre puesto en `"avatar"` coincida con un archivo PNG en la carpeta de retratos.
2.  **Validación**: Si rompes el formato JSON (por ejemplo, olvidando una coma), el juego cargará mochileros "fantasmas" o fallará al iniciar. Usa un validador de JSON si tienes dudas.
3.  **Dificultad**: El campo `difficulty` (1-5) determina qué tan raros o peligrosos son los eventos (aunque actualmente el motor los elige aleatoriamente de la lista del bioma).

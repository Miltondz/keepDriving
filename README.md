# 🚐 Keep Driving — Road Trip RPG

A high-fidelity, retro-inspired Road Trip RPG built with **Python** and **Pygame-ce**. Experience a procedurally generated journey where resource management, random encounters, and atmospheric driving meet.

![Game Preview](assets/preview.png)

![Gameplay Interface](assets/gameplay.png)

## 🌟 Key Features

### 🛤️ Dynamic World & Driving
*   **Procedural Routes:** Every run generates a unique set of road segments and settlements across different biomes (Desert, Forest, Mountain, etc.).
*   **High-Speed Mechanics & Consequences:** Accelerate up to **170 km/h** with torque-based acceleration, but beware: driving over 100 km/h exponentially increases the risk of **fatal Police Encounters** and drastically raises **real-time fuel consumption**.
*   **Dynamic Backgrounds:** Multi-layered parallax scrolling that reacts to your speed, biome, and correctly mirrored oncoming traffic logic.

### 🎮 Advanced HUD & UI
*   **Animated Dashboard:** A retro-styled lower HUD with transparent cutouts displaying a procedural scrolling road, along with a **Radar Array** that shows your vehicle's position, total distance driven, km to the next Point of Interest, and color-coded event markers.
*   **Status Systems:** Track Car Condition, dynamic analog Fuel needles, Player Sanity, and a **dynamic Speedometer** that turns red when speeding.
*   **Multi-View System:** Toggle between **Interior view (F1)**, **Map view (F2)**, and **Road view (F3)**, now featuring appropriate character seating avatars.

### 🎭 Interactive Systems
*   **📟 Mixtape & Cassette System:** The system dynamically scans your music folders for images and renders them as physical tapes. Includes a high-definition glovebox preview for each mixtape.
*   **💬 Cinematic Dialogue HUD:** Conversations with passengers feature automatic word wrapping and speaker portraits, placed strategically at the top of the screen.
*   **Resource Management:** Manage your cash to refuel and repair your van at settlements. Fuel consumption reacts in real-time to your speed and torque usage.

### 🌗 Atmospheric Systems
*   **Dynamic Day/Night Cycle:** A sophisticated lighting system that transitions the world from dawn to dusk, synchronized with a real-time LCD clock on the dashboard.
*   **Biome-Specific Palettes:** Each region (Desert, Forest, Mountain, City) features unique sky and ground palettes that shift beautifully with the time of day.

## ⌨️ Controls

| Key | Action |
|-----|--------|
| **W / ↑** | Accelerate |
| **S / ↓** | Brake / Reverse |
| **Mouse Click**| Advance passenger dialogue (on Dash) or Open Glovebox |
| **F1** | Interior View |
| **F2** | Strategy / Map View |
| **F3** | Driving / Road View (Default) |
| **ESC** | Quit Game / Close Glovebox |

**During Settlements:**
*   **R**: Interaction / Enter Shop
*   **L**: Leave Town

## 🛠️ Technical Stack

*   **Engine:** [Pygame-ce](https://pyga.me/) (Python Game Engine)
*   **Language:** Python 3.10+
*   **Assets:** Dynamic asset loading with a specialized **Surface Cache** to handle high-resolution textures without affecting frame rates.

## 🚀 Getting Started

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Miltondz/keepDriving.git
    cd keepDriving
    ```

2.  **Install Dependencies:**
    ```bash
    pip install pygame-ce
    ```

3.  **Run the Game:**
    ```bash
    python main.py
    ```

## 🗺️ Roadmap
- [x] High-speed police encounter logic.
- [x] Dynamic radar for HUD road.
- [x] Interactive multi-line passenger storytelling.
- [x] Precise Day/Night lighting and biome transitions.
- [x] Roadside object pre-visualization (approach markers).
- [x] **New:** Interactive Mixtape system with custom artwork loading.
- [x] **New:** Advanced Dialogue HUD with word-wrapping and portraits.
- [ ] Complex inventory system with usable items.
- [ ] Weather-specific handling physics (hydroplaning/skidding).

---
*Created with ❤️ for retro gaming fans.*

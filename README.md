# 🚐 Keep Driving — Road Trip RPG

A high-fidelity, retro-inspired Road Trip RPG built with **Python** and **Pygame-ce**. Experience a procedurally generated journey where resource management, random encounters, fast-paced highway driving, and atmospheric storytelling perfectly merge into a single retro-aesthetic package.

![Game Preview](assets/preview.png)
_Driving across beautifully generated procedural biomes._

![Gameplay Interface](assets/gameplay.png)
_Retro-styled transparent dashboard showcasing inventory, radar, and real-time analog instruments._

## 🌟 Key Features

### 🛤️ Dynamic World & Highway Driving
*   **Procedural Routes:** Every run generates a unique set of road segments, cities, specific encounters, and fully interactive settlements across distinct biomes (Desert, Forest, Mountain, Highway, Snow, City, Village, Coastal).
*   **High-Speed Mechanics & Consequences:** Accelerate up to **170 km/h** with torque-based acceleration physics! But beware: driving over 100 km/h exponentially increases the risk of fatal Police Encounters and drastically raises your real-time fuel consumption.
*   **Dynamic Backgrounds:** Multi-layered, infinitely scrolling parallax backgrounds that react to your speed, current biome, and correctly mirrored oncoming traffic logic. 
*   **Responsive AI Traffic:** Other vehicles spawn randomly on the road. Colliding with them at high speeds damages your car's physical condition and forces severe deceleration.

### 📖 Narrative-Driven Rogue-Like Layer
*   **Procedural Story Arcs:** Pick up hitchhikers with unique backstories and objectives that evolve through multiple stages based on your choices
*   **Emergent Storytelling:** Your decisions with hitchhikers (helping, refusing, trading) unlock different story paths and legacy rewards
*   **Legacy System:** Procedural unlocks based on run-specific counters (scavenging successes, resources given away, peaceful encounters, hazards avoided, trades completed, self-sufficiency)
*   **Multiple Narrative Variants:** Choose between post-apocalyptic and cyberpunk story settings, each with unique encounters, hitchhikers, and biomes

### 🏛️ Advanced HUD & UI
*   **Analog Dashboard:** A highly-detailed, retro-styled lower HUD with transparent cutouts displaying a procedural scrolling road. Features a **Radar Array** that shows your vehicle's position, total distance traveled, kilometers to the next Point of Interest, and color-coded event markers.
*   **Real-time Status Management:** Keep a constant eye on Car Condition, an analog Fuel needle physics simulation, and your character's remaining Energy/Sanity. Be careful: the speedometer dial will shift into a red warning zone if you start heavily speeding.
*   **Multi-View System:** Effortlessly toggle between **Interior view (F1)** to check your seats, **Map view (F2)** to chart your strategic path across nodes, and **Road view (F3)** for intense default driving. Features character avatars seated dynamically in the top window.

### 🎭 Interactive Systems & Settlements
*   **Settlement Docking System:** When stopping at gas stations, motels, or minimarkets, the exterior traffic will pause, giving you a clean cinematic view. Double-click the building to automatically scale and display the highly-detailed **interior overview** exactly on the right-hand panel of your screen. 
*   **📟 Mixtape & Cassette System:** The system dynamically scans your music folder for `.mp3` tracks and `.png`/`.jpg` album covers, rendering them as physical retro tapes. Slide a tape into the cassette deck to change the background music!
*   **💬 Cinematic Dialogue:** Intense, multi-line branching conversational encounters feature automatic word-wrapping and character portraits. Who you pick up hitchhiking will change the course of your journey.
*   **🧬 Legacy Screen:** Press **V** in any settlement to view your unlocked legacies and their permanent effects on your current run
*   **Resource Management:** Carefully manage your cash ($) to refuel and repair your van at varying roadside stops. Fuel burns realistically depending on your speed and applied torque.

### 🌗 Atmospheric Systems
*   **Dynamic Day/Night Cycle:** A sophisticated lighting system that transitions the world from dawn to dusk, synchronized with a real-time LCD 12-hour AM/PM clock on the dashboard. At night, your car emits a glowing cone of headlights.
*   **Biome-Specific Palettes:** Each region features a painstakingly selected combination of unique procedurally colored skies, field grounds, and multiple layers of mountain ranges that shift beautifully in tone depending on the time of day.

## ⌨️ Controls

| Key | Action |
|-----|--------|
| **W / ↑** | Accelerate |
| **S / ↓** | Brake / Reverse |
| **Mouse Click**| Advance passenger dialogue, Insert Mixtapes, select Encounters |
| **Double Click**| Enter Building Interiors (When stopped at Settlements) |
| **F1** | Interior View |
| **F2** | Strategy / Map View |
| **F3** | Driving / Road View (Default) |
| **ESC** | Quit Game / Close Glovebox / Exit Encounters |

**During Settlements:**
*   **R**: Quick Interaction / Refuel Auto-Repair
*   **F**: Repair Service
*   **H**: Recruit Hitchhiker
*   **L**: Leave Town (Restores Traffic and Resumes Highway)
*   **S**: Snack / Rest
*   **V**: View Legacies (NEW)

**During Gameplay:**
*   **SPACE**: Pause Game
*   **F1-F3**: View Modes (Interior/Map/Road)
*   **F4-F9**: Debug Weather/Time Controls
*   **[ , ]**: Volume Down / Volume Up
*   **N**: Next Track
*   **K**: Tape Collection

## 🏆 Legacy System

The legacy system tracks your playstyle throughout each run and grants permanent bonuses/penalties based on your choices:

### Scavenging Legacies
*   **The Wasteland Warden** (+15% yield from wrecked vehicles) - For frequent scavengers
*   **The Lone Wolf** (-25% scavenging time, -40% trust gains) - For solo players who don't share resources

### Social Legacies
*   **The Compassionate Scavenger** (+20% trade success with desperate hitchhikers) - For generous players
*   **The Mediator** (+15% success in social encounters) - For peaceful encounter specialists
*   **The Careful Navigator** (-10% fuel consumption when avoiding hazards) - For cautious drivers

### Trade Legacies
*   **The Seasoned Trader** (+10% profit on all trades) - For experienced traders
*   **The Self‑Reliant** (-15% reliance on NPC aid) - For players who rarely accept help

### Accessing Your Legacies
Press **V** while in any settlement to open the Legacy Screen and view all unlocked permanent effects for your current run.

## 🎮 Narrative Variants

The game features two distinct narrative settings that change encounters, hitchhikers, and story elements:

1. **Post-Apocalyptic** - Wasteland survival with limited resources and dangerous encounters
2. **Cyberpunk** - Neon-lit highways with corporate intrigue and high-tech scavenged items

Each variant includes unique hitchhiker story arcs that evolve through multiple stages, with legacy rewards tied to completing these arcs.

## 🛠️ Technical Stack & Architecture

*   **Engine:** [Pygame-ce](https://pyga.me/) (A highly optimized Python game engine fork).
*   **Language:** Python 3.10+
*   **Assets:** Dynamic asset loading with a specialized **Surface Cache**, preventing frame drops by pre-calculating and storing resized high-resolution textures.
*   **Narrative System:** External JSON files for encounters, hitchhikers, and locations, allowing for easy modification and expansion.
*   **Legacy System:** Procedural generation based on tracked player statistics throughout each run.

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

4.  **Explore the Narrative:**
    *   Pick up hitchhikers and make choices that affect their story arcs
    *   Visit settlements and press **V** to view your evolving legacy
    *   Try different playstyles (generous vs. selfish, peaceful vs. aggressive) to unlock different legacies

## 📝 Recent Changelog (2026-03-22)

### Added
- **Narrative-Driven Rogue-Like Layer:**
  - Procedural hitchhiker story arcs with multiple stages
  - Legacy system with permanent run-based bonuses/penalties
  - Two narrative variants: post-apocalyptic and cyberpunk
  - Legacy screen accessible with **V** key in settlements
  
- **Enhanced Settlement Interaction:**
  - Fixed hitchhiker duplication issue (only one recruitment per settlement visit)
  - Added legacy viewing option to settlement menu ([V] VIEW LEGACIES)
  
- **Technical Improvements:**
  - Fixed Unicode encoding issues in print statements
  - Resolved renderer UnboundLocalError for car position variables
  - Fixed special characters in legacy descriptions

### Fixed
- **Parallax Background Gaps & Crashes:**
  - Shifted all base procedural road layers downwards by `+10 pixels` to seamlessly hide blue sky-bar anomalies leaking below textures.
  - Resolved an `IndexError` crash in background hill rendering by ensuring the `highway` biome contains exactly 3 colors for procedural layer generation.
- **Resolution Import Errors (Unbound Locals):**
  - Removed rogue duplicate imports of native resolution variables inside input handlers, terminating `UnboundLocalErrors` associated with validating global `W` and `H` viewport boundaries.
- **Settlement Systems:**
  - Prevented multiple hitchhiker recruitment in the same settlement visit
  - Fixed legacy system special character encoding issues

---
*Created with ❤️ for retro road-trip gaming fans who love emergent storytelling and meaningful progression systems.*
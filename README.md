
# Dungeon Master AI – Python RPG Engine (Backend Only)

This repository contains the **backend core** of a modular role-playing game (RPG) engine, designed in Python using a clean object-oriented architecture and a stack-based finite state machine (FSM). The project aims to evolve into an AI-driven, narratively rich RPG system, where a virtual Dungeon Master powered by GPT can enhance player immersion.

![Descrizione immagine](Image.png)

## 🏗️ Architecture Overview

The project is organized into well-defined modules:

gioco_rpg/

├── main.py # Entry point 

├── core/ # Game loop and I/O interface 

├── entities/ # Player, NPCs, enemies, shared logic 

├── items/ # Objects and interactive elements 

├── states/ # Game states (map, combat, inventory, etc.) 

├── util/ # Dice rolling, helper functions 

├── data/ # Game data in JSON format

└── world/ # Map system, tile controller, environment


Each game phase (map exploration, combat, dialogues, inventory management) is handled through a **stacked FSM** (`BaseState`), enabling smooth transitions and layered interactions (e.g., opening a chest pauses exploration and pushes a dialog or loot state).

## 🔮 Features

- Modular structure ready for extension
- Complete core game logic (movement, combat, dialogues, inventory)
- ASCII-based map system using a tile controller
- Entity factory system for dynamic content generation
- Full separation of game logic from user interface (ready for future web/GUI/AI integrations)
- Fully testable backend (no Pygame dependencies in this repo)
- Centralized data loading system via data_manager.py using JSON format
- Improved monster combat system with monster type selection and difficulty levels
- Advanced map navigation system with destination selection state
- Enhanced interaction with potions and inventory items
- Improved placement of NPCs and interactive objects on maps

## 🚀 Current Roadmap

✅ Centralized data loading system via data_manager.py using JSON format  
✅ Improved monster combat system:  
   - Specific monster type selection  
   - Customizable difficulty levels  
   - Rewards and experience points proportional to difficulty  
✅ Enhanced map navigation:  
   - Dedicated map selection state  
   - Ability to choose destination at game start  
   - Elimination of automatic redirection to tavern  
✅ Improved interaction with objects and potions:  
   - More intuitive user interface for item usage  
   - Optimized potion effects  
   - Advanced inventory management  
✅ Enhanced placement of NPCs and interactive objects on maps:  
   - Precise predefined positions to improve gameplay experience  
   - Alternative positioning system when main positions are occupied  
⬜ Add modular I/O interfaces (text, GUI, AI)  
⬜ Web frontend (probably React)  
⬜ Implement Dungeon Master AI using GPT  
⬜ D&D rules improvement and adherence to official system  
⬜ Magic and spells system implementation  
⬜ Multiple combatants implementation (more enemies/allies)  
⬜ Online multiplayer implementation  
⬜ AI-generated game scenarios and realistic NPC faces  
⬜ AI-generated game scenes implementation  
⬜ AI voice synthesis integration for DM narration  

## 🧠 Future Vision: Dungeon Master AI

This project will serve as the backend foundation for an AI-driven narrative experience. Planned integrations include:

- GPT-powered Dungeon Master that reacts to in-game events and generates dynamic descriptions or dialogues
- Natural language command parsing
- Decision tree to narrative generation mapping
- Future web UI or terminal interface based on abstracted `IOInterface`

## 🎮 Getting Started

Clone the repository and run the main game loop:

```bash
git clone https://github.com/yourusername/gioco_rpg.git
cd gioco_rpg
python main.py
```

The game will launch in a text-based interface, allowing you to explore, interact, fight, and talk to characters.

## 📋 Requirements
- Python 3.10+
- No external libraries required (standard library only)

## 👥 Contribute
I'm seeking collaborators who want to help build:

- Web interface (HIGH PRIORITY)
- AI narrative engine (GPT-based)
- Storyline and world-building
- UI/UX feedback or playtesting

Feel free to open issues, forks or reach out directly.

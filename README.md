# Dungeon Master AI – Python RPG Engine (Backend Only)

This repository contains the **backend core** of a modular role-playing game (RPG) engine, designed in Python using a clean object-oriented architecture and a stack-based finite state machine (FSM). The goal of the project is to evolve into an AI-driven, narratively rich RPG system, where a virtual Dungeon Master powered by GPT can enhance player immersion.

## 🧱 Architecture Overview

The project is organized into well-defined modules:

gioco_rpg/
├── main.py # Entry point 
├── core/ # Game loop and I/O interface 
├── entities/ # Player, NPCs, enemies, shared logic 
├── items/ # Objects and interactive elements 
├── states/ # Game states (map, combat, inventory, etc.) 
├── util/ # Dice rolling, helper functions 
└── world/ # Map system, tile control, environment


Each game phase (map exploration, combat, dialogues, inventory management) is handled through a **stacked FSM** (`BaseState`), enabling smooth transitions and layered interactions (e.g., opening a chest pauses exploration and pushes a dialog or loot state).

## 🧠 Features

- Modular structure ready for extension
- Complete core game logic (movement, combat, dialogues, inventory)
- ASCII-based map system using a tile controller
- Entity factory system for dynamic content generation
- Full separation of game logic from user interface (ready for future web/GUI/AI integrations)
- Fully testable backend (no Pygame dependencies in this repo)

## 🚧 Current Objective


📅 Roadmap


 Unified map exploration with MappaStateEnhanced (done)

 Centralized NPC/object generation via EntityFactory (done)

 Remove legacy states (TavernaState, MercatoState)

 Add modular I/O interfaces (text, GUI, AI)

 Implement AI Dungeon Master using GPT API

 Web-based frontend (Flask + HTMX or similar)



## 🧠 Future Vision: Dungeon Master AI

This project will serve as the backend foundation for a narrative-driven AI experience. Planned integrations include:

- GPT-powered Dungeon Master that reacts to in-game events and generates dynamic descriptions or dialogues
- Natural language command parsing
- Decision tree to narrative generation mapping
- Future web UI or terminal interface based on abstracted `IOInterface`

## 📦 Getting Started

Clone the repository and run the main game loop:

git clone https://github.com/yourusername/gioco_rpg.git
cd gioco_rpg
python main.py
The game will launch in a text-based interface, allowing you to explore, interact, fight, and talk to characters.

🧪 Requirements
Python 3.10+

No external libraries required (standard library only)


🙌 Contribute
I'm seeking collaborators who want to help build:

Web interface (Flask/HTMX)

AI narrative engine (GPT-based)

Storyline and world-building

UI/UX feedback or playtesting

Feel free to open issues, forks or reach out directly.

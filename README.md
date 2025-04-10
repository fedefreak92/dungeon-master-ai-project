---

# RPG Game

A text-based role-playing game with a React frontend and a Flask backend.

## Requirements

- Python 3.8+
- Node.js 14+
- npm 6+

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd gioco_rpg
   ```

2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install frontend dependencies (optional, if you don’t want to rely on automatic build):
   ```
   cd frontend
   npm install
   cd ..
   ```

## Launch

### Development Mode

1. Start the backend:
   ```
   python server.py --debug
   ```

2. In a separate terminal, start the frontend:
   ```
   cd frontend
   npm run dev
   ```

3. Access the application at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api

### Production Mode

Start the full application (backend + frontend) with a single command:
```
python server.py
```

The server will automatically build the frontend if necessary and serve the complete app at http://localhost:5000.

### Launch Options

```
python server.py --help
```

Available options:
- `--port PORT`: Specify the port to run the server on (default: 5000)
- `--debug`: Start the server in debug mode
- `--rebuild-frontend`: Force rebuild of the frontend

## Application Structure

- `server.py`: Entry point for the backend application
- `frontend/`: Contains the React frontend source code
  - `src/`: React source code
  - `public/`: Static files
  - `dist/`: Built frontend (auto-generated)

## API

Backend APIs are accessible under the `/api` prefix. For a full list of endpoints, visit `/api` after starting the server.

## Development

### Backend

To add new backend features, edit `server.py` and create new API endpoints.

### Frontend

The frontend is built using React and Vite. To add new features:

1. Navigate to the `frontend` folder
2. Edit files in the `src` directory
3. Run the dev server using `npm run dev`
4. Build the frontend for production using `npm run build`

# RESTful API for RPG Game

This project implements a RESTful API exposing game features over HTTP, enabling integration with various user interfaces (web, mobile, etc.).

## Configuration

1. Ensure Python is installed (Python 3.6+)
2. Install required dependencies:
   ```
   pip install flask
   ```
3. Start the server:
   ```
   python server.py
   ```
4. The server will run on `http://localhost:5000`

## Endpoints

### `GET /`
Returns general server info and available endpoints.

### `POST /inizia`
Starts a new game.

**Parameters (JSON):**
- `nome` (optional): Character name (default: "Adventurer")
- `classe` (optional): Character class (default: "warrior")

**Example request:**
```json
{
  "nome": "Thorin",
  "classe": "warrior"
}
```

**Response:**
```json
{
  "id_sessione": "550e8400-e29b-41d4-a716-446655440000",
  "messaggio": "Game started",
  "stato": {
    "nome": "Thorin",
    "classe": "warrior",
    "hp": 25,
    "max_hp": 25,
    "stato": "TavernaState",
    "output": "Welcome to the tavern...",
    "posizione": {
      "mappa": "tavern",
      "x": 5,
      "y": 5
    },
    "inventario": ["Short Sword", "Healing Potion"]
  }
}
```

### `POST /comando`
Sends a command to the game.

**Parameters (JSON):**
- `id_sessione` (required): Game session ID
- `comando` (required): Command to execute

**Example:**
```json
{
  "id_sessione": "550e8400-e29b-41d4-a716-446655440000",
  "comando": "look"
}
```

### `GET /stato`
Returns the current game state.

**Query parameters:**
- `id_sessione` (required)

Example:
```
GET /stato?id_sessione=550e8400-e29b-41d4-a716-446655440000
```

### `POST /salva`
Saves the current game.

**Parameters (JSON):**
- `id_sessione` (required)
- `nome_file` (optional): Save file name (default: "salvataggio.json")

### `POST /carica`
Loads a previously saved game.

**Parameters (JSON):**
- `nome_file` (optional): Save file name (default: "salvataggio.json")

### `GET /mappa`
Returns information about the current map.

**Query parameters:**
- `id_sessione` (required)

### `POST /muovi`
Moves the player in a direction.

**Parameters (JSON):**
- `id_sessione` (required)
- `direzione` (required): One of `"north"`, `"south"`, `"east"`, `"west"`

---

## Security Notes

- Sessions are saved using pickle; in production, consider a more secure solution.
- No authentication is implemented; add auth if using this in production.

---

## Data Persistence

Sessions are saved in two ways:
1. In memory (while the server is running)
2. On disk inside the `sessioni/` folder (for persistence after restarts)

You can also export the game to a JSON file using the `/salva` endpoint.

---

## New Features

### Structured Output for Web GUI

To prepare the backend for integration with a Flask + HTMX web interface, new structured output features have been added:

1. All player-visible messages go through `gioco.io.mostra_messaggio()`
2. Output is structured and clean (no random newlines)
3. A helper method `get_output_structured()` returns messages as:

```python
[
    {"tipo": "system", "testo": "You opened the chest"},
    {"tipo": "narrative", "testo": "Inside, you find a scroll"}
]
```

This feature is available in both `TerminalIO` and `GameIOWeb`, enabling support for both interfaces.

#### Usage example with `TerminalIO`

```python
from core.io_interface import TerminalIO
from core.game import Game

io_handler = TerminalIO()
game = Game(None, None, io_handler, e_temporaneo=True)
game.io.mostra_messaggio("Welcome, adventurer!")
game.io.messaggio_sistema("New game started")

messages = game.io.get_output_structured()
```

#### Usage with `GameIOWeb` (for web interface)

```python
from core.stato_gioco import GameIOWeb, StatoGioco
from entities.giocatore import Giocatore
from states.taverna import TavernaState

giocatore = Giocatore("Adventurer", "warrior")
stato_gioco = StatoGioco(giocatore, TavernaState())
stato_gioco.processa_comando("look")
messages = stato_gioco.io_buffer.get_output_structured()
```

This structured output is ideal for formatting frontend responses using web frameworks like Flask + HTMX.

---

# Gioco RPG

Gioco di ruolo testuale con frontend React e backend Flask.

## Requisiti

- Python 3.8+
- Node.js 14+
- npm 6+

## Installazione

1. Clona il repository:
   ```
   git clone <repository-url>
   cd gioco_rpg
   ```

2. Installazione delle dipendenze backend:
   ```
   pip install -r requirements.txt
   ```

3. Installazione delle dipendenze frontend (opzionale, se non vuoi usare la compilazione automatica):
   ```
   cd frontend
   npm install
   cd ..
   ```

## Avvio

### Modalità sviluppo

1. Avvia il backend:
   ```
   python server.py --debug
   ```

2. Avvia il frontend in un terminale separato:
   ```
   cd frontend
   npm run dev
   ```

3. Accedi all'applicazione all'indirizzo:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api

### Modalità produzione

Avvia l'applicazione completa (backend + frontend) con un unico comando:
```
python server.py
```

Il server compilerà automaticamente il frontend se necessario e servirà l'applicazione completa all'indirizzo http://localhost:5000.

### Opzioni avvio

```
python server.py --help
```

Opzioni disponibili:
- `--port PORT`: Specifica la porta su cui avviare il server (default: 5000)
- `--debug`: Avvia il server in modalità debug
- `--rebuild-frontend`: Forza la ricompilazione del frontend

## Struttura dell'applicazione

- `server.py`: Punto di ingresso dell'applicazione backend
- `frontend/`: Contiene il codice sorgente del frontend React
  - `src/`: Codice sorgente React
  - `public/`: File statici
  - `dist/`: Build del frontend (generata automaticamente)

## API

Le API del backend sono accessibili tramite il prefisso `/api`. Per l'elenco completo degli endpoint disponibili, visita `/api` dopo aver avviato il server.

## Sviluppo

### Backend

Per aggiungere nuove funzionalità al backend, modifica il file `server.py` e aggiungi nuovi endpoint API.

### Frontend

Il frontend è sviluppato con React e Vite. Per aggiungere nuove funzionalità al frontend:

1. Naviga nella directory `frontend`
2. Modifica i file nella directory `src`
3. Esegui l'applicazione in modalità sviluppo con `npm run dev`
4. Compila il frontend per la produzione con `npm run build`

# API RESTful per Gioco RPG

Questo progetto implementa un'API RESTful che espone le funzionalità del gioco RPG tramite endpoints HTTP, consentendo l'integrazione con varie interfacce utente (web, mobile, ecc.).

## Configurazione

1. Assicurati di avere Python installato (Python 3.6+)
2. Installa le dipendenze necessarie:
   ```
   pip install flask
   ```
3. Avvia il server:
   ```
   python server.py
   ```
4. Il server sarà in esecuzione su `http://localhost:5000`

## Endpoints

### `GET /`
Mostra informazioni generali sul server e gli endpoints disponibili.

### `POST /inizia`
Crea una nuova partita.

**Parametri (JSON):**
- `nome` (opzionale): Nome del personaggio (default: "Avventuriero")
- `classe` (opzionale): Classe del personaggio (default: "guerriero")

**Esempio di richiesta:**
```json
{
  "nome": "Thorin",
  "classe": "guerriero"
}
```

**Risposta:**
```json
{
  "id_sessione": "550e8400-e29b-41d4-a716-446655440000",
  "messaggio": "Gioco iniziato",
  "stato": {
    "nome": "Thorin",
    "classe": "guerriero",
    "hp": 25,
    "max_hp": 25,
    "stato": "TavernaState",
    "output": "Benvenuto alla taverna...",
    "posizione": {
      "mappa": "taverna",
      "x": 5,
      "y": 5
    },
    "inventario": ["Spada corta", "Pozione di cura"]
  }
}
```

### `POST /comando`
Invia un comando alla partita.

**Parametri (JSON):**
- `id_sessione` (obbligatorio): ID della sessione di gioco
- `comando` (obbligatorio): Comando da eseguire

**Esempio di richiesta:**
```json
{
  "id_sessione": "550e8400-e29b-41d4-a716-446655440000",
  "comando": "guarda"
}
```

**Risposta:**
```json
{
  "output": "Ti trovi in una taverna affollata...",
  "stato": {
    "nome": "Thorin",
    "classe": "guerriero",
    "hp": 25,
    "max_hp": 25,
    "stato": "TavernaState",
    "output": "Ti trovi in una taverna affollata...",
    "posizione": {
      "mappa": "taverna",
      "x": 5,
      "y": 5
    },
    "inventario": ["Spada corta", "Pozione di cura"]
  }
}
```

### `GET /stato`
Ottiene lo stato attuale della partita.

**Parametri (query string):**
- `id_sessione` (obbligatorio): ID della sessione di gioco

**Esempio di richiesta:**
```
GET /stato?id_sessione=550e8400-e29b-41d4-a716-446655440000
```

**Risposta:**
```json
{
  "nome": "Thorin",
  "classe": "guerriero",
  "hp": 25,
  "max_hp": 25,
  "stato": "TavernaState",
  "output": "Ti trovi in una taverna affollata...",
  "posizione": {
    "mappa": "taverna",
    "x": 5,
    "y": 5
  },
  "inventario": ["Spada corta", "Pozione di cura"]
}
```

### `POST /salva`
Salva la partita corrente.

**Parametri (JSON):**
- `id_sessione` (obbligatorio): ID della sessione di gioco
- `nome_file` (opzionale): Nome del file di salvataggio (default: "salvataggio.json")

**Esempio di richiesta:**
```json
{
  "id_sessione": "550e8400-e29b-41d4-a716-446655440000",
  "nome_file": "partita_thorin.json"
}
```

**Risposta:**
```json
{
  "messaggio": "Partita salvata in partita_thorin.json"
}
```

### `POST /carica`
Carica una partita esistente.

**Parametri (JSON):**
- `nome_file` (opzionale): Nome del file di salvataggio (default: "salvataggio.json")

**Esempio di richiesta:**
```json
{
  "nome_file": "partita_thorin.json"
}
```

**Risposta:**
```json
{
  "id_sessione": "660f8500-e29b-41d4-a716-446655440001",
  "messaggio": "Partita caricata da partita_thorin.json",
  "stato": {
    "nome": "Thorin",
    "classe": "guerriero",
    "hp": 25,
    "max_hp": 25,
    "stato": "TavernaState",
    "output": "Ti trovi in una taverna affollata...",
    "posizione": {
      "mappa": "taverna",
      "x": 5,
      "y": 5
    },
    "inventario": ["Spada corta", "Pozione di cura"]
  }
}
```

### `GET /mappa`
Ottiene informazioni sulla mappa attuale.

**Parametri (query string):**
- `id_sessione` (obbligatorio): ID della sessione di gioco

**Esempio di richiesta:**
```
GET /mappa?id_sessione=550e8400-e29b-41d4-a716-446655440000
```

**Risposta:**
```json
{
  "mappa": "taverna",
  "x": 5,
  "y": 5,
  "oggetti_vicini": {
    "pozione": {
      "x": 6,
      "y": 5,
      "nome": "Pozione di cura"
    }
  },
  "npg_vicini": {
    "oste": {
      "x": 4,
      "y": 5,
      "nome": "Oste"
    }
  }
}
```

### `POST /muovi`
Muove il giocatore nella direzione specificata.

**Parametri (JSON):**
- `id_sessione` (obbligatorio): ID della sessione di gioco
- `direzione` (obbligatorio): Una delle direzioni "nord", "sud", "est", "ovest"

**Esempio di richiesta:**
```json
{
  "id_sessione": "550e8400-e29b-41d4-a716-446655440000",
  "direzione": "nord"
}
```

**Risposta:**
```json
{
  "spostamento": true,
  "stato": {
    "nome": "Thorin",
    "classe": "guerriero",
    "hp": 25,
    "max_hp": 25,
    "stato": "TavernaState",
    "output": "Ti sposti verso nord.",
    "posizione": {
      "mappa": "taverna",
      "x": 5,
      "y": 4
    },
    "inventario": ["Spada corta", "Pozione di cura"]
  }
}
```

## Note sulla sicurezza

- Le sessioni vengono salvate sul server in formato pickle. In un ambiente di produzione, considerare soluzioni più sicure.
- L'API non implementa autenticazione. Aggiungere un sistema di autenticazione per un utilizzo in produzione.

## Persistenza dati

Le sessioni vengono salvate in due modi:
1. In memoria (durante l'esecuzione del server)
2. Su disco nella cartella "sessioni" (per persistenza tra riavvii del server)

Inoltre, è possibile salvare l'intera partita in un file JSON tramite l'endpoint `/salva`.

## Nuove funzionalità

### Output strutturato per la GUI web

Per preparare il backend all'interfaccia web con Flask + HTMX, sono state aggiunte nuove funzionalità di output strutturato:

1. Ogni messaggio visibile al giocatore passa attraverso `gioco.io.mostra_messaggio()` 
2. L'output è organizzato in modo chiaro e separato (senza newline a caso)
3. È stato aggiunto un helper `get_output_structured()` che restituisce una lista di messaggi nel formato:

```python
[
    {"tipo": "sistema", "testo": "Hai aperto il forziere"},
    {"tipo": "narrativo", "testo": "Dentro trovi una pergamena"}
]
```

Questa funzionalità è disponibile sia nella classe `TerminalIO` che in `GameIOWeb`, permettendo così di supportare entrambe le interfacce.

#### Utilizzo dell'output strutturato

```python
# Esempio di utilizzo con TerminalIO
from core.io_interface import TerminalIO
from core.game import Game

io_handler = TerminalIO()
# Creazione oggetto temporaneo gioco
gioco = Game(None, None, io_handler, e_temporaneo=True)
gioco.io.mostra_messaggio("Benvenuto avventuriero!")
gioco.io.messaggio_sistema("Nuova partita iniziata")

# Ottieni tutti i messaggi in formato strutturato
messaggi = gioco.io.get_output_structured()
```

```python
# Esempio di utilizzo con GameIOWeb (per interfaccia web)
from core.stato_gioco import GameIOWeb, StatoGioco
from entities.giocatore import Giocatore
from states.taverna import TavernaState

# Crea un giocatore e uno stato di gioco
giocatore = Giocatore("Avventuriero", "guerriero")
stato_gioco = StatoGioco(giocatore, TavernaState())

# Elabora un comando
stato_gioco.processa_comando("guarda")

# Ottieni i messaggi in formato strutturato
messaggi = stato_gioco.io_buffer.get_output_structured()
```

Questa funzionalità facilita l'integrazione con framework web come Flask + HTMX, permettendo di formattare facilmente i messaggi per l'interfaccia utente. 
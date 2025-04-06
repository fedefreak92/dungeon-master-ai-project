from flask import Flask, request, jsonify, send_from_directory, send_file
from uuid import uuid4
import os
import pickle
import json
import time
import datetime
import logging
from flask_cors import CORS

from core.stato_gioco import StatoGioco
from entities.giocatore import Giocatore
from states.taverna import TavernaState
from util.data_manager import get_data_manager
from util.config import SESSIONS_DIR, SAVE_DIR, BACKUPS_DIR, get_save_path, list_save_files, delete_save_file, get_session_path

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gioco_rpg")

app = Flask(__name__)
CORS(app)  # Abilita CORS per consentire richieste da frontend

# Assicurati che le directory esistano
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# Directory per gli asset grafici
ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# Dizionario per memorizzare le sessioni attive in memoria
sessioni_attive = {}  # {uuid: StatoGioco}

# Dizionario per memorizzare le notifiche di sistema
notifiche_sistema = {}  # {uuid: [lista di notifiche]}

def salva_sessione(id_sessione, sessione):
    """Salva una sessione su disco"""
    percorso = get_session_path(id_sessione)
    with open(percorso, 'wb') as f:
        pickle.dump(sessione, f)

def carica_sessione(id_sessione):
    """Carica una sessione da disco"""
    percorso = get_session_path(id_sessione)
    if os.path.exists(percorso):
        with open(percorso, 'rb') as f:
            return pickle.load(f)
    return None

def aggiungi_notifica(id_sessione, tipo, messaggio, data=None):
    """Aggiunge una notifica al sistema"""
    if id_sessione not in notifiche_sistema:
        notifiche_sistema[id_sessione] = []
    
    notifica = {
        "id": str(uuid4()),
        "tipo": tipo,  # "info", "warning", "achievement", "quest", "combat", ecc.
        "messaggio": messaggio,
        "data": data or {},
        "timestamp": time.time(),
        "letta": False
    }
    
    notifiche_sistema[id_sessione].append(notifica)
    return notifica

@app.route("/")
def home():
    """Pagina principale"""
    return jsonify({
        "messaggio": "Server RPG attivo",
        "endpoints": {
            "POST /inizia": "Crea una nuova partita",
            "POST /comando": "Invia un comando alla partita",
            "GET /stato": "Ottieni lo stato attuale della partita",
            "POST /salva": "Salva la partita corrente",
            "POST /carica": "Carica una partita esistente",
            "GET /mappa": "Ottieni informazioni sulla mappa",
            "POST /muovi": "Muovi il giocatore in una direzione",
            "GET /inventario": "Ottieni l'inventario del giocatore",
            "GET /statistiche": "Ottieni le statistiche del giocatore",
            "GET /posizione": "Ottieni la posizione del giocatore",
            "GET /missioni": "Ottieni le missioni attive/completate",
            "GET /classi": "Ottieni informazioni sulle classi disponibili",
            "GET /salvataggi": "Ottieni la lista dei salvataggi disponibili",
            "GET /combattimento": "Ottieni lo stato del combattimento attuale",
            "POST /azione_combattimento": "Esegui un'azione di combattimento",
            "GET /npc": "Ottieni informazioni sugli NPC nella posizione attuale",
            "GET /log": "Ottieni il log degli eventi recenti",
            "POST /equipaggiamento": "Gestisci l'equipaggiamento del giocatore",
            "GET /azioni_disponibili": "Ottieni le azioni disponibili nel contesto attuale",
            "POST /dialogo": "Gestisci il dialogo con un NPC",
            "POST /esplora": "Esplora l'ambiente circostante",
            "POST /preferenze": "Salva le preferenze dell'utente",
            "POST /elimina_salvataggio": "Elimina un salvataggio",
            "GET /notifiche": "Ottieni le notifiche non lette",
            "POST /leggi_notifica": "Segna una notifica come letta",
            "GET /asset": "Ottieni un asset grafico",
            "GET /assets_info": "Ottieni informazioni sugli asset disponibili",
            "GET /tutorial": "Ottieni informazioni sui tutorial",
            "GET /achievements": "Ottieni gli achievement del giocatore",
            "GET /oggetto_dettagli": "Ottieni dettagli su un oggetto specifico",
            "GET /abilita": "Ottieni le abilità del giocatore",
            "POST /usa_abilita": "Usa un'abilità del giocatore",
            "POST /esporta_salvataggio": "Esporta un salvataggio come file",
            "POST /importa_salvataggio": "Importa un salvataggio da file"
        }
    })

@app.route("/inizia", methods=["POST"])
def inizia_gioco():
    """Inizia una nuova sessione di gioco"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    nome = data.get("nome", "Avventuriero")
    classe = data.get("classe", "guerriero").lower()
    
    # Crea un nuovo ID di sessione
    id_sessione = str(uuid4())
    
    # Crea un nuovo giocatore
    giocatore = Giocatore(nome, classe)
    
    # Crea una nuova sessione di gioco
    sessione = StatoGioco(giocatore, TavernaState())
    sessioni_attive[id_sessione] = sessione
    
    # Esegui il primo comando vuoto per ottenere l'output iniziale
    sessione.processa_comando("")
    
    # Salva la sessione su disco
    salva_sessione(id_sessione, sessione)
    
    # Ottieni lo stato iniziale
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "id_sessione": id_sessione, 
        "messaggio": "Gioco iniziato",
        "stato": stato
    })

@app.route("/comando", methods=["POST"])
def esegui_comando():
    """Elabora un comando inviato dal client"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    comando = data.get("comando", "")
    
    # Verifica che l'ID sessione sia stato fornito
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Controlla se la sessione è attiva in memoria
    sessione = sessioni_attive.get(id_sessione)
    
    # Se non è in memoria, prova a caricarla da disco
    if not sessione:
        sessione = carica_sessione(id_sessione)
        if sessione:
            # Se trovata su disco, caricala in memoria
            sessioni_attive[id_sessione] = sessione
    
    # Se ancora non trovata, restituisci errore
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Elabora il comando
    sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni lo stato corrente
    stato_attuale = sessione.get_stato_attuale()
    
    # Ottieni il nome dello stato corrente
    stato_nome = "NessunoStato"
    if sessione.game.stato_corrente():
        stato_nome = type(sessione.game.stato_corrente()).__name__
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Controlla se il gioco è terminato
    gioco_terminato = not sessione.game.attivo
    
    # Restituisci lo stato aggiornato
    return jsonify({
        "output": output_strutturato,
        "stato": stato_attuale,
        "stato_nome": stato_nome,
        "fine": gioco_terminato
    })

@app.route("/stato", methods=["GET"])
def ottieni_stato():
    """Ottieni lo stato attuale della sessione"""
    # Estrai l'ID sessione dalla query string
    id_sessione = request.args.get("id_sessione")
    
    # Verifica che l'ID sessione sia stato fornito
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Cerca la sessione in memoria o su disco
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Restituisci lo stato attuale
    return jsonify(sessione.get_stato_attuale())

@app.route("/salva", methods=["POST"])
def salva_partita():
    """Salva la partita su file"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    nome_file = data.get("nome_file", "salvataggio.json")
    
    # Verifica che l'ID sessione sia stato fornito
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Cerca la sessione
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Salva la partita
    try:
        # Ottieni il percorso completo tramite il modulo di configurazione
        percorso = get_save_path(nome_file)
        sessione.salva(percorso)
        logger.info(f"Partita salvata in {percorso}")
        return jsonify({"messaggio": f"Partita salvata in {nome_file}"})
    except Exception as e:
        logger.error(f"Errore durante il salvataggio: {str(e)}")
        return jsonify({"errore": f"Errore durante il salvataggio: {str(e)}"}), 500

@app.route("/carica", methods=["POST"])
def carica_partita():
    """Carica una partita da file"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    nome_file = data.get("nome_file", "salvataggio.json")
    
    # Verifica che l'ID sessione sia stato fornito
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Cerca la sessione o creane una nuova
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Carica la partita
    try:
        # Ottieni il percorso completo tramite il modulo di configurazione
        percorso = get_save_path(nome_file)
        
        if not os.path.exists(percorso):
            return jsonify({"errore": f"File di salvataggio non trovato: {nome_file}"}), 404
            
        risultato = sessione.carica(percorso)
        
        if risultato:
            # Salva la sessione aggiornata
            sessioni_attive[id_sessione] = sessione
            salva_sessione(id_sessione, sessione)
            
            # Ottieni informazioni sul giocatore
            stato = sessione.get_stato_attuale()
            
            return jsonify({
                "messaggio": f"Partita caricata da {nome_file}",
                "giocatore": stato.get("giocatore", {})
            })
        else:
            return jsonify({"errore": "Errore durante il caricamento"}), 500
    except Exception as e:
        logger.error(f"Errore durante il caricamento della partita: {str(e)}")
        return jsonify({"errore": f"Errore durante il caricamento: {str(e)}"}), 500

@app.route("/mappa", methods=["GET"])
def ottieni_mappa():
    """Ottieni informazioni sulla mappa attuale"""
    # Estrai l'ID sessione dalla query string
    id_sessione = request.args.get("id_sessione")
    
    # Verifica che l'ID sessione sia stato fornito
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Cerca la sessione
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Ottieni informazioni sulla mappa
    info_posizione = sessione.ottieni_posizione_giocatore()
    
    if not info_posizione:
        return jsonify({"errore": "Posizione del giocatore non disponibile"}), 404
    
    return jsonify(info_posizione)

@app.route("/muovi", methods=["POST"])
def muovi_giocatore():
    """Muovi il giocatore nella direzione specificata"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    direzione = data.get("direzione")
    
    # Verifica che l'ID sessione e la direzione siano stati forniti
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    if not direzione:
        return jsonify({"errore": "Direzione non fornita"}), 400
    
    # Cerca la sessione
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Muovi il giocatore
    spostamento = sessione.muovi_giocatore(direzione)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Restituisci lo stato aggiornato
    return jsonify({
        "spostamento": spostamento,
        "stato": sessione.get_stato_attuale()
    })

@app.route("/inventario", methods=["GET"])
def ottieni_inventario():
    """Ottieni l'inventario del giocatore"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Ottieni lo stato completo e estrai solo le informazioni sull'inventario
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "inventario": stato.get("inventario", []),
        "equipaggiamento": stato.get("equipaggiamento", {})
    })

@app.route("/statistiche", methods=["GET"])
def ottieni_statistiche():
    """Ottieni le statistiche del giocatore"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Ottieni lo stato completo e estrai solo le statistiche
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "nome": stato.get("nome", ""),
        "classe": stato.get("classe", ""),
        "hp": stato.get("hp", 0),
        "max_hp": stato.get("max_hp", 0),
        "statistiche": stato.get("statistiche", {})
    })

@app.route("/posizione", methods=["GET"])
def ottieni_posizione():
    """Ottieni la posizione attuale del giocatore"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Usa il metodo esistente per ottenere la posizione
    info_posizione = sessione.ottieni_posizione_giocatore()
    
    if not info_posizione:
        return jsonify({"errore": "Posizione del giocatore non disponibile"}), 404
    
    return jsonify(info_posizione)

@app.route("/classi", methods=["GET"])
def ottieni_classi():
    """Ottieni informazioni sulle classi di personaggio disponibili"""
    # Usa il gestore dati per caricare le classi dal file esterno
    return jsonify(get_data_manager().get_classes())

@app.route("/missioni", methods=["GET"])
def ottieni_missioni():
    """Ottieni l'elenco delle missioni attive e completate del giocatore"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Questa funzione presuppone che lo stato del gioco tenga traccia delle missioni
    # Implementa la logica per estrarre le missioni dallo stato del gioco
    stato = sessione.get_stato_attuale()
    missioni = {
        "attive": stato.get("missioni_attive", []),
        "completate": stato.get("missioni_completate", [])
    }
    
    return jsonify(missioni)

@app.route("/combattimento", methods=["GET"])
def ottieni_stato_combattimento():
    """Ottieni lo stato del combattimento attuale"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Questa funzione presuppone che il gioco abbia uno stato di combattimento
    stato = sessione.get_stato_attuale()
    combattimento = stato.get("combattimento", {})
    
    # Verifica se il personaggio è in combattimento
    # Il valore predefinito dipende dalla struttura utilizzata dal gioco
    in_combattimento = combattimento.get("attivo", False)
    
    if not in_combattimento:
        return jsonify({"in_combattimento": False})
    
    return jsonify({
        "in_combattimento": True,
        "round": combattimento.get("round", 1),
        "turno_di": combattimento.get("turno_di", "giocatore"),
        "nemici": combattimento.get("nemici", []),
        "azioni_disponibili": combattimento.get("azioni_disponibili", [])
    })

@app.route("/azione_combattimento", methods=["POST"])
def esegui_azione_combattimento():
    """Esegui un'azione di combattimento"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    azione = data.get("azione", "")
    bersaglio = data.get("bersaglio", "")
    parametri = data.get("parametri", {})
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not azione:
        return jsonify({"errore": "Azione non specificata"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Costruisci un comando formattato per l'azione di combattimento
    comando = f"{azione}"
    if bersaglio:
        comando += f" {bersaglio}"
    
    # Elabora il comando come un normale comando di gioco
    sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Ottieni lo stato aggiornato del combattimento
    stato = sessione.get_stato_attuale()
    combattimento = stato.get("combattimento", {})
    
    return jsonify({
        "output": output_strutturato,
        "stato": stato,
        "combattimento": combattimento
    })

@app.route("/npc", methods=["GET"])
def ottieni_npc():
    """Ottieni informazioni sugli NPC nella posizione attuale"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Questa funzione presuppone che lo stato del gioco tenga traccia degli NPC
    stato = sessione.get_stato_attuale()
    npc = stato.get("npc_presenti", [])
    
    return jsonify(npc)

@app.route("/oggetto", methods=["POST"])
def interagisci_oggetto():
    """Interagisci con un oggetto nell'inventario o nell'ambiente"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    oggetto = data.get("oggetto", "")
    azione = data.get("azione", "usa")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not oggetto:
        return jsonify({"errore": "Oggetto non specificato"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Costruisci il comando per l'interazione con l'oggetto
    comando = f"{azione} {oggetto}"
    
    # Elabora il comando
    sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Ottieni lo stato aggiornato
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "output": output_strutturato,
        "stato": stato
    })

@app.route("/salvataggi", methods=["GET"])
def elenca_salvataggi():
    """Ottieni la lista dei salvataggi disponibili"""
    try:
        # Ottieni tutti i file di salvataggio
        salvataggi = []
        for file in os.listdir(SAVE_DIR):
            if file.endswith(".json"):
                percorso = get_save_path(file)
                try:
                    with open(percorso, 'r') as f:
                        dati = json.load(f)
                        # Estrai le informazioni rilevanti dal salvataggio
                        info_salvataggio = {
                            "nome_file": file,
                            "nome_personaggio": dati.get("giocatore", {}).get("nome", "Sconosciuto"),
                            "classe": dati.get("giocatore", {}).get("classe", "Sconosciuto"),
                            "livello": dati.get("giocatore", {}).get("livello", 1),
                            "data_salvataggio": dati.get("metadata", {}).get("data_salvataggio", "Sconosciuta")
                        }
                        salvataggi.append(info_salvataggio)
                except Exception as e:
                    # Se un file è corrotto, lo saltiamo
                    continue
        
        return jsonify(salvataggi)
    except Exception as e:
        return jsonify({"errore": f"Errore durante l'enumerazione dei salvataggi: {str(e)}"}), 500

@app.route("/log", methods=["GET"])
def ottieni_log():
    """Ottieni il log degli eventi recenti"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Questa funzione presuppone che il gioco tenga traccia di un log di eventi
    stato = sessione.get_stato_attuale()
    log = stato.get("log_eventi", [])
    
    # Limitiamo il numero di eventi restituiti
    max_eventi = int(request.args.get("max", 50))
    log = log[-max_eventi:] if len(log) > max_eventi else log
    
    return jsonify({
        "eventi": log
    })

@app.route("/equipaggiamento", methods=["POST"])
def gestisci_equipaggiamento():
    """Gestisci l'equipaggiamento del giocatore"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    azione = data.get("azione", "")  # "equip", "unequip", "examine"
    oggetto = data.get("oggetto", "")
    slot = data.get("slot", "")  # es. "arma", "armatura", "anello", ecc.
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not oggetto:
        return jsonify({"errore": "Oggetto non specificato"}), 400
    
    if not azione:
        return jsonify({"errore": "Azione non specificata"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Costruisci il comando appropriato in base all'azione richiesta
    if azione == "equip":
        comando = f"equipaggia {oggetto}"
        if slot:
            comando += f" {slot}"
    elif azione == "unequip":
        comando = f"rimuovi {oggetto}"
    elif azione == "examine":
        comando = f"esamina {oggetto}"
    else:
        return jsonify({"errore": "Azione non valida"}), 400
    
    # Elabora il comando
    sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Ottieni lo stato aggiornato
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "output": output_strutturato,
        "stato": stato,
        "equipaggiamento": stato.get("equipaggiamento", {})
    })

@app.route("/azioni_disponibili", methods=["GET"])
def ottieni_azioni_disponibili():
    """Ottieni le azioni disponibili nel contesto attuale"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Questa funzione presuppone che il gioco possa restituire le azioni disponibili
    # nel contesto attuale (ad es. in base allo stato, posizione, NPC presenti, ecc.)
    stato = sessione.get_stato_attuale()
    
    # Ottieni il nome dello stato corrente
    stato_nome = "NessunoStato"
    if sessione.game.stato_corrente():
        stato_nome = type(sessione.game.stato_corrente()).__name__
    
    # Definisci azioni diverse in base al contesto
    azioni_contesto = {
        "base": ["esamina", "raccogli", "parla", "usa", "guarda"],
        "combattimento": ["attacca", "difendi", "scappa", "usa oggetto"],
        "dialogo": ["parla", "chiedi", "offri", "addio"],
        "commercio": ["compra", "vendi", "esamina", "esci"],
        "inventario": ["usa", "equipaggia", "getta", "esamina"]
    }
    
    # Le azioni disponibili possono essere estratte dallo stato o dedotte dal contesto
    azioni = []
    
    # Se il gioco fornisce direttamente le azioni disponibili, usale
    if "azioni_disponibili" in stato:
        azioni = stato["azioni_disponibili"]
    else:
        # Altrimenti, deduci le azioni in base al contesto
        if "combattimento" in stato and stato["combattimento"].get("attivo", False):
            azioni = azioni_contesto["combattimento"]
        elif stato_nome == "DialogoState":
            azioni = azioni_contesto["dialogo"]
        elif stato_nome == "CommercioState":
            azioni = azioni_contesto["commercio"]
        else:
            azioni = azioni_contesto["base"]
    
    # Aggiungi informazioni sui bersagli validi per le azioni
    bersagli = {
        "oggetti": stato.get("oggetti_ambiente", []),
        "npc": stato.get("npc_presenti", []),
        "direzioni": stato.get("uscite", [])
    }
    
    return jsonify({
        "azioni": azioni,
        "bersagli": bersagli,
        "contesto": stato_nome
    })

@app.route("/dialogo", methods=["POST"])
def gestisci_dialogo():
    """Gestisci il dialogo con un NPC"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    npc = data.get("npc", "")
    opzione = data.get("opzione", "")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not npc:
        return jsonify({"errore": "NPC non specificato"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Costruisci il comando di dialogo
    if opzione:
        comando = f"parla {npc} {opzione}"
    else:
        comando = f"parla {npc}"
    
    # Elabora il comando
    sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Ottieni lo stato aggiornato
    stato = sessione.get_stato_attuale()
    
    # Estrai le opzioni di dialogo disponibili se presenti
    opzioni_dialogo = []
    if "dialogo" in stato and "opzioni" in stato["dialogo"]:
        opzioni_dialogo = stato["dialogo"]["opzioni"]
    
    return jsonify({
        "output": output_strutturato,
        "stato": stato,
        "opzioni_dialogo": opzioni_dialogo
    })

@app.route("/esplora", methods=["POST"])
def esplora_ambiente():
    """Esplora l'ambiente circostante"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Esegui un comando "guarda" o "esplora"
    sessione.processa_comando("guarda")
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Ottieni lo stato aggiornato
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "output": output_strutturato,
        "stato": stato,
        "oggetti": stato.get("oggetti_ambiente", []),
        "uscite": stato.get("uscite", []),
        "npc": stato.get("npc_presenti", [])
    })

@app.route("/preferenze", methods=["POST"])
def salva_preferenze():
    """Salva le preferenze dell'utente"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    preferenze = data.get("preferenze", {})
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Salva le preferenze nel contesto della sessione
    # Questa operazione presuppone che StatoGioco abbia un modo per gestire le preferenze
    try:
        sessione.salva_preferenze(preferenze)
        salva_sessione(id_sessione, sessione)
        return jsonify({"messaggio": "Preferenze salvate con successo"})
    except Exception as e:
        return jsonify({"errore": f"Errore durante il salvataggio delle preferenze: {str(e)}"}), 500

@app.route("/elimina_salvataggio", methods=["POST"])
def elimina_salvataggio():
    """Elimina un salvataggio"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    nome_file = data.get("nome_file")
    
    if not nome_file:
        return jsonify({"errore": "Nome file non fornito"}), 400
    
    # Utilizza la funzione del modulo config
    try:
        if delete_save_file(nome_file):
            return jsonify({"messaggio": f"Salvataggio {nome_file} eliminato con successo"})
        else:
            return jsonify({"errore": "File di salvataggio non trovato"}), 404
    except Exception as e:
        logger.error(f"Errore durante l'eliminazione del salvataggio: {str(e)}")
        return jsonify({"errore": f"Errore durante l'eliminazione del salvataggio: {str(e)}"}), 500

@app.route("/notifiche", methods=["GET"])
def ottieni_notifiche():
    """Ottieni le notifiche per la sessione corrente"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Inizializza l'array di notifiche se non esiste
    if id_sessione not in notifiche_sistema:
        notifiche_sistema[id_sessione] = []
    
    # Filtra le notifiche in base ai parametri
    solo_non_lette = request.args.get("solo_non_lette", "true").lower() == "true"
    tipo = request.args.get("tipo")
    limite = int(request.args.get("limite", 50))
    
    notifiche = notifiche_sistema[id_sessione]
    
    # Applica i filtri
    if solo_non_lette:
        notifiche = [n for n in notifiche if not n.get("letta", False)]
    
    if tipo:
        notifiche = [n for n in notifiche if n.get("tipo") == tipo]
    
    # Limita il numero di notifiche
    notifiche = notifiche[-limite:] if len(notifiche) > limite else notifiche
    
    return jsonify({
        "notifiche": notifiche,
        "totale_non_lette": len([n for n in notifiche_sistema[id_sessione] if not n.get("letta", False)])
    })

@app.route("/leggi_notifica", methods=["POST"])
def leggi_notifica():
    """Segna una notifica come letta"""
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    id_notifica = data.get("id_notifica")
    tutte = data.get("tutte", False)
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if id_sessione not in notifiche_sistema:
        return jsonify({"errore": "Nessuna notifica trovata per questa sessione"}), 404
    
    if tutte:
        # Segna tutte le notifiche come lette
        for notifica in notifiche_sistema[id_sessione]:
            notifica["letta"] = True
        return jsonify({"messaggio": "Tutte le notifiche segnate come lette"})
    
    if not id_notifica:
        return jsonify({"errore": "ID notifica non fornito"}), 400
    
    # Cerca la notifica specifica
    for notifica in notifiche_sistema[id_sessione]:
        if notifica["id"] == id_notifica:
            notifica["letta"] = True
            return jsonify({"messaggio": "Notifica segnata come letta"})
    
    return jsonify({"errore": "Notifica non trovata"}), 404

@app.route("/asset/<path:nome_file>", methods=["GET"])
def ottieni_asset(nome_file):
    """Ottieni un asset grafico"""
    return send_from_directory(ASSETS_DIR, nome_file)

@app.route("/assets_info", methods=["GET"])
def ottieni_info_assets():
    """Ottieni informazioni sugli asset disponibili"""
    tipo = request.args.get("tipo")  # es. "personaggio", "ambiente", "oggetto", "nemico"
    
    # Usa il gestore dati per caricare le informazioni sugli asset
    assets = get_data_manager().get_asset_info(tipo)
    
    return jsonify({
        "assets": assets
    })

@app.route("/tutorial", methods=["GET"])
def ottieni_tutorial():
    """Ottieni informazioni sui tutorial disponibili"""
    id_sessione = request.args.get("id_sessione")
    tipo = request.args.get("tipo")  # es. "combattimento", "inventario", "dialogo"
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Verifica che la sessione esista
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Carica i tutorial dal file esterno utilizzando il gestore dati
    tutorial = get_data_manager().get_tutorials()
    
    # Se viene specificato un tipo, restituisci solo quel tutorial
    if tipo and tipo in tutorial:
        return jsonify(tutorial[tipo])
    
    # Altrimenti, restituisci tutti i tutorial
    return jsonify(tutorial)

@app.route("/achievements", methods=["GET"])
def ottieni_achievements():
    """Ottieni gli achievement del giocatore"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Verifica che la sessione esista
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # In un'implementazione reale, questi dati verrebbero estratti dallo stato del gioco
    stato = sessione.get_stato_attuale()
    
    # Carica tutti gli achievement possibili dal file esterno
    tutti_achievements = get_data_manager().get_achievements()
    
    # Ottieni gli achievement sbloccati dal giocatore
    achievements_sbloccati = stato.get("achievements", [])
    
    # Aggiorna lo stato di sblocco per ogni achievement
    for achievement in tutti_achievements:
        achievement["sbloccato"] = achievement["id"] in achievements_sbloccati
        
        # Se è sbloccato, aggiungi la data di sblocco
        if achievement["sbloccato"] and "timestamp_achievements" in stato:
            timestamp = stato["timestamp_achievements"].get(achievement["id"])
            if timestamp:
                achievement["data_sblocco"] = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify({
        "achievements": tutti_achievements,
        "totale": len(tutti_achievements),
        "sbloccati": len(achievements_sbloccati)
    })

@app.route("/oggetto_dettagli", methods=["GET"])
def ottieni_dettagli_oggetto():
    """Ottieni dettagli su un oggetto specifico"""
    id_sessione = request.args.get("id_sessione")
    id_oggetto = request.args.get("id_oggetto")
    nome_oggetto = request.args.get("nome_oggetto")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not id_oggetto and not nome_oggetto:
        return jsonify({"errore": "ID oggetto o nome oggetto non fornito"}), 400
    
    # Verifica che la sessione esista
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Ottieni l'inventario del giocatore
    stato = sessione.get_stato_attuale()
    inventario = stato.get("inventario", [])
    
    # Cerca l'oggetto nell'inventario
    oggetto = None
    for item in inventario:
        if (id_oggetto and item.get("id") == id_oggetto) or (nome_oggetto and item.get("nome") == nome_oggetto):
            oggetto = item
            break
    
    if not oggetto:
        return jsonify({"errore": "Oggetto non trovato nell'inventario"}), 404
    
    # Se l'oggetto è stato trovato, arricchisci i dettagli
    oggetto_dettagliato = oggetto.copy()
    
    # Aggiungi informazioni su come ottenere l'asset dell'oggetto
    oggetto_dettagliato["asset_url"] = f"/asset/oggetti/{oggetto.get('asset', 'oggetto_default.png')}"
    
    # Aggiungi possibili utilizzi dell'oggetto
    oggetto_dettagliato["utilizzi"] = []
    
    if oggetto.get("tipo") == "arma":
        oggetto_dettagliato["utilizzi"].append({"azione": "equipaggia", "descrizione": "Equipaggia quest'arma"})
        oggetto_dettagliato["utilizzi"].append({"azione": "esamina", "descrizione": "Esamina l'arma in dettaglio"})
    elif oggetto.get("tipo") == "pozione":
        oggetto_dettagliato["utilizzi"].append({"azione": "usa", "descrizione": "Bevi la pozione"})
        oggetto_dettagliato["utilizzi"].append({"azione": "esamina", "descrizione": "Esamina la pozione in dettaglio"})
    elif oggetto.get("tipo") == "cibo":
        oggetto_dettagliato["utilizzi"].append({"azione": "mangia", "descrizione": "Mangia il cibo"})
        oggetto_dettagliato["utilizzi"].append({"azione": "esamina", "descrizione": "Esamina il cibo in dettaglio"})
    
    # Aggiungi sempre l'opzione di scartare
    oggetto_dettagliato["utilizzi"].append({"azione": "getta", "descrizione": "Getta l'oggetto"})
    
    return jsonify(oggetto_dettagliato)

@app.route("/abilita", methods=["GET"])
def ottieni_abilita():
    """Ottieni le abilità del giocatore"""
    id_sessione = request.args.get("id_sessione")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    # Verifica che la sessione esista
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Ottieni le abilità del giocatore
    stato = sessione.get_stato_attuale()
    abilita = stato.get("abilita", [])
    
    return jsonify({
        "abilita": abilita,
        "mana_attuale": stato.get("mana", 0),
        "mana_massimo": stato.get("mana_max", 0)
    })

@app.route("/usa_abilita", methods=["POST"])
def usa_abilita():
    """Usa un'abilità del giocatore"""
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    id_abilita = data.get("id_abilita")
    nome_abilita = data.get("nome_abilita")
    bersaglio = data.get("bersaglio", "")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not id_abilita and not nome_abilita:
        return jsonify({"errore": "ID abilità o nome abilità non fornito"}), 400
    
    # Verifica che la sessione esista
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Costruisci il comando per l'abilità
    comando = f"usa_abilita "
    if id_abilita:
        comando += id_abilita
    else:
        comando += nome_abilita
    
    if bersaglio:
        comando += f" {bersaglio}"
    
    # Elabora il comando
    sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Ottieni l'output strutturato
    output_strutturato = sessione.io_buffer.get_output_structured()
    
    # Pulisci il buffer dei messaggi
    sessione.io_buffer.clear()
    
    # Ottieni lo stato aggiornato
    stato = sessione.get_stato_attuale()
    
    return jsonify({
        "output": output_strutturato,
        "stato": stato,
        "mana_attuale": stato.get("mana", 0),
        "uso_riuscito": not "errore" in output_strutturato
    })

@app.route("/esporta_salvataggio", methods=["POST"])
def esporta_salvataggio():
    """Esporta un salvataggio come file scaricabile"""
    data = request.json or {}
    id_sessione = data.get("id_sessione")
    nome_file = data.get("nome_file")
    
    if not id_sessione:
        return jsonify({"errore": "ID sessione non fornito"}), 400
    
    if not nome_file:
        # Genera un nome file basato sulla data e ora
        nome_file = f"salvataggio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Assicurati che il nome file abbia l'estensione .json
    if not nome_file.endswith(".json"):
        nome_file += ".json"
    
    # Verifica che la sessione esista
    sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
    if not sessione:
        return jsonify({"errore": "Sessione non trovata"}), 404
    
    # Salva temporaneamente il file
    percorso_temp = os.path.join(SAVE_DIR, nome_file)
    try:
        sessione.salva(percorso_temp)
        
        # Invia il file al client
        return send_file(
            percorso_temp,
            as_attachment=True,
            download_name=nome_file,
            mimetype="application/json"
        )
    except Exception as e:
        return jsonify({"errore": f"Errore durante l'esportazione: {str(e)}"}), 500

@app.route("/importa_salvataggio", methods=["POST"])
def importa_salvataggio():
    """Importa un salvataggio da file"""
    if "file" not in request.files:
        return jsonify({"errore": "Nessun file caricato"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"errore": "Nessun file selezionato"}), 400
    
    if not file.filename.endswith(".json"):
        return jsonify({"errore": "Il file deve essere in formato JSON"}), 400
    
    # Salva il file caricato
    nome_file = file.filename
    percorso = os.path.join(SAVE_DIR, nome_file)
    
    try:
        file.save(percorso)
        
        # Carica il salvataggio per verificare che sia valido
        with open(percorso, 'r') as f:
            dati_salvati = json.load(f)
        
        # Crea un nuovo ID di sessione
        id_sessione = str(uuid4())
        
        # Creiamo un giocatore dal salvataggio
        from entities.giocatore import Giocatore
        giocatore = Giocatore.from_dict(dati_salvati["giocatore"])
        
        # Creiamo una sessione temporanea con uno stato nullo
        sessione = StatoGioco(giocatore, None)
        
        # Carichiamo il gioco completo (incluso lo stack degli stati)
        if sessione.game.carica(percorso):
            # Memorizza la sessione
            sessioni_attive[id_sessione] = sessione
            salva_sessione(id_sessione, sessione)
            
            # Ottieni lo stato iniziale
            stato = sessione.get_stato_attuale()
            
            return jsonify({
                "id_sessione": id_sessione,
                "messaggio": f"Salvataggio importato da {nome_file}",
                "stato": stato
            })
        else:
            # Se il caricamento fallisce, elimina il file
            os.remove(percorso)
            return jsonify({"errore": "Il file di salvataggio non è valido"}), 400
        
    except Exception as e:
        # Se c'è un errore, elimina il file se esiste
        if os.path.exists(percorso):
            os.remove(percorso)
        return jsonify({"errore": f"Errore durante l'importazione: {str(e)}"}), 500

@app.route("/lista_salvataggi", methods=["GET"])
def lista_salvataggi():
    """Restituisce la lista dei salvataggi disponibili"""
    try:
        # Ottieni tutti i file di salvataggio
        salvataggi = []
        for file in list_save_files():
            percorso = get_save_path(file)
            try:
                with open(percorso, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Estrai informazioni rilevanti
                timestamp = data.get("timestamp", 0)
                versione = data.get("versione_gioco", "sconosciuta")
                nome_giocatore = data.get("giocatore", {}).get("nome", "Sconosciuto")
                livello = data.get("giocatore", {}).get("livello", 1)
                classe = data.get("giocatore", {}).get("classe", "sconosciuto")
                mappa = data.get("mappa_corrente", "sconosciuta")
                
                # Converti timestamp in data leggibile
                data_ora = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
                
                salvataggi.append({
                    "file": file,
                    "giocatore": nome_giocatore,
                    "livello": livello,
                    "classe": classe,
                    "mappa": mappa,
                    "data": data_ora,
                    "versione": versione
                })
            except Exception as e:
                # Salvataggio corrotto o non valido
                salvataggi.append({
                    "file": file,
                    "giocatore": "Salvataggio corrotto",
                    "errore": str(e)
                })
                
        return jsonify({"salvataggi": salvataggi})
    except Exception as e:
        logger.error(f"Errore nella lettura dei salvataggi: {str(e)}")
        return jsonify({"errore": f"Errore nella lettura dei salvataggi: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0") 
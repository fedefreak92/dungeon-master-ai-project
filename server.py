from flask import Flask, request, jsonify
from uuid import uuid4
import os
import pickle
import json

from core.stato_gioco import StatoGioco
from entities.giocatore import Giocatore
from states.taverna import TavernaState

app = Flask(__name__)

# Directory per i salvataggi delle sessioni
SESSIONI_DIR = "sessioni"
os.makedirs(SESSIONI_DIR, exist_ok=True)

# Dizionario per memorizzare le sessioni attive in memoria
sessioni_attive = {}  # {uuid: StatoGioco}

def salva_sessione(id_sessione, sessione):
    """Salva una sessione su disco"""
    percorso = os.path.join(SESSIONI_DIR, f"{id_sessione}.pickle")
    with open(percorso, 'wb') as f:
        pickle.dump(sessione, f)

def carica_sessione(id_sessione):
    """Carica una sessione da disco"""
    percorso = os.path.join(SESSIONI_DIR, f"{id_sessione}.pickle")
    if os.path.exists(percorso):
        with open(percorso, 'rb') as f:
            return pickle.load(f)
    return None

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
            "POST /carica": "Carica una partita esistente"
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
    output = sessione.processa_comando(comando)
    
    # Salva la sessione aggiornata
    salva_sessione(id_sessione, sessione)
    
    # Restituisci lo stato aggiornato
    return jsonify({
        "output": output,
        "stato": sessione.get_stato_attuale()
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
        sessione.salva(nome_file)
        return jsonify({"messaggio": f"Partita salvata in {nome_file}"})
    except Exception as e:
        return jsonify({"errore": f"Errore durante il salvataggio: {str(e)}"}), 500

@app.route("/carica", methods=["POST"])
def carica_partita():
    """Carica una partita esistente"""
    # Estrai i dati dalla richiesta
    data = request.json or {}
    nome_file = data.get("nome_file", "salvataggio.json")
    
    # Crea un ID sessione
    id_sessione = str(uuid4())
    
    # Crea un gioco temporaneo per il caricamento
    from core.game import Game
    gioco_temp = Game(None, None)
    
    # Tenta di caricare il gioco
    if gioco_temp.carica(nome_file):
        # Se il caricamento è riuscito, crea il gioco vero con lo stato iniziale
        from states.taverna import TavernaState
        sessione = StatoGioco(gioco_temp.giocatore, TavernaState())
        
        # Memorizza la sessione
        sessioni_attive[id_sessione] = sessione
        salva_sessione(id_sessione, sessione)
        
        # Ottieni lo stato iniziale
        stato = sessione.get_stato_attuale()
        
        return jsonify({
            "id_sessione": id_sessione,
            "messaggio": f"Partita caricata da {nome_file}",
            "stato": stato
        })
    else:
        return jsonify({"errore": f"Impossibile caricare la partita da {nome_file}"}), 404

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

if __name__ == "__main__":
    app.run(debug=True) 
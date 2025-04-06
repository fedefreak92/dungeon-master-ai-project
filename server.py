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
            "POST /carica": "Carica una partita esistente",
            "GET /mappa": "Ottieni informazioni sulla mappa",
            "POST /muovi": "Muovi il giocatore in una direzione",
            "GET /inventario": "Ottieni l'inventario del giocatore",
            "GET /statistiche": "Ottieni le statistiche del giocatore",
            "GET /posizione": "Ottieni la posizione del giocatore"
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
    
    try:
        # Leggiamo i dati dal file di salvataggio
        with open(nome_file, 'r') as f:
            dati_salvati = json.load(f)
            
        # Creiamo un giocatore dal salvataggio
        from entities.giocatore import Giocatore
        giocatore = Giocatore.from_dict(dati_salvati["giocatore"])
        
        # Creiamo una sessione temporanea con uno stato nullo
        sessione = StatoGioco(giocatore, None)
        
        # Carichiamo il gioco completo (incluso lo stack degli stati)
        if sessione.game.carica(nome_file):
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
    except Exception as e:
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

if __name__ == "__main__":
    app.run(debug=True) 
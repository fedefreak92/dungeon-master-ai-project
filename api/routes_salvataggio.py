from flask import jsonify, request, send_file
import os
import json
import datetime
import logging
from uuid import uuid4

# Configurazione del logger
logger = logging.getLogger(__name__)

# Import delle dipendenze necessarie
from api.decorators import validate_api
from core.stato_gioco import StatoGioco
from entities.giocatore import Giocatore
from api.utils import (
    sessioni_attive,
    carica_sessione,
    salva_sessione,
    marca_sessione_modificata
)
from util.config import SAVE_DIR, get_save_path, list_save_files, delete_save_file

def register_routes(app):
    """Registra tutte le rotte di salvataggio nell'app Flask"""
    
    @app.route("/api/salva", methods=["POST"])
    def salva_gioco():
        """Salva lo stato corrente del gioco"""
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        nome_file = data.get("nome_file")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        # Verifica che la sessione esista
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Genera un nome file se non fornito
        if not nome_file:
            nome_giocatore = sessione.giocatore.nome if hasattr(sessione, 'giocatore') and sessione.giocatore else "giocatore"
            nome_file = f"{nome_giocatore}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Assicurati che il nome file abbia l'estensione .json
        if not nome_file.endswith(".json"):
            nome_file += ".json"
        
        # Percorso completo del file di salvataggio
        percorso = get_save_path(nome_file)
        
        try:
            # Salva il gioco
            sessione.salva(percorso)
            return jsonify({
                "messaggio": f"Gioco salvato con successo come {nome_file}",
                "nome_file": nome_file
            })
        except Exception as e:
            logger.error(f"Errore durante il salvataggio: {str(e)}")
            return jsonify({"errore": f"Errore durante il salvataggio: {str(e)}"}), 500
    
    @app.route("/api/carica", methods=["POST"])
    def carica_gioco():
        """Carica una partita salvata"""
        data = request.json or {}
        nome_file = data.get("nome_file")
        
        if not nome_file:
            return jsonify({"errore": "Nome file non fornito"}), 400
        
        # Percorso completo del file di salvataggio
        percorso = get_save_path(nome_file)
        
        if not os.path.exists(percorso):
            return jsonify({"errore": f"File di salvataggio {nome_file} non trovato"}), 404
        
        try:
            # Carica il salvataggio
            with open(percorso, 'r') as f:
                dati_salvati = json.load(f)
            
            # Crea un nuovo ID di sessione
            id_sessione = str(uuid4())
            
            # Creiamo un giocatore dal salvataggio
            giocatore = Giocatore.from_dict(dati_salvati["giocatore"])
            
            # Creiamo una sessione temporanea con uno stato nullo
            sessione = StatoGioco(giocatore, None)
            
            # Carichiamo il gioco completo (incluso lo stack degli stati)
            if sessione.game.carica(percorso):
                # Memorizza la sessione
                sessioni_attive[id_sessione] = sessione
                marca_sessione_modificata(id_sessione)
                salva_sessione(id_sessione, sessione, True)
                
                # Ottieni lo stato iniziale
                stato = sessione.get_stato_attuale()
                
                return jsonify({
                    "id_sessione": id_sessione,
                    "messaggio": f"Salvataggio caricato da {nome_file}",
                    "stato": stato
                })
            else:
                return jsonify({"errore": "Errore nel caricamento del salvataggio"}), 500
                
        except Exception as e:
            logger.error(f"Errore durante il caricamento: {str(e)}")
            return jsonify({"errore": f"Errore durante il caricamento: {str(e)}"}), 500
    
    @app.route("/api/lista_salvataggi", methods=["GET"])
    def lista_salvataggi():
        """Restituisce la lista dei salvataggi disponibili"""
        try:
            # Ottieni tutti i file di salvataggio
            salvataggi = []
            for file in list_save_files():
                percorso = get_save_path(file)
                try:
                    with open(percorso, 'r') as f:
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
    
    @app.route("/api/elimina_salvataggio", methods=["POST"])
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
    
    @app.route("/api/esporta_salvataggio", methods=["POST"])
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
    
    @app.route("/api/importa_salvataggio", methods=["POST"])
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
            giocatore = Giocatore.from_dict(dati_salvati["giocatore"])
            
            # Creiamo una sessione temporanea con uno stato nullo
            sessione = StatoGioco(giocatore, None)
            
            # Carichiamo il gioco completo (incluso lo stack degli stati)
            if sessione.game.carica(percorso):
                # Memorizza la sessione
                sessioni_attive[id_sessione] = sessione
                marca_sessione_modificata(id_sessione)
                salva_sessione(id_sessione, sessione, True)
                
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

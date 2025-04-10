from flask import jsonify, request
import os
import json
import logging

# Configurazione del logger
logger = logging.getLogger(__name__)

# Import delle dipendenze necessarie
from api.decorators import validate_api
from api.utils import (
    sessioni_attive,
    carica_sessione,
    salva_sessione,
    marca_sessione_modificata
)
from util.data_manager import get_data_manager

def register_routes(app):
    """Registra tutte le rotte relative alla mappa nell'app Flask"""
    
    @app.route("/api/mappa", methods=["GET"])
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
        try:
            # Verifica che ci sia un giocatore e una mappa corrente
            if not hasattr(sessione, 'game') or not hasattr(sessione.game, 'giocatore'):
                return jsonify({"errore": "Sessione di gioco non valida"}), 404

            giocatore = sessione.game.giocatore
            if not hasattr(giocatore, 'mappa_corrente') or not giocatore.mappa_corrente:
                return jsonify({"errore": "Nessuna mappa corrente"}), 404
            
            # Dati base
            info_posizione = {
                "mappa": giocatore.mappa_corrente,
                "x": giocatore.x,
                "y": giocatore.y,
                "oggetti_vicini": {},
                "npg_vicini": {}
            }
            
            # Ottieni la mappa corrente
            mappa_corrente = sessione.game.gestore_mappe.ottieni_mappa(giocatore.mappa_corrente)
            if not mappa_corrente:
                return jsonify({"errore": "Mappa non trovata"}), 404
            
            # Aggiungi la griglia ASCII e numerica
            pos_giocatore = (giocatore.x, giocatore.y)
            info_posizione["griglia_ascii"] = mappa_corrente.genera_rappresentazione_ascii(pos_giocatore)
            info_posizione["griglia"] = mappa_corrente.griglia
            
            # Calcola raggio per ottenere tutti gli elementi
            raggio_completo = max(mappa_corrente.larghezza, mappa_corrente.altezza)
            
            # Ottieni oggetti e NPC con raggio grande
            try:
                oggetti_sulla_mappa = mappa_corrente.ottieni_oggetti_vicini(giocatore.x, giocatore.y, raggio_completo)
                
                # Converti le chiavi da tuple a stringhe per JSON
                for pos, obj in oggetti_sulla_mappa.items():
                    # Assicurati che ogni oggetto abbia un token
                    if not hasattr(obj, 'token') or not obj.token:
                        obj.token = 'O'  # Token di default
                    
                    pos_str = f"({pos[0]}, {pos[1]})"
                    info_posizione["oggetti_vicini"][pos_str] = {
                        "nome": getattr(obj, 'nome', 'Oggetto sconosciuto'),
                        "token": obj.token,
                        "stato": getattr(obj, 'stato', 'normale')
                    }
            except Exception as e:
                logger.error(f"Errore nel recuperare oggetti: {str(e)}")
            
            try:
                npg_sulla_mappa = mappa_corrente.ottieni_npg_vicini(giocatore.x, giocatore.y, raggio_completo)
                
                # Converti le chiavi da tuple a stringhe per JSON
                for pos, npg in npg_sulla_mappa.items():
                    # Assicurati che ogni NPC abbia un token
                    if not hasattr(npg, 'token') or not npg.token:
                        npg.token = 'N'  # Token di default
                    
                    pos_str = f"({pos[0]}, {pos[1]})"
                    info_posizione["npg_vicini"][pos_str] = {
                        "nome": getattr(npg, 'nome', 'NPC sconosciuto'),
                        "token": npg.token
                    }
            except Exception as e:
                logger.error(f"Errore nel recuperare NPC: {str(e)}")
            
            return jsonify(info_posizione)
            
        except Exception as e:
            logger.error(f"Errore nel recuperare informazioni mappa: {str(e)}", exc_info=True)
            return jsonify({
                "errore": f"Errore nel recupero delle informazioni mappa: {str(e)}",
                "mappa": getattr(sessione.game.giocatore, 'mappa_corrente', None) if hasattr(sessione, 'game') and hasattr(sessione.game, 'giocatore') else None,
                "x": 0,
                "y": 0
            }), 500
    
    @app.route("/api/posizione", methods=["GET"])
    def ottieni_posizione():
        """Ottieni la posizione attuale del giocatore"""
        id_sessione = request.args.get("id_sessione")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        try:
            # Ottieni informazioni di base sulla posizione
            giocatore = sessione.game.giocatore
            mappa_corrente = giocatore.mappa_corrente
            x = getattr(giocatore, 'x', 0)
            y = getattr(giocatore, 'y', 0)
            
            return jsonify({
                "mappa": mappa_corrente,
                "x": x,
                "y": y,
                "nome_luogo": sessione.get_luogo_attuale() if hasattr(sessione, 'get_luogo_attuale') else "Sconosciuto"
            })
        except Exception as e:
            logger.error(f"Errore nel recuperare la posizione: {str(e)}")
            return jsonify({
                "errore": f"Errore nel recupero della posizione: {str(e)}",
                "mappa": None,
                "x": 0,
                "y": 0
            }), 500
    
    @app.route("/api/muovi", methods=["POST"])
    def muovi_giocatore():
        """Muove il giocatore nella direzione specificata"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        direzione = data.get("direzione")
        
        # Verifica che l'ID sessione sia stato fornito
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        # Verifica che la direzione sia stata fornita
        if not direzione:
            return jsonify({"errore": "Direzione non fornita"}), 400
        
        # Cerca la sessione
        stato_gioco = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not stato_gioco:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Se non c'è in memoria, la mettiamo
        if id_sessione not in sessioni_attive:
            sessioni_attive[id_sessione] = stato_gioco
        
        try:
            # Salva la mappa corrente prima del movimento
            mappa_precedente = stato_gioco.game.giocatore.mappa_corrente
                
            # Muovi il personaggio
            risultato = stato_gioco.game.muovi_personaggio(direzione)
            
            # Marca la sessione come modificata
            marca_sessione_modificata(id_sessione)
            
            # Controlla se c'è stato un cambio mappa
            mappa_attuale = stato_gioco.game.giocatore.mappa_corrente
            cambio_mappa = mappa_precedente != mappa_attuale
            
            # Aggiungi l'informazione sul cambio mappa al risultato
            if 'cambio_mappa' not in risultato:
                risultato['cambio_mappa'] = cambio_mappa
            
            # Se c'è stato un cambio mappa, forziamo il salvataggio
            if cambio_mappa:
                logger.info(f"Cambio mappa rilevato: da {mappa_precedente} a {mappa_attuale}")
                salva_sessione(id_sessione, stato_gioco, True)
            
            return jsonify(risultato)
        except Exception as e:
            logger.error(f"Errore nel movimento: {str(e)}")
            return jsonify({"errore": f"Errore: {str(e)}"}), 500
    
    @app.route("/api/destinazioni", methods=["GET"])
    def ottieni_destinazioni():
        """Ottieni le destinazioni disponibili per il viaggio"""
        id_sessione = request.args.get("id_sessione")
        
        # Verifica che l'ID sessione sia stato fornito
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
            
        # Cerca la sessione
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni le mappe disponibili dal gestore mappe
        destinazioni = []
        
        # Ottieni la lista delle mappe dal gestore_mappe
        mappe_disponibili = list(sessione.game.gestore_mappe.mappe.keys())
        mappa_corrente = sessione.game.giocatore.mappa_corrente
        
        for mappa_nome in mappe_disponibili:
            # Recupera i dati della mappa
            mappa = sessione.game.gestore_mappe.ottieni_mappa(mappa_nome)
            
            if not mappa:
                continue
                
            # Crea un dizionario con le informazioni della mappa
            destinazione = {
                "id": mappa_nome,
                "nome": mappa_nome.capitalize(),
                "descrizione": f"Una {mappa_nome} da esplorare",
                "posizione_attuale": mappa_nome == mappa_corrente
            }
            
            destinazioni.append(destinazione)
        
        return jsonify(destinazioni)
    
    @app.route("/api/mappe_disponibili", methods=["GET"])
    def ottieni_mappe():
        """Ottieni informazioni sulle mappe disponibili"""
        map_id = request.args.get("id")
        
        try:
            logger.info(f"Richiesta mappe ricevuta, id: {map_id}")
            mappe = get_data_manager().get_map_data(map_id)
            
            if not mappe and map_id:
                return jsonify({"errore": f"Mappa con ID {map_id} non trovata"}), 404
                
            return jsonify(mappe)
        except Exception as e:
            logger.error(f"Errore nell'ottenere le mappe: {str(e)}")
            return jsonify({"errore": f"Errore durante il recupero delle mappe: {str(e)}"}), 500

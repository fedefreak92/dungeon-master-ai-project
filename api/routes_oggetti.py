from flask import request, jsonify, send_from_directory
import logging
import datetime
import os
from api.utils import salva_sessione, carica_sessione, marca_sessione_modificata, notifiche_sistema, sessioni_attive
from util.data_manager import get_data_manager

# Configura il logger
logger = logging.getLogger(__name__)

def register_routes(app):
    """Registra le rotte relative agli oggetti"""
    
    @app.route("/api/oggetto", methods=["POST"])
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
        
        # Memorizza lo stato prima dell'azione
        stato_pre_azione = sessione.get_stato_attuale()
        
        # Costruisci il comando per l'interazione con l'oggetto
        comando = f"{azione} {oggetto}"
        
        # Elabora il comando
        sessione.processa_comando(comando)
        
        # Marca la sessione come modificata
        marca_sessione_modificata(id_sessione)
        
        # Ottieni lo stato aggiornato
        stato = sessione.get_stato_attuale()
        
        # Verifica se ci sono stati cambiamenti significativi dopo l'interazione con l'oggetto
        evento_importante = False
        
        # Controlla se l'interazione ha cambiato lo stato del personaggio o del gioco
        if "giocatore" in stato and "giocatore" in stato_pre_azione:
            # Controlla i cambiamenti di salute
            hp_pre = stato_pre_azione.get("giocatore", {}).get("salute", 0)
            hp_post = stato.get("giocatore", {}).get("salute", 0)
            
            # Se c'è stato un cambiamento significativo della salute
            if abs(hp_post - hp_pre) > 20:
                evento_importante = True
                logger.info(f"Cambiamento significativo della salute: {hp_pre} -> {hp_post}")
                
            # Controlla se è stato ottenuto un livello
            livello_pre = stato_pre_azione.get("giocatore", {}).get("livello", 0)
            livello_post = stato.get("giocatore", {}).get("livello", 0)
            
            if livello_post > livello_pre:
                evento_importante = True
                logger.info(f"Livello ottenuto: {livello_pre} -> {livello_post}")
        
        # Controlla se è stato ottenuto un oggetto importante (solo se l'azione è 'raccogli')
        if azione.lower() in ["raccogli", "prendi"] and "inventario" in stato and "inventario" in stato_pre_azione:
            inv_pre = set(i.get("id", "") for i in stato_pre_azione.get("inventario", []))
            inv_post = [i for i in stato.get("inventario", []) if i.get("id", "") not in inv_pre]
            
            # Controlla se gli oggetti nuovi sono importanti
            for nuovo_oggetto in inv_post:
                rarita = nuovo_oggetto.get("rarita", "comune").lower()
                if rarita in ["raro", "epico", "leggendario"]:
                    evento_importante = True
                    logger.info(f"Oggetto {rarita} ottenuto: {nuovo_oggetto.get('nome', 'sconosciuto')}")
        
        # Salva la sessione in base all'importanza
        if evento_importante:
            logger.info(f"Evento importante rilevato nell'interazione con oggetto per la sessione {id_sessione}, salvataggio forzato")
            salva_sessione(id_sessione, sessione, True)
        else:
            salva_sessione(id_sessione, sessione)
        
        # Ottieni l'output strutturato
        output_strutturato = sessione.io_buffer.get_output_structured()
        
        # Pulisci il buffer dei messaggi
        sessione.io_buffer.clear()
        
        return jsonify({
            "output": output_strutturato,
            "stato": stato,
            "evento_importante": evento_importante
        })
    
    @app.route("/api/oggetto_dettagli", methods=["GET"])
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
    
    @app.route("/api/oggetti", methods=["GET"])
    def ottieni_oggetti():
        """Ottieni tutti gli oggetti disponibili nella sessione corrente"""
        id_sessione = request.args.get("id_sessione")
        tipo = request.args.get("tipo")  # Filtra per tipo: arma, pozione, cibo, ecc.
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        # Verifica che la sessione esista
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni l'inventario del giocatore
        stato = sessione.get_stato_attuale()
        inventario = stato.get("inventario", [])
        
        # Filtra per tipo se specificato
        if tipo:
            inventario = [item for item in inventario if item.get("tipo") == tipo]
        
        return jsonify({
            "oggetti": inventario,
            "totale": len(inventario)
        })

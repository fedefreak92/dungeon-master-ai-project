from flask import request, jsonify
import logging
from api.utils import (
    marca_sessione_modificata, sessioni_attive, salva_sessione, carica_sessione
)
from util.data_manager import get_data_manager
from api.decorators import register_api_route, validate_api

logger = logging.getLogger(__name__)

def register_routes(app):
    """Registra le rotte relative al combattimento"""
    
    @app.route("/api/combattimento", methods=["POST"])
    def inizia_combattimento():
        """Inizia un combattimento contro un nemico o gruppo di nemici"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        id_nemico = data.get("id_nemico")
        gruppo_nemici = data.get("gruppo_nemici", [])
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        if not id_nemico and not gruppo_nemici:
            return jsonify({"errore": "È necessario specificare un nemico o un gruppo di nemici"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        try:
            # Inizia il combattimento
            if id_nemico:
                # Combattimento contro un singolo nemico
                sessione.inizia_combattimento(id_nemico)
            else:
                # Combattimento contro un gruppo di nemici
                sessione.inizia_combattimento_gruppo(gruppo_nemici)
            
            # Marca la sessione come modificata
            marca_sessione_modificata(id_sessione)
            
            # Ottieni lo stato aggiornato
            stato = sessione.get_stato_attuale()
            
            # Salva la sessione
            salva_sessione(id_sessione, sessione)
            
            return jsonify({
                "stato": stato,
                "combattimento": sessione.get_stato_combattimento()
            })
        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione del combattimento: {str(e)}")
            return jsonify({"errore": f"Errore durante l'inizializzazione del combattimento: {str(e)}"}), 500
    
    @app.route("/api/azione_combattimento", methods=["POST"])
    def esegui_azione_combattimento():
        """Esegui un'azione durante il combattimento"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        azione = data.get("azione", "")
        bersaglio = data.get("bersaglio")
        parametri = data.get("parametri", {})
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        if not azione:
            return jsonify({"errore": "Azione non specificata"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        try:
            # Esegui l'azione di combattimento
            risultato = sessione.esegui_azione_combattimento(azione, bersaglio, parametri)
            
            # Marca la sessione come modificata
            marca_sessione_modificata(id_sessione)
            
            # Ottieni lo stato aggiornato
            stato = sessione.get_stato_attuale()
            
            # Ottieni lo stato del combattimento
            stato_combattimento = sessione.get_stato_combattimento()
            
            # Salva la sessione
            salva_sessione(id_sessione, sessione)
            
            return jsonify({
                "risultato": risultato,
                "stato": stato,
                "combattimento": stato_combattimento
            })
        except Exception as e:
            logger.error(f"Errore durante l'esecuzione dell'azione di combattimento: {str(e)}")
            return jsonify({"errore": f"Errore durante l'esecuzione dell'azione di combattimento: {str(e)}"}), 500
    
    @app.route("/api/mostri", methods=["GET"])
    def ottieni_mostri():
        """Ottieni informazioni sui mostri"""
        monster_id = request.args.get("id")
        
        try:
            logger.info(f"Richiesta mostri ricevuta, id: {monster_id}")
            mostri = get_data_manager().get_monsters(monster_id)
            
            if not mostri and monster_id:
                return jsonify({"errore": f"Mostro con ID {monster_id} non trovato"}), 404
                
            return jsonify(mostri)
        except Exception as e:
            logger.error(f"Errore nell'ottenere i mostri: {str(e)}")
            return jsonify({"errore": f"Errore durante il recupero dei mostri: {str(e)}"}), 500

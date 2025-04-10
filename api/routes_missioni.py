from flask import request, jsonify
import datetime
from api.utils import carica_sessione, sessioni_attive
from util.data_manager import get_data_manager

def register_routes(app):
    """Registra le rotte per missioni e achievements"""
    
    @app.route("/api/achievements", methods=["GET"])
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

    @app.route("/api/missioni", methods=["GET"])
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

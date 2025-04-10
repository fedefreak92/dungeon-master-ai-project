from flask import Flask, request, jsonify, send_from_directory
import os

# Importa le funzioni da api.utils
from api.utils import (
    sessioni_attive, carica_sessione, marca_sessione_modificata, salva_sessione, 
    notifiche_sistema
)

# Importa get_data_manager dal modulo corretto
from util.data_manager import get_data_manager

# Directory per gli asset grafici
ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def register_routes(app):
    """Registra le rotte relative al sistema"""
    
    @app.route("/api/preferenze", methods=["POST"])
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
            marca_sessione_modificata(id_sessione)
            salva_sessione(id_sessione, sessione)
            return jsonify({"messaggio": "Preferenze salvate con successo"})
        except Exception as e:
            return jsonify({"errore": f"Errore durante il salvataggio delle preferenze: {str(e)}"}), 500

    @app.route("/api/notifiche", methods=["GET"])
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

    @app.route("/api/leggi_notifica", methods=["POST"])
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

    @app.route("/api/asset/<path:nome_file>", methods=["GET"])
    def ottieni_asset(nome_file):
        """Ottieni un asset grafico"""
        return send_from_directory(ASSETS_DIR, nome_file)

    @app.route("/api/assets_info", methods=["GET"])
    def ottieni_info_assets():
        """Ottieni informazioni sugli asset disponibili"""
        tipo = request.args.get("tipo")  # es. "personaggio", "ambiente", "oggetto", "nemico"
        
        # Usa il gestore dati per caricare le informazioni sugli asset
        assets = get_data_manager().get_asset_info(tipo)
        
        return jsonify({
            "assets": assets
        })

    @app.route("/api/tutorial", methods=["GET"])
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

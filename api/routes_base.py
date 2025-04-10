from flask import Flask, request, jsonify, send_from_directory, send_file
import json
import logging
import datetime
import os

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gioco_rpg")

# Funzioni di base per l'istanza Flask
def ensure_json_response(response):
    """Assicura che tutte le risposte alle API restituiscano JSON valido"""
    if request.path.startswith('/api/'):
        logger.debug(f"Elaborazione risposta per {request.path}")
        
        # Assicurati che il Content-Type sia JSON per le API
        response.headers['Content-Type'] = 'application/json'
        
        # Controlla se la risposta è già in formato JSON
        if not response.is_json:
            logger.warning(f"Risposta non JSON rilevata per {request.path}, conversione forzata")
            
            # Converti la risposta in JSON se possibile
            try:
                current_data = response.get_data(as_text=True)
                
                # Se sembra HTML, crea una risposta JSON appropriata
                if current_data and ('<html' in current_data.lower() or '<!doctype' in current_data.lower()):
                    logger.warning(f"Rilevato HTML nella risposta API {request.path}")
                    
                    # Crea una risposta JSON valida
                    json_data = {
                        "success": True,
                        "messaggio": f"Risposta API per {request.path}"
                    }
                    
                    # Sostituisci la risposta HTML con JSON
                    response = Flask(__name__).response_class(
                        response=json.dumps(json_data),
                        status=response.status_code,
                        mimetype='application/json'
                    )
            except Exception as e:
                logger.error(f"Errore nella conversione della risposta in JSON: {str(e)}")
        
        # Aggiungi header per evitare problemi di CORS
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Accept,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        
        logger.debug(f"Headers finali per {request.path}: {dict(response.headers)}")
    
    return response

def handle_api_options(path):
    """Handler globale per le richieste OPTIONS agli endpoint API"""
    logger.info(f"Richiesta OPTIONS per /api/{path}")
    app = Flask(__name__)
    response = app.response_class(
        response="",
        status=200
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Accept,X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

def serve_frontend(path):
    """
    Serve l'applicazione frontend. Se il percorso non è specificato o è la radice,
    servi index.html, altrimenti cerca il file statico richiesto.
    """
    try:
        app = Flask(__name__)
        if path == "":
            # Per le richieste API, restituisci informazioni JSON
            if request.headers.get('accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "status": "online",
                    "name": "Gioco RPG API",
                    "version": "1.0.0",
                    "message": "Usa gli endpoint /api/* per interagire con il gioco"
                })
            
            # Per le richieste browser normali, servi l'applicazione frontend
            return send_from_directory(app.static_folder, 'index.html')
        else:
            # Prova a trovare il file statico richiesto
            static_file = app.static_folder + '/' + path
            if os.path.exists(static_file) and os.path.isfile(static_file):
                return send_file(static_file)
            else:
                # Se il file non esiste, servi index.html per consentire il routing SPA
                return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Errore nel servire il frontend: {str(e)}")
        return app.response_class(
            response=json.dumps({"error": "Errore interno del server"}),
            status=500,
            mimetype='application/json'
        )

# API routes
def home():
    """Pagina principale API"""
    return jsonify({
        "messaggio": "Server RPG attivo",
        "endpoints": {
            "POST /api/inizia": "Crea una nuova partita",
            "POST /api/comando": "Invia un comando alla partita",
            "GET /api/stato": "Ottieni lo stato attuale della partita",
            "POST /api/salva": "Salva la partita corrente",
            "POST /api/carica": "Carica una partita esistente",
            "GET /api/mappa": "Ottieni informazioni sulla mappa",
            "POST /api/muovi": "Muovi il giocatore in una direzione",
            "GET /api/inventario": "Ottieni l'inventario del giocatore",
            "GET /api/statistiche": "Ottieni le statistiche del giocatore",
            "GET /api/posizione": "Ottieni la posizione del giocatore",
            "GET /api/missioni": "Ottieni le missioni attive/completate",
            "GET /api/classi": "Ottieni informazioni sulle classi disponibili",
            "GET /api/salvataggi": "Ottieni la lista dei salvataggi disponibili",
            "GET /api/combattimento": "Ottieni lo stato del combattimento attuale",
            "POST /api/azione_combattimento": "Esegui un'azione di combattimento",
            "GET /api/npc": "Ottieni informazioni sugli NPC nella posizione attuale",
            "GET /api/log": "Ottieni il log degli eventi recenti",
            "POST /api/equipaggiamento": "Gestisci l'equipaggiamento del giocatore",
            "GET /api/azioni_disponibili": "Ottieni le azioni disponibili nel contesto attuale",
            "POST /api/dialogo": "Gestisci il dialogo con un NPC",
            "POST /api/esplora": "Esplora l'ambiente circostante",
            "POST /api/preferenze": "Salva le preferenze dell'utente",
            "POST /api/elimina_salvataggio": "Elimina un salvataggio",
            "GET /api/notifiche": "Ottieni le notifiche non lette",
            "POST /api/leggi_notifica": "Segna una notifica come letta",
            "GET /api/asset": "Ottieni un asset grafico",
            "GET /api/assets_info": "Ottieni informazioni sugli asset disponibili",
            "GET /api/tutorial": "Ottieni informazioni sui tutorial",
            "GET /api/achievements": "Ottieni gli achievement del giocatore",
            "GET /api/oggetto_dettagli": "Ottieni dettagli su un oggetto specifico",
            "GET /api/abilita": "Ottieni le abilità del giocatore",
            "POST /api/usa_abilita": "Usa un'abilità del giocatore",
            "POST /api/esporta_salvataggio": "Esporta un salvataggio come file",
            "POST /api/importa_salvataggio": "Importa un salvataggio da file",
            "GET /api/mostri": "Ottieni informazioni sui mostri",
            "GET /api/mappe_disponibili": "Ottieni informazioni sulle mappe disponibili",
            "GET /api/oggetti": "Ottieni informazioni sugli oggetti disponibili",
            "GET /api/health": "Verifica la salute del server",
            "GET /api/test": "Test endpoint"
        }
    })

def health_check():
    """
    Endpoint per verificare la salute del server.
    Ritorna successo se il server è disponibile.
    """
    try:
        # Dati base per la risposta
        data = {
            "success": True,
            "data": {
                "status": "ok",
                "timestamp": datetime.datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "messaggio": "Server disponibile"
        }
        
        # Converti in stringa JSON
        json_str = json.dumps(data)
        
        # Crea una risposta Flask
        app = Flask(__name__)
        response = app.response_class(
            response=json_str,
            status=200,
            mimetype='application/json'
        )
        
        # Imposta esplicitamente gli header
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        
        logger.info("Risposta health check inviata correttamente")
        return response
        
    except Exception as e:
        logger.error(f"Errore nell'endpoint health check: {str(e)}")
        
        # Anche in caso di errore, restituisci JSON
        error_data = {
            "success": False,
            "errore": "Errore durante il controllo salute del server"
        }
        
        app = Flask(__name__)
        error_response = app.response_class(
            response=json.dumps(error_data),
            status=500,
            mimetype='application/json'
        )
        error_response.headers['Content-Type'] = 'application/json'
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        
        return error_response

def test_endpoint():
    """
    Endpoint di test per verificare se il server può restituire JSON correttamente.
    """
    logger.info("Richiesta per /api/test ricevuta")
    
    test_data = {
        "success": True,
        "message": "Test endpoint funzionante",
        "data": {
            "number": 42,
            "string": "Hello, world!",
            "boolean": True,
            "array": [1, 2, 3, 4, 5],
            "object": {"key": "value"}
        }
    }
    
    logger.info("Ritorno dati di test")
    return jsonify(test_data)

# Middleware e gestori di errori
def handle_exception(error):
    logger.error(f"Errore non gestito: {str(error)}", exc_info=True)
    
    # Crea risposta JSON manualmente per qualsiasi tipo di errore
    app = Flask(__name__)
    response = app.response_class(
        response=json.dumps({
            "success": False,
            "errore": "Si è verificato un errore interno. Per favore riprova più tardi."
        }),
        status=500,
        mimetype='application/json'
    )
    return response

def not_found_error(error):
    app = Flask(__name__)
    response = app.response_class(
        response=json.dumps({
            "success": False,
            "errore": f"La risorsa richiesta non è stata trovata: {request.path}"
        }),
        status=404,
        mimetype='application/json'
    )
    return response

def method_not_allowed(error):
    app = Flask(__name__)
    response = app.response_class(
        response=json.dumps({
            "success": False, 
            "errore": f"Il metodo {request.method} non è consentito per questo endpoint"
        }),
        status=405,
        mimetype='application/json'
    )
    return response

def bad_request_error(error):
    app = Flask(__name__)
    response = app.response_class(
        response=json.dumps({
            "success": False,
            "errore": "La richiesta contiene parametri non validi o mancanti"
        }),
        status=400,
        mimetype='application/json'
    )
    return response

class ResponseDebugMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Ottieni la richiesta corrente
        path = environ.get('PATH_INFO', '')
        
        # Controlla se è una richiesta API
        if path.startswith('/api/'):
            # Wrapper per il callback start_response
            def debug_start_response(status, headers, exc_info=None):
                # Log dei dettagli della risposta
                logger.debug(f"API Risposta per {path} - Status: {status}")
                logger.debug(f"API Headers: {dict(headers)}")
                
                # Chiama il callback originale
                return start_response(status, headers, exc_info)
            
            # Chiama l'app con il wrapper
            return self.app(environ, debug_start_response)
        
        # Se non è una richiesta API, comportamento normale
        return self.app(environ, start_response)

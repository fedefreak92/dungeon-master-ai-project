from flask import Flask, request, jsonify, send_from_directory, send_file, render_template
from uuid import uuid4
import os
import pickle
import json
import time
import datetime
import logging
from flask_cors import CORS
import subprocess
import sys
import jsonschema
import threading
from jsonschema import validate, ValidationError, SchemaError
import atexit
import secrets
from functools import wraps
import mimetypes
import socket

# Importa le funzioni base dalle routes
from api.routes_base import (
    ensure_json_response, handle_api_options, serve_frontend,
    home, health_check, test_endpoint,
    handle_exception, not_found_error, method_not_allowed, bad_request_error,
    ResponseDebugMiddleware
)

# Importa i decoratori dal nuovo modulo
from api.decorators import json_response_decorator, register_api_route, validate_api

# Importa le funzioni spostate in api.utils
from api.utils import (
    get_schema_for_endpoint, validate_request_data, validate_response_data, resolve_schema_refs,
    salva_sessione, carica_sessione, marca_sessione_modificata, autosave_sessioni,
    avvia_autosave, ferma_autosave, cleanup, aggiungi_notifica, json_response,
    sessioni_attive, sessioni_modificate, notifiche_sistema, sessioni_lock,
    is_nodejs_installed, build_frontend
)

# Importa lo schema OpenAPI
from frontend.src.api.api_schema import apiSchema  # Modificato per importare lo schema API

from core.stato_gioco import StatoGioco
from entities.giocatore import Giocatore
from states.scelta_mappa_state import SceltaMappaState
from util.data_manager import get_data_manager
from util.config import SESSIONS_DIR, SAVE_DIR, BACKUPS_DIR, get_save_path, list_save_files, delete_save_file, get_session_path

# Importa le rotte del giocatore
from api.routes_giocatore import register_routes as register_giocatore_routes
# Importa le rotte della mappa
from api.routes_mappa import register_routes as register_mappa_routes
# Importa le rotte delle azioni
from api.routes_Azioni import register_routes as register_azioni_routes
# Importa le rotte del combattimento
from api.routes_combattimento import register_routes as register_combattimento_routes
# Importa le rotte degli oggetti
from api.routes_oggetti import register_routes as register_oggetti_routes
# Importa le rotte del salvataggio
from api.routes_salvataggio import register_routes as register_salvataggio_routes
# Importa le rotte del sistema
from api.routes_sistema import register_routes as register_sistema_routes
# Importa le rotte delle missioni e achievements
from api.routes_missioni import register_routes as register_missioni_routes

# Configura il logger
logger = logging.getLogger(__name__)

# Configurazione base di Flask
app = Flask(__name__, static_folder='dist')
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=30)

# Configura CORS per permettere richieste sia da localhost:3000 (sviluppo) che da localhost:5000 (produzione)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5000", "*"]}})

# Dopo la configurazione di CORS e prima della definizione delle routes API
app.config.setdefault('CORS_ALLOW_ORIGIN', '*')
app.config.setdefault('CORS_ALLOW_HEADERS', 'Content-Type,Authorization')
app.config.setdefault('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')

# Disabilita il debugger HTML per le chiamate API
# Il debugger HTML può interferire con le risposte JSON in modalità debug
app.config['PROPAGATE_EXCEPTIONS'] = True  # Permette di propagare le eccezioni agli handler
app.config['TRAP_HTTP_EXCEPTIONS'] = True  # Cattura le eccezioni HTTP per gestirle con i nostri handler
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False  # Evita che Flask mantenga il contesto su eccezione

# Inizializza il data_manager come proprietà dell'app
app.data_manager = get_data_manager()
logger.info("DataManager inizializzato come proprietà dell'app Flask")

# Configurazione dell'autosave
AUTOSAVE_INTERVAL = 180  # Intervallo di autosave in secondi (3 minuti)
autosave_thread = None
autosave_attivo = True

# Avvia il thread di autosave
avvia_autosave()

# Applica il decorator json_response_decorator a tutte le rotte /api/*
@app.after_request
def ensure_json_response_wrapper(response):
    return ensure_json_response(response)

# Gestore globale per le richieste OPTIONS a tutti gli endpoint API
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_api_options_wrapper(path):
    return handle_api_options(path)

# Assicurati che le directory esistano
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# Directory per gli asset grafici
ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# Rotte statiche
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend_wrapper(path):
    return serve_frontend(path)

# API routes
@app.route("/api")
def home_wrapper():
    return home()

# Registra le rotte del giocatore
register_giocatore_routes(app)
# Registra le rotte della mappa
register_mappa_routes(app)
# Registra le rotte delle azioni
register_azioni_routes(app)
# Registra le rotte del combattimento
register_combattimento_routes(app)
# Registra le rotte degli oggetti
register_oggetti_routes(app)
# Registra le rotte del salvataggio
register_salvataggio_routes(app)
# Registra le rotte del sistema
register_sistema_routes(app)
# Registra le rotte delle missioni e achievements
register_missioni_routes(app)

@app.route("/api/health", methods=["GET"])
def health_check_wrapper():
    return health_check()

# Funzione per standardizzare le risposte API
def json_response(data=None, success=True, messaggio="", errore="", code=200):
    """
    Genera una risposta JSON standardizzata.
    
    Args:
        data: Dati da restituire nel campo 'data'
        success: Se l'operazione è stata completata con successo
        messaggio: Messaggio informativo (in caso di successo)
        errore: Messaggio di errore (in caso di fallimento)
        code: Codice di stato HTTP
        
    Returns:
        Risposta JSON con la struttura standard
    """
    response = {
        "success": success
    }
    
    if data is not None:
        response["data"] = data
        
    if messaggio:
        response["messaggio"] = messaggio
        
    if errore:
        response["errore"] = errore
    
    return jsonify(response), code
    
# Gestore errori personalizzato
@app.errorhandler(Exception)
def handle_exception_wrapper(error):
    return handle_exception(error)

@app.errorhandler(404)
def not_found_error_wrapper(error):
    return not_found_error(error)

@app.errorhandler(405)
def method_not_allowed_wrapper(error):
    return method_not_allowed(error)

@app.errorhandler(400)
def bad_request_error_wrapper(error):
    return bad_request_error(error)

# Applico il decorator json_response_decorator a tutte le rotte API per garantire il Content-Type corretto
for endpoint, view_function in list(app.view_functions.items()):
    if endpoint.startswith('api.') or any(route.rule.startswith('/api/') for route in app.url_map.iter_rules() 
                                         if app.view_functions.get(route.endpoint) == view_function):
        app.view_functions[endpoint] = json_response_decorator(view_function)
        logger.debug(f"Applicato json_response_decorator all'endpoint: {endpoint}")

# Applica il middleware se in modalità debug
if app.config.get('DEBUG', False):
    app.wsgi_app = ResponseDebugMiddleware(app.wsgi_app)

if __name__ == "__main__":
    import argparse
    
    # Parsing degli argomenti da linea di comando
    parser = argparse.ArgumentParser(description='Server per il gioco RPG')
    parser.add_argument('--port', type=int, default=5000, help='Porta su cui servire l\'applicazione')
    parser.add_argument('--debug', action='store_true', help='Abilita la modalità debug')
    parser.add_argument('--rebuild-frontend', action='store_true', help='Forza la ricompilazione del frontend')
    args = parser.parse_args()
    
    # Se richiesto, rimuovi la cartella dist per forzare la ricompilazione
    if args.rebuild_frontend and os.path.exists(os.path.join('frontend', 'dist')):
        import shutil
        shutil.rmtree(os.path.join('frontend', 'dist'))
    
    # Compila il frontend
    build_frontend()
    
    # Avvia il server con modifiche per gestire correttamente le risposte JSON
    logger.info(f"Avvio del server sulla porta {args.port}...")
    try:
        # Usa use_reloader=False in debug mode per evitare problemi con Werkzeug
        if args.debug:
            app.config['ENV'] = 'development'
            app.config['DEBUG'] = True
            # In modalità debug, assicuriamoci che il debugger non interferisca con le API
            app.run(host="0.0.0.0", port=args.port, debug=True, use_reloader=True, 
                    use_debugger=False, threaded=True)
        else:
            app.config['ENV'] = 'production'
            app.config['DEBUG'] = False
            app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Errore durante l'avvio del server: {str(e)}") 
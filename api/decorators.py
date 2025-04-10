from flask import request, jsonify
import json
import logging
import jsonschema
from functools import wraps
import os
from jsonschema import validate, ValidationError, SchemaError

# Configura il logger
logger = logging.getLogger("gioco_rpg")

# Riferimento esterno allo schema API
from frontend.src.api.api_schema import apiSchema

# Importa funzioni spostate in api.utils
from api.utils import (
    get_schema_for_endpoint,
    validate_request_data,
    validate_response_data,
    resolve_schema_refs
)

def json_response_decorator(func):
    """
    Decorator che imposta l'header Content-Type a application/json
    per tutte le risposte delle API.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Se il risultato è una tupla (json, status_code)
        if isinstance(result, tuple) and len(result) >= 2:
            json_response, status_code = result[0], result[1]
            headers = {}
            
            # Se ci sono headers nella tupla
            if len(result) >= 3 and isinstance(result[2], dict):
                headers = result[2]
                
            # Assicurati che l'header Content-Type sia impostato a application/json
            headers['Content-Type'] = 'application/json'
            
            return json_response, status_code, headers
        elif hasattr(result, 'headers'):
            # Se il risultato è un oggetto response (come quelli restituiti da jsonify)
            result.headers['Content-Type'] = 'application/json'
            return result
        
        # Altrimenti ritorna il risultato invariato
        return result
    
    return wrapper

def register_api_route(rule, **options):
    """Registra una rotta API applicando automaticamente il decorator json_response_decorator"""
    def decorator(f):
        from flask import current_app as app
        endpoint = options.pop('endpoint', None)
        app.add_url_rule(rule, endpoint, json_response_decorator(f), **options)
        return f
    return decorator

def validate_api(func):
    """
    Decorator per validare le richieste e le risposte delle API.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ottieni il percorso dell'endpoint e il metodo HTTP
        endpoint = request.path.replace("/api", "")
        method = request.method.lower()
        
        # Validazione dei dati della richiesta
        if method in ["post", "put", "patch"]:
            data = request.json
            if data:
                valid, error = validate_request_data(endpoint, method, data)
                if not valid:
                    logger.warning(f"Validazione richiesta fallita per {endpoint} ({method}): {error}")
                    return jsonify({
                        "success": False,
                        "errore": f"Errore di validazione: {error}"
                    }), 400
        
        # Esegui la funzione decorata
        result = func(*args, **kwargs)
        
        # Estrai i dati della risposta
        if isinstance(result, tuple):
            response_data = result[0]
            status_code = result[1] if len(result) > 1 else 200
        else:
            response_data = result
            status_code = 200
            
        # Converti in dizionario se è una risposta Flask
        if hasattr(response_data, "get_json"):
            response_data = response_data.get_json()
            
        # Validazione dei dati della risposta
        if status_code < 400:  # Valida solo risposte di successo
            valid, error = validate_response_data(endpoint, method, response_data)
            if not valid:
                logger.error(f"Validazione risposta fallita per {endpoint} ({method}): {error}")
                # Registra ma non bloccare in caso di errore di validazione della risposta
        
        return result
    
    return wrapper

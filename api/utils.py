from flask import jsonify, request
import os
import pickle
import json
import time
import logging
import threading
import atexit
import jsonschema
from jsonschema import validate, ValidationError, SchemaError

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gioco_rpg")

# Riferimento esterno allo schema API
from frontend.src.api.api_schema import apiSchema

# Importazioni dalle configurazioni
from util.config import get_session_path

# Variabili globali
# Lock per proteggere l'accesso concorrente ai dizionari delle sessioni
sessioni_lock = threading.Lock()
# Dizionario per memorizzare lo stato di modifica delle sessioni
sessioni_modificate = {}  # {uuid: bool}
# Dizionario per memorizzare le sessioni attive in memoria
sessioni_attive = {}  # {uuid: StatoGioco}
# Dizionario per memorizzare le notifiche di sistema
notifiche_sistema = {}  # {uuid: [lista di notifiche]}
# Configurazione dell'autosave
AUTOSAVE_INTERVAL = 180  # Intervallo di autosave in secondi (3 minuti)
autosave_thread = None
autosave_attivo = True

def get_schema_for_endpoint(endpoint, method, request_or_response="request"):
    """
    Estrae lo schema per un determinato endpoint e metodo.
    
    Args:
        endpoint (str): Percorso dell'endpoint (es. "/inizia")
        method (str): Metodo HTTP (es. "post", "get")
        request_or_response (str): "request" o "response"
        
    Returns:
        dict: Schema per la validazione, None se non trovato
    """
    try:
        method = method.lower()
        # Verifica se l'endpoint esiste nello schema OpenAPI
        if endpoint not in apiSchema.get("paths", {}):
            logger.warning(f"Endpoint {endpoint} non trovato nello schema OpenAPI")
            return None
            
        # Verifica se il metodo esiste per l'endpoint
        if method not in apiSchema["paths"][endpoint]:
            logger.warning(f"Metodo {method} non trovato per l'endpoint {endpoint}")
            return None
            
        # Ottieni lo schema appropriato
        if request_or_response == "request" and "requestBody" in apiSchema["paths"][endpoint][method]:
            return apiSchema["paths"][endpoint][method]["requestBody"]["content"]["application/json"]["schema"]
        elif request_or_response == "response" and "responses" in apiSchema["paths"][endpoint][method]:
            # Prendi lo schema della risposta 200 (successo)
            if "200" in apiSchema["paths"][endpoint][method]["responses"]:
                return apiSchema["paths"][endpoint][method]["responses"]["200"]["content"]["application/json"]["schema"]
                
        return None
    except Exception as e:
        logger.error(f"Errore nell'estrazione dello schema: {str(e)}")
        return None

def validate_request_data(endpoint, method, data, query_params=None):
    """
    Valida i dati di una richiesta in base allo schema OpenAPI.
    
    Args:
        endpoint (str): Percorso dell'endpoint
        method (str): Metodo HTTP
        data (dict): Dati JSON della richiesta da validare
        query_params (dict): Parametri della query string da validare
        
    Returns:
        tuple: (validità, messaggio di errore)
    """
    schema = get_schema_for_endpoint(endpoint, method, "request")
    if not schema:
        # Se non c'è uno schema, consideriamo i dati validi
        return True, ""
        
    try:
        # Risolvi eventuali riferimenti nello schema
        resolve_schema_refs(schema)
        
        # Valida i dati JSON
        if data and "properties" in schema:
            jsonschema.validate(instance=data, schema=schema)
            
        # Valida i parametri della query string
        if query_params and "parameters" in apiSchema["paths"].get(endpoint, {}).get(method.lower(), {}):
            parameters = apiSchema["paths"][endpoint][method.lower()]["parameters"]
            for param in parameters:
                if param.get("in") == "query":
                    name = param.get("name")
                    required = param.get("required", False)
                    
                    # Se il parametro è richiesto ma non è presente
                    if required and (query_params is None or name not in query_params):
                        return False, f"Parametro richiesto '{name}' mancante nella query"
                        
                    # Se il parametro è presente, valida il tipo
                    if query_params and name in query_params:
                        param_schema = param.get("schema", {})
                        param_type = param_schema.get("type")
                        
                        # Validazione base dei tipi (per i tipi più comuni)
                        value = query_params[name]
                        if param_type == "integer":
                            try:
                                int(value)
                            except (ValueError, TypeError):
                                return False, f"Il parametro '{name}' deve essere un intero"
                        elif param_type == "number":
                            try:
                                float(value)
                            except (ValueError, TypeError):
                                return False, f"Il parametro '{name}' deve essere un numero"
                        elif param_type == "boolean":
                            if value.lower() not in ["true", "false", "1", "0"]:
                                return False, f"Il parametro '{name}' deve essere un booleano"
        
        return True, ""
    except ValidationError as e:
        logger.warning(f"Errore di validazione per {endpoint} ({method}): {str(e)}")
        return False, str(e)
    except SchemaError as e:
        logger.error(f"Errore nello schema per {endpoint} ({method}): {str(e)}")
        return False, f"Errore interno nello schema: {str(e)}"
    except Exception as e:
        logger.error(f"Errore generico durante la validazione: {str(e)}")
        return False, f"Errore di validazione: {str(e)}"

def validate_response_data(endpoint, method, data):
    """
    Valida i dati di una risposta in base allo schema OpenAPI.
    
    Args:
        endpoint (str): Percorso dell'endpoint
        method (str): Metodo HTTP
        data (dict): Dati da validare
        
    Returns:
        tuple: (validità, messaggio di errore)
    """
    schema = get_schema_for_endpoint(endpoint, method, "response")
    if not schema:
        # Se non c'è uno schema, consideriamo i dati validi
        return True, ""
        
    try:
        # Risolvi eventuali riferimenti nello schema
        resolve_schema_refs(schema)
        
        # Valida i dati
        jsonschema.validate(instance=data, schema=schema)
        return True, ""
    except ValidationError as e:
        logger.warning(f"Errore di validazione risposta per {endpoint} ({method}): {str(e)}")
        return False, str(e)
    except SchemaError as e:
        logger.error(f"Errore nello schema risposta per {endpoint} ({method}): {str(e)}")
        return False, f"Errore interno nello schema: {str(e)}"
    except Exception as e:
        logger.error(f"Errore generico durante la validazione risposta: {str(e)}")
        return False, f"Errore di validazione: {str(e)}"

def resolve_schema_refs(schema, cache=None):
    """
    Risolve i riferimenti ($ref) nello schema.
    Questa è una versione semplificata che gestisce solo i riferimenti interni.
    
    Args:
        schema (dict): Schema da processare
        cache (dict, optional): Cache per evitare ricorsioni infinite
    """
    if cache is None:
        cache = {}
        
    if not isinstance(schema, dict):
        return
        
    # Controlla se c'è un riferimento
    if "$ref" in schema:
        ref = schema["$ref"]
        # Gestisci solo riferimenti interni allo schema OpenAPI
        if ref.startswith("#/"):
            # Estrai il percorso
            path = ref[2:].split("/")
            # Cerca il riferimento nello schema principale
            ref_value = apiSchema
            for part in path:
                if part in ref_value:
                    ref_value = ref_value[part]
                else:
                    logger.error(f"Riferimento non trovato: {ref}")
                    return
                    
            # Copia le proprietà dal riferimento risolto allo schema corrente
            # (escluso il campo $ref)
            for key, value in ref_value.items():
                if key != "$ref":
                    schema[key] = value
                    
            # Rimuovi il campo $ref
            del schema["$ref"]
    
    # Processa ricorsivamente tutte le proprietà
    for key, value in schema.items():
        if isinstance(value, dict):
            resolve_schema_refs(value, cache)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    resolve_schema_refs(item, cache)

def salva_sessione(id_sessione, sessione, forza_salvataggio=False):
    """
    Salva una sessione su disco solo se necessario o se forzato
    
    Args:
        id_sessione: ID della sessione
        sessione: Oggetto StatoGioco da salvare
        forza_salvataggio: Se True, salva anche se non ci sono modifiche
    """
    with sessioni_lock:
        # Verifica se è necessario salvare (solo se modificata o forzato)
        if forza_salvataggio or sessioni_modificate.get(id_sessione, True):
            percorso = get_session_path(id_sessione)
            with open(percorso, 'wb') as f:
                pickle.dump(sessione, f)
            # Resetta il flag di modifica
            sessioni_modificate[id_sessione] = False
            logger.debug(f"Sessione {id_sessione} salvata su disco")

def carica_sessione(id_sessione):
    """Carica una sessione da disco"""
    percorso = get_session_path(id_sessione)
    if os.path.exists(percorso):
        with open(percorso, 'rb') as f:
            sessione = pickle.load(f)
            # Marca la sessione come non modificata quando caricata
            sessioni_modificate[id_sessione] = False
            return sessione
    return None

def marca_sessione_modificata(id_sessione):
    """
    Marca una sessione come modificata
    
    Args:
        id_sessione: ID della sessione da marcare come modificata
    """
    with sessioni_lock:
        sessioni_modificate[id_sessione] = True

def autosave_sessioni():
    """Thread per il salvataggio automatico delle sessioni attive"""
    global autosave_attivo
    
    logger.info("Thread di autosave avviato")
    
    while autosave_attivo:
        try:
            # Attendi l'intervallo di autosave
            time.sleep(AUTOSAVE_INTERVAL)
            
            # Copia le chiavi per evitare problemi di modifica durante l'iterazione
            with sessioni_lock:
                sessioni_da_salvare = list(sessioni_attive.keys())
            
            # Salva tutte le sessioni modificate
            for id_sessione in sessioni_da_salvare:
                try:
                    with sessioni_lock:
                        if id_sessione in sessioni_attive and sessioni_modificate.get(id_sessione, False):
                            salva_sessione(id_sessione, sessioni_attive[id_sessione])
                except Exception as e:
                    logger.error(f"Errore nell'autosave della sessione {id_sessione}: {str(e)}")
                    
            logger.debug("Completato ciclo di autosave")
        except Exception as e:
            logger.error(f"Errore nel thread di autosave: {str(e)}")
    
    logger.info("Thread di autosave terminato")

def avvia_autosave():
    """Avvia il thread di autosave"""
    global autosave_thread, autosave_attivo
    
    # Imposta il flag di attività
    autosave_attivo = True
    
    # Crea e avvia il thread di autosave
    autosave_thread = threading.Thread(target=autosave_sessioni, daemon=True)
    autosave_thread.start()
    
    logger.info("Thread di autosave avviato")

def ferma_autosave():
    """
    Ferma il thread di autosave e salva tutte le sessioni attive
    """
    global autosave_attivo
    
    logger.info("Arresto del thread di autosave in corso...")
    
    # Imposta il flag di stop
    autosave_attivo = False
    
    # Salva tutte le sessioni prima di terminare
    with sessioni_lock:
        for id_sessione, sessione in sessioni_attive.items():
            try:
                logger.info(f"Salvataggio finale della sessione {id_sessione}")
                salva_sessione(id_sessione, sessione, True)
            except Exception as e:
                logger.error(f"Errore durante il salvataggio finale della sessione {id_sessione}: {str(e)}")
    
    logger.info("Thread di autosave terminato")

@atexit.register
def cleanup():
    """Esegue pulizia delle risorse al termine dell'applicazione"""
    logger.info("Chiusura dell'applicazione in corso...")
    
    # Termina il thread di autosave e salva le sessioni
    ferma_autosave()
    
    logger.info("Pulizia completata")

def aggiungi_notifica(id_sessione, tipo, messaggio, data=None):
    """Aggiunge una notifica al sistema"""
    from uuid import uuid4
    
    if id_sessione not in notifiche_sistema:
        notifiche_sistema[id_sessione] = []
    
    notifica = {
        "id": str(uuid4()),
        "tipo": tipo,  # "info", "warning", "achievement", "quest", "combat", ecc.
        "messaggio": messaggio,
        "data": data or {},
        "timestamp": time.time(),
        "letta": False
    }
    
    notifiche_sistema[id_sessione].append(notifica)
    return notifica

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

def is_nodejs_installed():
    """Verifica se Node.js è installato nel sistema"""
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def build_frontend():
    """Compila il frontend React"""
    import subprocess
    import os
    try:
        # Controlla se Node.js è installato
        if not is_nodejs_installed():
            logger.warning("Node.js non rilevato nel sistema. Il frontend non sarà compilato automaticamente.")
            logger.warning("Per compilare il frontend manualmente, esegui: cd frontend && npm install && npm run build")
            if not os.path.exists(os.path.join('frontend', 'dist')):
                logger.error("La directory frontend/dist non esiste e Node.js non è installato.")
                logger.error("Il server servirà solo le API. Il frontend non sarà disponibile.")
            return
            
        # Controlla se la cartella dist esiste già
        if not os.path.exists(os.path.join('frontend', 'dist')):
            logger.info("Compilazione del frontend in corso...")
            # Salva la directory corrente
            current_dir = os.getcwd()
            try:
                # Cambia directory al frontend
                os.chdir('frontend')
                # Esegui npm install se node_modules non esiste
                if not os.path.exists('node_modules'):
                    logger.info("Installazione delle dipendenze del frontend...")
                    subprocess.run(['npm', 'install'], check=True)
                # Compila il frontend
                logger.info("Compilazione del frontend con npm run build...")
                subprocess.run(['npm', 'run', 'build'], check=True)
                logger.info("Frontend compilato con successo.")
            finally:
                # Assicurati di tornare alla directory originale anche in caso di errore
                os.chdir(current_dir)
        else:
            logger.info("Frontend già compilato. Usa --rebuild-frontend per ricompilare.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Errore durante la compilazione del frontend: {str(e)}")
        logger.error("Il server servirà solo le API. Per utilizzare il frontend, compilalo manualmente.")
    except Exception as e:
        logger.error(f"Errore inaspettato durante la compilazione del frontend: {str(e)}")
        logger.error("Il server servirà solo le API. Per utilizzare il frontend, compilalo manualmente.")

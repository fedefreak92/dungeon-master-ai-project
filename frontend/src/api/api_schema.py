"""
Converter per lo schema OpenAPI JavaScript in un formato Python importabile.
Questo file legge lo schema OpenAPI definito in JS e lo converte in un oggetto Python.
"""

import json
import os
import sys
import logging
import re

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Percorso allo schema JavaScript
SCHEMA_JS_PATH = os.path.join(os.path.dirname(__file__), 'api-schema.js')

def js_to_python_conversion(content):
    """
    Converte la sintassi JavaScript in Python compatibile.
    
    Args:
        content (str): Contenuto JavaScript
        
    Returns:
        str: Contenuto compatibile con Python
    """
    # Sostituisci true/false di JavaScript con True/False di Python
    content = re.sub(r'\btrue\b', 'True', content)
    content = re.sub(r'\bfalse\b', 'False', content)
    
    # Sostituisci null di JavaScript con None di Python
    content = re.sub(r'\bnull\b', 'None', content)
    
    return content

def extract_schema_from_js():
    """
    Estrae lo schema OpenAPI dal file JavaScript.
    
    Returns:
        dict: Schema OpenAPI come dizionario Python
    """
    try:
        with open(SCHEMA_JS_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Tenta di convertire direttamente il contenuto JS in sintassi Python
        try:
            # Rimuovi la parte iniziale della dichiarazione const
            if 'const apiSchema = ' in content:
                content = content.split('const apiSchema = ', 1)[1]
            # Rimuovi la parte finale con export default
            if 'export default' in content:
                content = content.split('export default', 1)[0]
            
            # Converti sintassi JS in Python
            content = js_to_python_conversion(content)
            
            # Prova a eseguire il codice direttamente
            namespace = {}
            exec('schema = ' + content.strip(), namespace)
            if 'schema' in namespace:
                logger.info("Schema API convertito con successo dal file JS")
                return namespace['schema']
        except Exception as e:
            logger.warning(f"Impossibile convertire direttamente lo schema JS: {e}")
            
        # Se la conversione diretta fallisce, usa lo schema base semplificato
        logger.warning("Utilizzo uno schema base semplificato per garantire il funzionamento del server")
        
        # Creiamo uno schema base con gli endpoints essenziali
        apiSchema = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Gioco RPG",
                "description": "API per interagire con il gioco RPG",
                "version": "1.0.0"
            },
            "paths": {
                "/inizia": {
                    "post": {
                        "summary": "Crea una nuova partita",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "nome": {"type": "string"},
                                            "classe": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Sessione creata con successo",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/comando": {
                    "post": {
                        "summary": "Invia un comando alla partita",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id_sessione": {"type": "string"},
                                            "comando": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Comando elaborato con successo",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/health": {
                    "get": {
                        "summary": "Verifica lo stato di salute del server",
                        "description": "Endpoint per verificare se il server è in esecuzione e risponde correttamente",
                        "responses": {
                            "200": {
                                "description": "Il server è attivo e risponde correttamente",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {
                                                    "type": "boolean",
                                                    "example": True
                                                },
                                                "data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "status": {
                                                            "type": "string",
                                                            "enum": ["ok", "degraded", "error"],
                                                            "example": "ok"
                                                        },
                                                        "timestamp": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                            "example": "2023-04-06T12:34:56.789Z"
                                                        },
                                                        "version": {
                                                            "type": "string",
                                                            "example": "1.0.0"
                                                        }
                                                    }
                                                },
                                                "messaggio": {
                                                    "type": "string",
                                                    "example": "Server disponibile"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Errore": {
                        "type": "object",
                        "properties": {
                            "errore": {
                                "type": "string"
                            }
                        }
                    },
                    "Giocatore": {
                        "type": "object",
                        "properties": {
                            "nome": {"type": "string"},
                            "classe": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        return apiSchema
    except Exception as e:
        logger.error(f"Errore nella lettura dello schema JS: {e}")
        return {}

# Estrai lo schema
apiSchema = extract_schema_from_js()

# Se lo schema è vuoto, crea uno schema base
if not apiSchema:
    logger.warning("Creazione di uno schema fallback poiché non è stato possibile estrarre lo schema originale")
    apiSchema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Gioco RPG API (Fallback)",
            "version": "1.0.0"
        },
        "paths": {}
    }

# Se si desidera eseguire questo script direttamente
if __name__ == "__main__":
    print(json.dumps(apiSchema, indent=2)) 
"""
Modulo per la validazione dei dati nelle API del gioco RPG.
Fornisce utility per validare manualmente i dati durante lo sviluppo.
"""

import os
import sys
import json
import logging
import jsonschema
from jsonschema import validate, ValidationError, SchemaError

# Aggiungi la directory principale al path per l'importazione
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Importa lo schema OpenAPI
try:
    from frontend.src.api.api_schema import apiSchema
except ImportError:
    logging.error("Impossibile importare lo schema API. Assicurati che il file api_schema.py esista.")
    apiSchema = {
        "openapi": "3.0.0", 
        "info": {"title": "API Schema (Error)", "version": "1.0.0"}, 
        "paths": {}
    }

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_schema(data, schema_ref):
    """
    Valida i dati contro uno schema di riferimento.
    
    Args:
        data (dict): Dati da validare
        schema_ref (str): Riferimento allo schema, es. "#/components/schemas/Giocatore"
        
    Returns:
        tuple: (validità, messaggio di errore)
    """
    # Estrai lo schema dal riferimento
    schema = resolve_schema_ref(schema_ref)
    if not schema:
        return False, f"Schema non trovato: {schema_ref}"
    
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Errore durante la validazione: {str(e)}"

def resolve_schema_ref(ref):
    """
    Risolve un riferimento a uno schema.
    
    Args:
        ref (str): Riferimento allo schema, es. "#/components/schemas/Giocatore"
        
    Returns:
        dict: Schema risolto
    """
    if not ref.startswith('#/'):
        return None
        
    path = ref[2:].split('/')
    schema = apiSchema
    
    for part in path:
        if part in schema:
            schema = schema[part]
        else:
            return None
            
    return schema

def validate_request(endpoint, method, data=None, query_params=None):
    """
    Valida i dati di una richiesta per un endpoint specifico.
    
    Args:
        endpoint (str): Percorso dell'endpoint (es. "/inizia")
        method (str): Metodo HTTP (es. "POST", "GET")
        data (dict): Dati JSON della richiesta
        query_params (dict): Parametri della query string
        
    Returns:
        tuple: (validità, messaggio di errore)
    """
    # Normalizza endpoint e method
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    method = method.lower()
    
    # Verifica se l'endpoint esiste
    if endpoint not in apiSchema.get("paths", {}):
        return False, f"Endpoint non trovato: {endpoint}"
        
    # Verifica se il metodo esiste
    if method not in apiSchema["paths"][endpoint]:
        return False, f"Metodo {method} non supportato per {endpoint}"
        
    # Valida i dati JSON del body
    if data and "requestBody" in apiSchema["paths"][endpoint][method]:
        request_schema = apiSchema["paths"][endpoint][method]["requestBody"]["content"]["application/json"]["schema"]
        try:
            jsonschema.validate(instance=data, schema=request_schema)
        except ValidationError as e:
            return False, f"Errore nella validazione del body: {str(e)}"
    
    # Valida i parametri della query string
    if query_params and "parameters" in apiSchema["paths"][endpoint][method]:
        parameters = apiSchema["paths"][endpoint][method]["parameters"]
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
                    
                    # Validazione base dei tipi
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

def validate_response(endpoint, method, data):
    """
    Valida i dati di una risposta per un endpoint specifico.
    
    Args:
        endpoint (str): Percorso dell'endpoint (es. "/inizia")
        method (str): Metodo HTTP (es. "POST", "GET")
        data (dict): Dati della risposta
        
    Returns:
        tuple: (validità, messaggio di errore)
    """
    # Normalizza endpoint e method
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    method = method.lower()
    
    # Verifica se l'endpoint esiste
    if endpoint not in apiSchema.get("paths", {}):
        return False, f"Endpoint non trovato: {endpoint}"
        
    # Verifica se il metodo esiste
    if method not in apiSchema["paths"][endpoint]:
        return False, f"Metodo {method} non supportato per {endpoint}"
        
    # Verifica se c'è uno schema di risposta
    if "responses" not in apiSchema["paths"][endpoint][method]:
        return False, f"Nessuna definizione di risposta per {endpoint} ({method})"
        
    # Cerca lo schema per la risposta 200 (success)
    if "200" not in apiSchema["paths"][endpoint][method]["responses"]:
        return False, f"Nessuna definizione di risposta 200 per {endpoint} ({method})"
        
    # Ottieni lo schema della risposta
    response_schema = apiSchema["paths"][endpoint][method]["responses"]["200"]["content"]["application/json"]["schema"]
    
    # Valida i dati
    try:
        jsonschema.validate(instance=data, schema=response_schema)
        return True, ""
    except ValidationError as e:
        return False, f"Errore nella validazione della risposta: {str(e)}"
    except Exception as e:
        return False, f"Errore durante la validazione: {str(e)}"

def get_schema_documentation():
    """
    Restituisce la documentazione formattata degli schemi disponibili.
    
    Returns:
        str: Documentazione formattata
    """
    if "components" not in apiSchema or "schemas" not in apiSchema["components"]:
        return "Nessuno schema disponibile"
        
    schemas = apiSchema["components"]["schemas"]
    doc = []
    
    doc.append("# Schemi disponibili")
    doc.append("")
    
    for name, schema in schemas.items():
        doc.append(f"## {name}")
        if "description" in schema:
            doc.append(f"{schema['description']}")
        doc.append("")
        
        if "properties" in schema:
            doc.append("### Proprietà")
            doc.append("")
            doc.append("| Nome | Tipo | Descrizione |")
            doc.append("| ---- | ---- | ----------- |")
            
            for prop_name, prop in schema["properties"].items():
                prop_type = prop.get("type", "object")
                if prop_type == "array" and "items" in prop:
                    items = prop["items"]
                    if "$ref" in items:
                        ref = items["$ref"].split("/")[-1]
                        prop_type = f"array di {ref}"
                    else:
                        prop_type = f"array di {items.get('type', 'object')}"
                elif "$ref" in prop:
                    ref = prop["$ref"].split("/")[-1]
                    prop_type = f"riferimento a {ref}"
                
                description = prop.get("description", "")
                doc.append(f"| {prop_name} | {prop_type} | {description} |")
            
            doc.append("")
    
    return "\n".join(doc)

def get_endpoint_documentation():
    """
    Restituisce la documentazione formattata degli endpoint disponibili.
    
    Returns:
        str: Documentazione formattata
    """
    if "paths" not in apiSchema:
        return "Nessun endpoint disponibile"
        
    paths = apiSchema["paths"]
    doc = []
    
    doc.append("# Endpoint API disponibili")
    doc.append("")
    
    for path, methods in sorted(paths.items()):
        doc.append(f"## {path}")
        doc.append("")
        
        for method, details in methods.items():
            method_upper = method.upper()
            summary = details.get("summary", "")
            description = details.get("description", "")
            
            doc.append(f"### {method_upper}")
            if summary:
                doc.append(f"**{summary}**")
            if description:
                doc.append(f"{description}")
            doc.append("")
            
            # Parametri
            if "parameters" in details:
                doc.append("#### Parametri")
                doc.append("")
                doc.append("| Nome | In | Tipo | Richiesto | Descrizione |")
                doc.append("| ---- | -- | ---- | --------- | ----------- |")
                
                for param in details["parameters"]:
                    name = param.get("name", "")
                    param_in = param.get("in", "")
                    required = "Sì" if param.get("required", False) else "No"
                    description = param.get("description", "")
                    param_type = "object"
                    
                    if "schema" in param:
                        param_type = param["schema"].get("type", "object")
                        
                    doc.append(f"| {name} | {param_in} | {param_type} | {required} | {description} |")
                
                doc.append("")
            
            # Request Body
            if "requestBody" in details:
                doc.append("#### Request Body")
                doc.append("")
                
                content = details["requestBody"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    
                    if "properties" in schema:
                        doc.append("| Proprietà | Tipo | Richiesto | Descrizione |")
                        doc.append("| --------- | ---- | --------- | ----------- |")
                        
                        properties = schema["properties"]
                        required_props = schema.get("required", [])
                        
                        for prop_name, prop in properties.items():
                            prop_type = prop.get("type", "object")
                            required = "Sì" if prop_name in required_props else "No"
                            description = prop.get("description", "")
                            
                            doc.append(f"| {prop_name} | {prop_type} | {required} | {description} |")
                        
                        doc.append("")
            
            # Risposte
            if "responses" in details:
                doc.append("#### Risposte")
                doc.append("")
                
                for status, response in details["responses"].items():
                    doc.append(f"##### {status}")
                    doc.append(f"{response.get('description', '')}")
                    doc.append("")
                    
                    if "content" in response and "application/json" in response["content"]:
                        schema = response["content"]["application/json"].get("schema", {})
                        
                        if "$ref" in schema:
                            ref = schema["$ref"].split("/")[-1]
                            doc.append(f"Risposta di tipo: {ref}")
                        elif "properties" in schema:
                            doc.append("| Proprietà | Tipo | Descrizione |")
                            doc.append("| --------- | ---- | ----------- |")
                            
                            for prop_name, prop in schema["properties"].items():
                                prop_type = prop.get("type", "object")
                                description = prop.get("description", "")
                                
                                doc.append(f"| {prop_name} | {prop_type} | {description} |")
                        
                        doc.append("")
            
            doc.append("---")
            doc.append("")
    
    return "\n".join(doc)

# Funzioni per esportare la documentazione
def export_documentation(filename="api_documentation.md"):
    """
    Esporta la documentazione degli endpoint e degli schemi in un file Markdown.
    
    Args:
        filename (str): Nome del file di output
        
    Returns:
        bool: True se l'operazione è riuscita, False altrimenti
    """
    try:
        endpoint_doc = get_endpoint_documentation()
        schema_doc = get_schema_documentation()
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(endpoint_doc)
            f.write("\n\n")
            f.write(schema_doc)
            
        logger.info(f"Documentazione esportata in {filename}")
        return True
    except Exception as e:
        logger.error(f"Errore durante l'esportazione della documentazione: {str(e)}")
        return False

# Esempi di utilizzo
if __name__ == "__main__":
    # Esempio di validazione di uno schema
    giocatore = {
        "nome": "Avventuriero",
        "classe": "guerriero",
        "livello": 1,
        "hp": 100,
        "max_hp": 100,
        "mana": 50,
        "max_mana": 50,
        "esperienza": 0,
        "prossimo_livello": 100
    }
    
    valid, message = validate_schema(giocatore, "#/components/schemas/Giocatore")
    print(f"Validazione giocatore: {'Valido' if valid else 'Non valido'}")
    if not valid:
        print(f"Errore: {message}")
        
    # Esempio di validazione di una richiesta
    inizia_request = {
        "nome": "Avventuriero",
        "classe": "guerriero"
    }
    
    valid, message = validate_request("/inizia", "POST", inizia_request)
    print(f"Validazione richiesta inizia: {'Valida' if valid else 'Non valida'}")
    if not valid:
        print(f"Errore: {message}")
        
    # Esporta la documentazione
    export_documentation() 
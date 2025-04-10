from flask import jsonify, request
import os
import json
import logging
from uuid import uuid4

# Configurazione del logger
logger = logging.getLogger(__name__)

# Import delle dipendenze necessarie
from api.decorators import validate_api
from util.data_manager import get_data_manager
from api.utils import (
    sessioni_attive, 
    carica_sessione, 
    salva_sessione, 
    marca_sessione_modificata
)

def register_routes(app):
    """Registra tutte le rotte del giocatore nell'app Flask"""
    
    @app.route("/api/inizia", methods=["POST"])
    @validate_api
    def inizia_gioco():
        """
        Endpoint API per iniziare una nuova partita.
        Crea un nuovo personaggio giocante e una nuova sessione.
        """
        try:
            data = request.json
            logger.info(f"Richiesta inizia gioco: {data}")
            
            # Verifica i parametri
            nome = data.get("nome")
            classe = data.get("classe")
            
            if not nome or not classe:
                logger.warning(f"Parametri mancanti: nome={nome}, classe={classe}")
                risposta = {
                    "success": False,
                    "errore": "Nome e classe sono obbligatori"
                }
                return jsonify(risposta), 400
                
            # Verifica che la classe esista
            try:
                # Usa lo stesso metodo di caricamento della classe Giocatore
                classi_disponibili = {}
                
                # Prova il percorso relativo
                percorso_file = os.path.join("data", "classes", "classes.json")
                if os.path.exists(percorso_file):
                    with open(percorso_file, "r", encoding="utf-8") as file:
                        classi_disponibili = json.load(file)
                        logger.info(f"Classi caricate per inizializzazione: {list(classi_disponibili.keys())}")
                else:
                    # Prova il percorso assoluto
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    percorso_assoluto = os.path.join(base_dir, "data", "classes", "classes.json")
                    if os.path.exists(percorso_assoluto):
                        with open(percorso_assoluto, "r", encoding="utf-8") as file:
                            classi_disponibili = json.load(file)
                            logger.info(f"Classi caricate da percorso assoluto: {list(classi_disponibili.keys())}")
                    else:
                        # Classi hardcoded
                        classi_disponibili = {
                            "guerriero": {},
                            "mago": {},
                            "ladro": {},
                            "chierico": {}
                        }
                        logger.warning("File classi non trovato, uso classi hardcoded")
                
                # Verifica che la classe scelta esiste
                if classe not in classi_disponibili:
                    logger.warning(f"Classe {classe} non disponibile. Classi disponibili: {list(classi_disponibili.keys())}")
                    risposta = {
                        "success": False,
                        "errore": f"Classe {classe} non disponibile. Classi disponibili: {list(classi_disponibili.keys())}"
                    }
                    return jsonify(risposta), 400
                    
            except Exception as e:
                logger.error(f"Errore nel caricamento delle classi: {str(e)}")
                # Per compatibilità, verifichiamo le classi predefinite
                if classe not in ["guerriero", "mago", "ladro", "chierico"]:
                    risposta = {
                        "success": False,
                        "errore": f"Classe {classe} non disponibile. Classi disponibili: guerriero, mago, ladro, chierico"
                    }
                    return jsonify(risposta), 400
                
            # Genera un ID sessione unico
            id_sessione = str(uuid4())
            logger.info(f"Generato ID sessione: {id_sessione}")
            
            # Crea una nuova istanza di StatoGioco
            try:
                from entities.giocatore import Giocatore
                from core.stato_gioco import StatoGioco
                
                # Crea il giocatore
                logger.info(f"Creazione giocatore con nome={nome}, classe={classe}")
                giocatore = Giocatore(nome, classe)
                
                # Importiamo lo stato di scelta mappa
                from states.scelta_mappa_state import SceltaMappaState
                
                # Crea lo stato di gioco con lo stato iniziale
                stato_iniziale = SceltaMappaState()
                stato_gioco = StatoGioco(giocatore, stato_iniziale)
                
                # Aggiungi log di debug per verificare lo stack degli stati
                logger.debug(f"Stack degli stati dopo inizializzazione: {[type(s).__name__ for s in stato_gioco.game.stato_stack]}")
                logger.debug(f"Debug stack stati: {stato_gioco.debug_stack_stati()}")
                
                # Registra la sessione
                sessioni_attive[id_sessione] = stato_gioco
                
                # Marca la sessione come modificata
                marca_sessione_modificata(id_sessione)
                
                # Salva la sessione su disco
                salva_sessione(id_sessione, stato_gioco, True)
                
                # Ottieni lo stato corrente in formato dizionario
                stato_corrente = stato_gioco.get_stato_attuale()
                nome_stato = type(stato_gioco.game.stato_corrente()).__name__ if stato_gioco.game.stato_corrente() else "Nessuno"
                
                # Mostra un log informativo sulla creazione della sessione
                logger.info(f"Creata sessione {id_sessione} per il giocatore {nome} ({classe})")
                logger.info(f"Stato iniziale: {nome_stato}")
                
                # Restituisci una risposta con ID sessione e stato iniziale
                risposta = {
                    "success": True,
                    "id_sessione": id_sessione,
                    "stato": stato_corrente,
                    "stato_nome": nome_stato,
                    "messaggio": f"Benvenuto, {nome}! La tua avventura inizia ora."
                }
                
                logger.info(f"Gioco iniziato con successo per {nome} ({classe}), sessione: {id_sessione}")
                return jsonify(risposta)
                
            except Exception as e:
                logger.error(f"Errore nella creazione dello stato di gioco: {str(e)}")
                logger.exception("Traceback completo:")
                risposta = {
                    "success": False,
                    "errore": f"Errore nella creazione dello stato di gioco: {str(e)}"
                }
                return jsonify(risposta), 500
                
        except Exception as e:
            logger.error(f"Errore non gestito in inizia_gioco: {str(e)}")
            logger.exception("Traceback completo:")
            risposta = {
                "success": False,
                "errore": f"Errore non gestito: {str(e)}"
            }
            return jsonify(risposta), 500
    
    @app.route("/api/statistiche", methods=["GET"])
    def ottieni_statistiche():
        """Ottieni le statistiche del giocatore"""
        id_sessione = request.args.get("id_sessione")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni lo stato completo e estrai solo le statistiche
        stato = sessione.get_stato_attuale()
        
        return jsonify({
            "nome": stato.get("nome", ""),
            "classe": stato.get("classe", ""),
            "hp": stato.get("hp", 0),
            "max_hp": stato.get("max_hp", 0),
            "statistiche": stato.get("statistiche", {})
        })
    
    @app.route("/api/inventario", methods=["GET"])
    def ottieni_inventario():
        """Ottieni l'inventario del giocatore"""
        id_sessione = request.args.get("id_sessione")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni lo stato completo e estrai solo le informazioni sull'inventario
        stato = sessione.get_stato_attuale()
        
        return jsonify({
            "inventario": stato.get("inventario", []),
            "equipaggiamento": stato.get("equipaggiamento", {})
        })
    
    @app.route("/api/equipaggiamento", methods=["POST"])
    def gestisci_equipaggiamento():
        """Gestisci l'equipaggiamento del giocatore"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        azione = data.get("azione", "")  # "equip", "unequip", "examine"
        oggetto = data.get("oggetto", "")
        slot = data.get("slot", "")  # es. "arma", "armatura", "anello", ecc.
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        if not oggetto:
            return jsonify({"errore": "Oggetto non specificato"}), 400
        
        if not azione:
            return jsonify({"errore": "Azione non specificata"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Memorizza lo stato prima dell'azione
        stato_pre_azione = sessione.get_stato_attuale()
        
        # Costruisci il comando appropriato in base all'azione richiesta
        if azione == "equip":
            comando = f"equipaggia {oggetto}"
            if slot:
                comando += f" {slot}"
        elif azione == "unequip":
            comando = f"rimuovi {oggetto}"
        elif azione == "examine":
            comando = f"esamina {oggetto}"
        else:
            return jsonify({"errore": "Azione non valida"}), 400
        
        # Elabora il comando
        sessione.processa_comando(comando)
        
        # Marca la sessione come modificata
        marca_sessione_modificata(id_sessione)
        
        # Ottieni lo stato aggiornato
        stato = sessione.get_stato_attuale()
        
        # Verifica se la modifica dell'equipaggiamento è significativa
        evento_importante = False
        
        # Solo per le azioni di equipaggiamento e rimozione
        if azione in ["equip", "unequip"]:
            # Verifica se l'oggetto è importante
            oggetto_nome = oggetto.lower()
            
            # Lista di parole chiave che identificano oggetti importanti
            parole_oggetti_importanti = ["leggendario", "mitico", "divino", "raro", "epico", 
                                        "antico", "artefatto", "sacro", "magico", "incantato"]
            
            # Controlla se l'oggetto contiene una delle parole chiave
            if any(parola in oggetto_nome for parola in parole_oggetti_importanti):
                evento_importante = True
                logger.info(f"Oggetto importante '{oggetto}' {azione=='equip' and 'equipaggiato' or 'rimosso'}")
            
            # Controlla se l'oggetto modificato era in uno slot importante 
            # (le armi e le armature sono sempre importanti)
            if azione == "equip" and slot and slot.lower() in ["arma", "armatura", "principale", "secondaria"]:
                evento_importante = True
                logger.info(f"Modificato equipaggiamento in slot importante: {slot}")
            
            # Controlla se ci sono stati cambiamenti significativi nelle statistiche del giocatore
            if "giocatore" in stato and "giocatore" in stato_pre_azione:
                # Statistiche da monitorare
                statistiche = ["attacco", "difesa", "agilità", "costituzione", "magia"]
                
                for stat in statistiche:
                    valore_pre = stato_pre_azione.get("giocatore", {}).get(stat, 0)
                    valore_post = stato.get("giocatore", {}).get(stat, 0)
                    
                    # Se la statistica è cambiata significativamente (>10%)
                    if valore_pre > 0 and abs((valore_post - valore_pre) / valore_pre) > 0.1:
                        evento_importante = True
                        logger.info(f"Cambiamento significativo in {stat}: {valore_pre} -> {valore_post}")
                        break
        
        # Salva la sessione in base all'importanza
        if evento_importante:
            logger.info(f"Evento importante rilevato nella gestione equipaggiamento per la sessione {id_sessione}, salvataggio forzato")
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
            "equipaggiamento": stato.get("equipaggiamento", {}),
            "evento_importante": evento_importante
        })
    
    @app.route("/api/classi", methods=["GET", "OPTIONS"])
    def ottieni_classi():
        """
        Endpoint API per ottenere le classi di personaggio giocante disponibili.
        """
        # Gestisci la richiesta OPTIONS per CORS
        if request.method == "OPTIONS":
            response = app.response_class(
                response="",
                status=200
            )
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept, X-Requested-With")
            response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
            return response
        
        try:
            logger.info("Richiesta per /api/classi ricevuta")
            
            # Log dei dettagli della richiesta
            logger.info(f"Headers richiesta: {dict(request.headers)}")
            logger.info(f"URL richiesta: {request.url}")
            logger.info(f"Metodo richiesta: {request.method}")
            
            # Utilizza il DataManager per caricare le classi
            data_manager = get_data_manager()
            classi = data_manager.get_classes()
            
            # Log del contenuto che stiamo inviando
            logger.info(f"Restituendo classi: {classi}")
            json_str = json.dumps(classi)
            logger.info(f"Lunghezza JSON: {len(json_str)} byte")
            
            # Crea una risposta JSON con il tipo MIME corretto
            response = app.response_class(
                response=json_str,
                status=200,
                mimetype='application/json'
            )
            
            # Assicurati che il Content-Type sia corretto
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept, X-Requested-With'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            
            # Log dei dettagli della risposta
            logger.info(f"Headers risposta: {dict(response.headers)}")
            
            return response
        except Exception as e:
            logger.error(f"Errore nel recupero delle classi: {str(e)}")
            logger.exception("Traceback completo:")
            
            # In caso di errore, usa comunque i dati hardcoded
            classi_fallback = {
                "guerriero": {"nome": "Guerriero", "descrizione": "Un combattente esperto"},
                "mago": {"nome": "Mago", "descrizione": "Un potente incantatore"},
                "ladro": {"nome": "Ladro", "descrizione": "Un abile furfante"},
                "chierico": {"nome": "Chierico", "descrizione": "Un sacerdote divino"}
            }
            
            error_response = app.response_class(
                response=json.dumps(classi_fallback),
                status=200,
                mimetype='application/json'
            )
            
            # Assicurati che il Content-Type sia corretto anche in caso di errore
            error_response.headers['Content-Type'] = 'application/json'
            error_response.headers['Access-Control-Allow-Origin'] = '*'
            error_response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept, X-Requested-With'
            error_response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            
            # Log dei dettagli della risposta di errore
            logger.info(f"Headers risposta di errore: {dict(error_response.headers)}")
            
            return error_response
    
    @app.route("/api/abilita", methods=["GET"])
    def ottieni_abilita():
        """Ottieni le abilità del giocatore"""
        id_sessione = request.args.get("id_sessione")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        # Verifica che la sessione esista
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni le abilità del giocatore
        stato = sessione.get_stato_attuale()
        abilita = stato.get("abilita", [])
        
        return jsonify({
            "abilita": abilita,
            "mana_attuale": stato.get("mana", 0),
            "mana_massimo": stato.get("mana_max", 0)
        })
    
    @app.route("/api/usa_abilita", methods=["POST"])
    def usa_abilita():
        """Usa un'abilità del giocatore"""
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        id_abilita = data.get("id_abilita")
        nome_abilita = data.get("nome_abilita")
        bersaglio = data.get("bersaglio", "")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        if not id_abilita and not nome_abilita:
            return jsonify({"errore": "ID abilità o nome abilità non fornito"}), 400
        
        # Verifica che la sessione esista
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Memorizza lo stato prima dell'uso dell'abilità
        stato_pre_azione = sessione.get_stato_attuale()
        
        # Costruisci il comando per l'abilità
        comando = f"usa_abilita "
        if id_abilita:
            comando += id_abilita
        else:
            comando += nome_abilita
        
        if bersaglio:
            comando += f" {bersaglio}"
        
        # Elabora il comando
        sessione.processa_comando(comando)
        
        # Marca la sessione come modificata
        marca_sessione_modificata(id_sessione)
        
        # Ottieni lo stato aggiornato
        stato = sessione.get_stato_attuale()
        
        # Determina se l'abilità usata è importante
        evento_importante = False
        
        # Lista di abilità che sono considerate importanti
        abilita_importanti = ["resurrezione", "teletrasporto", "metamorfosi", "evocazione", 
                            "esplosione", "tempesta", "guarigione_totale", "invisibilità"]
        
        # Ottieni il nome dell'abilità usata
        abilita_usata = nome_abilita or id_abilita
        
        # Controlla se il nome dell'abilità contiene parole chiave importanti
        if any(importante.lower() in abilita_usata.lower() for importante in abilita_importanti):
            evento_importante = True
            logger.info(f"Abilità importante '{abilita_usata}' usata")
        
        # Controlla se l'abilità ha causato cambiamenti significativi
        if "giocatore" in stato and "giocatore" in stato_pre_azione:
            # Verifica cambiamenti nella salute
            hp_pre = stato_pre_azione.get("giocatore", {}).get("salute", 0)
            hp_post = stato.get("giocatore", {}).get("salute", 0)
            
            if abs(hp_post - hp_pre) > 50:
                evento_importante = True
                logger.info(f"Cambiamento significativo della salute: {hp_pre} -> {hp_post}")
            
            # Verifica cambiamenti nel mana
            mana_pre = stato_pre_azione.get("giocatore", {}).get("mana", 0)
            mana_post = stato.get("giocatore", {}).get("mana", 0)
            
            # Se è stato consumato molto mana, potrebbe essere un'abilità importante
            if mana_pre - mana_post > 30:
                evento_importante = True
                logger.info(f"Consumo significativo di mana: {mana_pre} -> {mana_post}")
        
        # Controlla se il combattimento è cambiato
        combattimento_pre = stato_pre_azione.get("combattimento", {}).get("attivo", False)
        combattimento_post = stato.get("combattimento", {}).get("attivo", False)
        
        # Se l'abilità ha iniziato o terminato un combattimento
        if combattimento_pre != combattimento_post:
            evento_importante = True
            if combattimento_post:
                logger.info("L'abilità ha iniziato un combattimento")
            else:
                logger.info("L'abilità ha terminato un combattimento")
        
        # Salva la sessione in base all'importanza
        if evento_importante:
            logger.info(f"Evento importante rilevato nell'uso dell'abilità per la sessione {id_sessione}, salvataggio forzato")
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

    # Restituisci un dizionario di rotte esportate
    return {
        "inizia_gioco": inizia_gioco,
        "ottieni_statistiche": ottieni_statistiche,
        "ottieni_inventario": ottieni_inventario,
        "gestisci_equipaggiamento": gestisci_equipaggiamento,
        "ottieni_classi": ottieni_classi,
        "ottieni_abilita": ottieni_abilita,
        "usa_abilita": usa_abilita
    }

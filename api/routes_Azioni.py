from flask import jsonify, request
import os
import json
import logging
from uuid import uuid4
import datetime

# Configurazione del logger
logger = logging.getLogger(__name__)

# Import delle dipendenze necessarie
from api.decorators import validate_api
from api.utils import (
    sessioni_attive, 
    carica_sessione, 
    salva_sessione, 
    marca_sessione_modificata,
    aggiungi_notifica
)

def register_routes(app):
    """Registra tutte le rotte relative alle azioni nell'app Flask"""
    
    @app.route("/api/comando", methods=["POST"])
    @validate_api
    def esegui_comando():
        """Elabora un comando inviato dal client"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        comando = data.get("comando", "")
        
        # Verifica che l'ID sessione sia stato fornito
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        # Controlla se la sessione è attiva in memoria
        sessione = sessioni_attive.get(id_sessione)
        
        # Se non è in memoria, prova a caricarla da disco
        if not sessione:
            sessione = carica_sessione(id_sessione)
            if sessione:
                # Se trovata su disco, caricala in memoria
                sessioni_attive[id_sessione] = sessione
        
        # Se ancora non trovata, restituisci errore
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Elabora il comando
        sessione.processa_comando(comando)
        
        # Marca la sessione come modificata
        marca_sessione_modificata(id_sessione)
        
        # Ottieni lo stato corrente
        stato_attuale = sessione.get_stato_attuale()
        
        # Ottieni il nome dello stato corrente
        stato_nome = "NessunoStato"
        if sessione.game.stato_corrente():
            stato_nome = type(sessione.game.stato_corrente()).__name__
        
        # Ottieni l'output strutturato
        output_strutturato = sessione.io_buffer.get_output_structured()
        
        # Pulisci il buffer dei messaggi
        sessione.io_buffer.clear()
        
        # Controlla se il gioco è terminato
        gioco_terminato = not sessione.game.attivo
        
        # Se il gioco è terminato, salva la sessione
        if gioco_terminato:
            logger.info(f"Gioco terminato per la sessione {id_sessione}, salvataggio finale")
            salva_sessione(id_sessione, sessione, True)
        else:
            # Salvataggio normale
            salva_sessione(id_sessione, sessione)
        
        # Restituisci lo stato aggiornato
        return jsonify({
            "output": output_strutturato,
            "stato": stato_attuale,
            "stato_nome": stato_nome,
            "fine": gioco_terminato
        })

    @app.route("/api/azioni_disponibili", methods=["GET"])
    def azioni_disponibili():
        """Ottieni le azioni disponibili nel contesto attuale"""
        id_sessione = request.args.get("id_sessione")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        # Verifica che la sessione esista
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni lo stato corrente
        stato = sessione.get_stato_attuale()
        stato_corrente = sessione.game.stato_corrente()
        
        # Lista base di azioni sempre disponibili
        azioni_base = [
            {"id": "guarda", "nome": "Guarda", "descrizione": "Esamina l'ambiente circostante"},
            {"id": "inventario", "nome": "Inventario", "descrizione": "Controlla il tuo inventario"},
            {"id": "stato", "nome": "Stato", "descrizione": "Controlla il tuo stato attuale"}
        ]
        
        # Azioni specifiche per lo stato corrente
        azioni_specifiche = []
        
        # Se lo stato corrente ha un metodo per ottenere le azioni disponibili, usalo
        if stato_corrente and hasattr(stato_corrente, "get_azioni_disponibili"):
            try:
                azioni_specifiche = stato_corrente.get_azioni_disponibili()
            except Exception as e:
                logger.error(f"Errore nell'ottenere le azioni specifiche: {str(e)}")
        
        # Aggiungi azioni basate sull'ambiente corrente
        azioni_ambiente = []
        
        # Aggiungi azioni per gli oggetti nell'ambiente
        oggetti = stato.get("oggetti_ambiente", [])
        for oggetto in oggetti:
            nome = oggetto.get("nome", "oggetto")
            azioni_ambiente.append({
                "id": f"esamina {nome}",
                "nome": f"Esamina {nome}",
                "descrizione": f"Esamina l'oggetto {nome}"
            })
            azioni_ambiente.append({
                "id": f"prendi {nome}",
                "nome": f"Prendi {nome}",
                "descrizione": f"Raccogli l'oggetto {nome}"
            })
        
        # Aggiungi azioni per gli NPC nell'ambiente
        npcs = stato.get("npc_presenti", [])
        for npc in npcs:
            nome = npc.get("nome", "personaggio")
            azioni_ambiente.append({
                "id": f"parla {nome}",
                "nome": f"Parla con {nome}",
                "descrizione": f"Inizia una conversazione con {nome}"
            })
        
        # Aggiungi azioni per le uscite disponibili
        uscite = stato.get("uscite", [])
        for direzione in uscite:
            azioni_ambiente.append({
                "id": f"vai {direzione}",
                "nome": f"Vai {direzione}",
                "descrizione": f"Vai verso {direzione}"
            })
        
        # Restituisci tutte le azioni disponibili
        return jsonify({
            "azioni_base": azioni_base,
            "azioni_specifiche": azioni_specifiche,
            "azioni_ambiente": azioni_ambiente
        })

    @app.route("/api/esplora", methods=["POST"])
    def esplora_ambiente():
        """Esplora l'ambiente circostante"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Memorizza lo stato prima dell'esplorazione
        stato_pre_esplorazione = sessione.get_stato_attuale()
        
        # Esegui un comando "guarda" o "esplora"
        sessione.processa_comando("guarda")
        
        # Marca la sessione come modificata
        marca_sessione_modificata(id_sessione)
        
        # Ottieni lo stato aggiornato
        stato = sessione.get_stato_attuale()
        
        # Verifica se l'esplorazione ha rivelato elementi significativi
        evento_importante = False
        
        # Verifica se sono stati scoperti nuovi oggetti
        oggetti_pre = set(o.get("id", "") for o in stato_pre_esplorazione.get("oggetti_ambiente", []))
        oggetti_post = [o for o in stato.get("oggetti_ambiente", []) if o.get("id", "") not in oggetti_pre]
        
        # Controlla se sono stati scoperti oggetti importanti
        for nuovo_oggetto in oggetti_post:
            nome = nuovo_oggetto.get("nome", "").lower()
            if any(importante in nome for importante in ["chiave", "tesoro", "forziere", "reliquia", "mappa"]):
                evento_importante = True
                logger.info(f"Oggetto importante scoperto: {nome}")
                break
        
        # Verifica se sono stati scoperti nuovi NPC
        npc_pre = set(n.get("id", "") for n in stato_pre_esplorazione.get("npc_presenti", []))
        npc_post = [n for n in stato.get("npc_presenti", []) if n.get("id", "") not in npc_pre]
        
        if npc_post:
            evento_importante = True
            logger.info(f"Nuovi NPC scoperti durante l'esplorazione: {len(npc_post)}")
        
        # Verifica se sono state scoperte nuove uscite o passaggi
        uscite_pre = set(u for u in stato_pre_esplorazione.get("uscite", []))
        uscite_post = set(u for u in stato.get("uscite", []))
        
        if uscite_post - uscite_pre:
            evento_importante = True
            logger.info(f"Nuove uscite scoperte: {', '.join(uscite_post - uscite_pre)}")
        
        # Salva la sessione in base all'importanza
        if evento_importante:
            logger.info(f"Evento importante rilevato nell'esplorazione per la sessione {id_sessione}, salvataggio forzato")
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
            "oggetti": stato.get("oggetti_ambiente", []),
            "uscite": stato.get("uscite", []),
            "npc": stato.get("npc_presenti", []),
            "evento_importante": evento_importante
        })

    @app.route("/api/dialogo", methods=["POST"])
    def gestisci_dialogo():
        """Gestisci il dialogo con un NPC"""
        # Estrai i dati dalla richiesta
        data = request.json or {}
        id_sessione = data.get("id_sessione")
        npc_id = data.get("npc_id")
        risposta_id = data.get("risposta_id")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        if not npc_id:
            return jsonify({"errore": "ID NPC non fornito"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni lo stato corrente
        stato = sessione.get_stato_attuale()
        
        # Verifica se l'NPC è presente
        npc_presenti = stato.get("npc_presenti", [])
        npc_target = None
        
        for npc in npc_presenti:
            if npc.get("id") == npc_id:
                npc_target = npc
                break
        
        if not npc_target:
            return jsonify({"errore": f"NPC con ID {npc_id} non trovato nella posizione attuale"}), 404
        
        # Costruisci il comando di dialogo
        if risposta_id:
            # Se è stata selezionata una risposta, usa il comando "rispondi"
            comando = f"rispondi {risposta_id} a {npc_target.get('nome')}"
        else:
            # Altrimenti, inizia un nuovo dialogo
            comando = f"parla con {npc_target.get('nome')}"
        
        # Elabora il comando
        sessione.processa_comando(comando)
        
        # Marca la sessione come modificata
        marca_sessione_modificata(id_sessione)
        
        # Ottieni lo stato aggiornato
        stato_aggiornato = sessione.get_stato_attuale()
        
        # Ottieni l'output strutturato
        output = sessione.io_buffer.get_output_structured()
        
        # Pulisci il buffer dei messaggi
        sessione.io_buffer.clear()
        
        # Verifica se ci sono opzioni di dialogo
        opzioni_dialogo = stato_aggiornato.get("opzioni_dialogo", [])
        dialogo_attivo = len(opzioni_dialogo) > 0
        
        # Se è stata rivelata un'informazione importante durante il dialogo, salva
        evento_importante = False
        
        # Controlla se il dialogo ha rivelato informazioni su missioni
        if any("missione" in msg.lower() for msg in output if isinstance(msg, str)):
            evento_importante = True
            logger.info(f"Informazioni su missioni rivelate nel dialogo con {npc_target.get('nome')}")
            
            # Aggiungi una notifica per la nuova missione
            aggiungi_notifica(id_sessione, {
                "tipo": "missione",
                "titolo": f"Nuova informazione su missione",
                "messaggio": f"{npc_target.get('nome')} ti ha fornito informazioni su una missione",
                "timestamp": datetime.datetime.now().timestamp()
            })
        
        # Controlla se è stato ottenuto un oggetto durante il dialogo
        inventario_pre = stato.get("inventario", [])
        inventario_post = stato_aggiornato.get("inventario", [])
        
        if len(inventario_post) > len(inventario_pre):
            evento_importante = True
            logger.info(f"Oggetto ottenuto durante il dialogo con {npc_target.get('nome')}")
        
        # Salva la sessione in base all'importanza
        if evento_importante:
            salva_sessione(id_sessione, sessione, True)
        else:
            salva_sessione(id_sessione, sessione)
        
        return jsonify({
            "output": output,
            "dialogo_attivo": dialogo_attivo,
            "opzioni_dialogo": opzioni_dialogo,
            "npc": npc_target,
            "evento_importante": evento_importante
        })

    @app.route("/api/npc", methods=["GET"])
    def ottieni_info_npc():
        """Ottieni informazioni sugli NPC nella posizione attuale o su un NPC specifico"""
        id_sessione = request.args.get("id_sessione")
        npc_id = request.args.get("id")
        
        if not id_sessione:
            return jsonify({"errore": "ID sessione non fornito"}), 400
        
        sessione = sessioni_attive.get(id_sessione) or carica_sessione(id_sessione)
        
        if not sessione:
            return jsonify({"errore": "Sessione non trovata"}), 404
        
        # Ottieni lo stato corrente
        stato = sessione.get_stato_attuale()
        
        # Se è specificato un ID, restituisci le informazioni su quel NPC specifico
        if npc_id:
            npc_presenti = stato.get("npc_presenti", [])
            
            for npc in npc_presenti:
                if npc.get("id") == npc_id:
                    # Aggiungi dettagli sulla relazione con il giocatore e lo stato del dialogo
                    npc_dettagliato = npc.copy()
                    
                    # Aggiungi informazioni sullo stato del dialogo
                    npc_dettagliato["dialogo_disponibile"] = True
                    
                    # Verifica se ci sono missioni disponibili da questo NPC
                    npc_dettagliato["ha_missioni"] = False
                    
                    # Se il NPC è un commerciante, aggiungi informazioni sul negozio
                    if npc.get("tipo") == "commerciante":
                        npc_dettagliato["commercio_disponibile"] = True
                    
                    return jsonify(npc_dettagliato)
            
            return jsonify({"errore": f"NPC con ID {npc_id} non trovato"}), 404
        else:
            # Restituisci informazioni su tutti gli NPC nella posizione attuale
            return jsonify({
                "npc_presenti": stato.get("npc_presenti", [])
            })

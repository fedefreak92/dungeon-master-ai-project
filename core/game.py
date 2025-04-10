from world.gestore_mappe import GestitoreMappe
from core.io_interface import TerminalIO
import json
import ast  # Importa ast per literal_eval


class Game:
    def __init__(self, giocatore, stato_iniziale, io_handler, e_temporaneo=False):
        """
        Inizializza il gioco con un giocatore e uno stato iniziale
        
        Args:
            giocatore: L'oggetto giocatore
            stato_iniziale: Lo stato iniziale del gioco
            io_handler: Handler per input/output obbligatorio
            e_temporaneo: Se True, indica che è un'istanza temporanea solo per caricamento
        """
        self.giocatore = giocatore
        self.stato_stack = []  # Stack degli stati
        self.attivo = True
        self.io = io_handler
        
        # Inizializza il gestore delle mappe
        self.gestore_mappe = GestitoreMappe()
        
        # Imposta la mappa iniziale del giocatore (taverna per default)
        # Solo se il giocatore è già stato creato
        if self.giocatore is not None:
            self.imposta_mappa_iniziale()
        
        # Non aggiungere lo stato iniziale se è None o se è un'istanza temporanea
        if stato_iniziale is not None and not e_temporaneo:
            self.push_stato(stato_iniziale)

    def imposta_mappa_iniziale(self, mappa_nome=None):
        """
        Imposta la mappa iniziale per il giocatore
        
        Args:
            mappa_nome (str, optional): Nome della mappa iniziale. Se None, non imposta alcuna mappa.
        """
        if mappa_nome is None:
            # Non impostiamo una mappa di default, lasciamo la scelta al giocatore
            return True
            
        mappa = self.gestore_mappe.ottieni_mappa(mappa_nome)
        if mappa:
            self.gestore_mappe.imposta_mappa_attuale(mappa_nome)
            x, y = mappa.pos_iniziale_giocatore
            self.giocatore.imposta_posizione(mappa_nome, x, y)
            return True
        return False

    def cambia_mappa(self, mappa_nome, x=None, y=None):
        """
        Cambia la mappa corrente del giocatore
        
        Args:
            mappa_nome (str): Nome della mappa di destinazione
            x (int, optional): Posizione X di destinazione
            y (int, optional): Posizione Y di destinazione
            
        Returns:
            bool: True se il cambio mappa è avvenuto, False altrimenti
        """
        return self.gestore_mappe.cambia_mappa_giocatore(self.giocatore, mappa_nome, x, y)

    def stato_corrente(self):
        """
        Restituisce lo stato corrente in modo sicuro
        
        Returns:
            Lo stato corrente o None se lo stack è vuoto
        """
        try:
            return self.stato_stack[-1] if self.stato_stack else None
        except IndexError:
            return None

    def push_stato(self, nuovo_stato):
        """
        Inserisce un nuovo stato sopra quello corrente.
        Previene la duplicazione di stati dello stesso tipo.
        
        Args:
            nuovo_stato: Il nuovo stato da aggiungere
            
        Returns:
            bool: True se lo stato è stato aggiunto, False altrimenti
        """
        try:
            # Verifica che lo stato non sia None
            if nuovo_stato is None:
                self.io.mostra_messaggio("Errore: tentativo di aggiungere uno stato nullo.")
                return False
            
            # Verifica che non si stia aggiungendo uno stato dello stesso tipo di quello corrente
            stato_corrente = self.stato_corrente()
            if stato_corrente and type(stato_corrente) == type(nuovo_stato):
                self.io.mostra_messaggio(f"Attenzione: si sta tentando di aggiungere uno stato {type(nuovo_stato).__name__} identico a quello già presente.")
                return False
            
            # Imposta il contesto di gioco nello stato prima di usarlo
            if hasattr(nuovo_stato, 'set_game_context'):
                nuovo_stato.set_game_context(self)
                
            if stato_corrente:
                stato_corrente.pausa(self)  # Mette in pausa lo stato corrente
            self.stato_stack.append(nuovo_stato)
            nuovo_stato.entra(self)
            
            # Log debug
            self.io.mostra_messaggio(f"Stato {type(nuovo_stato).__name__} aggiunto. Stack: {[type(s).__name__ for s in self.stato_stack]}")
            return True
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il push dello stato: {e}")
            self.attivo = False
            return False

    def pop_stato(self):
        """
        Rimuove lo stato corrente e torna al precedente.
        
        Returns:
            bool: True se lo stato è stato rimosso con successo, False altrimenti
        """
        try:
            if not self.stato_stack:
                self.io.mostra_messaggio("Nessuno stato da rimuovere.")
                return False
                
            stato_corrente = self.stato_stack[-1]
            if stato_corrente is None:
                # Rimuovi stato nullo senza chiamare metodi su di esso
                self.io.mostra_messaggio("Rimozione di uno stato non valido.")
                self.stato_stack.pop()
            else:
                # Procedi normalmente
                nome_stato = type(stato_corrente).__name__
                stato_corrente.esci(self)
                self.stato_stack.pop()
                self.io.mostra_messaggio(f"Stato {nome_stato} rimosso dallo stack.")
                
            # Riprende lo stato precedente se esiste
            if self.stato_corrente():
                if self.stato_corrente() is not None:
                    # Assicurati che lo stato abbia il contesto di gioco corretto
                    if hasattr(self.stato_corrente(), 'set_game_context'):
                        self.stato_corrente().set_game_context(self)
                    self.stato_corrente().riprendi(self)
                    self.io.mostra_messaggio(f"Ritorno allo stato: {type(self.stato_corrente()).__name__}")
                else:
                    # Rimuovi anche questo stato se è None
                    self.io.mostra_messaggio("Stato precedente non valido, verrà rimosso.")
                    self.stato_stack.pop()
            
            # Se non ci sono più stati, termina il gioco
            if not self.stato_stack:
                self.io.mostra_messaggio("Tutti gli stati sono stati rimossi. Il gioco terminerà.")
                self.attivo = False  # Nessuno stato rimasto
                
            # Log debug dello stack attuale
            self.io.mostra_messaggio(f"Stack degli stati: {[type(s).__name__ for s in self.stato_stack]}")
            return True
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il pop dello stato: {e}")
            # In caso di errore critico, rimuovi lo stato comunque
            if self.stato_stack:
                self.stato_stack.pop()
            if not self.stato_stack:
                self.attivo = False
            return False

    def cambia_stato(self, nuovo_stato):
        """
        Sostituisce lo stato corrente con uno nuovo
        
        Args:
            nuovo_stato: Il nuovo stato che sostituirà quello corrente
        """
        try:
            # Imposta il contesto di gioco nello stato prima di usarlo
            if hasattr(nuovo_stato, 'set_game_context'):
                nuovo_stato.set_game_context(self)
                
            if self.stato_corrente():
                self.stato_corrente().esci(self)
                self.stato_stack.pop()
            self.stato_stack.append(nuovo_stato)
            nuovo_stato.entra(self)
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il cambio di stato: {e}")
            self.attivo = False

    def esegui(self):
        """
        Esegue il loop principale del gioco
        """
        self.attivo = True  # Assicuriamoci che il gioco sia attivo all'inizio
        
        while self.attivo:
            # Verifica che ci sia almeno uno stato nello stack
            if not self.stato_corrente():
                self.io.mostra_messaggio("Nessuno stato attivo. Il gioco terminerà.")
                break
                
            try:
                # Esegue lo stato corrente
                self.stato_corrente().esegui(self)
            except Exception as e:
                self.io.mostra_messaggio(f"Errore durante l'esecuzione dello stato: {e}")
                import traceback
                self.io.mostra_messaggio(traceback.format_exc())
                self.pop_stato()  # Gestione automatica degli errori
                
                # Se non ci sono più stati, termina il gioco
                if not self.stato_stack:
                    self.attivo = False

    def termina(self):
        """
        Termina il gioco in modo pulito
        """
        while self.stato_stack:
            self.pop_stato()
            
        self.attivo = False

    def sblocca_area(self, area_id):
        """
        Gestisce lo sblocco di un'area nel mondo.
        
        Args:
            area_id (str): Identificatore dell'area da sbloccare
        """
        self.io.mostra_messaggio(f"L'area {area_id} è stata sbloccata!")
        # Logica per sbloccare l'area
        
        # Se l'area è una mappa, possiamo attivarla
        if area_id in self.gestore_mappe.mappe:
            self.io.mostra_messaggio(f"La mappa {area_id} è ora accessibile!")
        
    def attiva_trappola(self, trappola_id, danno=0):
        """
        Attiva una trappola nel mondo.
        
        Args:
            trappola_id (str): Identificatore della trappola
            danno (int): Quantità di danno da infliggere
        """
        self.io.mostra_messaggio(f"Una trappola si attiva!")
        if danno > 0:
            self.giocatore.subisci_danno(danno)
        
    def modifica_ambiente(self, ambiente_id, nuovo_stato):
        """
        Modifica un ambiente del mondo.
        
        Args:
            ambiente_id (str): Identificatore dell'ambiente
            nuovo_stato (str): Nuovo stato dell'ambiente
        """
        self.io.mostra_messaggio(f"L'ambiente {ambiente_id} cambia: {nuovo_stato}")
        # Logica per modificare l'ambiente

    def ottieni_posizione_giocatore(self):
        """
        Restituisce informazioni sulla posizione corrente del giocatore
        
        Returns:
            dict: Informazioni sulla posizione corrente
        """
        if not self.giocatore.mappa_corrente:
            return None
            
        mappa = self.gestore_mappe.ottieni_mappa(self.giocatore.mappa_corrente)
        if not mappa:
            return None
            
        return {
            "mappa": self.giocatore.mappa_corrente,
            "x": self.giocatore.x,
            "y": self.giocatore.y,
            "oggetti_vicini": self.giocatore.ottieni_oggetti_vicini(self.gestore_mappe),
            "npg_vicini": self.giocatore.ottieni_npg_vicini(self.gestore_mappe)
        }
        
    def muovi_giocatore(self, direzione):
        """
        Muove il giocatore in una direzione specifica
        
        Args:
            direzione (str): Una delle direzioni "nord", "sud", "est", "ovest"
            
        Returns:
            bool: True se il movimento è avvenuto, False altrimenti
        """
        direzioni = {
            "nord": (0, -1),
            "sud": (0, 1),
            "est": (1, 0),
            "ovest": (-1, 0)
        }
        
        if direzione not in direzioni:
            return False
            
        dx, dy = direzioni[direzione]
        spostamento = self.giocatore.muovi(dx, dy, self.gestore_mappe)
        
        if not spostamento:
            self.io.mostra_messaggio("Non puoi muoverti in quella direzione!")
            
        return spostamento

    def salva(self, file_path="salvataggio.json"):
        """
        Salva lo stato corrente del gioco in un file JSON
        
        Args:
            file_path (str): Percorso del file di salvataggio
            
        Returns:
            bool: True se il salvataggio è riuscito, False altrimenti
        """
        try:
            # Importa il modulo di configurazione
            from util.config import get_save_path, create_backup, SAVE_FORMAT_VERSION
            import logging
            import json

            logger = logging.getLogger("gioco_rpg")
            
            # Converti il percorso usando il modulo di configurazione
            save_path = get_save_path(file_path)
            
            # Crea un backup se il file esiste già
            if save_path.exists():
                backup_path = create_backup(save_path)
                if backup_path:
                    logger.info(f"Creato backup del salvataggio precedente: {backup_path}")
                    
            # Ottieni dati serializzabili del giocatore
            if hasattr(self.giocatore, 'to_dict'):
                giocatore_data = self.giocatore.to_dict()
            else:
                # Fallback al salvataggio base
                inventario_data = []
                for oggetto in self.giocatore.inventario:
                    if hasattr(oggetto, 'to_dict') and callable(getattr(oggetto, 'to_dict')):
                        inventario_data.append(oggetto.to_dict())
                    else:
                        # Salva tutti gli attributi dell'oggetto
                        oggetto_data = {
                            "nome": getattr(oggetto, 'nome', 'Oggetto sconosciuto'),
                            "tipo": getattr(oggetto, 'tipo', 'vario'),
                            "descrizione": getattr(oggetto, 'descrizione', ''),
                            "valore": getattr(oggetto, 'valore', 0),
                            "effetto": getattr(oggetto, 'effetto', {}),
                        }
                        inventario_data.append(oggetto_data)
                        
                # Serializza arma equipaggiata
                arma_data = None
                if hasattr(self.giocatore, 'arma') and self.giocatore.arma:
                    if hasattr(self.giocatore.arma, 'to_dict'):
                        arma_data = self.giocatore.arma.to_dict()
                    else:
                        arma_data = {
                            "nome": getattr(self.giocatore.arma, 'nome', 'Arma sconosciuta'),
                            "tipo": "arma",
                            "descrizione": getattr(self.giocatore.arma, 'descrizione', ''),
                            "valore": getattr(self.giocatore.arma, 'valore', 0),
                            "effetto": getattr(self.giocatore.arma, 'effetto', {}),
                        }
                
                # Serializza armatura equipaggiata
                armatura_data = None
                if hasattr(self.giocatore, 'armatura') and self.giocatore.armatura:
                    if hasattr(self.giocatore.armatura, 'to_dict'):
                        armatura_data = self.giocatore.armatura.to_dict()
                    else:
                        armatura_data = {
                            "nome": getattr(self.giocatore.armatura, 'nome', 'Armatura sconosciuta'),
                            "tipo": "armatura",
                            "descrizione": getattr(self.giocatore.armatura, 'descrizione', ''),
                            "valore": getattr(self.giocatore.armatura, 'valore', 0),
                            "effetto": getattr(self.giocatore.armatura, 'effetto', {}),
                        }
                        
                # Serializza accessori
                accessori_data = []
                if hasattr(self.giocatore, 'accessori'):
                    for acc in self.giocatore.accessori:
                        if hasattr(acc, 'to_dict'):
                            accessori_data.append(acc.to_dict())
                        else:
                            acc_data = {
                                "nome": getattr(acc, 'nome', 'Accessorio sconosciuto'),
                                "tipo": "accessorio",
                                "descrizione": getattr(acc, 'descrizione', ''),
                                "valore": getattr(acc, 'valore', 0),
                                "effetto": getattr(acc, 'effetto', {}),
                            }
                            accessori_data.append(acc_data)
                        
                giocatore_data = {
                    "nome": self.giocatore.nome,
                    "classe": self.giocatore.classe,
                    "hp": self.giocatore.hp,
                    "hp_max": getattr(self.giocatore, 'hp_max', self.giocatore.hp),
                    "mappa": self.giocatore.mappa_corrente,
                    "posizione": [self.giocatore.x, self.giocatore.y],
                    "oro": getattr(self.giocatore, 'oro', 0),
                    "inventario": inventario_data,
                    "arma": arma_data,
                    "armatura": armatura_data,
                    "accessori": accessori_data,
                    "forza_base": getattr(self.giocatore, 'forza_base', 10),
                    "destrezza_base": getattr(self.giocatore, 'destrezza_base', 10),
                    "costituzione_base": getattr(self.giocatore, 'costituzione_base', 10),
                    "intelligenza_base": getattr(self.giocatore, 'intelligenza_base', 10),
                    "saggezza_base": getattr(self.giocatore, 'saggezza_base', 10),
                    "carisma_base": getattr(self.giocatore, 'carisma_base', 10),
                    "livello": getattr(self.giocatore, 'livello', 1),
                    "esperienza": getattr(self.giocatore, 'esperienza', 0),
                }
                
            # Serializza lo stack degli stati
            stati_data = []
            for stato in self.stato_stack:
                if hasattr(stato, 'to_dict'):
                    stati_data.append(stato.to_dict())
                else:
                    # Fallback per stati che non hanno to_dict
                    stati_data.append({"type": stato.__class__.__name__})
            
            # Componi il dizionario completo
            data = {
                "giocatore": giocatore_data,
                "stati": stati_data,
                "attivo": self.attivo,
                "mappa_corrente": self.giocatore.mappa_corrente,
                "versione_gioco": SAVE_FORMAT_VERSION,  # Usa la versione dal modulo config
                "timestamp": __import__('time').time(),  # Quando è stato fatto il salvataggio
                "mappe": self.gestore_mappe.to_dict()  # Salva lo stato completo delle mappe
            }
            
            # Aggiungi tutti gli NPG mappa per mappa
            data["npg"] = {
                nome_mappa: {
                    str(posizione): npg.to_dict() for posizione, npg in mappa.npg.items()
                }
                for nome_mappa, mappa in self.gestore_mappe.mappe.items()
            }
            
            # Serializza e salva su file
            save_path.parent.mkdir(exist_ok=True, parents=True)  # Assicura che la directory esista
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            logger.info(f"Salvataggio completato: {save_path}")
            return True
            
        except Exception as e:
            import traceback
            logging.getLogger("gioco_rpg").error(f"Errore durante il salvataggio: {e}")
            logging.getLogger("gioco_rpg").error(traceback.format_exc())
            return False
    
    def carica(self, file_path="salvataggio.json"):
        """
        Carica uno stato di gioco da un file JSON
        
        Args:
            file_path (str): Percorso del file di salvataggio
            
        Returns:
            bool: True se il caricamento è riuscito, False altrimenti
        """
        try:
            # Importa moduli
            from util.config import get_save_path, validate_save_data, migrate_save_data
            import logging
            import json
            
            logger = logging.getLogger("gioco_rpg")
            save_path = get_save_path(file_path)
            
            # Verifica esistenza file
            if not save_path.exists():
                logger.error(f"File di salvataggio non trovato: {save_path}")
                self.io.mostra_messaggio(f"File di salvataggio non trovato: {save_path}")
                return False
            
            # Carica e valida dati
            try:
                with open(save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"File di salvataggio non valido (JSON errato): {e}")
                self.io.mostra_messaggio("File di salvataggio danneggiato")
                return False
                
            # Valida dati caricati
            valid, message = validate_save_data(data)
            if not valid:
                logger.error(message)
                self.io.mostra_messaggio(message)
                return False
                
            # Migra dati se necessario
            data = migrate_save_data(data)
            
            # Registry per oggetti già caricati (evita riferimenti circolari)
            # Da usare solo con le classi che supportano il parametro
            loaded_objects = {}
            
            # Importa tutti i moduli di stato
            from entities.giocatore import Giocatore
            from entities.npg import NPG
            from items.oggetto import Oggetto
            from items.oggetto_interattivo import OggettoInterattivo
            
            # Mappa delle classi di stato ai loro moduli
            mapping_stati = {
                "TavernaState": "states.taverna",
                "DialogoState": "states.dialogo", 
                "CombattimentoState": "states.combattimento",
                "MercatoState": "states.mercato",
                "GestioneInventarioState": "states.gestione_inventario",
                "ProvaAbilitaState": "states.prova_abilita",
                "MappaState": "states.mappa_state",
                "MenuState": "states.menu"
            }
            
            # Carica il giocatore
            try:
                # Usa direttamente la versione standard senza loaded_objects per il giocatore
                self.giocatore = Giocatore.from_dict(data["giocatore"])
            except KeyError:
                logger.error("Dati del giocatore mancanti o incompleti nel salvataggio")
                self.io.mostra_messaggio("Dati del giocatore mancanti o incompleti nel salvataggio")
                return False
            except Exception as e:
                logger.error(f"Errore nella creazione del giocatore: {str(e)}")
                self.io.mostra_messaggio(f"Errore nella creazione del giocatore: {str(e)}")
                return False

            # Ricrea lo stack degli stati
            self.stato_stack = []
            for stato_dato in data.get("stati", []):
                # Ottieni il tipo dello stato
                stato_tipo = stato_dato.get("type")
                if not stato_tipo:
                    continue
                    
                # Importa dinamicamente la classe di stato
                try:
                    # Utilizza il mapping per trovare il modulo corretto
                    if stato_tipo in mapping_stati:
                        modulo_nome = mapping_stati[stato_tipo]
                        
                        # Importa dinamicamente il modulo
                        import importlib
                        modulo = importlib.import_module(modulo_nome)
                        
                        # Ottieni la classe dallo stesso nome
                        classe_stato = getattr(modulo, stato_tipo)
                        
                        # Ricostruisci lo stato usando from_dict
                        if hasattr(classe_stato, 'from_dict'):
                            # Usa semplicemente la versione standard
                            stato = classe_stato.from_dict(stato_dato)
                            self.stato_stack.append(stato)
                        else:
                            logger.warning(f"Stato {stato_tipo} non ha un metodo from_dict")
                            self.io.mostra_messaggio(f"Avviso: {stato_tipo} non ha un metodo from_dict")
                    else:
                        logger.warning(f"Mappatura non trovata per {stato_tipo}")
                        self.io.mostra_messaggio(f"Avviso: mappatura non trovata per {stato_tipo}")
                except Exception as e:
                    logger.error(f"Errore nel caricamento dello stato {stato_tipo}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue

            # Carica le mappe e gli oggetti interattivi se presenti
            if "mappe" in data:
                try:
                    self.gestore_mappe.from_dict(data["mappe"])
                    logger.info("Mondo di gioco caricato con successo!")
                except Exception as e:
                    logger.error(f"Errore nel caricamento delle mappe: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                # Compatibilità con vecchi salvataggi - ricrea NPC nelle mappe
                for mappa_nome, npcs in data.get("npg", {}).items():
                    mappa = self.gestore_mappe.ottieni_mappa(mappa_nome)
                    if mappa:
                        for pos_str, npg_data in npcs.items():
                            try:
                                import ast
                                pos = ast.literal_eval(pos_str)
                                npg = NPG.from_dict(npg_data)
                                mappa.npg[pos] = npg
                            except Exception as e:
                                logger.error(f"Errore nel caricamento dell'NPG in posizione {pos_str}: {str(e)}")
                        
            # Imposta la mappa corrente
            mappa_corrente = data.get("mappa_corrente", "taverna")
            self.gestore_mappe.imposta_mappa_attuale(mappa_corrente)
            
            # Imposta lo stato attivo
            self.attivo = data.get("attivo", True)
            
            # Pulisci vecchi backup
            from util.config import clean_old_backups
            clean_old_backups()
            
            logger.info(f"Partita di {self.giocatore.nome} caricata con successo!")
            self.io.mostra_messaggio(f"Partita di {self.giocatore.nome} caricata con successo!")
            return True
            
        except Exception as e:
            import traceback
            logging.getLogger("gioco_rpg").error(f"Errore durante il caricamento: {e}")
            logging.getLogger("gioco_rpg").error(traceback.format_exc())
            self.io.mostra_messaggio(f"Errore durante il caricamento: {e}")
            return False

    def debug_stack_stati(self):
        """
        Fornisce una vista dettagliata dello stack degli stati per il debug
        
        Returns:
            dict: Dizionario con informazioni sullo stack
        """
        try:
            stati_info = []
            for i, stato in enumerate(self.stato_stack):
                tipo_stato = type(stato).__name__
                # Aggiungi attributi specifici se disponibili
                info_aggiuntive = {}
                if hasattr(stato, 'nome_stato'):
                    info_aggiuntive['nome_stato'] = stato.nome_stato
                if hasattr(stato, 'fase'):
                    info_aggiuntive['fase'] = stato.fase
                stati_info.append({
                    'indice': i,
                    'tipo': tipo_stato,
                    'info': info_aggiuntive
                })
                
            risultato = {
                'stato_corrente': type(self.stato_corrente()).__name__ if self.stato_corrente() else "Nessuno",
                'numero_stati': len(self.stato_stack),
                'stati': stati_info,
                'attivo': self.attivo
            }
            
            return risultato
        except Exception as e:
            return {
                'errore': f"Errore durante la generazione del debug: {str(e)}",
                'numero_stati': len(self.stato_stack) if hasattr(self, 'stato_stack') else 0
            }

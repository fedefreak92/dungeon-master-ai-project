from world.mappa import Mappa
import random
from items.oggetto_interattivo import OggettoInterattivo, Porta, Baule, Leva, Trappola
from entities.giocatore import Giocatore
from entities.npg import NPG
from entities.nemico import Nemico
from world.mappa import MappaComponente, MappaCaricatore
from pathlib import Path
from util.data_manager import get_data_manager
import json
import os
import logging
from util.config import get_save_path, create_backup, SAVE_FORMAT_VERSION

class GestitoreMappe:
    def __init__(self):
        """Inizializza il gestore mappe"""
        self.mappe = {}  # Nome mappa -> oggetto Mappa
        self.mappa_attuale = None
        self.data_manager = get_data_manager()
        self.mappa_caricatore = MappaCaricatore(Path("data/mappe"))
        self.inizializza_mappe()
        
    def inizializza_mappe(self):
        """Crea e configura tutte le mappe del gioco esclusivamente da JSON"""
        # Carica le mappe da file JSON
        mappe_json = self.carica_mappe_da_json()
        
        if not mappe_json:
            logging.error("Nessuna mappa JSON trovata. Il gioco non può continuare senza mappe.")
            raise ValueError("Nessuna mappa JSON trovata in data/mappe. Controlla che i file JSON delle mappe esistano.")
            
        # Usa le mappe caricate da JSON
        for nome, mappa in mappe_json.items():
            self.mappe[nome] = mappa
            # Carica gli oggetti interattivi e NPG per questa mappa
            self.carica_oggetti_interattivi_da_json(mappa, nome)
            self.carica_npg_da_json(mappa, nome)
        
        logging.info(f"Caricate {len(mappe_json)} mappe da file JSON")
        
        # Imposta la mappa "taverna" come mappa attuale di default
        if "taverna" in self.mappe:
            self.imposta_mappa_attuale("taverna")
        elif self.mappe:
            # Altrimenti, usa la prima mappa disponibile
            primo_nome = next(iter(self.mappe.keys()))
            self.imposta_mappa_attuale(primo_nome)
            logging.info(f"Mappa taverna non trovata, impostata mappa {primo_nome} come default")
        else:
            logging.error("Nessuna mappa caricata")
        
    def carica_mappe_da_json(self):
        """
        Carica le mappe dai file JSON nella directory data/mappe.
        
        Returns:
            dict: Dizionario di mappe caricate (nome -> oggetto Mappa) o {} se fallisce
        """
        mappe = {}
        
        try:
            # Ottieni l'elenco di tutti i file .json nella directory mappe
            file_mappe = self.mappa_caricatore.elenca_mappe_disponibili()
            
            if not file_mappe:
                logging.error("Nessun file mappa trovato in data/mappe")
                return {}
                
            # Carica ogni mappa
            for nome_file in file_mappe:
                try:
                    mappa = self.mappa_caricatore.carica_mappa(nome_file)
                    # Verifica che la mappa sia valida
                    if self._verifica_mappa_valida(mappa):
                        mappe[mappa.nome] = mappa
                        logging.info(f"Mappa caricata: {mappa.nome}")
                    else:
                        logging.error(f"Mappa {nome_file} non valida, ignorata")
                except Exception as e:
                    logging.error(f"Errore nel caricamento della mappa {nome_file}: {e}")
                    import traceback
                    logging.error(traceback.format_exc())
            
            return mappe
        except Exception as e:
            logging.error(f"Errore generale nel caricamento delle mappe: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return {}
    
    def _verifica_mappa_valida(self, mappa):
        """
        Verifica che una mappa sia valida e completa.
        
        Args:
            mappa: L'oggetto Mappa da verificare
            
        Returns:
            bool: True se la mappa è valida, False altrimenti
        """
        # Verifica che la mappa abbia un nome
        if not mappa.nome:
            logging.error("Mappa senza nome")
            return False
            
        # Verifica che la griglia sia presente e delle dimensioni corrette
        if not mappa.griglia:
            logging.error(f"Mappa {mappa.nome} senza griglia")
            return False
            
        # Verifica che le dimensioni della griglia corrispondano a quelle dichiarate
        if len(mappa.griglia) != mappa.altezza:
            logging.error(f"Mappa {mappa.nome}: altezza dichiarata {mappa.altezza} ma griglia ha {len(mappa.griglia)} righe")
            return False
            
        for riga in mappa.griglia:
            if len(riga) != mappa.larghezza:
                logging.error(f"Mappa {mappa.nome}: larghezza dichiarata {mappa.larghezza} ma riga ha {len(riga)} colonne")
                return False
        
        # Verifica che la posizione iniziale sia impostata e valida
        x, y = mappa.pos_iniziale_giocatore
        if x == 0 and y == 0:
            logging.error(f"Mappa {mappa.nome}: posizione iniziale del giocatore non impostata")
            return False
            
        if x < 0 or x >= mappa.larghezza or y < 0 or y >= mappa.altezza:
            logging.error(f"Mappa {mappa.nome}: posizione iniziale del giocatore ({x}, {y}) fuori dai limiti della mappa")
            return False
            
        # Se la posizione iniziale è in un muro, è un errore
        if mappa.griglia[y][x] != 0:  # Assumendo che 0 sia lo spazio vuoto
            logging.error(f"Mappa {mappa.nome}: posizione iniziale del giocatore ({x}, {y}) è in un muro")
            return False
            
        # Tutte le verifiche sono passate
        return True
    
    def salva_mappe_su_json(self):
        """
        Salva tutte le mappe correnti in file JSON.
        
        Returns:
            bool: True se il salvataggio è riuscito per tutte le mappe
        """
        successo = True
        
        for nome, mappa in self.mappe.items():
            try:
                # Salva la mappa in formato JSON
                if not self.mappa_caricatore.salva_mappa(mappa):
                    successo = False
                    logging.error(f"Errore nel salvataggio della mappa {nome}")
            except Exception as e:
                successo = False
                logging.error(f"Errore durante il salvataggio della mappa {nome}: {e}")
                
        return successo

    def carica_npg_da_json(self, mappa, nome_mappa):
        """
        Carica gli NPC per una mappa dalle configurazioni JSON.
        
        Args:
            mappa (Mappa): Oggetto mappa in cui posizionare gli NPC
            nome_mappa (str): Nome della mappa
        """
        try:
            # Nome del file: mappe_npg.json
            # Struttura: {"taverna": [{"nome": "Durnan", "posizione": [5, 5]}, ...], ...}
            npg_config = self.data_manager.load_data("npc", "mappe_npg.json").get(nome_mappa, [])
            
            if not npg_config:
                logging.info(f"Nessuna configurazione di NPG trovata per la mappa {nome_mappa}")
                return
                
            # Per ogni configurazione di NPG
            for config in npg_config:
                nome_npg = config.get("nome")
                posizione = config.get("posizione")
                
                if not nome_npg or not posizione or len(posizione) != 2:
                    logging.warning(f"Configurazione NPG non valida: {config}")
                    continue
                    
                # Crea l'NPG
                npg = NPG(nome_npg)
                
                # Posiziona l'NPG sulla mappa
                x, y = posizione
                # Verifica che x e y siano validi e all'interno dei limiti della mappa
                if 0 <= x < mappa.larghezza and 0 <= y < mappa.altezza:
                    # Verifica che la posizione non sia già occupata
                    if (x, y) in mappa.oggetti or (x, y) in mappa.npg:
                        logging.warning(f"Posizione ({x}, {y}) già occupata, impossibile posizionare NPG {nome_npg}")
                        continue
                        
                    # Verifica che la posizione non sia un muro
                    if mappa.griglia[y][x] != 0:  # Assumendo che 0 sia lo spazio vuoto
                        logging.warning(f"Posizione ({x}, {y}) è un muro, impossibile posizionare NPG {nome_npg}")
                        continue
                        
                    mappa.aggiungi_npg(npg, x, y)
                    logging.info(f"NPG {nome_npg} posizionato in ({x}, {y}) sulla mappa {nome_mappa}")
                else:
                    logging.warning(f"Posizione non valida per NPG {nome_npg}: ({x}, {y})")
        except Exception as e:
            logging.error(f"Errore durante il caricamento degli NPG per la mappa {nome_mappa}: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    def carica_oggetti_interattivi_da_json(self, mappa, nome_mappa):
        """
        Carica gli oggetti interattivi per una mappa dalle configurazioni JSON.
        
        Args:
            mappa (Mappa): Oggetto mappa in cui posizionare gli oggetti
            nome_mappa (str): Nome della mappa
        """
        try:
            # Ottieni la configurazione degli oggetti per questa mappa
            oggetti_config = self.data_manager.get_map_objects(nome_mappa)
            
            # Se non ci sono configurazioni, avvisa ma non è un errore critico
            if not oggetti_config:
                logging.warning(f"Nessuna configurazione di oggetti trovata per la mappa {nome_mappa}")
                return
            
            # Per ogni configurazione di oggetto
            for config in oggetti_config:
                nome_oggetto = config.get("nome")
                posizione = config.get("posizione")
                
                if not nome_oggetto or not posizione or len(posizione) != 2:
                    logging.warning(f"Configurazione oggetto non valida: {config}")
                    continue
                    
                # Carica l'oggetto interattivo dal JSON
                oggetto = OggettoInterattivo.carica_da_json(nome_oggetto)
                
                if oggetto:
                    # Posiziona l'oggetto sulla mappa
                    x, y = posizione
                    # Verifica che x e y siano validi e all'interno dei limiti della mappa
                    if 0 <= x < mappa.larghezza and 0 <= y < mappa.altezza:
                        # Verifica che la posizione non sia già occupata
                        if (x, y) in mappa.oggetti or (x, y) in mappa.npg:
                            logging.warning(f"Posizione ({x}, {y}) già occupata, impossibile posizionare oggetto {nome_oggetto}")
                            continue
                            
                        # Verifica che la posizione non sia un muro
                        if mappa.griglia[y][x] != 0:  # Assumendo che 0 sia lo spazio vuoto
                            logging.warning(f"Posizione ({x}, {y}) è un muro, impossibile posizionare oggetto {nome_oggetto}")
                            continue
                            
                        mappa.aggiungi_oggetto(oggetto, x, y)
                        logging.info(f"Oggetto {nome_oggetto} posizionato in ({x}, {y}) sulla mappa {nome_mappa}")
                    else:
                        logging.warning(f"Posizione non valida per oggetto {nome_oggetto}: ({x}, {y})")
                else:
                    logging.warning(f"Oggetto {nome_oggetto} non trovato nei dati JSON")
        except Exception as e:
            logging.error(f"Errore durante il caricamento degli oggetti per la mappa {nome_mappa}: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
    def ottieni_mappa(self, nome):
        """Restituisce una mappa per nome"""
        return self.mappe.get(nome)
    
    def imposta_mappa_attuale(self, nome):
        """Imposta la mappa attuale per riferimento facile"""
        if nome in self.mappe:
            self.mappa_attuale = self.mappe[nome]
            return True
        return False
        
    def trasferisci_oggetti_da_stato(self, nome_mappa, stato):
        """Trasferisce oggetti e NPG dallo stato alla mappa corrispondente"""
        mappa = self.mappe.get(nome_mappa)
        if not mappa:
            return False
            
        # Ottieni le posizioni degli oggetti interattivi dalla configurazione JSON
        oggetti_config = self.data_manager.get_map_objects(nome_mappa)
        pos_oggetti = {}
        
        if oggetti_config:
            for config in oggetti_config:
                nome_oggetto = config.get("nome")
                posizione = config.get("posizione")
                if nome_oggetto and posizione and len(posizione) == 2:
                    pos_oggetti[nome_oggetto] = tuple(posizione)
        
        # Posiziona gli oggetti interattivi sulla mappa usando le posizioni da JSON
        for chiave, oggetto in stato.oggetti_interattivi.items():
            if chiave in pos_oggetti:
                x, y = pos_oggetti[chiave]
                if 0 <= x < mappa.larghezza and 0 <= y < mappa.altezza:
                    if (x, y) not in mappa.oggetti and (x, y) not in mappa.npg:
                        mappa.aggiungi_oggetto(oggetto, x, y)
                    else:
                        logging.warning(f"Posizione ({x}, {y}) già occupata, impossibile posizionare oggetto {chiave}")
                else:
                    logging.warning(f"Posizione non valida per oggetto {chiave}: ({x}, {y})")
            else:
                logging.warning(f"Nessuna posizione definita per oggetto {chiave}, oggetto non posizionato")
        
        # Carica posizioni NPG da JSON
        npg_config = self.data_manager.load_data("npc", "mappe_npg.json").get(nome_mappa, [])
        pos_npg = {}
        
        if npg_config:
            for config in npg_config:
                nome_npg = config.get("nome")
                posizione = config.get("posizione")
                if nome_npg and posizione and len(posizione) == 2:
                    pos_npg[nome_npg] = tuple(posizione)
        
        # Posiziona gli NPG sulla mappa usando le posizioni da JSON
        for nome, npg in stato.npg_presenti.items():
            if nome in pos_npg:
                x, y = pos_npg[nome]
                if 0 <= x < mappa.larghezza and 0 <= y < mappa.altezza:
                    if (x, y) not in mappa.oggetti and (x, y) not in mappa.npg:
                        mappa.aggiungi_npg(npg, x, y)
                    else:
                        logging.warning(f"Posizione ({x}, {y}) già occupata, impossibile posizionare NPG {nome}")
                else:
                    logging.warning(f"Posizione non valida per NPG {nome}: ({x}, {y})")
            else:
                logging.warning(f"Nessuna posizione definita per NPG {nome}, NPG non posizionato")
            
        return True

    def muovi_giocatore(self, giocatore, dx, dy):
        """
        Gestisce lo spostamento del giocatore sulla mappa.
        
        Args:
            giocatore (Giocatore): Il giocatore da muovere
            dx, dy (int): Delta di spostamento
            
        Returns:
            dict: Risultato del movimento con chiavi 'successo', 'messaggio', 'cambio_mappa'
        """
        # Verifica che siamo su una mappa valida
        if not giocatore.mappa_corrente or giocatore.mappa_corrente not in self.mappe:
            return {"successo": False, "messaggio": "Mappa non valida", "cambio_mappa": False}
            
        mappa = self.mappe[giocatore.mappa_corrente]
        
        # Calcola la nuova posizione
        nuovo_x = giocatore.x + dx
        nuovo_y = giocatore.y + dy
        
        # Verifica che la nuova posizione sia valida
        if not (0 <= nuovo_x < mappa.larghezza and 0 <= nuovo_y < mappa.altezza):
            return {"successo": False, "messaggio": "Posizione fuori dai limiti della mappa", "cambio_mappa": False}
        
        # Verifica se c'è un muro
        if mappa.griglia[nuovo_y][nuovo_x] != 0:  # Assumendo che 0 sia lo spazio vuoto
            return {"successo": False, "messaggio": "C'è un muro in quella direzione", "cambio_mappa": False}
        
        # Verifica se c'è un oggetto bloccante
        if (nuovo_x, nuovo_y) in mappa.oggetti:
            oggetto = mappa.oggetti[(nuovo_x, nuovo_y)]
            # Verifica se l'oggetto è bloccante
            if hasattr(oggetto, 'bloccante') and oggetto.bloccante:
                return {"successo": False, "messaggio": f"C'è un {oggetto.nome} bloccante", "cambio_mappa": False}
        
        # Verifica se c'è un NPC (che sono sempre bloccanti)
        if (nuovo_x, nuovo_y) in mappa.npg:
            npg = mappa.npg[(nuovo_x, nuovo_y)]
            return {"successo": False, "messaggio": f"{npg.nome} ti blocca il passaggio", "cambio_mappa": False}
        
        # Verifica se c'è una porta
        porta_dest = None
        if (nuovo_x, nuovo_y) in mappa.porte:
            porta_dest = mappa.porte[(nuovo_x, nuovo_y)]
        
        # Aggiorna la posizione del giocatore
        giocatore.x = nuovo_x
        giocatore.y = nuovo_y
        
        # Se c'è una porta, cambia mappa
        if porta_dest:
            mappa_dest, x_dest, y_dest = porta_dest
            # Cambia mappa
            risultato = self.cambia_mappa_giocatore(giocatore, mappa_dest, x_dest, y_dest)
            if risultato["successo"]:
                return {"successo": True, "messaggio": f"Sei entrato in {mappa_dest}", "cambio_mappa": True}
            else:
                return {"successo": True, "messaggio": risultato["messaggio"], "cambio_mappa": False}
        
        return {"successo": True, "messaggio": "Ti sei spostato", "cambio_mappa": False}
    
    def cambia_mappa_giocatore(self, giocatore, nome_mappa, x=None, y=None):
        """
        Cambia la mappa corrente del giocatore.
        
        Args:
            giocatore (Giocatore): Il giocatore da spostare
            nome_mappa (str): Nome della nuova mappa
            x, y (int, optional): Posizione in cui posizionare il giocatore nella nuova mappa
            
        Returns:
            dict: Risultato dell'operazione con chiavi 'successo' e 'messaggio'
        """
        # Verifica che la mappa esista
        if nome_mappa not in self.mappe:
            return {"successo": False, "messaggio": f"Mappa {nome_mappa} non esistente"}
            
        # Ottieni la nuova mappa
        nuova_mappa = self.mappe[nome_mappa]
        
        # Se x e y non sono specificati, usa la posizione iniziale della mappa
        if x is None or y is None:
            x, y = nuova_mappa.pos_iniziale_giocatore
            
        # Verifica che la posizione sia valida
        if not (0 <= x < nuova_mappa.larghezza and 0 <= y < nuova_mappa.altezza):
            return {"successo": False, "messaggio": f"Posizione ({x}, {y}) fuori dai limiti della mappa {nome_mappa}"}
            
        # Verifica che la posizione non sia un muro
        if nuova_mappa.griglia[y][x] != 0:  # Assumendo che 0 sia lo spazio vuoto
            return {"successo": False, "messaggio": f"Posizione ({x}, {y}) è un muro nella mappa {nome_mappa}"}
            
        # Verifica che la posizione non sia occupata
        if (x, y) in nuova_mappa.oggetti or (x, y) in nuova_mappa.npg:
            return {"successo": False, "messaggio": f"Posizione ({x}, {y}) già occupata nella mappa {nome_mappa}"}
            
        # Aggiorna la mappa e la posizione del giocatore
        giocatore.mappa_corrente = nome_mappa
        giocatore.x = x
        giocatore.y = y
        
        # Imposta la nuova mappa come mappa attuale
        self.imposta_mappa_attuale(nome_mappa)
        
        return {"successo": True, "messaggio": f"Sei entrato in {nome_mappa}"}
    
    def ottieni_info_posizione(self, x, y, mappa=None):
        """
        Ottiene informazioni su cosa si trova in una posizione specifica.
        
        Args:
            x, y (int): Coordinate da controllare
            mappa (Mappa, optional): Mappa in cui cercare. Se None, usa la mappa attuale.
            
        Returns:
            dict: Informazioni sulla posizione con chiavi 'tipo', 'oggetto' e 'messaggio'
        """
        # Se non è specificata una mappa, usa la mappa attuale
        mappa = mappa or self.mappa_attuale
        if not mappa:
            return {"tipo": "errore", "oggetto": None, "messaggio": "Nessuna mappa attiva"}
            
        # Verifica che la posizione sia valida
        if not (0 <= x < mappa.larghezza and 0 <= y < mappa.altezza):
            return {"tipo": "fuori_mappa", "oggetto": None, "messaggio": "Posizione fuori dai limiti della mappa"}
            
        # Verifica se c'è un muro
        if mappa.griglia[y][x] != 0:  # Assumendo che 0 sia lo spazio vuoto
            return {"tipo": "muro", "oggetto": None, "messaggio": "C'è un muro qui"}
            
        # Verifica se c'è un oggetto
        if (x, y) in mappa.oggetti:
            oggetto = mappa.oggetti[(x, y)]
            return {"tipo": "oggetto", "oggetto": oggetto, "messaggio": f"C'è {oggetto.nome} qui"}
            
        # Verifica se c'è un NPC
        if (x, y) in mappa.npg:
            npg = mappa.npg[(x, y)]
            return {"tipo": "npg", "oggetto": npg, "messaggio": f"C'è {npg.nome} qui"}
            
        # Verifica se c'è una porta
        if (x, y) in mappa.porte:
            porta_dest = mappa.porte[(x, y)]
            mappa_dest = porta_dest[0]
            return {"tipo": "porta", "oggetto": porta_dest, "messaggio": f"C'è una porta verso {mappa_dest} qui"}
            
        # Se non c'è nulla
        return {"tipo": "vuoto", "oggetto": None, "messaggio": "Non c'è nulla qui"}
    
    def to_dict(self):
        """
        Converte il gestore mappe in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione del gestore mappe in formato dizionario
        """
        # Lista delle mappe serializzate
        mappe_dict = {}
        for nome, mappa in self.mappe.items():
            mappe_dict[nome] = mappa.to_dict()
            
        return {
            "mappe": mappe_dict,
            "mappa_attuale": self.mappa_attuale.nome if self.mappa_attuale else None,
            "versione": SAVE_FORMAT_VERSION
        }
        
    def from_dict(self, data):
        """
        Carica lo stato del gestore mappe da un dizionario.
        
        Args:
            data (dict): Dizionario contenente lo stato del gestore mappe
            
        Returns:
            bool: True se il caricamento è avvenuto con successo, False altrimenti
        """
        try:
            from world.mappa import Mappa
            
            # Carica le mappe dal dizionario
            mappe_data = data.get("mappe", {})
            self.mappe = {}
            
            for nome_mappa, mappa_dict in mappe_data.items():
                self.mappe[nome_mappa] = Mappa.from_dict(mappa_dict)
                
                # Carica gli oggetti interattivi per questa mappa
                self.carica_oggetti_interattivi_da_json(self.mappe[nome_mappa], nome_mappa)
            
            # Imposta la mappa attuale
            mappa_attuale_nome = data.get("mappa_attuale")
            if mappa_attuale_nome and mappa_attuale_nome in self.mappe:
                self.mappa_attuale = self.mappe[mappa_attuale_nome]
            elif self.mappe:
                # Se non c'è una mappa attuale, imposta la prima disponibile
                self.mappa_attuale = next(iter(self.mappe.values()))
            
            return True
        except Exception as e:
            print(f"Errore durante il caricamento delle mappe: {e}")
            return False
    
    def salva(self, percorso_file="mappe_salvataggio.json"):
        """
        Salva lo stato completo di tutte le mappe e relativi oggetti interattivi.
        
        Args:
            percorso_file (str): Percorso del file in cui salvare i dati
            
        Returns:
            bool: True se il salvataggio è avvenuto con successo, False altrimenti
        """
        logger = logging.getLogger("gioco_rpg")
        
        try:
            # Crea il dizionario di salvataggio
            dati_salvataggio = self.to_dict()
            
            # Determina il percorso di salvataggio
            save_path = get_save_path(percorso_file)
            
            # Crea un backup se il file esiste già
            if os.path.exists(save_path):
                backup_success = create_backup(save_path)
                if backup_success:
                    logger.info(f"Backup creato per {save_path}")
                else:
                    logger.warning(f"Impossibile creare backup per {save_path}")
            
            # Assicura che la directory esista
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Salva il file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(dati_salvataggio, f, indent=4, ensure_ascii=False)
            
            # Salva anche gli oggetti interattivi
            oggetti_salvati = self.salva_oggetti_interattivi_modificati()
            
            logger.info(f"Mappe salvate con successo in {save_path}")
            return True
        except Exception as e:
            import traceback
            logging.getLogger("gioco_rpg").error(f"Errore durante il salvataggio delle mappe: {e}")
            logging.getLogger("gioco_rpg").error(traceback.format_exc())
            return False
            
    def salva_oggetti_interattivi_modificati(self):
        """
        Salva gli oggetti interattivi modificati nel sistema JSON.
        
        Returns:
            bool: True se il salvataggio è avvenuto con successo, False altrimenti
        """
        logger = logging.getLogger("gioco_rpg")
        
        try:
            # Ottieni tutti gli oggetti interattivi da tutte le mappe
            oggetti_per_mappa = {}
            oggetti_interattivi = []
            
            for nome_mappa, mappa in self.mappe.items():
                oggetti_per_mappa[nome_mappa] = []
                
                for pos, oggetto in mappa.oggetti.items():
                    # Aggiungi l'oggetto alla lista generale per il salvataggio
                    oggetti_interattivi.append(oggetto)
                    
                    # Aggiungi la posizione alla lista per questa mappa
                    oggetti_per_mappa[nome_mappa].append({
                        "nome": oggetto.nome,
                        "posizione": list(pos)  # Converti la tupla in lista per la serializzazione JSON
                    })
            
            # Salva le posizioni degli oggetti per ogni mappa
            for nome_mappa, oggetti in oggetti_per_mappa.items():
                self.data_manager.save_map_objects(nome_mappa, oggetti)
                logger.info(f"Salvate posizioni di {len(oggetti)} oggetti per la mappa {nome_mappa}")
            
            # Salva gli oggetti interattivi stessi
            oggetti_salvati = 0
            oggetti_con_errori = 0
            
            for oggetto in oggetti_interattivi:
                try:
                    oggetto.salva_su_json()
                    oggetti_salvati += 1
                except Exception as e:
                    logger.error(f"Errore nel salvataggio dell'oggetto {oggetto.nome}: {e}")
                    oggetti_con_errori += 1
            
            if oggetti_con_errori > 0:
                logger.warning(f"Salvati {oggetti_salvati} oggetti con {oggetti_con_errori} errori")
            else:
                logger.info(f"Salvati con successo {oggetti_salvati} oggetti interattivi")
                
            return oggetti_con_errori == 0
        except Exception as e:
            import traceback
            logging.getLogger("gioco_rpg").error(f"Errore durante il salvataggio degli oggetti interattivi: {e}")
            logging.getLogger("gioco_rpg").error(traceback.format_exc())
            return False

    def carica(self, percorso_file="mappe_salvataggio.json"):
        """
        Carica lo stato completo di tutte le mappe e relativi oggetti interattivi.
        
        Args:
            percorso_file (str): Percorso del file da cui caricare i dati
            
        Returns:
            bool: True se il caricamento è avvenuto con successo, False altrimenti
        """
        logger = logging.getLogger("gioco_rpg")
        
        try:
            # Determina il percorso di caricamento
            save_path = get_save_path(percorso_file)
            
            # Verifica che il file esista
            if not os.path.exists(save_path):
                logger.error(f"File di salvataggio non trovato: {save_path}")
                return False
            
            # Carica il file
            with open(save_path, 'r', encoding='utf-8') as f:
                dati_salvati = json.load(f)
            
            # Verifica la versione
            versione_salvata = dati_salvati.get("versione", "1.0")
            if versione_salvata != SAVE_FORMAT_VERSION:
                logger.warning(f"Versione del salvataggio ({versione_salvata}) diversa da quella corrente ({SAVE_FORMAT_VERSION})")
            
            # Carica le mappe dal dizionario
            mappe_data = dati_salvati.get("mappe", {})
            self.mappe = {}
            
            for nome_mappa, mappa_dict in mappe_data.items():
                try:
                    # Utilizziamo il metodo from_dict già esistente nella classe Mappa
                    self.mappe[nome_mappa] = Mappa.from_dict(mappa_dict)
                    
                    # Carica gli oggetti interattivi per questa mappa
                    self.carica_oggetti_interattivi_da_json(self.mappe[nome_mappa], nome_mappa)
                except Exception as e:
                    logger.error(f"Errore nel caricamento della mappa {nome_mappa}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # Imposta la mappa attuale
            mappa_attuale_nome = dati_salvati.get("mappa_attuale")
            if mappa_attuale_nome and mappa_attuale_nome in self.mappe:
                self.mappa_attuale = self.mappe[mappa_attuale_nome]
                logger.info(f"Mappa attuale impostata a: {mappa_attuale_nome}")
            elif self.mappe:
                # Se non c'è una mappa attuale, imposta la prima disponibile
                self.mappa_attuale = next(iter(self.mappe.values()))
                logger.warning(f"Mappa attuale non specificata, impostata a: {self.mappa_attuale.nome}")
            else:
                logger.error("Nessuna mappa caricata")
                return False
                
            logger.info(f"Mappe caricate con successo da {save_path}")
            return True
        except Exception as e:
            import traceback
            logging.getLogger("gioco_rpg").error(f"Errore durante il caricamento delle mappe: {e}")
            logging.getLogger("gioco_rpg").error(traceback.format_exc())
            return False

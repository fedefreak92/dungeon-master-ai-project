import os
import json
import logging
from pathlib import Path

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Percorso base per i dati
DATA_DIR = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))

class DataManager:
    """
    Gestore per i dati statici del gioco.
    Carica i dati dai file JSON nella directory 'data'.
    """
    
    _instance = None
    _data_cache = {}
    
    def __new__(cls):
        """Implementazione singleton per avere una sola istanza del gestore dati."""
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inizializza le directory per i dati."""
        logger.info(f"Inizializzazione DataManager - Directory base: {DATA_DIR.absolute()}")
        logger.info(f"Directory base esiste: {DATA_DIR.exists()}")
        
        self._data_paths = {
            "classi": DATA_DIR / "classes",
            "tutorials": DATA_DIR / "tutorials",
            "achievements": DATA_DIR / "achievements",
            "oggetti": DATA_DIR / "items",
            "npc": DATA_DIR / "npc",
            "assets_info": DATA_DIR / "assets_info",
            "mostri": DATA_DIR / "monsters",
            "mappe": DATA_DIR / "mappe"
        }
        
        # Debug di tutti i percorsi di dati
        logger.info("Elenco percorsi dati:")
        for data_type, path in self._data_paths.items():
            exists = path.exists()
            logger.info(f"- {data_type}: {path.absolute()} (esiste: {exists})")
            if exists:
                files = list(path.glob("*.json"))
                logger.info(f"  File trovati: {[f.name for f in files]}")
            else:
                logger.warning(f"Directory dati non trovata: {path}")
                
                # Prova a creare la directory se non esiste
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Directory {path} creata")
                except Exception as e:
                    logger.error(f"Impossibile creare directory {path}: {str(e)}")
    
    def load_data(self, data_type, file_name=None, reload=False):
        """
        Carica i dati da un file JSON.
        
        Args:
            data_type (str): Tipo di dati da caricare (classi, tutorials, ecc.)
            file_name (str, optional): Nome del file specifico. Se None, usa il valore predefinito.
            reload (bool, optional): Se True, ricarica i dati anche se già in cache.
            
        Returns:
            dict/list: I dati caricati dal file JSON.
        """
        if data_type not in self._data_paths:
            logger.error(f"Tipo di dati non valido: {data_type}")
            return {}
        
        # Determina il nome del file predefinito se non specificato
        if file_name is None:
            file_name = f"{data_type}.json"
        
        # Chiave per la cache
        cache_key = f"{data_type}/{file_name}"
        
        # Se i dati sono già in cache e non è richiesto il ricaricamento, restituiscili
        if not reload and cache_key in self._data_cache:
            logger.info(f"Ritorno dati dalla cache per {cache_key}")
            return self._data_cache[cache_key]
        
        # Percorso completo del file
        file_path = self._data_paths[data_type] / file_name
        logger.info(f"Percorso completo per {data_type}/{file_name}: {file_path.absolute()}")
        logger.info(f"File esiste: {file_path.exists()}")
        
        try:
            if not file_path.exists():
                logger.error(f"File non trovato: {file_path}")
                logger.info(f"Controllo directory {self._data_paths[data_type]}: esiste={self._data_paths[data_type].exists()}")
                if self._data_paths[data_type].exists():
                    logger.info(f"Contenuto directory {self._data_paths[data_type]}: {list(self._data_paths[data_type].glob('*.json'))}")
                return {}
            
            logger.info(f"Apertura file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Letti {len(content)} byte da {file_path}")
                
                # Log dei primi 100 caratteri per debug
                if len(content) > 0:
                    logger.info(f"Primi 100 caratteri: {content[:100].replace(chr(10), '\\n')}")
                else:
                    logger.warning(f"File {file_path} è vuoto")
                    return {}
                    
                try:
                    data = json.loads(content)
                    logger.info(f"JSON caricato con successo: tipo={type(data)}, lunghezza={len(data) if isinstance(data, (dict, list)) else 'N/A'}")
                    self._data_cache[cache_key] = data
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"Errore nel parsing JSON di {file_path}: {str(e)}")
                    logger.error(f"Posizione errore: linea {e.lineno}, colonna {e.colno}")
                    logger.error(f"Contenuto problematico: {content[max(0, e.pos-20):min(len(content), e.pos+20)]}")
                    return {}
        except Exception as e:
            logger.error(f"Errore nel caricamento del file {file_path}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def get_all_data_files(self, data_type):
        """
        Restituisce tutti i file di dati di un certo tipo.
        
        Args:
            data_type (str): Tipo di dati da cercare.
            
        Returns:
            list: Lista di nomi dei file disponibili.
        """
        if data_type not in self._data_paths:
            logger.error(f"Tipo di dati non valido: {data_type}")
            return []
        
        path = self._data_paths[data_type]
        if not path.exists():
            return []
        
        return [f.name for f in path.glob("*.json")]
    
    def get_classes(self):
        """Ottieni informazioni sulle classi di personaggio."""
        logger.info("Caricamento classi da data/classes/classes.json")
        logger.info(f"Directory corrente: {os.getcwd()}")
        
        # Prima prova a caricare dalla cache o con il metodo standard
        classi = self.load_data("classi", "classes.json", reload=True)  # Forza il reload
        logger.info(f"Risultato load_data: {classi if classi else 'vuoto'}")
        
        # Se non ci sono classi o è vuoto, prova a caricare direttamente dal file
        if not classi or len(classi) == 0:
            logger.warning("Classi non trovate, provo percorsi alternativi")
            
            # Elenco di percorsi possibili per il file classes.json
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "classes", "classes.json"),  # ../data/classes/classes.json
                os.path.join("data", "classes", "classes.json"),  # data/classes/classes.json relativo alla directory di lavoro
                os.path.join(".", "data", "classes", "classes.json"),  # ./data/classes/classes.json
                # Prova anche la directory 'classi' (alternativa italiana a 'classes')
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "classi", "classes.json"),  # ../data/classi/classes.json
                os.path.join("data", "classi", "classes.json"),  # data/classi/classes.json
                os.path.join(".", "data", "classi", "classes.json"),  # ./data/classi/classes.json
                # Prova con nomi file alternativi
                os.path.join("data", "classi", "classi.json"),  # data/classi/classi.json
                os.path.join("data", "classes", "classi.json")   # data/classes/classi.json
            ]
            
            # Log di tutti i possibili percorsi
            for idx, path in enumerate(possible_paths):
                abs_path = os.path.abspath(path)
                exists = os.path.exists(abs_path)
                logger.info(f"Path {idx}: {abs_path} - Esiste: {exists}")
            
            for file_path in possible_paths:
                try:
                    abs_path = os.path.abspath(file_path)
                    if os.path.exists(abs_path):
                        logger.info(f"Trovato file classi in: {abs_path}")
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            logger.info(f"Contenuto file (primi 100 caratteri): {content[:100]}")
                            classi = json.loads(content)
                            logger.info(f"Classi caricate direttamente: {list(classi.keys())}")
                            
                            # Aggiungi alla cache
                            self._data_cache["classi/classes.json"] = classi
                            
                            # Interrompi dopo aver trovato un file valido
                            break
                    else:
                        logger.debug(f"File classi non trovato in: {abs_path}")
                except Exception as e:
                    logger.error(f"Errore nel caricamento da {file_path}: {str(e)}")
                    logger.exception("Traceback completo:")
        else:
            logger.info(f"Classi caricate dalla cache: {list(classi.keys())}")
            
        # Aggiungi il campo nome a ciascuna classe
        if classi and isinstance(classi, dict):
            for classe_key, classe_data in classi.items():
                if isinstance(classe_data, dict) and "nome" not in classe_data:
                    classi[classe_key]["nome"] = classe_key.capitalize()
                    logger.info(f"Aggiunto nome mancante per classe {classe_key}")
        
        # Se ancora nessun risultato, restituisci un dizionario vuoto
        if not classi:
            logger.error("Impossibile caricare le classi da qualsiasi percorso")
            return {}
                
        logger.info(f"Ritorno classi: {list(classi.keys())}")
        return classi
    
    def get_tutorials(self):
        """Ottieni i tutorial del gioco."""
        return self.load_data("tutorials")
    
    def get_achievements(self):
        """Ottieni gli achievement del gioco."""
        return self.load_data("achievements")
    
    def get_items(self, category=None):
        """
        Ottieni gli oggetti del gioco, opzionalmente filtrati per categoria.
        
        Args:
            category (str, optional): Categoria di oggetti (armi, armature, ecc.)
            
        Returns:
            list: Lista di oggetti.
        """
        if category:
            file_name = f"{category}.json"
            return self.load_data("oggetti", file_name)
        else:
            # Carica tutti gli oggetti da tutti i file
            items = []
            for file_name in self.get_all_data_files("oggetti"):
                items_data = self.load_data("oggetti", file_name)
                if isinstance(items_data, list):
                    items.extend(items_data)
                elif isinstance(items_data, dict):
                    # Se è un dizionario, aggiungi gli oggetti con la categoria
                    category = file_name.replace(".json", "")
                    for item_id, item in items_data.items():
                        item_copy = item.copy()
                        item_copy["id"] = item_id
                        item_copy["categoria"] = category
                        items.append(item_copy)
            return items
    
    def get_asset_info(self, asset_type=None):
        """
        Ottieni informazioni sugli asset grafici.
        
        Args:
            asset_type (str, optional): Tipo di asset (personaggio, ambiente, ecc.)
            
        Returns:
            dict: Informazioni sugli asset.
        """
        file_name = f"{asset_type}.json" if asset_type else "assets.json"
        return self.load_data("assets_info", file_name)
    
    def get_npc_data(self, nome_npc=None):
        """
        Ottieni dati di uno o tutti gli NPC.
        
        Args:
            nome_npc (str, optional): Nome dello specifico NPC richiesto.
            
        Returns:
            dict: Dati dell'NPC o di tutti gli NPC.
        """
        npcs = self.load_data("npc", "npcs.json")
        if nome_npc:
            return npcs.get(nome_npc, {})
        return npcs
    
    def get_npc_conversation(self, nome_npc, stato="inizio"):
        """
        Ottieni la conversazione di un NPC per lo stato specificato.
        
        Args:
            nome_npc (str): Nome dell'NPC.
            stato (str, optional): Stato della conversazione.
            
        Returns:
            dict: Dati della conversazione per lo stato specificato.
        """
        conversations = self.load_data("npc", "conversations.json")
        npc_conversations = conversations.get(nome_npc)
        
        # Se non ci sono conversazioni specifiche per questo NPC, usa quelle di default
        if not npc_conversations:
            npc_conversations = conversations.get("default", {})
            
        # Restituisci la conversazione per lo stato specificato o quella iniziale
        return npc_conversations.get(stato, npc_conversations.get("inizio", {}))
    
    def get_all_npc_conversations(self, nome_npc):
        """
        Ottieni tutte le conversazioni di un NPC.
        
        Args:
            nome_npc (str): Nome dell'NPC.
            
        Returns:
            dict: Tutte le conversazioni dell'NPC.
        """
        conversations = self.load_data("npc", "conversations.json")
        return conversations.get(nome_npc, conversations.get("default", {}))
    
    def get_interactive_objects(self, nome_oggetto=None):
        """
        Ottieni dati degli oggetti interattivi.
        
        Args:
            nome_oggetto (str, optional): Nome dello specifico oggetto richiesto.
            
        Returns:
            dict or list: Dati dell'oggetto specifico o lista di tutti gli oggetti interattivi.
        """
        oggetti = self.load_data("oggetti", "oggetti_interattivi.json")
        if nome_oggetto:
            for oggetto in oggetti:
                if oggetto.get("nome") == nome_oggetto:
                    return oggetto
            return {}
        return oggetti
    
    def save_interactive_objects(self, oggetti):
        """
        Salva i dati degli oggetti interattivi.
        
        Args:
            oggetti (list): Lista di oggetti interattivi da salvare.
            
        Returns:
            bool: True se il salvataggio è riuscito, False altrimenti.
        """
        return self.save_data("oggetti", oggetti, "oggetti_interattivi.json")
    
    def get_map_objects(self, nome_mappa):
        """
        Ottieni gli oggetti interattivi associati a una mappa specifica.
        
        Args:
            nome_mappa (str): Nome della mappa.
            
        Returns:
            list: Lista di oggetti interattivi presenti nella mappa.
        """
        mappe_oggetti = self.load_data("oggetti", "mappe_oggetti.json")
        return mappe_oggetti.get(nome_mappa, [])
    
    def save_map_objects(self, nome_mappa, oggetti_posizioni):
        """
        Salva gli oggetti interattivi associati a una mappa.
        
        Args:
            nome_mappa (str): Nome della mappa.
            oggetti_posizioni (list): Lista di oggetti interattivi con le loro posizioni.
            
        Returns:
            bool: True se il salvataggio è riuscito, False altrimenti.
        """
        mappe_oggetti = self.load_data("oggetti", "mappe_oggetti.json")
        mappe_oggetti[nome_mappa] = oggetti_posizioni
        return self.save_data("oggetti", mappe_oggetti, "mappe_oggetti.json")
    
    def save_data(self, data_type, data, file_name=None):
        """
        Salva i dati in un file JSON.
        
        Args:
            data_type (str): Tipo di dati da salvare.
            data (dict/list): Dati da salvare.
            file_name (str, optional): Nome del file. Se None, usa il valore predefinito.
            
        Returns:
            bool: True se il salvataggio è riuscito, False altrimenti.
        """
        if data_type not in self._data_paths:
            logger.error(f"Tipo di dati non valido: {data_type}")
            return False
        
        # Determina il nome del file predefinito se non specificato
        if file_name is None:
            file_name = f"{data_type}.json"
        
        # Percorso completo del file
        file_path = self._data_paths[data_type] / file_name
        
        try:
            # Assicurati che la directory esista
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Aggiorna la cache
            cache_key = f"{data_type}/{file_name}"
            self._data_cache[cache_key] = data
            
            return True
        except Exception as e:
            logger.error(f"Errore nel salvataggio del file {file_path}: {str(e)}")
            return False
    
    def get_monsters(self, monster_id=None):
        """
        Ottieni dati di uno o tutti i mostri.
        
        Args:
            monster_id (str, optional): ID dello specifico mostro richiesto.
            
        Returns:
            dict: Dati del mostro o di tutti i mostri.
        """
        mostri = self.load_data("mostri", "monsters.json")
        if monster_id:
            return mostri.get(monster_id, {})
        return mostri
    
    def get_map_data(self, map_id=None):
        """
        Ottieni dati di una o tutte le mappe.
        
        Args:
            map_id (str, optional): ID della specifica mappa richiesta.
            
        Returns:
            dict: Dati della mappa o di tutte le mappe.
        """
        mappe = self.load_data("mappe", "maps.json")
        if map_id:
            return mappe.get(map_id, {})
        return mappe

# Istanza globale per facile accesso
data_manager = DataManager()

def get_data_manager():
    """
    Ottieni l'istanza del gestore dati.
    
    Returns:
        DataManager: L'istanza singleton del gestore dati.
    """
    return data_manager 
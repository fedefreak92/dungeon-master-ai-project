import os
import pathlib
import logging
from pathlib import Path

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definizione delle cartelle principali
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = BASE_DIR / "salvataggi"
SESSIONS_DIR = BASE_DIR / "sessioni"
BACKUPS_DIR = BASE_DIR / "backup"

# Assicurati che tutte le directory esistano
for directory in [DATA_DIR, SAVE_DIR, SESSIONS_DIR, BACKUPS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Costanti per i percorsi di salvataggio
DEFAULT_SAVE_PATH = SAVE_DIR / "salvataggio.json"
DEFAULT_MAP_SAVE_PATH = SAVE_DIR / "mappe_salvataggio.json"
DEFAULT_SESSION_PREFIX = "sessione_"
DEFAULT_BACKUP_PREFIX = "backup_"

# Versione corrente del formato di salvataggio
SAVE_FORMAT_VERSION = "1.0.0"

def get_save_path(filename=None):
    """
    Ottiene il percorso completo per un file di salvataggio.
    
    Args:
        filename (str, optional): Nome del file di salvataggio
        
    Returns:
        Path: Percorso completo del file di salvataggio
    """
    if not filename:
        return DEFAULT_SAVE_PATH
    
    # Se il nome del file non ha estensione .json, aggiungila
    if not filename.lower().endswith('.json'):
        filename += '.json'
    
    return SAVE_DIR / filename

def get_standardized_paths(filename=None):
    """
    Ottiene tutti i percorsi standardizzati per un file.
    
    Args:
        filename (str, optional): Nome del file
        
    Returns:
        dict: Dizionario con tutti i percorsi standardizzati
    """
    # Normalizza il nome file
    if filename and not filename.lower().endswith('.json'):
        filename += '.json'
    
    base_filename = filename or "salvataggio.json"
    map_filename = "mappe_" + base_filename if filename else "mappe_salvataggio.json"
    
    return {
        "save": SAVE_DIR / base_filename,
        "maps": SAVE_DIR / map_filename,
        "backup_dir": BACKUPS_DIR,
        "data_dir": DATA_DIR,
        "sessions_dir": SESSIONS_DIR
    }

def get_backup_path(original_filename):
    """
    Genera un percorso per il backup di un file.
    
    Args:
        original_filename (str): Nome del file originale
        
    Returns:
        Path: Percorso completo del file di backup
    """
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(original_filename)
    
    # Rimuovi estensione
    name, ext = os.path.splitext(filename)
    backup_name = f"{DEFAULT_BACKUP_PREFIX}{name}_{timestamp}{ext}"
    
    return BACKUPS_DIR / backup_name

def create_backup(filepath):
    """
    Crea un backup del file specificato.
    
    Args:
        filepath (str o Path): Percorso del file da copiare
        
    Returns:
        Path: Percorso del file di backup, None se si è verificato un errore
    """
    import shutil
    
    source_path = Path(filepath)
    if not source_path.exists():
        logger.error(f"Impossibile creare backup: il file {filepath} non esiste")
        return None
    
    backup_path = get_backup_path(source_path)
    
    try:
        # Assicurati che la directory di backup esista
        backup_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Copia il file
        shutil.copy2(source_path, backup_path)
        logger.info(f"Backup creato: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Errore durante la creazione del backup: {e}")
        return None

def get_session_path(session_id):
    """
    Ottiene il percorso completo per un file di sessione.
    
    Args:
        session_id (str): ID della sessione
        
    Returns:
        Path: Percorso completo del file di sessione
    """
    return SESSIONS_DIR / f"{DEFAULT_SESSION_PREFIX}{session_id}.pickle"

def list_save_files():
    """
    Elenca tutti i file di salvataggio disponibili.
    
    Returns:
        list: Lista di nomi di file di salvataggio
    """
    return [f.name for f in SAVE_DIR.glob("*.json")]

def list_backup_files():
    """
    Elenca tutti i file di backup disponibili.
    
    Returns:
        list: Lista di nomi di file di backup
    """
    return [f.name for f in BACKUPS_DIR.glob("*.json")]

def validate_save_data(data):
    """
    Valida il contenuto di un file di salvataggio.
    
    Args:
        data (dict): Dati di salvataggio da validare
        
    Returns:
        tuple: (validità, messaggio di errore)
    """
    if not data:
        return False, "File di salvataggio vuoto o non valido"
    
    # Verifica campi principali
    campi_obbligatori = ["giocatore", "versione_gioco"]
    for campo in campi_obbligatori:
        if campo not in data:
            return False, f"Campo '{campo}' mancante nel salvataggio"
    
    # Verifica dati giocatore
    giocatore = data.get("giocatore", {})
    if not isinstance(giocatore, dict):
        return False, "I dati del giocatore non sono validi"
        
    campi_giocatore = ["nome", "classe", "hp", "hp_max"]
    for campo in campi_giocatore:
        if campo not in giocatore:
            return False, f"Campo '{campo}' mancante nei dati del giocatore"
    
    # Verifica versione
    versione = data.get("versione_gioco", "sconosciuta")
    if versione != SAVE_FORMAT_VERSION:
        logger.warning(f"Versione del salvataggio ({versione}) diversa da quella corrente ({SAVE_FORMAT_VERSION})")
        # Non blocca il caricamento, solo un avviso
    
    return True, ""

def migrate_save_data(data):
    """
    Migra i dati alla versione corrente se necessario.
    
    Args:
        data (dict): Dati del salvataggio
        
    Returns:
        dict: Dati migrati alla versione corrente
    """
    versione_origine = data.get("versione_gioco", "0.0.0")
    
    # Se già nella versione corrente, non fare nulla
    if versione_origine == SAVE_FORMAT_VERSION:
        return data
        
    logger.info(f"Migrazione dati da versione {versione_origine} a {SAVE_FORMAT_VERSION}")
    
    # Migrazione dalla 0.9.0 alla 1.0.0
    if versione_origine == "0.9.0" and SAVE_FORMAT_VERSION == "1.0.0":
        # Aggiorna formato
        data["versione_gioco"] = "1.0.0"
        
        # Aggiungi eventuali campi mancanti
        if "giocatore" in data and isinstance(data["giocatore"], dict):
            giocatore = data["giocatore"]
            if "accessori" not in giocatore:
                giocatore["accessori"] = []
                
    # Altre migrazioni da aggiungere in futuro
    
    return data

def delete_save_file(filename):
    """
    Elimina un file di salvataggio.
    
    Args:
        filename (str): Nome del file da eliminare
        
    Returns:
        bool: True se l'eliminazione è riuscita, False altrimenti
    """
    file_path = get_save_path(filename)
    try:
        if file_path.exists():
            # Prima crea un backup
            create_backup(file_path)
            # Poi elimina
            file_path.unlink()
            logger.info(f"File di salvataggio eliminato: {file_path}")
            return True
        else:
            logger.warning(f"File di salvataggio non trovato: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Errore durante l'eliminazione del file {file_path}: {e}")
        return False

def clean_old_backups(max_backups=20):
    """
    Rimuove i backup più vecchi se ce ne sono troppi.
    
    Args:
        max_backups (int): Numero massimo di backup da mantenere
    """
    backup_files = list(BACKUPS_DIR.glob("*.json"))
    
    # Ordina per data di modifica (più vecchi prima)
    backup_files.sort(key=lambda f: f.stat().st_mtime)
    
    # Rimuovi i backup più vecchi se necessario
    if len(backup_files) > max_backups:
        files_to_remove = backup_files[:(len(backup_files) - max_backups)]
        for file in files_to_remove:
            try:
                file.unlink()
                logger.info(f"Rimosso backup vecchio: {file.name}")
            except Exception as e:
                logger.error(f"Errore durante la rimozione del backup {file.name}: {e}") 
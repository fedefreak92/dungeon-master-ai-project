from core.game import Game
from core.io_interface import GameIO


class GameIOWeb(GameIO):
    """Gestore di input/output del gioco specifico per l'interfaccia web"""
    
    def __init__(self):
        self.buffer = []
        self.last_input = ""
    
    def mostra_messaggio(self, testo: str):
        """Memorizza un messaggio narrativo nel buffer"""
        self.buffer.append({"tipo": "narrativo", "testo": testo})
    
    def messaggio_sistema(self, testo: str):
        """Memorizza un messaggio di sistema nel buffer"""
        self.buffer.append({"tipo": "sistema", "testo": testo})
    
    def messaggio_errore(self, testo: str):
        """Memorizza un messaggio di errore nel buffer"""
        self.buffer.append({"tipo": "errore", "testo": testo})
    
    def richiedi_input(self, prompt: str = "") -> str:
        """Restituisce l'ultimo input memorizzato e memorizza il prompt"""
        self.buffer.append({"tipo": "prompt", "testo": prompt})
        return self.last_input
    
    def set_input(self, input_text: str):
        """Imposta l'input che verrà restituito alla prossima chiamata di richiedi_input"""
        self.last_input = input_text
    
    def get_output(self) -> list:
        """Restituisce tutto l'output accumulato come una lista di dizionari"""
        return self.buffer
    
    def get_output_text(self) -> str:
        """Restituisce tutto l'output accumulato come una stringa"""
        return "\n".join([msg["testo"] for msg in self.buffer])
    
    def clear(self):
        """Pulisce il buffer"""
        self.buffer = []


class StatoGioco:
    """
    Classe che incapsula tutto lo stato del gioco in un unico oggetto
    per facilitare la serializzazione e la gestione dello stato tra richieste HTTP
    """
    
    def __init__(self, giocatore, stato_iniziale):
        """
        Inizializza un nuovo stato di gioco
        
        Args:
            giocatore: L'oggetto giocatore
            stato_iniziale: Lo stato iniziale del gioco (es. TavernaState)
        """
        self.game = Game(giocatore, stato_iniziale)
        self.io_buffer = GameIOWeb()
        self.game.io = self.io_buffer
        self.ultimo_output = ""
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di StatoGioco a partire da un dizionario di dati
        
        Args:
            data (dict): Dizionario contenente i dati serializzati del gioco
            
        Returns:
            StatoGioco: Nuova istanza di StatoGioco costruita dai dati
        """
        from core.game import Game
        from entities.giocatore import Giocatore

        # Crea il giocatore dai dati serializzati
        giocatore = Giocatore.from_dict(data["giocatore"])
        
        # Crea un'istanza di Game temporanea
        gioco = Game(giocatore, None, e_temporaneo=True)
        gioco.carica()  # carica lo stato del gioco
        
        # Crea l'istanza di StatoGioco
        istanza = cls(giocatore, gioco.stato_corrente())
        istanza.game = gioco
        istanza.io_buffer = GameIOWeb()
        istanza.game.io = istanza.io_buffer
        istanza.ultimo_output = data.get("output", "")
        
        return istanza
        
    def processa_comando(self, comando: str) -> str:
        """
        Elabora un comando del giocatore e restituisce l'output
        
        Args:
            comando: Il comando da elaborare
            
        Returns:
            L'output generato dall'elaborazione del comando
        """
        # Pulisce il buffer prima di elaborare il comando
        self.io_buffer.clear()
        
        # Imposta l'input che verrà utilizzato
        self.io_buffer.set_input(comando)
        
        # Elabora il comando nello stato corrente
        if self.game.stato_corrente():
            self.game.stato_corrente().esegui(self.game)
        
        # Memorizza e restituisce l'output
        self.ultimo_output = self.io_buffer.get_output_text()
        return self.ultimo_output
    
    def get_stato_attuale(self):
        """
        Restituisce un dizionario con lo stato attuale del gioco
        
        Returns:
            Dizionario con le informazioni sullo stato corrente
        """
        # Ottieni oggetti equipaggiati in formato serializzabile
        arma_equipaggiata = self.game.giocatore.arma.nome if self.game.giocatore.arma else ""
        armatura_equipaggiata = self.game.giocatore.armatura.nome if self.game.giocatore.armatura else ""
        accessori_equipaggiati = [acc.nome for acc in self.game.giocatore.accessori] if self.game.giocatore.accessori else []
        
        # Lista semplificata dell'inventario
        inventario = [obj.nome for obj in self.game.giocatore.inventario]
        
        # Stato corrente come stringa
        stato_nome = type(self.game.stato_corrente()).__name__
        
        # Caratteristiche serializzabili e semplificate
        statistiche = {
            "forza": self.game.giocatore.forza,
            "destrezza": self.game.giocatore.destrezza,
            "costituzione": self.game.giocatore.costituzione,
            "intelligenza": self.game.giocatore.intelligenza,
            "saggezza": self.game.giocatore.saggezza,
            "carisma": self.game.giocatore.carisma,
            "oro": self.game.giocatore.oro,
            "livello": self.game.giocatore.livello,
            "esperienza": self.game.giocatore.esperienza
        }
        
        return {
            "nome": self.game.giocatore.nome,
            "classe": self.game.giocatore.classe,
            "hp": self.game.giocatore.hp,
            "max_hp": self.game.giocatore.hp_max,
            "stato": stato_nome,
            "output": self.ultimo_output,
            "posizione": {
                "mappa": self.game.giocatore.mappa_corrente,
                "x": self.game.giocatore.x,
                "y": self.game.giocatore.y
            },
            "inventario": inventario,
            "equipaggiamento": {
                "arma": arma_equipaggiata,
                "armatura": armatura_equipaggiata,
                "accessori": accessori_equipaggiati
            },
            "statistiche": statistiche
        }
    
    def salva(self, file_path="salvataggio.json"):
        """
        Salva lo stato corrente su file
        
        Args:
            file_path: Percorso del file di salvataggio
            
        Returns:
            bool: True se il salvataggio è avvenuto con successo, False altrimenti
        """
        try:
            # Ottieni stato completo
            stato_corrente = self.get_stato_attuale()
            
            # Ottieni informazioni sulle mappe se disponibili
            mappe_data = {}
            if hasattr(self.game, 'gestore_mappe') and hasattr(self.game.gestore_mappe, 'mappe'):
                for nome_mappa, mappa in self.game.gestore_mappe.mappe.items():
                    if hasattr(mappa, 'to_dict'):
                        mappe_data[nome_mappa] = mappa.to_dict()
            
            # Aggiungi informazioni sulle mappe allo stato
            stato_corrente['mappe'] = mappe_data
            
            # Delega al Game per salvare su file
            risultato = self.game.salva(file_path)
            
            if risultato:
                self.io_buffer.mostra_messaggio(f"Partita salvata con successo su {file_path}")
            else:
                self.io_buffer.mostra_messaggio("Errore durante il salvataggio")
                
            return risultato
        except Exception as e:
            self.io_buffer.mostra_messaggio(f"Errore durante il salvataggio: {e}")
            return False
    
    def carica(self, file_path="salvataggio.json"):
        """
        Carica lo stato da file
        
        Args:
            file_path: Percorso del file di salvataggio
            
        Returns:
            True se il caricamento è riuscito, False altrimenti
        """
        return self.game.carica(file_path)
    
    def ottieni_posizione_giocatore(self):
        """
        Restituisce informazioni sulla posizione corrente del giocatore
        
        Returns:
            Dizionario con le informazioni sulla posizione
        """
        return self.game.ottieni_posizione_giocatore()
    
    def muovi_giocatore(self, direzione):
        """
        Muove il giocatore nella direzione specificata
        
        Args:
            direzione: "nord", "sud", "est", "ovest"
            
        Returns:
            True se il movimento è avvenuto, False altrimenti
        """
        return self.game.muovi_giocatore(direzione) 
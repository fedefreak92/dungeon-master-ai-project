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
    
    def get_output_structured(self) -> list:
        """
        Restituisce l'output strutturato in formato lista di dizionari
        Esempio:
        [
            {"tipo": "sistema", "testo": "Hai aperto il forziere"},
            {"tipo": "narrativo", "testo": "Dentro trovi una pergamena"}
        ]
        """
        return self.buffer
    
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
        self.io_buffer = GameIOWeb()
        self.game = Game(giocatore, stato_iniziale, io_handler=self.io_buffer)
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
        
        # Crea un'istanza io_buffer
        io_buffer = GameIOWeb()
        
        # Crea un'istanza di Game temporanea
        gioco = Game(giocatore, None, io_handler=io_buffer, e_temporaneo=True)
        gioco.carica()  # carica lo stato del gioco
        
        # Crea l'istanza di StatoGioco
        istanza = cls(giocatore, gioco.stato_corrente())
        istanza.game = gioco
        istanza.io_buffer = io_buffer
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
        stato_nome = type(self.game.stato_corrente()).__name__ if self.game.stato_corrente() else "Nessuno"
        
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
            # Importa le classi degli stati instabili
            from states.combattimento import CombattimentoState
            from states.mercato import MercatoState
            from states.dialogo import DialogoState
            from states.prova_abilita import ProvaAbilitaState
            
            # Verifica se il gioco è in uno stato instabile
            if isinstance(self.game.stato_corrente(), (CombattimentoState, ProvaAbilitaState, DialogoState)):
                self.io_buffer.mostra_messaggio("Non puoi salvare durante un combattimento, una prova o un dialogo.")
                return False
                
            # Verifica la fase nel MercatoState (solo durante le vendite non è consentito)
            if isinstance(self.game.stato_corrente(), MercatoState) and hasattr(self.game.stato_corrente(), 'fase'):
                fase_mercato = self.game.stato_corrente().fase
                if fase_mercato in ["vendi_oggetto_lista", "vendi_oggetto_conferma", "compra_pozione"]:
                    self.io_buffer.mostra_messaggio("Non puoi salvare durante una transazione al mercato.")
                    return False
            
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
        """Restituisce informazioni sulla posizione del giocatore"""
        if not hasattr(self, 'game') or not hasattr(self.game, 'giocatore'):
            return None
        
        giocatore = self.game.giocatore
        
        if not giocatore.mappa_corrente:
            return None
        
        mappa_corrente = self.game.gestore_mappe.ottieni_mappa(giocatore.mappa_corrente)
        
        if not mappa_corrente:
            return None
        
        # Usa -1 come raggio per ottenere TUTTI gli elementi sulla mappa
        oggetti_vicini = mappa_corrente.ottieni_oggetti_vicini(giocatore.x, giocatore.y, -1)
        npg_vicini = mappa_corrente.ottieni_npg_vicini(giocatore.x, giocatore.y, -1)
        
        # Converti le chiavi da tuple a stringhe per JSON
        oggetti_json = {}
        for pos, obj in oggetti_vicini.items():
            # Assicurati che ogni oggetto abbia un token
            if not hasattr(obj, 'token') or not obj.token:
                obj.token = 'O'  # Token di default per oggetti
            
            # Converti la posizione in stringa per JSON
            pos_str = f"({pos[0]}, {pos[1]})"
            oggetti_json[pos_str] = {
                "nome": obj.nome,
                "token": obj.token,
                "stato": getattr(obj, 'stato', 'normale')
            }
        
        npg_json = {}
        for pos, npg in npg_vicini.items():
            # Assicurati che ogni NPC abbia un token
            if not hasattr(npg, 'token') or not npg.token:
                npg.token = 'N'  # Token di default per NPC
            
            # Converti la posizione in stringa per JSON
            pos_str = f"({pos[0]}, {pos[1]})"
            npg_json[pos_str] = {
                "nome": npg.nome,
                "token": npg.token
            }
        
        # Crea una risposta completa con tutti i dati necessari
        return {
            "mappa": giocatore.mappa_corrente,
            "nome_mappa": giocatore.mappa_corrente.capitalize(),
            "x": giocatore.x,
            "y": giocatore.y,
            "larghezza": mappa_corrente.larghezza,
            "altezza": mappa_corrente.altezza,
            "griglia": mappa_corrente.griglia,
            "griglia_ascii": mappa_corrente.genera_rappresentazione_ascii((giocatore.x, giocatore.y)),
            "oggetti_vicini": oggetti_json,
            "npg_vicini": npg_json
        }
    
    def muovi_giocatore(self, direzione):
        """
        Muove il giocatore nella direzione specificata
        
        Args:
            direzione: "nord", "sud", "est", "ovest"
            
        Returns:
            True se il movimento è avvenuto, False altrimenti
        """
        return self.game.muovi_giocatore(direzione)
    
    def debug_stack_stati(self):
        """
        Fornisce informazioni sullo stack degli stati per scopi di debug
        
        Returns:
            str: Stringa descrittiva dello stack degli stati
        """
        try:
            # Ottieni lo stato corrente
            stato_corrente = self.game.stato_corrente()
            stato_corrente_nome = type(stato_corrente).__name__ if stato_corrente else "Nessuno"
            
            # Ottieni lo stack completo
            stack_nomi = [type(s).__name__ for s in self.game.stato_stack]
            
            # Crea una rappresentazione dettagliata
            stack_info = {
                "stato_corrente": stato_corrente_nome,
                "stack_completo": stack_nomi,
                "numero_stati": len(self.game.stato_stack)
            }
            
            # Stringa di sintesi per i log
            return f"Stato corrente: {stato_corrente_nome}, Stack: {stack_nomi}"
        except Exception as e:
            return f"Errore nel debug stack: {e}" 
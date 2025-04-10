from states.base_state import BaseGameState
from states.taverna import TavernaState
from states.mercato import MercatoState
from states.mappa_state import MappaState
from util.funzioni_utili import avanti

class SceltaMappaState(BaseGameState):
    """
    Stato che permette al giocatore di scegliere tra diverse mappe disponibili.
    Funziona come un hub centrale per navigare tra le diverse aree del gioco.
    """
    
    def __init__(self, gioco=None):
        """
        Inizializza lo stato di scelta mappa.
        
        Args:
            gioco: L'istanza del gioco (opzionale)
        """
        super().__init__(gioco)
        self.nome_stato = "scelta_mappa"
        self.stato_precedente = None
        
        # Flag per indicare se è la prima esecuzione dopo il caricamento del gioco
        self.prima_esecuzione = True
        
    def entra(self, gioco=None):
        """
        Metodo chiamato quando si entra nello stato.
        
        Args:
            gioco: L'istanza del gioco (opzionale)
        """
        super().entra(gioco)
        # Salva lo stato corrente della mappa per poter tornare indietro se necessario
        if gioco:
            self.mappa_corrente = gioco.giocatore.mappa_corrente
    
    def esegui(self, gioco):
        """
        Esegue la logica principale dello stato.
        
        Args:
            gioco: L'istanza del gioco
        """
        # Mostra il menu di scelta mappa
        gioco.io.mostra_messaggio("\n=== SELEZIONE DESTINAZIONE ===")
        
        # Ottieni l'elenco delle mappe disponibili dal gestore mappe
        mappe_disponibili = list(gioco.gestore_mappe.mappe.keys())
        
        # Mostra le opzioni
        gioco.io.mostra_messaggio("Dove desideri andare?")
        
        # Mostra le mappe disponibili
        for i, nome_mappa in enumerate(mappe_disponibili, 1):
            # Capitalizza il nome della mappa per una presentazione migliore
            nome_formattato = nome_mappa.capitalize()
            # Evidenzia la mappa corrente
            if nome_mappa == gioco.giocatore.mappa_corrente:
                gioco.io.mostra_messaggio(f"{i}. {nome_formattato} (posizione attuale)")
            else:
                gioco.io.mostra_messaggio(f"{i}. {nome_formattato}")
                
        # Aggiungi l'opzione per tornare indietro
        gioco.io.mostra_messaggio(f"{len(mappe_disponibili) + 1}. Torna indietro")
        
        # Ottieni la scelta dell'utente
        scelta = gioco.io.richiedi_input("\nScegli una destinazione: ")
        
        # Verifica se l'input è vuoto
        if not scelta or not scelta.strip():
            gioco.io.messaggio_errore("Inserisci un numero valido.")
            avanti(gioco)
            # Non richiamare ricorsivamente ma torna al chiamante
            return
            
        try:
            scelta_num = int(scelta)
            
            # Verifica se l'utente ha scelto di tornare indietro
            if scelta_num == len(mappe_disponibili) + 1:
                if gioco.stato_corrente() is self:
                    gioco.pop_stato()  # Torna allo stato precedente
                return
                
            # Verifica che la scelta sia valida
            if 1 <= scelta_num <= len(mappe_disponibili):
                mappa_scelta = mappe_disponibili[scelta_num - 1]
                
                # Verifica se la mappa scelta è diversa da quella corrente
                if mappa_scelta != gioco.giocatore.mappa_corrente:
                    gioco.io.mostra_messaggio(f"Ti dirigi verso {mappa_scelta.capitalize()}...")
                    avanti(gioco)
                    
                    # Esegui il cambio mappa
                    self._cambia_mappa(gioco, mappa_scelta)
                    return  # Interrompe l'esecuzione qui dopo il cambio mappa
                else:
                    # Se è la prima esecuzione dopo il caricamento, entriamo comunque nella mappa
                    if self.prima_esecuzione:
                        self.prima_esecuzione = False  # Resettiamo il flag
                        gioco.io.mostra_messaggio(f"Entri in {mappa_scelta.capitalize()}...")
                        avanti(gioco)
                        
                        # Esegui il cambio mappa come se fosse una nuova mappa
                        self._cambia_mappa(gioco, mappa_scelta)
                        return
                    else:
                        # Comportamento normale quando si è già nella mappa
                        gioco.io.mostra_messaggio("Sei già in questa posizione.")
                        avanti(gioco)
                        return
            else:
                gioco.io.messaggio_errore("Scelta non valida.")
                avanti(gioco)
                return
                
        except ValueError:
            gioco.io.messaggio_errore("Inserisci un numero valido.")
            avanti(gioco)
            return
            
    def _cambia_mappa(self, gioco, mappa_destinazione):
        """
        Gestisce il cambio di mappa e di stato.
        
        Args:
            gioco: L'istanza del gioco
            mappa_destinazione: Nome della mappa di destinazione
        """
        try:
            # Cambia la mappa corrente del giocatore
            mappa = gioco.gestore_mappe.ottieni_mappa(mappa_destinazione)
            if not mappa:
                gioco.io.messaggio_errore(f"Mappa {mappa_destinazione} non trovata.")
                return
                
            # Prepara il nuovo stato in base alla mappa scelta
            nuovo_stato = None
            if mappa_destinazione == "taverna":
                nuovo_stato = TavernaState(gioco)
                # Imposta prima_visita a False se il giocatore aveva già una mappa attiva
                # (significa che non è la prima volta che entra nel gioco)
                if hasattr(self, 'mappa_corrente') and self.mappa_corrente:
                    nuovo_stato.prima_visita = False
            elif mappa_destinazione == "mercato":
                nuovo_stato = MercatoState(gioco)
            else:
                # Per altre mappe, usa MappaState con lo stato corretto come origine
                nuovo_stato = MappaState()
            
            # Verifica che il nuovo stato sia stato creato correttamente
            if nuovo_stato:
                # Cambia la mappa corrente
                gioco.gestore_mappe.imposta_mappa_attuale(mappa_destinazione)
                x, y = mappa.pos_iniziale_giocatore
                gioco.giocatore.imposta_posizione(mappa_destinazione, x, y)
                
                # Stampiamo un messaggio di debug
                gioco.io.mostra_messaggio(f"DEBUG: Posizione impostata a {mappa_destinazione} ({x}, {y})")
                
                # Verifica che la posizione sia stata impostata correttamente
                if gioco.giocatore.mappa_corrente != mappa_destinazione:
                    gioco.io.messaggio_errore(f"Errore: impossibile impostare la mappa corrente a {mappa_destinazione}")
                    return
                
                # Invece di rimuovere questo stato e poi aggiungere quello nuovo,
                # sostituiamo direttamente lo stato corrente usando cambia_stato
                if hasattr(nuovo_stato, 'set_game_context'):
                    nuovo_stato.set_game_context(gioco)
                gioco.cambia_stato(nuovo_stato)
                
                # Aggiungiamo un messaggio per confermare all'utente che è arrivato
                gioco.io.mostra_messaggio(f"Sei arrivato a {mappa_destinazione.capitalize()}.")
                
                # Eseguiamo subito lo stato per evitare interruzioni del flusso
                try:
                    nuovo_stato.esegui(gioco)
                except Exception as e:
                    gioco.io.messaggio_errore(f"Errore nell'esecuzione del nuovo stato: {str(e)}")
            else:
                gioco.io.messaggio_errore(f"Errore nella creazione dello stato per {mappa_destinazione}.")
        except Exception as e:
            gioco.io.messaggio_errore(f"Errore durante il cambio mappa: {str(e)}")
            
    def to_dict(self):
        """
        Converte lo stato in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dello stato in formato dizionario
        """
        data = super().to_dict()
        data.update({
            "mappa_corrente": getattr(self, 'mappa_corrente', None),
            "prima_esecuzione": getattr(self, 'prima_esecuzione', False)
        })
        return data
        
    @classmethod
    def from_dict(cls, data, game=None):
        """
        Crea un'istanza di SceltaMappaState da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            game: Istanza del gioco (opzionale)
            
        Returns:
            SceltaMappaState: Nuova istanza dello stato
        """
        state = cls(game)
        state.mappa_corrente = data.get("mappa_corrente")
        state.prima_esecuzione = data.get("prima_esecuzione", False)
        return state 
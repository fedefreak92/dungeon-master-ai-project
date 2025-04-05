from world.gestore_mappe import GestitoreMappe
from core.io_interface import TerminalIO
import json


class Game:
    def __init__(self, giocatore, stato_iniziale):
        """
        Inizializza il gioco con un giocatore e uno stato iniziale
        
        Args:
            giocatore: L'oggetto giocatore
            stato_iniziale: Lo stato iniziale del gioco
        """
        self.giocatore = giocatore
        self.stato_stack = []  # Stack degli stati
        self.attivo = True
        self.io = TerminalIO()
        
        # Inizializza il gestore delle mappe
        self.gestore_mappe = GestitoreMappe()
        
        # Imposta la mappa iniziale del giocatore (taverna per default)
        # Solo se il giocatore è già stato creato
        if self.giocatore is not None:
            self.imposta_mappa_iniziale()
        
        self.push_stato(stato_iniziale)

    def imposta_mappa_iniziale(self, mappa_nome="taverna"):
        """
        Imposta la mappa iniziale per il giocatore
        
        Args:
            mappa_nome (str): Nome della mappa iniziale (default: "taverna")
        """
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
        Inserisce un nuovo stato sopra quello corrente
        
        Args:
            nuovo_stato: Il nuovo stato da aggiungere
        """
        try:
            if self.stato_corrente():
                self.stato_corrente().pausa(self)  # Mette in pausa lo stato corrente
            self.stato_stack.append(nuovo_stato)
            nuovo_stato.entra(self)
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il push dello stato: {e}")
            self.attivo = False

    def pop_stato(self):
        """
        Rimuove lo stato corrente e torna al precedente
        """
        try:
            if self.stato_stack:
                stato_corrente = self.stato_stack[-1]
                stato_corrente.esci(self)
                self.stato_stack.pop()
                
                # Riprende lo stato precedente se esiste
                if self.stato_corrente():
                    self.stato_corrente().riprendi(self)
                else:
                    self.attivo = False  # Nessuno stato rimasto
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il pop dello stato: {e}")
            self.attivo = False

    def cambia_stato(self, nuovo_stato):
        """
        Sostituisce lo stato corrente con uno nuovo
        
        Args:
            nuovo_stato: Il nuovo stato che sostituirà quello corrente
        """
        try:
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
        while self.attivo and self.stato_corrente():
            try:
                self.stato_corrente().esegui(self)
            except Exception as e:
                self.io.mostra_messaggio(f"Errore durante l'esecuzione dello stato: {e}")
                self.pop_stato()  # Gestione automatica degli errori
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
        """
        data = {
            "nome": self.giocatore.nome,
            "classe": self.giocatore.classe,
            "hp": self.giocatore.hp,
            "mappa": self.giocatore.mappa_corrente,
            "posizione": [self.giocatore.x, self.giocatore.y],
            "inventario": [obj.nome for obj in self.giocatore.inventario]
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def carica(self, file_path="salvataggio.json"):
        """
        Carica uno stato di gioco da un file JSON
        
        Args:
            file_path (str): Percorso del file di salvataggio
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            # Ricrea giocatore
            nome = data["nome"]
            classe = data["classe"]
            from entities.giocatore import Giocatore
            giocatore = Giocatore(nome, classe)
            giocatore.hp = data["hp"]
            giocatore.x, giocatore.y = data["posizione"]
            giocatore.mappa_corrente = data["mappa"]
            self.giocatore = giocatore
            
            # Imposta la mappa corrente
            self.gestore_mappe.imposta_mappa_attuale(self.giocatore.mappa_corrente)
            
            self.io.mostra_messaggio(f"Partita di {nome} caricata con successo!")
            return True
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il caricamento: {e}")
            return False

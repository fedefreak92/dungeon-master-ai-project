from items.oggetto import Oggetto
from entities.entita import Entita, ABILITA_ASSOCIATE, io

class Giocatore(Entita):
    def __init__(self, nome, classe):
        # Inizializziamo valori specifici per il giocatore
        self.classe = classe
        
        # Chiamiamo il costruttore della classe base con valori predefiniti per un giocatore
        super().__init__(nome, hp=20, hp_max=20, forza_base=12, difesa=2, destrezza_base=10, costituzione_base=12, intelligenza_base=10, saggezza_base=10, carisma_base=10)
        
        # Sovrascrivi il token
        self.token = "P"  # P per Player
        
        # Impostiamo altri valori diversi dai predefiniti di Entita
        self.oro = 100
        
        # Attributi per la posizione sulla mappa
        self.mappa_corrente = None  # Nome della mappa corrente
        self.x = 0  # Coordinata X sulla mappa
        self.y = 0  # Coordinata Y sulla mappa
        
        # Inizializza competenze in abilità specifiche per classe
        self._inizializza_competenze()
        
        # Attributi specifici per classe che non sono in Entita
        self._inizializza_per_classe()
        self._crea_inventario_base()
    
    def _inizializza_competenze(self):
        """Inizializza le competenze in abilità in base alla classe"""
        if self.classe == "guerriero":
            self.abilita_competenze["atletica"] = True
            self.abilita_competenze["intimidire"] = True
        elif self.classe == "mago":
            self.abilita_competenze["arcano"] = True
            self.abilita_competenze["storia"] = True
        elif self.classe == "ladro":
            self.abilita_competenze["furtività"] = True
            self.abilita_competenze["acrobazia"] = True
        # Per tutte le altre classi, nessuna competenza specifica
    
    def _inizializza_per_classe(self):
        """Imposta attributi specifici in base alla classe del personaggio"""
        if self.classe == "guerriero":
            self.hp += 5
            self.hp_max += 5
            self.forza_base += 4  # Invece di modificare il modificatore
            # Ricalcola il modificatore
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
        elif self.classe == "mago":
            self.forza_base -= 2  # Forza più bassa
            self.intelligenza_base = 16  # Intelligenza alta
            # Ricalcola i modificatori
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            self.modificatore_intelligenza = self.calcola_modificatore(self.intelligenza_base)
        elif self.classe == "ladro":
            self.destrezza_base = 16  # Destrezza alta
            # Ricalcola il modificatore
            self.modificatore_destrezza = self.calcola_modificatore(self.destrezza_base)
            self.fortuna = 5  # Attributo specifico del ladro
        # Per tutte le altre classi, usare i valori predefiniti
    
    def _crea_inventario_base(self):
        """Crea un inventario base in base alla classe del personaggio"""
        # Oggetti comuni per tutti
        pozione = Oggetto("Pozione di cura", "cura", {"cura": 10}, 5, "Ripristina 10 punti vita")
        chiave = Oggetto("Chiave comune", "chiave", {}, 1, "Una chiave semplice che potrebbe aprire porte o forzieri")
        
        # Armi base per tutte le classi
        arma_base = None
        armatura_base = None
        
        if self.classe == "guerriero":
            arma_base = Oggetto("Spada corta", "arma", {"forza": 3}, 15, "Una spada corta ma robusta")
            armatura_base = Oggetto("Cotta di maglia", "armatura", {"difesa": 3}, 25, "Una cotta di maglia che offre buona protezione")
            
        elif self.classe == "mago":
            arma_base = Oggetto("Bastone arcano", "arma", {"forza": 1, "intelligenza": 2}, 20, "Un bastone che amplifica i poteri magici")
            armatura_base = Oggetto("Veste da mago", "armatura", {"difesa": 1, "intelligenza": 1}, 15, "Una veste leggera con proprietà magiche")
            
        elif self.classe == "ladro":
            arma_base = Oggetto("Pugnale", "arma", {"forza": 2, "destrezza": 1}, 12, "Un pugnale affilato e maneggevole")
            armatura_base = Oggetto("Armatura di cuoio", "armatura", {"difesa": 2, "destrezza": 1}, 18, "Un'armatura leggera che non limita i movimenti")
            
        else:
            arma_base = Oggetto("Bastone da viaggio", "arma", {"forza": 1}, 5, "Un semplice bastone di legno")
            armatura_base = Oggetto("Abiti robusti", "armatura", {"difesa": 1}, 5, "Vestiti rinforzati che offrono minima protezione")
            
        # Aggiunta degli oggetti all'inventario
        self.inventario.append(pozione)
        self.inventario.append(chiave)
        self.inventario.append(arma_base)
        self.inventario.append(armatura_base)
        
        # Equipaggia automaticamente arma e armatura base
        arma_base.equipaggia(self)
        armatura_base.equipaggia(self)
        
        # Aggiungi un accessorio base in base alla classe
        if self.classe == "guerriero":
            amuleto = Oggetto("Amuleto della forza", "accessorio", {"forza": 1}, 10, "Un amuleto che aumenta la forza")
            self.inventario.append(amuleto)
            amuleto.equipaggia(self)
        elif self.classe == "mago":
            anello = Oggetto("Anello della mente", "accessorio", {"intelligenza": 1}, 10, "Un anello che migliora la concentrazione")
            self.inventario.append(anello)
            anello.equipaggia(self)
        elif self.classe == "ladro":
            guanti = Oggetto("Guanti del ladro", "accessorio", {"destrezza": 1}, 10, "Guanti che migliorano la manualità")
            self.inventario.append(guanti)
            guanti.equipaggia(self)
    
    def attacca(self, nemico):
        # Utilizziamo prima l'implementazione di base da Entita
        # se il nemico ha subisci_danno() implementato
        if hasattr(nemico, 'subisci_danno'):
            return super().attacca(nemico)
        
        # Altrimenti usiamo il vecchio codice per compatibilità
        danno = self.forza 
        io.mostra_messaggio(f"{self.nome} attacca {nemico.nome} e infligge {danno} danni!")
        
        if hasattr(nemico, 'ferisci'):
            nemico.ferisci(danno)
        else:
            nemico.hp -= danno
    
    def _sali_livello(self):
        """Override del metodo della classe base per un messaggio personalizzato"""
        # Chiamiamo prima il metodo della classe base
        super()._sali_livello()
        # Poi aggiungiamo il nostro messaggio personalizzato
        io.mostra_messaggio("Sei diventato più forte!")

    def imposta_posizione(self, mappa_nome, x, y):
        """
        Imposta la posizione del giocatore su una mappa specifica
        
        Args:
            mappa_nome (str): Nome della mappa
            x (int): Coordinata X
            y (int): Coordinata Y
        """
        self.mappa_corrente = mappa_nome
        self.x = x
        self.y = y
    
    def muovi(self, dx, dy, gestore_mappe):
        """
        Tenta di muovere il giocatore nella direzione specificata
        
        Args:
            dx (int): Spostamento sull'asse X
            dy (int): Spostamento sull'asse Y
            gestore_mappe: Gestore delle mappe di gioco
            
        Returns:
            bool: True se il movimento è avvenuto, False altrimenti
        """
        if not gestore_mappe or not self.mappa_corrente:
            return False
        
        return gestore_mappe.muovi_giocatore(self, dx, dy)
    
    def ottieni_posizione(self):
        """
        Restituisce la posizione corrente del giocatore
        
        Returns:
            tuple: Coordinate (x, y) o None se non impostata
        """
        if self.mappa_corrente:
            return (self.x, self.y)
        return None
    
    def interagisci_con_oggetto_adiacente(self, gestore_mappe):
        """
        Interagisce con l'oggetto adiacente al giocatore, se presente
        
        Args:
            gestore_mappe: Gestore delle mappe di gioco
            
        Returns:
            bool: True se è avvenuta un'interazione, False altrimenti
        """
        if not gestore_mappe or not self.mappa_corrente:
            return False
        
        mappa = gestore_mappe.ottieni_mappa(self.mappa_corrente)
        if not mappa:
            return False
        
        # Controlla in tutte le direzioni adiacenti
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = self.x + dx, self.y + dy
            oggetto = mappa.ottieni_oggetto_a(x, y)
            if oggetto:
                io.mostra_messaggio(f"Interagisci con {oggetto.nome}")
                oggetto.interagisci(self)
                return True
            
        io.mostra_messaggio("Non ci sono oggetti con cui interagire nelle vicinanze.")
        return False
    
    def interagisci_con_npg_adiacente(self, gestore_mappe, gioco):
        """
        Interagisce con l'NPG adiacente al giocatore, se presente
        
        Args:
            gestore_mappe: Gestore delle mappe di gioco
            gioco: Riferimento all'oggetto gioco principale
            
        Returns:
            bool: True se è avvenuta un'interazione, False altrimenti
        """
        if not gestore_mappe or not self.mappa_corrente:
            return False
        
        mappa = gestore_mappe.ottieni_mappa(self.mappa_corrente)
        if not mappa:
            return False
        
        # Controlla in tutte le direzioni adiacenti
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = self.x + dx, self.y + dy
            npg = mappa.ottieni_npg_a(x, y)
            if npg:
                io.mostra_messaggio(f"Parli con {npg.nome}")
                from test_state.stati.dialogo import DialogoState
                gioco.push_stato(DialogoState(npg))
                return True
            
        io.mostra_messaggio("Non ci sono personaggi con cui parlare nelle vicinanze.")
        return False
    
    def ottieni_oggetti_vicini(self, gestore_mappe, raggio=1):
        """
        Restituisce gli oggetti vicini al giocatore
        
        Args:
            gestore_mappe: Gestore delle mappe di gioco
            raggio (int): Raggio di ricerca
            
        Returns:
            dict: Dizionario di oggetti vicini
        """
        if not gestore_mappe or not self.mappa_corrente:
            return {}
        
        mappa = gestore_mappe.ottieni_mappa(self.mappa_corrente)
        if not mappa:
            return {}
        
        return mappa.ottieni_oggetti_vicini(self.x, self.y, raggio)
    
    def ottieni_npg_vicini(self, gestore_mappe, raggio=1):
        """
        Restituisce gli NPG vicini al giocatore
        
        Args:
            gestore_mappe: Gestore delle mappe di gioco
            raggio (int): Raggio di ricerca
            
        Returns:
            dict: Dizionario di NPG vicini
        """
        if not gestore_mappe or not self.mappa_corrente:
            return {}
        
        mappa = gestore_mappe.ottieni_mappa(self.mappa_corrente)
        if not mappa:
            return {}
        
        return mappa.ottieni_npg_vicini(self.x, self.y, raggio)

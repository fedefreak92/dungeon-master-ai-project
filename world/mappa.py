import itertools
from items.oggetto_interattivo import OggettoInterattivo
from entities.npg import NPG
from entities.entita import Entita
from entities.giocatore import Giocatore
from entities.nemico import Nemico

class Mappa:
    def __init__(self, nome, larghezza, altezza, tipo="interno"):
        """
        Inizializza una mappa di gioco.
        
        Args:
            nome (str): Nome della mappa (es. "taverna", "mercato")
            larghezza (int): Larghezza della mappa in celle
            altezza (int): Altezza della mappa in celle
            tipo (str): Tipo di mappa ("interno", "esterno", "dungeon", ecc.)
        """
        self.nome = nome
        self.larghezza = larghezza
        self.altezza = altezza
        self.tipo = tipo
        
        # Matrice che rappresenta la mappa (0=vuoto, 1=muro, ecc.)
        self.griglia = [[0 for _ in range(larghezza)] for _ in range(altezza)]
        
        # Dizionari per tenere traccia degli oggetti sulla mappa
        self.oggetti = {}  # chiave: (x, y), valore: oggetto
        self.npg = {}      # chiave: (x, y), valore: npg
        self.porte = {}    # chiave: (x, y), valore: (mappa_destinazione, x_dest, y_dest)
        
        # Posizione iniziale del giocatore su questa mappa
        self.pos_iniziale_giocatore = (0, 0)
        
    def aggiungi_oggetto(self, oggetto, x, y):
        """Aggiunge un oggetto alla mappa in una posizione specifica"""
        self.oggetti[(x, y)] = oggetto
        oggetto.posizione = (x, y, self.nome)  # Aggiorna la posizione dell'oggetto
        
    def aggiungi_npg(self, npg, x, y):
        """Aggiunge un NPG alla mappa in una posizione specifica"""
        self.npg[(x, y)] = npg
        npg.imposta_posizione(x, y)  # Utilizza il metodo esistente in NPG
        
    def aggiungi_porta(self, porta, x, y, mappa_dest, x_dest, y_dest):
        """Collega una porta a un'altra mappa e posizione"""
        self.oggetti[(x, y)] = porta
        porta.posizione = (x, y, self.nome)
        self.porte[(x, y)] = (mappa_dest, x_dest, y_dest)
        
    def imposta_muro(self, x, y):
        """Marca una cella come muro"""
        if 0 <= x < self.larghezza and 0 <= y < self.altezza:
            self.griglia[y][x] = 1
            
    def imposta_posizione_iniziale(self, x, y):
        """Imposta la posizione iniziale del giocatore su questa mappa"""
        self.pos_iniziale_giocatore = (x, y)
        
    def ottieni_oggetto_a(self, x, y):
        """Restituisce l'oggetto alla posizione specificata o None"""
        return self.oggetti.get((x, y))
        
    def ottieni_npg_a(self, x, y):
        """Restituisce l'NPG alla posizione specificata o None"""
        return self.npg.get((x, y))
    
    def ottieni_porta_a(self, x, y):
        """Restituisce la destinazione della porta alla posizione specificata o None"""
        return self.porte.get((x, y))
        
    def is_posizione_valida(self, x, y):
        """Verifica se la posizione è valida e attraversabile"""
        if 0 <= x < self.larghezza and 0 <= y < self.altezza:
            return self.griglia[y][x] == 0  # 0 = cella vuota
        return False
    
    def genera_rappresentazione_ascii(self, pos_giocatore=None):
        """
        Genera una rappresentazione ASCII della mappa
        
        Args:
            pos_giocatore: Tuple (x, y) della posizione del giocatore
        
        Returns:
            str: Rappresentazione ASCII della mappa
        """
        mappa_ascii = []
        for y in range(self.altezza):
            riga = ""
            for x in range(self.larghezza):
                if pos_giocatore and pos_giocatore == (x, y):
                    if pos_giocatore[0] == x and pos_giocatore[1] == y:
                        riga += "P"  # Giocatore, usiamo sempre P per coerenza visiva
                elif (x, y) in self.npg:
                    riga += self.npg[(x, y)].token  # Usa il token dell'NPG
                elif (x, y) in self.oggetti:
                    riga += self.oggetti[(x, y)].token  # Usa il token dell'oggetto
                elif self.griglia[y][x] == 1:
                    riga += "#"  # Muro
                else:
                    riga += "."  # Spazio vuoto
            mappa_ascii.append(riga)
        
        return "\n".join(mappa_ascii)
    
    def ottieni_oggetti_vicini(self, x, y, raggio=1):
        """
        Restituisce gli oggetti entro un certo raggio dalla posizione
        
        Args:
            x, y: Coordinate centrali
            raggio: Distanza massima in celle
            
        Returns:
            dict: Dizionario di posizioni e oggetti
        """
        oggetti_vicini = {}
        for dx, dy in itertools.product(range(-raggio, raggio + 1), range(-raggio, raggio + 1)):
            pos = (x + dx, y + dy)
            if pos in self.oggetti:
                oggetti_vicini[pos] = self.oggetti[pos]
        return oggetti_vicini
    
    def ottieni_npg_vicini(self, x, y, raggio=1):
        """
        Restituisce gli NPG entro un certo raggio dalla posizione
        
        Args:
            x, y: Coordinate centrali
            raggio: Distanza massima in celle
            
        Returns:
            dict: Dizionario di posizioni e NPG
        """
        npg_vicini = {}
        for dx, dy in itertools.product(range(-raggio, raggio + 1), range(-raggio, raggio + 1)):
            pos = (x + dx, y + dy)
            if pos in self.npg:
                npg_vicini[pos] = self.npg[pos]
        return npg_vicini
    
    def carica_layout_da_stringa(self, layout_str):
        """
        Carica il layout della mappa da una stringa di caratteri
        # = muro, . = pavimento, P = posizione iniziale giocatore
        
        Args:
            layout_str: Stringa multi-linea che rappresenta la mappa
        """
        righe = layout_str.strip().split('\n')
        for y, riga in enumerate(righe):
            for x, cella in enumerate(riga):
                if cella == '#':
                    self.imposta_muro(x, y)
                elif cella == 'P':
                    self.imposta_posizione_iniziale(x, y)

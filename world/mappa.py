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
        for dx in range(-raggio, raggio + 1):
            for dy in range(-raggio, raggio + 1):
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
        for dx in range(-raggio, raggio + 1):
            for dy in range(-raggio, raggio + 1):
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
    
    def to_dict(self):
        """
        Converte la mappa in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione della mappa in formato dizionario
        """
        # Converte la griglia in una lista per la serializzazione
        griglia_serializzata = [riga.copy() for riga in self.griglia]
        
        # Serializza oggetti e NPG usando to_dict se disponibile
        oggetti_dict = {}
        for pos, obj in self.oggetti.items():
            if hasattr(obj, 'to_dict'):
                oggetti_dict[str(pos)] = obj.to_dict()
            else:
                oggetti_dict[str(pos)] = {"nome": obj.nome, "token": obj.token}
        
        npg_dict = {}
        for pos, npg in self.npg.items():
            if hasattr(npg, 'to_dict'):
                npg_dict[str(pos)] = npg.to_dict()
            else:
                npg_dict[str(pos)] = {"nome": npg.nome, "token": npg.token}
        
        # Serializza le porte
        porte_dict = {str(pos): list(dest) for pos, dest in self.porte.items()}
        
        return {
            "nome": self.nome,
            "larghezza": self.larghezza,
            "altezza": self.altezza,
            "tipo": self.tipo,
            "griglia": griglia_serializzata,
            "oggetti": oggetti_dict,
            "npg": npg_dict,
            "porte": porte_dict,
            "pos_iniziale_giocatore": self.pos_iniziale_giocatore
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea una nuova istanza di Mappa da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati della mappa
            
        Returns:
            Mappa: Nuova istanza di Mappa
        """
        # Crea una nuova mappa con i parametri di base
        mappa = cls(
            nome=data.get("nome", "mappa_sconosciuta"),
            larghezza=data.get("larghezza", 10),
            altezza=data.get("altezza", 10),
            tipo=data.get("tipo", "interno")
        )
        
        # Carica la griglia
        if "griglia" in data:
            mappa.griglia = [riga.copy() for riga in data["griglia"]]
        
        # Carica gli oggetti
        from items.oggetto_interattivo import OggettoInterattivo
        for pos_str, obj_data in data.get("oggetti", {}).items():
            try:
                # Converti la stringa di posizione in tupla
                pos = eval(pos_str)  # Sicuro perché la posizione è una tupla semplice (x, y)
                
                # Crea l'oggetto usando from_dict se disponibile
                if isinstance(obj_data, dict):
                    obj = OggettoInterattivo.from_dict(obj_data)
                    mappa.oggetti[pos] = obj
                    # Aggiorna la posizione dell'oggetto
                    obj.posizione = (pos[0], pos[1], mappa.nome)
            except Exception as e:
                print(f"Errore durante il caricamento dell'oggetto in {pos_str}: {e}")
        
        # Carica gli NPG
        from entities.npg import NPG
        for pos_str, npg_data in data.get("npg", {}).items():
            try:
                # Converti la stringa di posizione in tupla
                pos = eval(pos_str)
                
                # Crea l'NPG usando from_dict se disponibile
                if isinstance(npg_data, dict):
                    if hasattr(NPG, 'from_dict'):
                        npg = NPG.from_dict(npg_data)
                    else:
                        npg = NPG(npg_data.get("nome", "NPC"), token=npg_data.get("token", "N"))
                    
                    mappa.npg[pos] = npg
                    npg.imposta_posizione(pos[0], pos[1])
            except Exception as e:
                print(f"Errore durante il caricamento dell'NPG in {pos_str}: {e}")
        
        # Carica le porte
        for pos_str, dest_data in data.get("porte", {}).items():
            try:
                pos = eval(pos_str)
                # Converti la lista di destinazione in tupla
                if isinstance(dest_data, list) and len(dest_data) == 3:
                    mappa.porte[pos] = (dest_data[0], dest_data[1], dest_data[2])
            except Exception as e:
                print(f"Errore durante il caricamento della porta in {pos_str}: {e}")
        
        # Carica la posizione iniziale del giocatore
        if "pos_iniziale_giocatore" in data:
            mappa.pos_iniziale_giocatore = tuple(data["pos_iniziale_giocatore"])
        
        return mappa

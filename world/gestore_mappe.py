from world.mappa import Mappa
import random
from items.oggetto_interattivo import OggettoInterattivo, Porta, Baule, Leva, Trappola
from entities.giocatore import Giocatore
from entities.npg import NPG

class GestitoreMappe:
    def __init__(self):
        """Inizializza il gestore mappe"""
        self.mappe = {}  # Nome mappa -> oggetto Mappa
        self.mappa_attuale = None
        self.inizializza_mappe()
        
    def inizializza_mappe(self):
        """Crea e configura tutte le mappe del gioco"""
        # Crea mappa taverna
        taverna = Mappa("taverna", 25, 20, "interno")
        self._configura_mappa_taverna(taverna)
        
        # Crea mappa mercato
        mercato = Mappa("mercato", 35, 25, "esterno")
        self._configura_mappa_mercato(mercato)
        
        # Crea mappa cantina
        cantina = Mappa("cantina", 20, 15, "dungeon")
        self._configura_mappa_cantina(cantina)
        
        # Aggiungi le mappe al gestore
        self.mappe["taverna"] = taverna
        self.mappe["mercato"] = mercato
        self.mappe["cantina"] = cantina
        
    def _configura_mappa_taverna(self, mappa):
        """Configura il layout della mappa taverna"""
        # Layout di base della taverna usando una stringa multi-linea con griglia migliorata
        # Legenda:
        # # = muro
        # . = pavimento
        # P = posizione iniziale giocatore
        layout = """
#########################
#.......................#
#.......................#
#.......................#
#.......##..##..........#
#.......##..##..........#
#.......................#
#.......................#
#...........P...........#
#.......................#
#.......................#
#.......................#
#.....##....##...........#
#.....##....##...........#
#.......................#
#.......................#
#.......................#
#.......................#
#.......................#
#########################
"""
        mappa.carica_layout_da_stringa(layout)
        
        # Collegamento con altre mappe (porte)
        # Porta che collega la taverna alla cantina
        x, y = 22, 9  # Posizione della porta
        mappa.imposta_muro(x, y)  # La porta è un "muro speciale"
        
        # Porta che collega la taverna al mercato
        x, y = 12, 18  # Posizione porta d'uscita
        mappa.imposta_muro(x, y)  # La porta è un "muro speciale"
        
        # Esempi di uso dei token personalizzati
        durnan = NPG("Durnan", token="D")  # "D" per Durnan
        mappa.aggiungi_npg(durnan, 6, 6)
        
        elminster = NPG("Elminster", token="E")  # "E" per Elminster
        mappa.aggiungi_npg(elminster, 9, 9)
        
        porta_cantina = Porta("Porta della cantina", "Una porta che conduce alla cantina.", 
                             stato="chiusa", richiede_chiave=True, posizione="taverna", 
                             posizione_destinazione="cantina", token="D")
        mappa.aggiungi_porta(porta_cantina, 22, 9, "cantina", 1, 7)
        
        mirt = NPG("Mirt", token="M")  # "M" per Mirt
        mappa.aggiungi_npg(mirt, 5, 5)  # o qualsiasi coordinata appropriata
        
        # Aggiungi manualmente gli oggetti interattivi principali
        bancone = OggettoInterattivo("Bancone", "Un lungo bancone di legno...", token="O")
        mappa.aggiungi_oggetto(bancone, 4, 4)
        
        camino = OggettoInterattivo("Camino", "Un grande camino in pietra...", token="O")
        mappa.aggiungi_oggetto(camino, 15, 3)
        
        baule = Baule("Baule nascosto", "Un piccolo baule nascosto...", token="C")
        mappa.aggiungi_oggetto(baule, 8, 10)
        
        leva = Leva("Leva segreta", "Una leva nascosta dietro un quadro.", token="L")
        mappa.aggiungi_oggetto(leva, 20, 5)
        
        trappola = Trappola("Trappola nel pavimento", "Una parte del pavimento...", token="T")
        mappa.aggiungi_oggetto(trappola, 10, 15)
        
    def _configura_mappa_mercato(self, mappa):
        """Configura il layout della mappa mercato"""
        # Layout di base del mercato con griglia migliorata
        layout = """
###################################
#.................................#
#.................................#
#.................................#
#.................................#
#....##.......##.......##........#
#....##.......##.......##........#
#.................................#
#.................................#
#.................................#
#................P................#
#.................................#
#.................................#
#.................................#
#.................................#
#....##.......##.......##........#
#....##.......##.......##........#
#.................................#
#.................................#
#.................................#
#.................................#
#.................................#
#.................................#
#.................................#
###################################
"""
        mappa.carica_layout_da_stringa(layout)
        
        # Collegamento con la taverna
        x, y = 17, 1  # Posizione porta d'ingresso alla taverna
        mappa.imposta_muro(x, y)  # La porta è un "muro speciale"
        
    def _configura_mappa_cantina(self, mappa):
        """Configura il layout della mappa cantina"""
        # Layout di base della cantina con griglia migliorata
        layout = """
####################
#..................#
#..................#
#..................#
#......####........#
#..................#
#..................#
#.P................#
#..................#
#..................#
#..................#
#..................#
#..................#
#..................#
####################
"""
        mappa.carica_layout_da_stringa(layout)
        
        # Collegamento con la taverna
        x, y = 1, 7  # Posizione scala per tornare alla taverna
        
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
            
        # Posizioni predefinite per gli oggetti interattivi
        pos_oggetti = {
            # Taverna
            "bancone": (4, 4),
            "camino": (15, 3),
            "baule_nascondiglio": (8, 10),
            "porta_cantina": (22, 9),
            "leva_segreta": (20, 5),
            "trappola_pavimento": (10, 15),
            "altare_magico": (18, 15)
        }
        
        # Posiziona gli oggetti interattivi sulla mappa
        for chiave, oggetto in stato.oggetti_interattivi.items():
            # Verifica se abbiamo una posizione predefinita
            if chiave in pos_oggetti:
                x, y = pos_oggetti[chiave]
                if mappa.is_posizione_valida(x, y) and (x, y) not in mappa.oggetti and (x, y) not in mappa.npg:
                    mappa.aggiungi_oggetto(oggetto, x, y)
                    continue
            
            # Altrimenti posiziona in modo casuale
            posizionato = False
            tentativi = 0
            
            while not posizionato and tentativi < 20:
                x = random.randint(1, mappa.larghezza - 2)
                y = random.randint(1, mappa.altezza - 2)
                
                # Verifica se la posizione è valida e libera
                if mappa.is_posizione_valida(x, y) and (x, y) not in mappa.oggetti and (x, y) not in mappa.npg:
                    mappa.aggiungi_oggetto(oggetto, x, y)
                    posizionato = True
                
                tentativi += 1
        
        # Posizioni predefinite per gli NPG
        pos_npg = {
            "Durnan": (6, 6),
            "Elminster": (9, 9),
            "Mirt": (5, 5)  # Usa la stessa posizione definita in _configura_mappa_taverna
        }
        
        # Posiziona NPG
        for nome, npg in stato.npg_presenti.items():
            # Verifica se abbiamo una posizione predefinita
            if nome in pos_npg:
                x, y = pos_npg[nome]
                if mappa.is_posizione_valida(x, y) and (x, y) not in mappa.oggetti and (x, y) not in mappa.npg:
                    mappa.aggiungi_npg(npg, x, y)
                    continue
                
            # Altrimenti posiziona in modo casuale
            posizionato = False
            tentativi = 0
            
            while not posizionato and tentativi < 20:
                x = random.randint(1, mappa.larghezza - 2)
                y = random.randint(1, mappa.altezza - 2)
                
                # Verifica se la posizione è valida e libera
                if mappa.is_posizione_valida(x, y) and (x, y) not in mappa.oggetti and (x, y) not in mappa.npg:
                    mappa.aggiungi_npg(npg, x, y)
                    posizionato = True
                
                tentativi += 1
            
        return True
        
    def muovi_giocatore(self, giocatore, dx, dy):
        """
        Muove il giocatore sulla mappa corrente.
        
        Args:
            giocatore: Oggetto giocatore
            dx, dy: Direzione di movimento
            
        Returns:
            bool: True se il movimento è avvenuto, False altrimenti
        """
        if not self.mappa_attuale:
            return False
            
        nuovo_x = giocatore.x + dx
        nuovo_y = giocatore.y + dy
        
        # Verifica se il movimento è possibile
        if self.mappa_attuale.is_posizione_valida(nuovo_x, nuovo_y):
            # Controlla se c'è una porta
            destinazione = self.mappa_attuale.ottieni_porta_a(nuovo_x, nuovo_y)
            if destinazione:
                # Cambia mappa
                mappa_dest, x_dest, y_dest = destinazione
                self.cambia_mappa_giocatore(giocatore, mappa_dest, x_dest, y_dest)
                return True
                
            # Verifica se c'è un oggetto o NPG
            if (nuovo_x, nuovo_y) in self.mappa_attuale.oggetti or (nuovo_x, nuovo_y) in self.mappa_attuale.npg:
                # Non permettere di muoversi sopra oggetti o NPG
                return False
                
            # Movimento valido
            giocatore.x = nuovo_x
            giocatore.y = nuovo_y
            return True
            
        return False
        
    def cambia_mappa_giocatore(self, giocatore, nome_mappa, x=None, y=None):
        """
        Sposta il giocatore in una nuova mappa.
        
        Args:
            giocatore: Oggetto giocatore
            nome_mappa: Nome della mappa di destinazione
            x, y: Coordinate nella nuova mappa (opzionali)
        
        Returns:
            bool: True se il cambio mappa è avvenuto, False altrimenti
        """
        if nome_mappa not in self.mappe:
            return False
            
        # Imposta la nuova mappa corrente
        self.mappa_attuale = self.mappe[nome_mappa]
        
        # Se non sono fornite coordinate, usa la posizione iniziale della mappa
        if x is None or y is None:
            x, y = self.mappa_attuale.pos_iniziale_giocatore
            
        # Aggiorna la posizione del giocatore
        giocatore.x = x
        giocatore.y = y
        giocatore.mappa_corrente = nome_mappa
        
        return True
        
    def ottieni_info_posizione(self, x, y, mappa=None):
        """
        Restituisce informazioni sulla posizione.
        
        Args:
            x, y: Coordinate
            mappa: Oggetto mappa (se None, usa mappa_attuale)
            
        Returns:
            dict: Informazioni sulla posizione
        """
        if mappa is None:
            mappa = self.mappa_attuale
            
        if not mappa:
            return None
            
        info = {
            "tipo": "vuoto",
            "oggetto": None,
            "npg": None,
            "porta": None
        }
        
        # Controlla il tipo di cella
        if not mappa.is_posizione_valida(x, y):
            info["tipo"] = "muro"
        elif (x, y) in mappa.oggetti:
            info["tipo"] = "oggetto"
            info["oggetto"] = mappa.oggetti[(x, y)]
        elif (x, y) in mappa.npg:
            info["tipo"] = "npg"
            info["npg"] = mappa.npg[(x, y)]
        elif (x, y) in mappa.porte:
            info["tipo"] = "porta"
            info["porta"] = mappa.porte[(x, y)]
            
        return info
    
    def salva(self, percorso_file="mappe_salvataggio.json"):
        """
        Salva lo stato completo di tutte le mappe e relativi oggetti interattivi.
        
        Args:
            percorso_file (str): Percorso del file dove salvare i dati
            
        Returns:
            bool: True se il salvataggio è avvenuto con successo, False altrimenti
        """
        try:
            # Crea un dizionario con tutte le mappe serializzate
            mappe_data = {}
            for nome_mappa, mappa in self.mappe.items():
                # Utilizziamo il metodo to_dict già esistente nella classe Mappa
                mappe_data[nome_mappa] = mappa.to_dict()
            
            # Aggiungi metadati utili
            dati_salvataggio = {
                "mappe": mappe_data,
                "mappa_attuale": self.mappa_attuale.nome if self.mappa_attuale else None,
                "versione": "1.0.0",
                "timestamp": __import__('time').time()
            }
            
            # Salva su file
            with open(percorso_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(dati_salvataggio, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Errore durante il salvataggio delle mappe: {e}")
            return False

    def carica(self, percorso_file="mappe_salvataggio.json"):
        """
        Carica lo stato completo di tutte le mappe e relativi oggetti interattivi.
        
        Args:
            percorso_file (str): Percorso del file da cui caricare i dati
            
        Returns:
            bool: True se il caricamento è avvenuto con successo, False altrimenti
        """
        try:
            import json
            import os
            
            # Verifica se il file esiste
            if not os.path.exists(percorso_file):
                return False
            
            # Carica il file
            with open(percorso_file, 'r', encoding='utf-8') as f:
                dati_salvati = json.load(f)
            
            # Verifica la versione per compatibilità futura
            versione = dati_salvati.get("versione", "0.0.0")
            
            # Carica le mappe
            mappe_data = dati_salvati.get("mappe", {})
            if not mappe_data:
                return False
            
            # Ricrea tutte le mappe dal salvataggio
            from world.mappa import Mappa
            self.mappe = {}
            
            for nome_mappa, mappa_dict in mappe_data.items():
                # Utilizziamo il metodo from_dict già esistente nella classe Mappa
                self.mappe[nome_mappa] = Mappa.from_dict(mappa_dict)
            
            # Imposta la mappa attuale
            mappa_attuale_nome = dati_salvati.get("mappa_attuale")
            if mappa_attuale_nome and mappa_attuale_nome in self.mappe:
                self.mappa_attuale = self.mappe[mappa_attuale_nome]
            elif self.mappe:
                # Se non c'è una mappa attuale, imposta la prima disponibile
                self.mappa_attuale = next(iter(self.mappe.values()))
            
            return True
        except Exception as e:
            print(f"Errore durante il caricamento delle mappe: {e}")
            return False

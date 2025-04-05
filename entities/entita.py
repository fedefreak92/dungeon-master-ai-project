import random
from core.io_interface import TerminalIO

# Istanza globale dell'interfaccia di I/O
io = TerminalIO()

# Mappa delle abilità associate alle caratteristiche (D&D 5e style)
ABILITA_ASSOCIATE = {
    "acrobazia": "destrezza",
    "furtività": "destrezza",
    "giocare d'azzardo": "destrezza",
    "addestrare animali": "saggezza",
    "percezione": "saggezza",
    "intuito": "saggezza",
    "natura": "intelligenza",
    "religione": "intelligenza",
    "arcano": "intelligenza",
    "storia": "intelligenza",
    "indagare": "intelligenza",
    "persuasione": "carisma",
    "intimidire": "carisma",
    "inganno": "carisma",
    "atletica": "forza",
    "sopravvivenza": "saggezza",
    "medicina": "saggezza"
}

class Dado:
    def __init__(self, facce):
        self.facce = facce

    def tira(self):
        return random.randint(1, self.facce)

class Entita:
    def __init__(self, nome, hp=10, hp_max=10, forza_base=10, difesa=0, destrezza_base=10, costituzione_base=10, intelligenza_base=10, saggezza_base=10, carisma_base=10, token="E"):
        self.nome = nome
        self.hp = hp
        self.hp_max = hp_max
        self.token = token
        
        # Valori base delle caratteristiche
        self.forza_base = forza_base
        self.destrezza_base = destrezza_base
        self.costituzione_base = costituzione_base
        self.intelligenza_base = intelligenza_base
        self.saggezza_base = saggezza_base
        self.carisma_base = carisma_base
        
        # Modificatori calcolati
        self.modificatore_forza = self.calcola_modificatore(forza_base)
        self.modificatore_destrezza = self.calcola_modificatore(destrezza_base)
        self.modificatore_costituzione = self.calcola_modificatore(costituzione_base)
        self.modificatore_intelligenza = self.calcola_modificatore(intelligenza_base)
        self.modificatore_saggezza = self.calcola_modificatore(saggezza_base)
        self.modificatore_carisma = self.calcola_modificatore(carisma_base)
        
        # Attributi per la posizione
        self.x = 0
        self.y = 0
        self.mappa_corrente = None
        
        # Competenze in abilità
        self.abilita_competenze = {}  # Esempio: {"percezione": True, "persuasione": False}
        self.bonus_competenza = 2  # Può crescere con il livello
        
        # Altri attributi
        self.difesa = difesa
        self.inventario = []
        self.oro = 0
        self.esperienza = 0
        self.livello = 1
        self.arma = None
        self.armatura = None
        self.accessori = []
        
    def subisci_danno(self, danno):
        """Metodo unificato per subire danno, considerando la difesa"""
        danno_effettivo = max(1, danno - self.difesa)
        self.hp = max(0, self.hp - danno_effettivo)
        return self.hp > 0
        
    def attacca(self, bersaglio):
        """Metodo unificato per attaccare"""
        danno = self.modificatore_forza
        io.mostra_messaggio(f"{self.nome} attacca {bersaglio.nome} e infligge {danno} danni!")
        return bersaglio.subisci_danno(danno)
        
    def cura(self, quantita):
        """Cura l'entità"""
        self.hp = min(self.hp_max, self.hp + quantita)
        
    def aggiungi_item(self, item):
        """Aggiunge un item all'inventario"""
        self.inventario.append(item)
        
    def rimuovi_item(self, nome_item):
        """Rimuove un item dall'inventario"""
        for item in self.inventario:
            if (isinstance(item, str) and item == nome_item) or (hasattr(item, 'nome') and item.nome == nome_item):
                self.inventario.remove(item)
                return True
        return False
        
    def e_vivo(self):
        """Verifica se l'entità è viva"""
        return self.hp > 0
        
    def ferisci(self, danno):
        """Metodo alternativo per subire danno, per compatibilità"""
        return self.subisci_danno(danno)
        
    def aggiungi_oro(self, quantita):
        """Aggiunge oro all'entità"""
        self.oro += quantita
        io.mostra_messaggio(f"{self.nome} ha ricevuto {quantita} monete d'oro! (Totale: {self.oro})")
        
    def guadagna_esperienza(self, quantita):
        """Aggiunge esperienza e verifica se è possibile salire di livello"""
        self.esperienza += quantita
        
        # Verifica salita di livello: 100 * livello attuale
        esperienza_necessaria = 100 * self.livello
        
        if self.esperienza >= esperienza_necessaria:
            self.livello += 1
            self.esperienza -= esperienza_necessaria
            self._sali_livello()
            return True
        return False
        
    def _sali_livello(self):
        """Applica i miglioramenti per il salire di livello"""
        self.hp_max += 5
        self.hp = self.hp_max  # Cura completamente quando sale di livello
        
        # Incrementa un valore base a caso
        import random
        caratteristiche = ["forza_base", "destrezza_base", "costituzione_base", 
                          "intelligenza_base", "saggezza_base", "carisma_base"]
        caratteristica_da_aumentare = random.choice(caratteristiche)
        
        setattr(self, caratteristica_da_aumentare, getattr(self, caratteristica_da_aumentare) + 1)
        # Ricalcola il modificatore corrispondente
        nome_modificatore = f"modificatore_{caratteristica_da_aumentare[:-5]}"  # Rimuovi "_base"
        setattr(self, nome_modificatore, self.calcola_modificatore(getattr(self, caratteristica_da_aumentare)))
        
        self.difesa += 1
        io.mostra_messaggio(f"\n*** {self.nome} è salito al livello {self.livello}! ***")
        io.mostra_messaggio(f"La sua {caratteristica_da_aumentare.replace('_base', '')}, difesa e salute massima sono aumentate!")

    def prova_abilita(self, abilita, difficolta):
        dado = Dado(20)
        tiro = dado.tira()
        
        # Ottieni il modificatore appropriato
        if abilita == "forza":
            modificatore = self.modificatore_forza
        elif abilita == "destrezza":
            modificatore = self.modificatore_destrezza
        # e così via...
        else:
            modificatore = getattr(self, f"modificatore_{abilita}", 0)
            
        risultato = tiro + modificatore
        io.mostra_messaggio(f"{self.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
        return risultato >= difficolta

    def tiro_salvezza(self, tipo, difficolta):
        return self.prova_abilita(tipo, difficolta)

    def calcola_modificatore(self, valore):
        return (valore - 10) // 2

    @property
    def forza(self):
        return self.modificatore_forza

    @forza.setter
    def forza(self, valore):
        self.modificatore_forza = valore
        
    @property
    def destrezza(self):
        return self.modificatore_destrezza
        
    @destrezza.setter
    def destrezza(self, valore):
        self.modificatore_destrezza = valore
        
    @property
    def costituzione(self):
        return self.modificatore_costituzione
        
    @costituzione.setter
    def costituzione(self, valore):
        self.modificatore_costituzione = valore
        
    @property
    def intelligenza(self):
        return self.modificatore_intelligenza
        
    @intelligenza.setter
    def intelligenza(self, valore):
        self.modificatore_intelligenza = valore
        
    @property
    def saggezza(self):
        return self.modificatore_saggezza
        
    @saggezza.setter
    def saggezza(self, valore):
        self.modificatore_saggezza = valore
        
    @property
    def carisma(self):
        return self.modificatore_carisma
        
    @carisma.setter
    def carisma(self, valore):
        self.modificatore_carisma = valore

    def imposta_posizione(self, mappa_nome_o_x, x_o_y=None, y=None):
        """
        Imposta la posizione dell'entità su una mappa specifica o solo le coordinate
        
        Supporta due modalità di chiamata:
        1. imposta_posizione(mappa_nome, x, y) - imposta mappa e coordinate
        2. imposta_posizione(x, y) - imposta solo le coordinate mantenendo la mappa corrente
        
        Args:
            mappa_nome_o_x: Nome della mappa o coordinata X
            x_o_y: Coordinata X o Y
            y: Coordinata Y o None
        """
        if y is None:
            # Vecchia modalità: imposta_posizione(x, y)
            x = mappa_nome_o_x
            y = x_o_y
            # Non modifichiamo mappa_corrente
        else:
            # Nuova modalità: imposta_posizione(mappa_nome, x, y)
            self.mappa_corrente = mappa_nome_o_x
            x = x_o_y
        
        self.x = x
        self.y = y
    
    def ottieni_posizione(self):
        """
        Restituisce la posizione corrente dell'entità
        
        Returns:
            tuple: Coordinate (x, y) o None se non impostata
        """
        if self.mappa_corrente:
            return (self.x, self.y)
        return None

    def modificatore_abilita(self, nome_abilita):
        """Calcola il modificatore totale di un'abilità considerando la competenza"""
        caratteristica = ABILITA_ASSOCIATE.get(nome_abilita.lower())
        if not caratteristica:
            io.mostra_messaggio(f"Abilità sconosciuta: {nome_abilita}")
            return 0

        modificatore_base = getattr(self, f"modificatore_{caratteristica}", 0)
        competenza_bonus = self.bonus_competenza if self.abilita_competenze.get(nome_abilita.lower()) else 0
        return modificatore_base + competenza_bonus

    def to_dict(self):
        """
        Converte l'entità in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dell'entità in formato dizionario
        """
        return {
            "nome": self.nome,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "token": self.token,
            "forza_base": self.forza_base,
            "destrezza_base": self.destrezza_base,
            "costituzione_base": self.costituzione_base,
            "intelligenza_base": self.intelligenza_base,
            "saggezza_base": self.saggezza_base,
            "carisma_base": self.carisma_base,
            "x": self.x,
            "y": self.y,
            "mappa_corrente": self.mappa_corrente,
            "abilita_competenze": self.abilita_competenze,
            "bonus_competenza": self.bonus_competenza,
            "difesa": self.difesa,
            "inventario": [obj.to_dict() if hasattr(obj, 'to_dict') else (obj if isinstance(obj, str) else obj.nome) for obj in self.inventario],
            "oro": self.oro,
            "esperienza": self.esperienza,
            "livello": self.livello,
            "arma": self.arma.to_dict() if self.arma and hasattr(self.arma, 'to_dict') else (self.arma if isinstance(self.arma, str) else (self.arma.nome if self.arma else None)),
            "armatura": self.armatura.to_dict() if self.armatura and hasattr(self.armatura, 'to_dict') else (self.armatura if isinstance(self.armatura, str) else (self.armatura.nome if self.armatura else None)),
            "accessori": [acc.to_dict() if hasattr(acc, 'to_dict') else (acc if isinstance(acc, str) else acc.nome) for acc in self.accessori],
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di Entita da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dell'entità
            
        Returns:
            Entita: Nuova istanza di Entita
        """
        entita = cls(
            nome=data.get("nome", "Sconosciuto"),
            hp=data.get("hp", 10),
            hp_max=data.get("hp_max", 10),
            forza_base=data.get("forza_base", 10),
            difesa=data.get("difesa", 0),
            destrezza_base=data.get("destrezza_base", 10),
            costituzione_base=data.get("costituzione_base", 10),
            intelligenza_base=data.get("intelligenza_base", 10),
            saggezza_base=data.get("saggezza_base", 10),
            carisma_base=data.get("carisma_base", 10),
            token=data.get("token", "E")
        )
        
        entita.x = data.get("x", 0)
        entita.y = data.get("y", 0)
        entita.mappa_corrente = data.get("mappa_corrente")
        entita.abilita_competenze = data.get("abilita_competenze", {})
        entita.bonus_competenza = data.get("bonus_competenza", 2)
        entita.oro = data.get("oro", 0)
        entita.esperienza = data.get("esperienza", 0)
        entita.livello = data.get("livello", 1)
        
        # Gli oggetti più complessi verranno gestiti dalle sottoclassi
        
        return entita

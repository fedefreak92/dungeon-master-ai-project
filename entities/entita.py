import random
from core.io_interface import TerminalIO

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
        
        # Contesto di gioco
        self.gioco = None
        
    def set_game_context(self, gioco):
        """
        Imposta il contesto di gioco per questa entità.
        
        Args:
            gioco: L'istanza del gioco
        """
        self.gioco = gioco
        
        # Propaga il contesto agli oggetti contenuti nell'inventario
        for item in self.inventario:
            if hasattr(item, 'set_game_context'):
                item.set_game_context(gioco)
                
    def subisci_danno(self, danno, gioco=None):
        """Metodo unificato per subire danno, considerando la difesa"""
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
        danno_effettivo = max(1, danno - self.difesa)
        self.hp = max(0, self.hp - danno_effettivo)
        
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"{self.nome} subisce {danno_effettivo} danni!")
            
        return self.hp > 0
        
    def attacca(self, bersaglio, gioco=None):
        """Metodo unificato per attaccare"""
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
        danno = self.modificatore_forza
        
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"{self.nome} attacca {bersaglio.nome} e infligge {danno} danni!")
            
        return bersaglio.subisci_danno(danno, game_ctx)
        
    def cura(self, quantita, gioco=None):
        """Cura l'entità"""
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
        self.hp = min(self.hp_max, self.hp + quantita)
        
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"{self.nome} recupera {quantita} punti vita!")
        
    def aggiungi_item(self, item):
        """Aggiunge un item all'inventario"""
        # Se l'item è una stringa, verifichiamo se corrisponde a un oggetto conosciuto
        if isinstance(item, str):
            from util.data_manager import get_data_manager
            from items.oggetto import Oggetto
            
            data_manager = get_data_manager()
            
            # Cerca nelle pozioni
            pozioni = data_manager.load_data("oggetti", "pozioni.json")
            for pozione in pozioni:
                if pozione["nome"] == item or (item == "Pozione" and pozione["nome"] == "Pozione di cura"):
                    # Crea un oggetto corrispondente
                    oggetto = Oggetto.from_dict(pozione)
                    self.inventario.append(oggetto)
                    return
                    
            # Se non trova corrispondenze, aggiungi come stringa
            self.inventario.append(item)
        else:
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
        
    def ferisci(self, danno, gioco):
        """Metodo alternativo per subire danno, per compatibilità"""
        return self.subisci_danno(danno, gioco)
        
    def aggiungi_oro(self, quantita, gioco=None):
        """Aggiunge oro all'entità"""
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
        self.oro += quantita
        
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"{self.nome} ha ricevuto {quantita} monete d'oro! (Totale: {self.oro})")
        
    def guadagna_esperienza(self, quantita, gioco=None):
        """Aggiunge esperienza e verifica se è possibile salire di livello"""
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
        self.esperienza += quantita
        
        # Verifica salita di livello: 100 * livello attuale
        esperienza_necessaria = 100 * self.livello
        
        if self.esperienza >= esperienza_necessaria:
            self.livello += 1
            self.esperienza -= esperienza_necessaria
            self._sali_livello(game_ctx)
            return True
        return False
        
    def _sali_livello(self, gioco=None):
        """Applica i miglioramenti per il salire di livello"""
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
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
        
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"\n*** {self.nome} è salito al livello {self.livello}! ***")
            game_ctx.io.mostra_messaggio(f"La sua {caratteristica_da_aumentare.replace('_base', '')}, difesa e salute massima sono aumentate!")

    def prova_abilita(self, abilita, difficolta, gioco=None):
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
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
        
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"{self.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
            
        return risultato >= difficolta

    def tiro_salvezza(self, tipo, difficolta, gioco=None):
        return self.prova_abilita(tipo, difficolta, gioco)

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

    def modificatore_abilita(self, nome_abilita, gioco):
        """Calcola il modificatore totale di un'abilità considerando la competenza"""
        caratteristica = ABILITA_ASSOCIATE.get(nome_abilita.lower())
        if not caratteristica:
            gioco.io.mostra_messaggio(f"Abilità sconosciuta: {nome_abilita}")
            return 0

        modificatore_base = getattr(self, f"modificatore_{caratteristica}", 0)
        competenza_bonus = self.bonus_competenza if self.abilita_competenze.get(nome_abilita.lower()) else 0
        return modificatore_base + competenza_bonus

    def to_dict(self, already_serialized=None):
        """
        Converte l'entità in un dizionario per la serializzazione.
        Gestisce riferimenti circolari attraverso il parametro already_serialized.
        
        Args:
            already_serialized (set, optional): Set di ID di oggetti già serializzati
            
        Returns:
            dict: Rappresentazione dell'entità in formato dizionario
        """
        # Per retrocompatibilità, se il metodo è chiamato con un numero errato di parametri
        # comportati come il vecchio metodo
        import inspect
        if already_serialized is not None and not isinstance(already_serialized, set):
            # Potrebbe essere un caso di chiamata errata, ignora il parametro
            already_serialized = None
            
        # Inizializza il set se non fornito
        if already_serialized is None:
            already_serialized = set()
            
        # Evita riferimenti circolari
        if id(self) in already_serialized:
            return {"reference_id": id(self), "nome": self.nome, "tipo": "riferimento"}
            
        # Aggiungi questo oggetto al set
        already_serialized.add(id(self))
        
        # Funzione per serializzare in modo sicuro
        def serialize_safely(item):
            if item is None:
                return None
            if not hasattr(item, 'to_dict'):
                if isinstance(item, (str, int, float, bool)):
                    return item
                return getattr(item, 'nome', str(item))
                
            # Tenta prima con already_serialized
            try:
                return item.to_dict(already_serialized)
            except TypeError:
                # Se fallisce, tenta senza parametro
                return item.to_dict()
        
        # Serializza liste in modo sicuro
        def serialize_list(items):
            result = []
            for item in items:
                result.append(serialize_safely(item))
            return result
        
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
            "inventario": serialize_list(self.inventario),
            "oro": self.oro,
            "esperienza": self.esperienza,
            "livello": self.livello,
            "arma": serialize_safely(self.arma),
            "armatura": serialize_safely(self.armatura),
            "accessori": serialize_list(self.accessori),
        }
    
    @classmethod
    def from_dict(cls, data, loaded_objects=None):
        """
        Crea un'istanza di Entità da un dizionario.
        Gestisce riferimenti circolari attraverso loaded_objects.
        
        Args:
            data (dict): Dizionario con i dati dell'entità
            loaded_objects (dict, optional): Dizionario di oggetti già caricati
            
        Returns:
            Entita: Nuova istanza di Entità
        """
        # Gestisci il caso dei riferimenti
        if data.get("tipo") == "riferimento" and "reference_id" in data:
            ref_id = data["reference_id"]
            if loaded_objects and ref_id in loaded_objects:
                return loaded_objects[ref_id]
            return None
        
        # Crea l'oggetto base
        entita = cls(
            nome=data.get("nome", "Sconosciuto"),
            hp=data.get("hp", 10),
            hp_max=data.get("hp_max", 10),
            forza_base=data.get("forza_base", 10),
            destrezza_base=data.get("destrezza_base", 10),
            costituzione_base=data.get("costituzione_base", 10),
            intelligenza_base=data.get("intelligenza_base", 10),
            saggezza_base=data.get("saggezza_base", 10),
            carisma_base=data.get("carisma_base", 10),
            difesa=data.get("difesa", 0),
            token=data.get("token", "E")
        )
        
        # Registra l'oggetto per riferimenti futuri
        if loaded_objects is not None:
            loaded_objects[id(entita)] = entita
        
        # Imposta attributi aggiuntivi
        entita.x = data.get("x", 0)
        entita.y = data.get("y", 0)
        entita.mappa_corrente = data.get("mappa_corrente", None)
        entita.abilita_competenze = data.get("abilita_competenze", {})
        entita.bonus_competenza = data.get("bonus_competenza", 2)
        entita.difesa = data.get("difesa", 0)
        entita.oro = data.get("oro", 0)
        entita.esperienza = data.get("esperienza", 0)
        entita.livello = data.get("livello", 1)
        
        # Gli oggetti complessi (inventario, arma, armatura, accessori) 
        # verranno gestiti nelle classi derivate
        
        return entita

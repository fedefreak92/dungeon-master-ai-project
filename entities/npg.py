from entities.giocatore import Giocatore
from items.oggetto import Oggetto
from entities.entita import Entita, ABILITA_ASSOCIATE
from util.data_manager import get_data_manager

class NPG(Entita):
    def __init__(self, nome, token=None):
        # Carica i dati dell'NPC dal file JSON
        self.data_manager = get_data_manager()
        self.npc_data = self.data_manager.get_npc_data(nome)
        
        # Usa il token fornito o quello definito nei dati, altrimenti usa "N" come default
        token = token or self.npc_data.get("token", "N")
        
        # Chiamiamo il costruttore della classe base
        super().__init__(nome, hp=10, hp_max=10, forza_base=13, difesa=1, token=token)
        
        # Attributi specifici per NPG
        self.stato_corrente = "default"
        self.background = ""
        self.professione = ""
        
        # Inizializzazioni specifiche per NPG
        self._inizializza_attributi()
        
        # Conversazioni non più caricate qui, ma dinamicamente quando necessario
        
    def _inizializza_attributi(self):
        """Inizializza attributi specifici per ogni NPG dai dati esterni"""
        # Se non abbiamo dati per questo NPC, mantieni i valori predefiniti
        if not self.npc_data:
            return
            
        # Imposta gli attributi dai dati caricati
        self.hp_max = self.npc_data.get("hp_max", 10)
        self.hp = self.hp_max
        self.oro = self.npc_data.get("oro", 0)
        self.forza_base = self.npc_data.get("forza_base", 10)
        self.difesa = self.npc_data.get("difesa", 1)
        self.livello = self.npc_data.get("livello", 1)
        
        # Imposta attributi opzionali se presenti nei dati
        if "destrezza_base" in self.npc_data:
            self.destrezza_base = self.npc_data["destrezza_base"]
        if "costituzione_base" in self.npc_data:
            self.costituzione_base = self.npc_data["costituzione_base"]
        if "intelligenza_base" in self.npc_data:
            self.intelligenza_base = self.npc_data["intelligenza_base"]
        if "saggezza_base" in self.npc_data:
            self.saggezza_base = self.npc_data["saggezza_base"]
        if "carisma_base" in self.npc_data:
            self.carisma_base = self.npc_data["carisma_base"]
            
        # Ricalcola tutti i modificatori
        self.modificatore_forza = self.calcola_modificatore(self.forza_base)
        self.modificatore_destrezza = self.calcola_modificatore(self.destrezza_base)
        self.modificatore_costituzione = self.calcola_modificatore(self.costituzione_base)
        self.modificatore_intelligenza = self.calcola_modificatore(self.intelligenza_base)
        self.modificatore_saggezza = self.calcola_modificatore(self.saggezza_base)
        self.modificatore_carisma = self.calcola_modificatore(self.carisma_base)
        
        # Imposta background e professione
        self.background = self.npc_data.get("background", "")
        self.professione = self.npc_data.get("professione", "")
        
        # Carica l'inventario
        self.inventario = []
        self.arma = None
        self.armatura = None
        self.accessori = []
        
        # Popola l'inventario
        for item_data in self.npc_data.get("inventario", []):
            oggetto = Oggetto(
                item_data["nome"],
                item_data["tipo"],
                item_data.get("statistiche", {}),
                item_data.get("valore", 0),
                item_data.get("descrizione", "")
            )
            self.inventario.append(oggetto)
            
            # Equipaggia automaticamente gli oggetti segnati come equipaggiati
            if item_data.get("equipaggiata", False):
                if item_data["tipo"] == "arma" and not self.arma:
                    self.arma = oggetto
                elif item_data["tipo"] == "armatura" and not self.armatura:
                    self.armatura = oggetto
                elif item_data["tipo"] == "accessorio":
                    self.accessori.append(oggetto)

    def cambia_stato(self, nuovo_stato):
        """
        Cambia lo stato del personaggio
        
        Args:
            nuovo_stato (str): Il nuovo stato del personaggio
        """
        self.stato_corrente = nuovo_stato

    def ottieni_conversazione(self, stato=None):
        """
        Ottiene i dati della conversazione per lo stato specificato
        
        Args:
            stato (str, optional): Lo stato della conversazione
            
        Returns:
            dict: Dati della conversazione o None se non esiste
        """
        # Se non viene specificato uno stato, usa lo stato corrente
        stato = stato or self.stato_corrente
        
        # Carica la conversazione dal file JSON
        conv_data = self.data_manager.get_npc_conversation(self.nome, stato)
        
        # Converti il formato dei dati dal file JSON al formato utilizzato internamente
        if conv_data:
            # Adatta il formato delle opzioni se necessario
            if "opzioni" in conv_data:
                options = []
                for opt in conv_data["opzioni"]:
                    # Gestisci sia il formato array di array che array di oggetti
                    if isinstance(opt, list):
                        # Se opt è una lista [testo, destinazione]
                        options.append((opt[0], opt[1]))
                    elif isinstance(opt, dict):
                        # Se opt è un dizionario {"testo": "...", "destinazione": "..."}
                        options.append((opt["testo"], opt["destinazione"]))
                    else:
                        # Formato non riconosciuto, ignora
                        continue
                conv_data["opzioni"] = options
            
            return conv_data
        
        return None
        
    def mostra_info(self):
        """
        Mostra le informazioni dell'NPG
        
        Returns:
            str: Informazioni formattate dell'NPG
        """
        info = f"=== {self.nome} ===\n"
        info += f"Professione: {self.professione}\n"
        info += f"Background: {self.background}\n"
        info += f"HP: {self.hp}/{self.hp_max}\n"
        info += f"Oro: {self.oro}\n"
        info += "Inventario:\n"
        for item in self.inventario:
            info += f"- {item.nome} ({item.tipo}): {item.descrizione}\n"
        return info

    def attacca(self, bersaglio, gioco=None):
        """Attacca un bersaglio utilizzando il metodo unificato"""
        # Usa il metodo della classe base per gestire l'attacco
        return super().attacca(bersaglio, gioco)

    def trasferisci_oro(self, giocatore, quantita, gioco=None):
        """
        Trasferisce oro dall'NPG al giocatore
        
        Args:
            giocatore (Giocatore): Il giocatore che riceve l'oro
            quantita (int): Quantità di oro da trasferire
            gioco: Riferimento all'oggetto gioco principale
            
        Returns:
            bool: True se il trasferimento è riuscito, False se l'NPG non ha abbastanza oro
        """
        if self.oro >= quantita:
            self.oro -= quantita
            giocatore.aggiungi_oro(quantita, gioco)
            return True
        return False

    def to_dict(self, already_serialized=None):
        """
        Converte l'NPG in un dizionario per la serializzazione.
        
        Args:
            already_serialized (set, optional): Set di ID di oggetti già serializzati
            
        Returns:
            dict: Rappresentazione dell'NPG in formato dizionario
        """
        # Ottieni il dizionario base dalla classe genitore
        data = super().to_dict(already_serialized)
        
        # Aggiungi attributi specifici di NPG
        data.update({
            "stato_corrente": self.stato_corrente,
            "background": self.background,
            "professione": self.professione,
            # Le conversazioni non vengono serializzate perché vengono caricate dinamicamente
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di NPG da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dell'NPG
            
        Returns:
            NPG: Nuova istanza di NPG
        """
        # Creiamo prima un'istanza di NPG solo con il nome
        npg = cls(
            nome=data.get("nome", "Sconosciuto"),
            token=data.get("token", "N")
        )
        
        # Impostiamo manualmente gli attributi serializzati
        npg.hp = data.get("hp", 10)
        npg.hp_max = data.get("hp_max", 10)
        npg.x = data.get("x", 0)
        npg.y = data.get("y", 0)
        npg.mappa_corrente = data.get("mappa_corrente")
        npg.abilita_competenze = data.get("abilita_competenze", {})
        npg.bonus_competenza = data.get("bonus_competenza", 2)
        npg.oro = data.get("oro", 0)
        npg.esperienza = data.get("esperienza", 0)
        npg.livello = data.get("livello", 1)
        npg.difesa = data.get("difesa", 0)
        
        # Impostiamo i valori base che sono stati serializzati
        npg.forza_base = data.get("forza_base", 10)
        npg.destrezza_base = data.get("destrezza_base", 10)
        npg.costituzione_base = data.get("costituzione_base", 10)
        npg.intelligenza_base = data.get("intelligenza_base", 10)
        npg.saggezza_base = data.get("saggezza_base", 10)
        npg.carisma_base = data.get("carisma_base", 10)
        
        # Ricalcoliamo i modificatori
        npg.modificatore_forza = npg.calcola_modificatore(npg.forza_base)
        npg.modificatore_destrezza = npg.calcola_modificatore(npg.destrezza_base)
        npg.modificatore_costituzione = npg.calcola_modificatore(npg.costituzione_base)
        npg.modificatore_intelligenza = npg.calcola_modificatore(npg.intelligenza_base)
        npg.modificatore_saggezza = npg.calcola_modificatore(npg.saggezza_base)
        npg.modificatore_carisma = npg.calcola_modificatore(npg.carisma_base)
        
        # Imposta attributi specifici
        npg.stato_corrente = data.get("stato_corrente", "default")
        npg.background = data.get("background", "")
        npg.professione = data.get("professione", "")
        
        return npg

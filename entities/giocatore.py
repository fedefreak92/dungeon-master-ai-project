import json
import os
from items.oggetto import Oggetto
from entities.entita import Entita, ABILITA_ASSOCIATE

class Giocatore(Entita):
    def __init__(self, nome, classe):
        # Inizializziamo valori specifici per il giocatore
        self.classe = classe
        
        # Carichiamo i dati delle classi dal JSON
        self.dati_classi = self._carica_dati_classi()
        
        # Otteniamo le statistiche base per la classe selezionata
        stats_base = self._ottieni_statistiche_classe(classe)
        
        # Chiamiamo il costruttore della classe base con valori dalla classe scelta
        super().__init__(nome, 
                         hp=stats_base.get("hp_base", 20), 
                         hp_max=stats_base.get("hp_base", 20), 
                         forza_base=stats_base.get("forza", 12), 
                         difesa=2, 
                         destrezza_base=stats_base.get("destrezza", 10), 
                         costituzione_base=stats_base.get("costituzione", 12), 
                         intelligenza_base=stats_base.get("intelligenza", 10), 
                         saggezza_base=stats_base.get("saggezza", 10), 
                         carisma_base=stats_base.get("carisma", 10), 
                         token="P")  # P per Player
        
        # Impostiamo altri valori diversi dai predefiniti di Entita
        self.oro = 100
        self.mana = stats_base.get("mana_base", 0)
        self.mana_max = stats_base.get("mana_base", 0)
        
        # Inizializza attributi per le missioni
        self.progresso_missioni = {}
        self.missioni_attive = []
        self.missioni_completate = []
        
        # Inizializza competenze in abilità specifiche per classe
        self._inizializza_competenze()
        
        # Attributi specifici per classe che non sono in Entita
        self._inizializza_per_classe()
        self._crea_inventario_base()
    
    def _carica_dati_classi(self):
        """Carica i dati delle classi dal file JSON"""
        percorso_file = os.path.join("data", "classes", "classes.json")
        try:
            with open(percorso_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # In caso di errore, restituiamo un dizionario vuoto
            return {}
    
    def _ottieni_statistiche_classe(self, classe):
        """Ottiene le statistiche base per la classe specificata"""
        if classe in self.dati_classi:
            return self.dati_classi[classe].get("statistiche_base", {})
        return {}
    
    def _inizializza_competenze(self):
        """Inizializza le competenze in abilità in base alla classe"""
        # Verifichiamo se la classe esiste nei dati delle classi
        if self.classe in self.dati_classi:
            # In futuro si potrebbe estendere per leggere le competenze dal JSON
            pass
        
        # Manteniamo le competenze codificate esistenti per compatibilità
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
        # Se la classe esiste nei dati delle classi
        if self.classe in self.dati_classi:
            dati_classe = self.dati_classi[self.classe]
            stats_base = dati_classe.get("statistiche_base", {})
            
            # Aggiorniamo le statistiche base con quelle dal JSON
            self.hp = dati_classe.get("hp_base", self.hp)
            self.hp_max = dati_classe.get("hp_base", self.hp_max)
            
            # Ricalcola i modificatori
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            self.modificatore_destrezza = self.calcola_modificatore(self.destrezza_base)
            self.modificatore_costituzione = self.calcola_modificatore(self.costituzione_base)
            self.modificatore_intelligenza = self.calcola_modificatore(self.intelligenza_base)
            self.modificatore_saggezza = self.calcola_modificatore(self.saggezza_base)
            self.modificatore_carisma = self.calcola_modificatore(self.carisma_base)
            
            # Attributo specifico del ladro
            if self.classe == "ladro":
                self.fortuna = 5
        else:
            # Gestione delle classi attualmente codificate per compatibilità
            if self.classe == "guerriero":
                self.hp += 5
                self.hp_max += 5
                self.forza_base += 4
                self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            elif self.classe == "mago":
                self.forza_base -= 2
                self.intelligenza_base = 16
                self.modificatore_forza = self.calcola_modificatore(self.forza_base)
                self.modificatore_intelligenza = self.calcola_modificatore(self.intelligenza_base)
            elif self.classe == "ladro":
                self.destrezza_base = 16
                self.modificatore_destrezza = self.calcola_modificatore(self.destrezza_base)
                self.fortuna = 5
    
    def _crea_inventario_base(self):
        """Crea un inventario base in base alla classe del personaggio"""
        # Oggetti comuni per tutti
        pozione = Oggetto("Pozione di cura", "cura", {"cura": 10}, 5, "Ripristina 10 punti vita")
        chiave = Oggetto("Chiave comune", "chiave", {}, 1, "Una chiave semplice che potrebbe aprire porte o forzieri")
        
        # Armi base per tutte le classi
        arma_base = None
        armatura_base = None
        
        # Se la classe esiste nei dati delle classi, usa l'equipaggiamento definito in JSON
        if self.classe in self.dati_classi:
            equipaggiamento = self.dati_classi[self.classe].get("equipaggiamento_iniziale", [])
            
            # Crea oggetti in base all'equipaggiamento definito nel JSON
            if equipaggiamento and len(equipaggiamento) >= 3:
                arma_nome = equipaggiamento[0]
                armatura_nome = equipaggiamento[2] if len(equipaggiamento) > 2 else "Abiti semplici"
                
                if "spada" in arma_nome.lower() or "mazza" in arma_nome.lower():
                    arma_base = Oggetto(arma_nome, "arma", {"forza": 3}, 15, f"Un {arma_nome.lower()} robusto")
                elif "bastone" in arma_nome.lower():
                    arma_base = Oggetto(arma_nome, "arma", {"forza": 1, "intelligenza": 2}, 20, f"Un {arma_nome.lower()} che amplifica i poteri magici")
                elif "pugnale" in arma_nome.lower():
                    arma_base = Oggetto(arma_nome, "arma", {"forza": 2, "destrezza": 1}, 12, f"Un {arma_nome.lower()} affilato e maneggevole")
                else:
                    arma_base = Oggetto(arma_nome, "arma", {"forza": 2}, 10, f"Un {arma_nome.lower()}")
                
                if "maglia" in armatura_nome.lower() or "pesante" in armatura_nome.lower():
                    armatura_base = Oggetto(armatura_nome, "armatura", {"difesa": 3}, 25, f"Una {armatura_nome.lower()} che offre buona protezione")
                elif "veste" in armatura_nome.lower() or "mago" in armatura_nome.lower():
                    armatura_base = Oggetto(armatura_nome, "armatura", {"difesa": 1, "intelligenza": 1}, 15, f"Una {armatura_nome.lower()} leggera con proprietà magiche")
                elif "cuoio" in armatura_nome.lower() or "leggera" in armatura_nome.lower():
                    armatura_base = Oggetto(armatura_nome, "armatura", {"difesa": 2, "destrezza": 1}, 18, f"Un'armatura leggera che non limita i movimenti")
                else:
                    armatura_base = Oggetto(armatura_nome, "armatura", {"difesa": 1}, 10, f"Un {armatura_nome.lower()}")
            else:
                # Equipaggiamento predefinito se non definito nel JSON
                arma_base = Oggetto("Bastone da viaggio", "arma", {"forza": 1}, 5, "Un semplice bastone di legno")
                armatura_base = Oggetto("Abiti robusti", "armatura", {"difesa": 1}, 5, "Vestiti rinforzati che offrono minima protezione")
        else:
            # Usa il codice esistente per le classi predefinite
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
        elif self.classe == "chierico":
            simbolo = Oggetto("Simbolo sacro", "accessorio", {"saggezza": 1}, 10, "Un simbolo sacro che aumenta la saggezza")
            self.inventario.append(simbolo)
            simbolo.equipaggia(self)

    def attacca(self, nemico, gioco=None):
        """Attacca un nemico utilizzando il metodo unificato"""
        # Usa il metodo della classe base per gestire l'attacco
        return super().attacca(nemico, gioco)
    
    def _sali_livello(self, gioco=None):
        """Override del metodo della classe base per un messaggio personalizzato"""
        # Chiamiamo prima il metodo della classe base
        super()._sali_livello(gioco)
        # Poi aggiungiamo il nostro messaggio personalizzato
        
        # Aggiungi il messaggio usando l'interfaccia I/O del gioco
        if gioco:
            gioco.io.mostra_messaggio("Sei diventato più forte!")

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
    
    def interagisci_con_oggetto_adiacente(self, gestore_mappe, gioco=None):
        """
        Interagisce con l'oggetto adiacente al giocatore, se presente
        
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
            oggetto = mappa.ottieni_oggetto_a(x, y)
            if oggetto:
                if gioco and gioco.io:
                    gioco.io.mostra_messaggio(f"Interagisci con {oggetto.nome}")
                oggetto.interagisci(self)
                return True
            
        if gioco and gioco.io:
            gioco.io.mostra_messaggio("Non ci sono oggetti con cui interagire nelle vicinanze.")
        return False
    
    def interagisci_con_npg_adiacente(self, gestore_mappe, gioco=None):
        """
        Interagisce con l'NPG adiacente al giocatore, se presente
        
        Args:
            gestore_mappe: Gestore delle mappe di gioco
            gioco: Riferimento all'oggetto gioco principale (opzionale se memorizzato)
            
        Returns:
            bool: True se è avvenuta un'interazione, False altrimenti
        """
        # Usa il contesto di gioco memorizzato se non viene fornito
        game_ctx = gioco if gioco else getattr(self, 'gioco', None)
        
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
                if game_ctx and game_ctx.io:
                    game_ctx.io.mostra_messaggio(f"Parli con {npg.nome}")
                from states.dialogo import DialogoState
                game_ctx.push_stato(DialogoState(npg))
                return True
            
        if game_ctx and game_ctx.io:
            game_ctx.io.mostra_messaggio("Non ci sono personaggi con cui parlare nelle vicinanze.")
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

    def to_dict(self, already_serialized=None):
        """
        Converte il giocatore in un dizionario per la serializzazione.
        
        Args:
            already_serialized (set, optional): Set di ID di oggetti già serializzati
            
        Returns:
            dict: Rappresentazione del giocatore in formato dizionario
        """
        # Ottieni il dizionario base dalla classe genitore
        data = super().to_dict(already_serialized)
        
        # Aggiungi attributi specifici del giocatore
        data.update({
            "classe": self.classe,
            "progresso_missioni": self.progresso_missioni,
            "missioni_attive": self.missioni_attive,
            "missioni_completate": self.missioni_completate,
            "posizione": [self.x, self.y],  # Per compatibilità
            "mana": getattr(self, "mana", 0),
            "mana_max": getattr(self, "mana_max", 0)
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di Giocatore da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati del giocatore
            
        Returns:
            Giocatore: Nuova istanza di Giocatore
        """
        # Estrai i dati specifici della sottoclasse
        nome = data.get("nome", "Sconosciuto")
        classe = data.get("classe", "guerriero")
        
        # Crea l'istanza con i parametri base
        giocatore = cls(nome, classe)
        
        # Imposta gli attributi base usando la classe base
        # Ignoriamo l'inizializzazione che fa Entita.from_dict
        # perché il costruttore di Giocatore ha una logica specifica
        
        # Imposta gli attributi base
        giocatore.hp = data.get("hp", giocatore.hp)
        giocatore.hp_max = data.get("hp_max", giocatore.hp_max)
        giocatore.forza_base = data.get("forza_base", giocatore.forza_base)
        giocatore.destrezza_base = data.get("destrezza_base", giocatore.destrezza_base)
        giocatore.costituzione_base = data.get("costituzione_base", giocatore.costituzione_base)
        giocatore.intelligenza_base = data.get("intelligenza_base", giocatore.intelligenza_base)
        giocatore.saggezza_base = data.get("saggezza_base", giocatore.saggezza_base)
        giocatore.carisma_base = data.get("carisma_base", giocatore.carisma_base)
        
        # Imposta i modificatori
        giocatore.modificatore_forza = giocatore.calcola_modificatore(giocatore.forza_base)
        giocatore.modificatore_destrezza = giocatore.calcola_modificatore(giocatore.destrezza_base)
        giocatore.modificatore_costituzione = giocatore.calcola_modificatore(giocatore.costituzione_base)
        giocatore.modificatore_intelligenza = giocatore.calcola_modificatore(giocatore.intelligenza_base)
        giocatore.modificatore_saggezza = giocatore.calcola_modificatore(giocatore.saggezza_base)
        giocatore.modificatore_carisma = giocatore.calcola_modificatore(giocatore.carisma_base)
        
        # Imposta posizione
        if "posizione" in data and isinstance(data["posizione"], list) and len(data["posizione"]) >= 2:
            giocatore.x, giocatore.y = data["posizione"]
        else:
            giocatore.x = data.get("x", 0)
            giocatore.y = data.get("y", 0)
            
        giocatore.mappa_corrente = data.get("mappa_corrente")
        
        # Ripristina altri attributi
        giocatore.abilita_competenze = data.get("abilita_competenze", {})
        giocatore.bonus_competenza = data.get("bonus_competenza", 2)
        giocatore.difesa = data.get("difesa", 0)
        giocatore.oro = data.get("oro", 0)
        giocatore.esperienza = data.get("esperienza", 0)
        giocatore.livello = data.get("livello", 1)
        
        # Gestisci missioni
        giocatore.progresso_missioni = data.get("progresso_missioni", {})
        giocatore.missioni_attive = data.get("missioni_attive", [])
        giocatore.missioni_completate = data.get("missioni_completate", [])
        
        # Caricamento dell'inventario e dell'equipaggiamento richiede oggetti
        # Questo è fatto esternamente o in modo più complesso
        from items.oggetto import Oggetto
        
        # Gestisci inventario
        inventario_raw = data.get("inventario", [])
        inventario = []
        
        for item in inventario_raw:
            if isinstance(item, dict):
                inventario.append(Oggetto.from_dict(item))
            elif isinstance(item, str):
                # Crea un oggetto generico se solo il nome è disponibile
                inventario.append(Oggetto(item, "comune"))
                
        giocatore.inventario = inventario
        
        # Ripristina arma
        arma_data = data.get("arma")
        if isinstance(arma_data, dict):
            giocatore.arma = Oggetto.from_dict(arma_data)
        elif isinstance(arma_data, str):
            giocatore.arma = Oggetto(arma_data, "arma")
        
        # Ripristina armatura
        armatura_data = data.get("armatura")
        if isinstance(armatura_data, dict):
            giocatore.armatura = Oggetto.from_dict(armatura_data)
        elif isinstance(armatura_data, str):
            giocatore.armatura = Oggetto(armatura_data, "armatura")
            
        # Ripristina accessori
        accessori_data = data.get("accessori", [])
        accessori = []
        
        for acc in accessori_data:
            if isinstance(acc, dict):
                accessori.append(Oggetto.from_dict(acc))
            elif isinstance(acc, str):
                accessori.append(Oggetto(acc, "accessorio"))
                
        giocatore.accessori = accessori
        
        return giocatore

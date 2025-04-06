import json
import os
import random
from entities.entita import Entita

class Nemico(Entita):
    def __init__(self, nome, hp=10, danno=2, token="M", forza_base=None, difesa=0, tipo_mostro=None):
        # Se viene fornito un tipo_mostro, carica i dati dal JSON
        if tipo_mostro:
            dati_mostro = self._carica_dati_mostro(tipo_mostro)
            if dati_mostro:
                nome = dati_mostro.get("nome", nome)
                hp = dati_mostro.get("statistiche", {}).get("hp", hp)
                forza_base = dati_mostro.get("statistiche", {}).get("forza", 10 + danno * 2)
                difesa = dati_mostro.get("statistiche", {}).get("difesa", 0)
                token = dati_mostro.get("token", token)
                
                # Attributi specifici dal JSON
                self.descrizione = dati_mostro.get("descrizione", "")
                self.armi = dati_mostro.get("armi", [])
                self.armatura = dati_mostro.get("armatura", "")
                self.valore_esperienza = dati_mostro.get("esperienza", 50)  # Rinominiamo per evitare conflitti
                self.tipo_mostro = tipo_mostro
                
                # DEBUG
                print(f"DEBUG Nemico - Caricamento {tipo_mostro}: esperienza={self.valore_esperienza}")
                
                # Altre statistiche dal JSON
                destrezza_base = dati_mostro.get("statistiche", {}).get("destrezza", 10)
                costituzione_base = dati_mostro.get("statistiche", {}).get("costituzione", 10)
                intelligenza_base = dati_mostro.get("statistiche", {}).get("intelligenza", 6)
                saggezza_base = dati_mostro.get("statistiche", {}).get("saggezza", 8)
                carisma_base = dati_mostro.get("statistiche", {}).get("carisma", 6)
                
                # Chiamiamo il costruttore con i dati caricati dal JSON
                super().__init__(nome, hp=hp, hp_max=hp, forza_base=forza_base, difesa=difesa, token=token,
                                 destrezza_base=destrezza_base, costituzione_base=costituzione_base, 
                                 intelligenza_base=intelligenza_base, saggezza_base=saggezza_base, 
                                 carisma_base=carisma_base)
                
                # Imposta l'oro in base al JSON
                self.oro = dati_mostro.get("oro", 10)
                return
        
        # Se non viene fornito un tipo_mostro o non viene trovato nel JSON, usa i valori predefiniti
        if forza_base is None:
            forza_base = 10 + danno * 2
            
        # Chiamiamo il costruttore della classe base con i valori predefiniti
        super().__init__(nome, hp=hp, hp_max=hp, forza_base=forza_base, difesa=difesa, token=token)
        
        # Attributi base
        self.descrizione = ""
        self.armi = []
        self.armatura = ""
        self.valore_esperienza = 50  # Rinominiamo per evitare conflitti
        self.tipo_mostro = None
        
        # Imposta l'oro base
        self.oro = 10
    
    def _carica_dati_mostro(self, tipo_mostro):
        """Carica i dati di un mostro dal file JSON"""
        percorso_file = os.path.join("data", "monsters", "monsters.json")
        try:
            with open(percorso_file, "r", encoding="utf-8") as file:
                mostri = json.load(file)
                return mostri.get(tipo_mostro, None)
        except (FileNotFoundError, json.JSONDecodeError):
            # In caso di errore, restituisci None
            return None
    
    @classmethod
    def crea_casuale(cls, difficolta=None):
        """
        Crea un nemico casuale in base alla difficoltà specificata.
        
        Args:
            difficolta (str, optional): La difficoltà del nemico ('facile', 'medio', 'difficile').
                                       Se None, sceglie un nemico casuale di qualsiasi difficoltà.
        
        Returns:
            Nemico: Un'istanza di nemico casuale.
        """
        percorso_file = os.path.join("data", "monsters", "monsters.json")
        try:
            with open(percorso_file, "r", encoding="utf-8") as file:
                mostri = json.load(file)
                
                # Filtra i mostri in base alla difficoltà
                if difficolta:
                    mostri_filtrati = {k: v for k, v in mostri.items() 
                                      if v.get("difficolta", "medio") == difficolta}
                    if not mostri_filtrati:
                        mostri_filtrati = mostri  # Se non ci sono mostri della difficoltà richiesta, usa tutti
                else:
                    mostri_filtrati = mostri
                
                # Scegli un mostro casuale
                if mostri_filtrati:
                    tipo_mostro = random.choice(list(mostri_filtrati.keys()))
                    return cls(nome="", tipo_mostro=tipo_mostro)
                else:
                    # Se non ci sono mostri nel JSON, crea un nemico generico
                    return cls("Mostro Generico", 15, 3)
        except (FileNotFoundError, json.JSONDecodeError):
            # In caso di errore, crea un nemico generico
            return cls("Mostro Generico", 15, 3)
    
    @classmethod
    def ottieni_tipi_mostri(cls):
        """
        Ottiene la lista dei tipi di mostri disponibili nel file JSON.
        
        Returns:
            list: Lista dei tipi di mostri disponibili.
        """
        percorso_file = os.path.join("data", "monsters", "monsters.json")
        try:
            with open(percorso_file, "r", encoding="utf-8") as file:
                mostri = json.load(file)
                return list(mostri.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            # In caso di errore, restituisci una lista vuota
            return []
    
    def attacca(self, giocatore, gioco=None):
        """Attacca il giocatore utilizzando il metodo unificato"""
        # L'attacco è ora gestito completamente in CombattimentoState._attacco_nemico
        # Questo metodo è mantenuto per retrocompatibilità
        return super().attacca(giocatore, gioco)
    
    def to_dict(self):
        """
        Converte il nemico in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione del nemico in formato dizionario
        """
        data = super().to_dict()
        data.update({
            "descrizione": self.descrizione,
            "armi": self.armi,
            "armatura": self.armatura,
            "esperienza": self.valore_esperienza,
            "tipo_mostro": self.tipo_mostro
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di Nemico da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati del nemico
            
        Returns:
            Nemico: Nuova istanza di Nemico
        """
        # Se abbiamo un tipo_mostro, usiamo quello per ricaricare i dati
        if "tipo_mostro" in data and data["tipo_mostro"]:
            nemico = cls(nome="", tipo_mostro=data["tipo_mostro"])
            
            # Aggiorna eventuali valori specifici
            if "hp" in data:
                nemico.hp = data["hp"]
            if "nome" in data:
                nemico.nome = data["nome"]
            
            return nemico
        
        # Altrimenti creiamo un nemico con i dati dal dizionario
        nome = data.get("nome", "Mostro Sconosciuto")
        hp = data.get("hp", 10)
        forza_base = data.get("forza_base", 14)
        difesa = data.get("difesa", 0)
        token = data.get("token", "M")
        
        nemico = cls(nome, hp, 2, token, forza_base, difesa)  # 2 è un valore di danno predefinito
        
        # Aggiorna altri attributi
        nemico.descrizione = data.get("descrizione", "")
        nemico.armi = data.get("armi", [])
        nemico.armatura = data.get("armatura", "")
        nemico.valore_esperienza = data.get("esperienza", 50)
        nemico.tipo_mostro = data.get("tipo_mostro", None)
        nemico.oro = data.get("oro", 10)
        
        return nemico

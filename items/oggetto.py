class Oggetto:
    def __init__(self, nome, tipo, effetto=None, valore=0, descrizione=""):
        self.nome = nome
        self.tipo = tipo
        self.effetto = effetto or {}
        self.valore = valore
        self.descrizione = descrizione
        
    def __str__(self):
        return f"{self.nome} ({self.descrizione})"
    
    def __repr__(self):
        return f"Oggetto(nome={self.nome}, tipo={self.tipo}, effetto={self.effetto}, valore={self.valore}, descrizione={self.descrizione})"

    def usa(self, giocatore, gioco=None):
        if self.tipo == "cura":
            giocatore.cura(self.effetto.get("cura", 0), gioco)
            if gioco:
                gioco.io.mostra_messaggio(f"Usi {self.nome} e recuperi {self.effetto.get('cura', 0)} HP.")
            giocatore.rimuovi_item(self.nome)
        elif self.tipo == "cura_leggera":
            giocatore.cura(self.effetto.get("cura_leggera", 5), gioco)
            if gioco:
                gioco.io.mostra_messaggio(f"Usi {self.nome} e recuperi {self.effetto.get('cura_leggera', 5)} HP.")
            giocatore.rimuovi_item(self.nome)
        elif self.tipo == "cura_grave":
            giocatore.cura(self.effetto.get("cura_grave", 15), gioco)
            if gioco:
                gioco.io.mostra_messaggio(f"Usi {self.nome} e recuperi {self.effetto.get('cura_grave', 15)} HP.")
            giocatore.rimuovi_item(self.nome)
        elif self.tipo == "arma":
            self.equipaggia(giocatore, gioco)
        elif self.tipo == "armatura":
            self.equipaggia(giocatore, gioco)
        elif self.tipo == "chiave":
            if gioco:
                gioco.io.mostra_messaggio(f"Usi la chiave {self.nome}, ma non succede nulla... per ora.")
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"L'oggetto {self.nome} non può essere usato direttamente.")
            return False
        return True

    def vendi(self, giocatore, gioco):
        giocatore.aggiungi_oro(self.valore, gioco)
        giocatore.rimuovi_item(self.nome)
        gioco.io.mostra_messaggio(f"Hai venduto {self.nome} per {self.valore} monete d'oro")
    
    def equipaggia(self, giocatore, gioco=None):
        # Versione silenziosa se non viene fornito gioco
        if self.tipo == "arma":
            # Rimuovo effetti dell'arma precedente se presente
            if giocatore.arma:
                giocatore.forza -= giocatore.arma.effetto.get("forza", 0)
            giocatore.arma = self
            giocatore.forza += self.effetto.get("forza", 0)
            if gioco:
                gioco.io.mostra_messaggio(f"Hai equipaggiato {self.nome}. La tua forza aumenta di {self.effetto.get('forza', 0)}!")
        elif self.tipo == "armatura":
            # Rimuovo effetti dell'armatura precedente se presente
            if giocatore.armatura:
                giocatore.difesa -= giocatore.armatura.effetto.get("difesa", 0)
            giocatore.armatura = self
            giocatore.difesa += self.effetto.get("difesa", 0)
            if gioco:
                gioco.io.mostra_messaggio(f"Hai indossato {self.nome}. La tua difesa aumenta di {self.effetto.get('difesa', 0)}!")
        elif self.tipo == "accessorio":
            giocatore.accessori.append(self)
            # Applica eventuali effetti degli accessori
            for stat, valore in self.effetto.items():
                if hasattr(giocatore, stat):
                    setattr(giocatore, stat, getattr(giocatore, stat) + valore)
            if gioco:
                gioco.io.mostra_messaggio(f"Hai equipaggiato {self.nome} come accessorio.")

    def rimuovi(self, giocatore, gioco=None):
        # Versione silenziosa se non viene fornito gioco
        if self.tipo == "arma":
            if giocatore.arma:
                giocatore.forza -= giocatore.arma.effetto.get("forza", 0)
            giocatore.arma = None
            if gioco:
                gioco.io.mostra_messaggio(f"Hai rimosso l'arma {self.nome}.")
        elif self.tipo == "armatura":
            if giocatore.armatura:
                giocatore.difesa -= giocatore.armatura.effetto.get("difesa", 0)
            giocatore.armatura = None
            if gioco:
                gioco.io.mostra_messaggio(f"Hai rimosso l'armatura {self.nome}.")
        elif self.tipo == "accessorio":
            if self in giocatore.accessori:
                # Rimuovi eventuali effetti degli accessori
                for stat, valore in self.effetto.items():
                    if hasattr(giocatore, stat):
                        setattr(giocatore, stat, getattr(giocatore, stat) - valore)
                giocatore.accessori.remove(self)
            if gioco:
                gioco.io.mostra_messaggio(f"Hai rimosso l'accessorio {self.nome}.")
    
    def to_dict(self):
        """
        Converte l'oggetto in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dell'oggetto in formato dizionario
        """
        return {
            "nome": self.nome,
            "tipo": self.tipo,
            "effetto": self.effetto,
            "valore": self.valore,
            "descrizione": self.descrizione
        }
    
    @classmethod
    def from_dict(cls, dati):
        """
        Crea un'istanza di Oggetto da un dizionario.
        
        Args:
            dati (dict): Dizionario con i dati dell'oggetto
            
        Returns:
            Oggetto: Nuova istanza di Oggetto
        """
        return cls(
            nome=dati["nome"],
            tipo=dati["tipo"],
            effetto=dati.get("effetto", {}),
            valore=dati.get("valore", 0),
            descrizione=dati.get("descrizione", "")
        )
        
    # Metodo di compatibilità con il nome precedente
    @classmethod 
    def da_dizionario(cls, dati):
        """Alias per retrocompatibilità"""
        return cls.from_dict(dati)
    
    

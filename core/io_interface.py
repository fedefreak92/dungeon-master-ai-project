from abc import ABC, abstractmethod

# Interfaccia astratta per I/O del gioco
class GameIO(ABC):
    def __init__(self):
        self.ultimo_input = None
    
    @abstractmethod
    def mostra_messaggio(self, testo: str):
        """Mostra un messaggio narrativo del gioco"""
        pass

    @abstractmethod
    def messaggio_sistema(self, testo: str):
        """Mostra un messaggio tecnico/di sistema"""
        pass
        
    @abstractmethod
    def messaggio_errore(self, testo: str):
        """Mostra un messaggio di errore"""
        pass

    @abstractmethod
    def richiedi_input(self, prompt: str = "") -> str:
        pass
    
    def get_ultimo_input(self) -> str:
        """Restituisce l'ultimo input inserito"""
        return self.ultimo_input
        
    def get_output_structured(self) -> list:
        """
        Restituisce l'output strutturato in formato lista di dizionari
        [
            {"tipo": "sistema", "testo": "Hai aperto il forziere"},
            {"tipo": "narrativo", "testo": "Dentro trovi una pergamena"}
        ]
        """
        # Implementazione di default vuota
        return []

# Implementazione base per terminale
class TerminalIO(GameIO):
    def __init__(self):
        super().__init__()
        self.buffer = []
        
    def mostra_messaggio(self, testo: str):
        print(testo)
        self.buffer.append({"tipo": "narrativo", "testo": testo})
        
    def messaggio_sistema(self, testo: str):
        print(f"[SISTEMA] {testo}")
        self.buffer.append({"tipo": "sistema", "testo": testo})
        
    def messaggio_errore(self, testo: str):
        print(f"[ERRORE] {testo}")
        self.buffer.append({"tipo": "errore", "testo": testo})

    def richiedi_input(self, prompt: str = "") -> str:
        self.ultimo_input = input(prompt)
        self.buffer.append({"tipo": "prompt", "testo": prompt})
        return self.ultimo_input
        
    def get_output_structured(self) -> list:
        """Restituisce l'output strutturato come lista di dizionari"""
        return self.buffer
        
    def clear(self):
        """Pulisce il buffer dei messaggi"""
        self.buffer = []
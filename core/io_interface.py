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

# Implementazione base per terminale
class TerminalIO(GameIO):
    def __init__(self):
        super().__init__()
        
    def mostra_messaggio(self, testo: str):
        print(testo)
        
    def messaggio_sistema(self, testo: str):
        print(f"[SISTEMA] {testo}")
        
    def messaggio_errore(self, testo: str):
        print(f"[ERRORE] {testo}")

    def richiedi_input(self, prompt: str = "") -> str:
        self.ultimo_input = input(prompt)
        return self.ultimo_input
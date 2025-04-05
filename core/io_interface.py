from abc import ABC, abstractmethod

# Interfaccia astratta per I/O del gioco
class GameIO(ABC):
    @abstractmethod
    def mostra_messaggio(self, testo: str):
        pass

    @abstractmethod
    def richiedi_input(self, prompt: str = "") -> str:
        pass

# Implementazione base per terminale
class TerminalIO(GameIO):
    def mostra_messaggio(self, testo: str):
        print(testo)

    def richiedi_input(self, prompt: str = "") -> str:
        return input(prompt)
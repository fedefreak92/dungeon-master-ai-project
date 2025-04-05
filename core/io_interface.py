from abc import ABC, abstractmethod

# Interfaccia astratta per I/O del gioco
class GameIO(ABC):
    """Interfaccia astratta per gestire l'input e l'output del gioco.

    Questa classe astratta definisce i metodi necessari per interagire con l'utente,
    sia per mostrare messaggi che per richiedere input.
    """
    @abstractmethod
    def mostra_messaggio(self, testo: str):
        pass

    @abstractmethod
    def richiedi_input(self, prompt: str = "") -> str:
        pass

# Implementazione base per terminale
class TerminalIO(GameIO):
    """Implementazione di GameIO per l'interazione tramite terminale.

    Questa classe gestisce l'input e l'output del gioco tramite la console.
    """
    def mostra_messaggio(self, testo: str):
        print(testo)

    def richiedi_input(self, prompt: str = "") -> str:
        return input(prompt)
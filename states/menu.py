from states.base_state import BaseState
from states.combattimento import CombattimentoState

class MenuState(BaseState):
    def esegui(self, gioco):
        gioco.io.mostra_messaggio("\n=== Menu Principale ===")
        gioco.io.mostra_messaggio("1. Inizia Gioco")
        gioco.io.mostra_messaggio("2. Esci")
        
        scelta = gioco.io.richiedi_input("Scegli un'opzione: ")
        
        if scelta == "1":
            gioco.cambia_stato(CombattimentoState())
        elif scelta == "2":
            gioco.running = False
        else:
            gioco.io.messaggio_errore("Scelta non valida!") 
            
    def to_dict(self):
        """
        Converte lo stato in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dello stato in formato dizionario
        """
        # Utilizza il metodo base perché MenuState non ha attributi aggiuntivi
        return super().to_dict()

    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di MenuState da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            
        Returns:
            MenuState: Nuova istanza dello stato
        """
        return cls() 
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
            gioco.io.mostra_messaggio("Scelta non valida!") 
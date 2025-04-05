from entities.giocatore import Giocatore
from states.combattimento import CombattimentoState
from states.menu import MenuState
from core.game import Game
from states.taverna import TavernaState
from util.funzioni_utili import avanti
from items.oggetto import Oggetto
from entities.entita import Entita
from world.mappa import Mappa
from world.gestore_mappe import GestitoreMappe
from core.io_interface import TerminalIO


def main():
    # Crea un oggetto temporaneo per l'I/O iniziale
    io_temp = TerminalIO()
    io_temp.mostra_messaggio("Benvenuto avventuriero!")
    
    # Mostra menu iniziale
    io_temp.mostra_messaggio("1. Nuova Partita")
    io_temp.mostra_messaggio("2. Carica Partita")
    scelta = io_temp.richiedi_input("> ")

    if scelta == "2":
        # Crea un gioco temporaneo solo per il caricamento
        gioco_temp = Game(None, None)
        
        if gioco_temp.carica():
            # Se il caricamento è riuscito, crea il gioco vero con lo stato iniziale
            gioco = Game(gioco_temp.giocatore, TavernaState())
            # Imposta la mappa corrente
            gioco.gestore_mappe.imposta_mappa_attuale(gioco.giocatore.mappa_corrente)
        else:
            # Se il caricamento fallisce, crea una nuova partita
            io_temp.mostra_messaggio("Creazione di una nuova partita...")
            nome = io_temp.richiedi_input("Come ti chiami? ")
            classe = io_temp.richiedi_input("Che classe sei? Es. guerriero o mago o ladro").lower()
            giocatore = Giocatore(nome, classe)
            gioco = Game(giocatore, TavernaState())
    else:
        # Chiedi input iniziale
        nome = io_temp.richiedi_input("Come ti chiami? ")
        classe = io_temp.richiedi_input("Che classe sei? Es. guerriero o mago o ladro").lower()
        giocatore = Giocatore(nome, classe)
        
        # Crea il gioco con il giocatore
        gioco = Game(giocatore, TavernaState())
    
    gioco.esegui()
    
    # Fine del gioco
    gioco.io.mostra_messaggio("\n=== Fine dello spettacolo! ===")
    avanti(gioco)

if __name__ == "__main__":
    main()

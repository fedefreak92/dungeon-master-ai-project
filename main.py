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
    # Crea un oggetto per l'I/O che verrà utilizzato per tutta l'applicazione
    io_handler = TerminalIO()
    
    # Creazione oggetto temporaneo gioco per i messaggi iniziali
    gioco_temp = Game(None, None, io_handler, e_temporaneo=True)
    
    gioco_temp.io.mostra_messaggio("Benvenuto avventuriero!")
    
    # Mostra menu iniziale
    gioco_temp.io.mostra_messaggio("1. Nuova Partita")
    gioco_temp.io.mostra_messaggio("2. Carica Partita")
    scelta = gioco_temp.io.richiedi_input("> ")

    if scelta == "2":
        # Crea un gioco temporaneo solo per il caricamento, passando l'io_handler
        gioco_temp = Game(None, None, io_handler, e_temporaneo=True)
        
        if gioco_temp.carica():
            # Se il caricamento è riuscito, crea il gioco vero con lo stato iniziale
            gioco = Game(gioco_temp.giocatore, TavernaState(), io_handler)
            # Imposta il contesto di gioco nel giocatore
            if hasattr(gioco.giocatore, 'set_game_context'):
                gioco.giocatore.set_game_context(gioco)
            # Imposta la mappa corrente
            gioco.gestore_mappe.imposta_mappa_attuale(gioco.giocatore.mappa_corrente)
        else:
            # Se il caricamento fallisce, crea una nuova partita
            gioco_temp.io.mostra_messaggio("Creazione di una nuova partita...")
            nome = gioco_temp.io.richiedi_input("Come ti chiami? ")
            classe = gioco_temp.io.richiedi_input("Che classe sei? Es. guerriero o mago o ladro").lower()
            giocatore = Giocatore(nome, classe)
            gioco = Game(giocatore, TavernaState(), io_handler)
            # Imposta il contesto di gioco nel giocatore
            if hasattr(gioco.giocatore, 'set_game_context'):
                gioco.giocatore.set_game_context(gioco)
    else:
        # Chiedi input iniziale
        nome = gioco_temp.io.richiedi_input("Come ti chiami? ")
        classe = gioco_temp.io.richiedi_input("Che classe sei? Es. guerriero o mago o ladro").lower()
        giocatore = Giocatore(nome, classe)
        
        # Crea il gioco con il giocatore
        gioco = Game(giocatore, TavernaState(), io_handler)
        # Imposta il contesto di gioco nel giocatore
        if hasattr(gioco.giocatore, 'set_game_context'):
            gioco.giocatore.set_game_context(gioco)
    
    gioco.esegui()
    
    # Fine del gioco
    gioco.io.mostra_messaggio("\n=== Fine dello spettacolo! ===")
    avanti(gioco)

if __name__ == "__main__":
    main()

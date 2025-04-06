from entities.giocatore import Giocatore
from states.combattimento import CombattimentoState
from states.menu import MenuState
from core.game import Game
from states.taverna import TavernaState
from states.scelta_mappa_state import SceltaMappaState
from util.funzioni_utili import avanti
from items.oggetto import Oggetto
from entities.entita import Entita
from world.mappa import Mappa
from world.gestore_mappe import GestitoreMappe
from core.io_interface import TerminalIO
import json
import os


def ottieni_classi_disponibili():
    """Ottiene l'elenco delle classi disponibili dal file JSON"""
    percorso_file = os.path.join("data", "classes", "classes.json")
    try:
        with open(percorso_file, "r", encoding="utf-8") as file:
            classi = json.load(file)
            return list(classi.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        # In caso di errore, restituisci le classi predefinite
        return ["guerriero", "mago", "ladro"]


def richiedi_classe(io_handler):
    """Richiede all'utente di scegliere una classe tra quelle disponibili"""
    classi_disponibili = ottieni_classi_disponibili()
    
    io_handler.mostra_messaggio("Classi disponibili:")
    for i, classe in enumerate(classi_disponibili, 1):
        io_handler.mostra_messaggio(f"{i}. {classe}")
        
    while True:
        scelta = io_handler.richiedi_input("Scegli una classe (numero o nome): ")
        
        # Se l'utente ha inserito un numero
        if scelta.isdigit():
            indice = int(scelta) - 1
            if 0 <= indice < len(classi_disponibili):
                return classi_disponibili[indice]
        # Se l'utente ha inserito il nome della classe
        elif scelta.lower() in [c.lower() for c in classi_disponibili]:
            for c in classi_disponibili:
                if c.lower() == scelta.lower():
                    return c
                    
        io_handler.mostra_messaggio("Scelta non valida. Riprova.")


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
            gioco = Game(gioco_temp.giocatore, None, io_handler)
            # Imposta la mappa corrente
            gioco.gestore_mappe.imposta_mappa_attuale(gioco.giocatore.mappa_corrente)
            # Carica lo stato di scelta mappa
            gioco.push_stato(SceltaMappaState(gioco))
            
            # Imposta il contesto di gioco nel giocatore
            if hasattr(gioco.giocatore, 'set_game_context'):
                gioco.giocatore.set_game_context(gioco)
        else:
            # Se il caricamento fallisce, crea una nuova partita
            gioco_temp.io.mostra_messaggio("Creazione di una nuova partita...")
            nome = gioco_temp.io.richiedi_input("Come ti chiami? ")
            classe = richiedi_classe(gioco_temp.io)
            giocatore = Giocatore(nome, classe)
            # Crea il gioco con il giocatore
            gioco = Game(giocatore, None, io_handler)
            # Carica lo stato di scelta mappa
            gioco.push_stato(SceltaMappaState(gioco))
            
            # Imposta il contesto di gioco nel giocatore
            if hasattr(gioco.giocatore, 'set_game_context'):
                gioco.giocatore.set_game_context(gioco)
    else:
        # Chiedi input iniziale
        nome = gioco_temp.io.richiedi_input("Come ti chiami? ")
        classe = richiedi_classe(gioco_temp.io)
        giocatore = Giocatore(nome, classe)
        
        # Crea il gioco con il giocatore
        gioco = Game(giocatore, None, io_handler)
        
        # Benvenuto iniziale
        gioco.io.mostra_messaggio(f"Benvenuto {giocatore.nome} il {giocatore.classe}! La tua avventura sta per iniziare.")
        gioco.io.mostra_messaggio("Scegli dove vuoi andare per cominciare la tua avventura...")
        avanti(gioco)
        
        # Carica lo stato di scelta mappa
        gioco.push_stato(SceltaMappaState(gioco))
        
        # Imposta il contesto di gioco nel giocatore
        if hasattr(gioco.giocatore, 'set_game_context'):
            gioco.giocatore.set_game_context(gioco)
    
    gioco.esegui()
    
    # Fine del gioco
    gioco.io.mostra_messaggio("\n=== Fine dello spettacolo! ===")
    avanti(gioco)

if __name__ == "__main__":
    main()

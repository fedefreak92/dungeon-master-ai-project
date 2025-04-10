from core.io_interface import TerminalIO
from core.stato_gioco import GameIOWeb
from core.game import Game

def test_terminal_io():
    """Test del metodo get_output_structured per TerminalIO"""
    io_handler = TerminalIO()
    
    # Creiamo un oggetto gioco temporaneo per i test
    gioco_temp = Game(None, None, io_handler, e_temporaneo=True)
    
    # Aggiungiamo diversi tipi di messaggi
    gioco_temp.io.mostra_messaggio("Benvenuto avventuriero!")
    gioco_temp.io.messaggio_sistema("Nuova partita iniziata")
    gioco_temp.io.messaggio_errore("Comando non valido")
    
    # Verifichiamo che il buffer contenga i messaggi corretti
    output = gioco_temp.io.get_output_structured()
    
    # Verifichiamo la lunghezza
    assert len(output) == 3, f"Dovrebbero esserci 3 messaggi, ma ne sono stati trovati {len(output)}"
    
    # Verifichiamo il contenuto
    assert output[0]["tipo"] == "narrativo" and output[0]["testo"] == "Benvenuto avventuriero!"
    assert output[1]["tipo"] == "sistema" and output[1]["testo"] == "Nuova partita iniziata"
    assert output[2]["tipo"] == "errore" and output[2]["testo"] == "Comando non valido"
    
    print("Test TerminalIO superato!")
    
def test_game_io_web():
    """Test del metodo get_output_structured per GameIOWeb"""
    io_handler = GameIOWeb()
    
    # Creiamo un oggetto gioco temporaneo per i test
    gioco_temp = Game(None, None, io_handler, e_temporaneo=True)
    
    # Aggiungiamo diversi tipi di messaggi
    gioco_temp.io.mostra_messaggio("Hai trovato un forziere")
    gioco_temp.io.messaggio_sistema("Hai ottenuto 50 monete d'oro")
    gioco_temp.io.messaggio_errore("Non puoi aprire il forziere")
    gioco_temp.io.richiedi_input("Cosa vuoi fare?")
    
    # Verifichiamo che il buffer contenga i messaggi corretti
    output = gioco_temp.io.get_output_structured()
    
    # Verifichiamo la lunghezza
    assert len(output) == 4, f"Dovrebbero esserci 4 messaggi, ma ne sono stati trovati {len(output)}"
    
    # Verifichiamo il contenuto
    assert output[0]["tipo"] == "narrativo" and output[0]["testo"] == "Hai trovato un forziere"
    assert output[1]["tipo"] == "sistema" and output[1]["testo"] == "Hai ottenuto 50 monete d'oro"
    assert output[2]["tipo"] == "errore" and output[2]["testo"] == "Non puoi aprire il forziere"
    assert output[3]["tipo"] == "prompt" and output[3]["testo"] == "Cosa vuoi fare?"
    
    print("Test GameIOWeb superato!")
    
if __name__ == "__main__":
    test_terminal_io()
    test_game_io_web()
    print("Tutti i test superati!") 
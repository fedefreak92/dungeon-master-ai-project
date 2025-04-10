"""
Test per la gestione dello stack degli stati
"""
from entities.giocatore import Giocatore
from core.stato_gioco import StatoGioco, GameIOWeb
from core.game import Game
from states.scelta_mappa_state import SceltaMappaState
from states.taverna import TavernaState
from states.mercato import MercatoState
from states.mappa_state import MappaState
import logging

# Configura il logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_inizializzazione_stato():
    """Testa che l'inizializzazione dello stato non crei duplicati"""
    # Crea un giocatore
    giocatore = Giocatore("Test", "guerriero")
    
    # Crea lo stato iniziale
    stato_iniziale = SceltaMappaState()
    
    # Crea lo stato di gioco
    io_handler = GameIOWeb()
    stato_gioco = StatoGioco(giocatore, stato_iniziale)
    
    # Verifica lo stack iniziale
    stack = [type(s).__name__ for s in stato_gioco.game.stato_stack]
    logger.info(f"Stack degli stati iniziale: {stack}")
    
    # Verifica che ci sia esattamente uno stato di tipo SceltaMappaState
    assert len(stack) == 1, f"Lo stack dovrebbe contenere 1 stato, ne contiene {len(stack)}"
    assert stack[0] == "SceltaMappaState", f"Lo stato dovrebbe essere SceltaMappaState, è {stack[0]}"
    
    return stato_gioco

def test_push_stato():
    """Testa il push di un nuovo stato sullo stack"""
    stato_gioco = test_inizializzazione_stato()
    
    # Aggiungi un nuovo stato
    stato_gioco.game.push_stato(TavernaState(stato_gioco.game))
    
    # Verifica lo stack
    stack = [type(s).__name__ for s in stato_gioco.game.stato_stack]
    logger.info(f"Stack dopo push di TavernaState: {stack}")
    
    # Verifica che ci siano due stati
    assert len(stack) == 2, f"Lo stack dovrebbe contenere 2 stati, ne contiene {len(stack)}"
    assert stack[1] == "TavernaState", f"Il nuovo stato dovrebbe essere TavernaState, è {stack[1]}"
    
    # Tenta di aggiungere uno stato dello stesso tipo
    stato_gioco.game.push_stato(TavernaState(stato_gioco.game))
    
    # Verifica che lo stack non sia cambiato
    stack_dopo = [type(s).__name__ for s in stato_gioco.game.stato_stack]
    logger.info(f"Stack dopo tentativo di push duplicato: {stack_dopo}")
    
    # Verifica che lo stack sia rimasto lo stesso
    assert len(stack_dopo) == 2, f"Lo stack dovrebbe ancora contenere 2 stati, ne contiene {len(stack_dopo)}"
    assert stack_dopo[1] == "TavernaState", f"L'ultimo stato dovrebbe essere TavernaState, è {stack_dopo[1]}"
    
    return stato_gioco

def test_pop_stato():
    """Testa il pop di uno stato dallo stack"""
    stato_gioco = test_push_stato()
    
    # Rimuovi l'ultimo stato
    stato_gioco.game.pop_stato()
    
    # Verifica lo stack
    stack = [type(s).__name__ for s in stato_gioco.game.stato_stack]
    logger.info(f"Stack dopo pop: {stack}")
    
    # Verifica che ci sia solo lo stato iniziale
    assert len(stack) == 1, f"Lo stack dovrebbe contenere 1 stato, ne contiene {len(stack)}"
    assert stack[0] == "SceltaMappaState", f"Lo stato dovrebbe essere SceltaMappaState, è {stack[0]}"
    
    return stato_gioco

def test_cambia_stato():
    """Testa il cambio di stato"""
    stato_gioco = test_inizializzazione_stato()
    
    # Cambia lo stato
    stato_gioco.game.cambia_stato(MercatoState(stato_gioco.game))
    
    # Verifica lo stack
    stack = [type(s).__name__ for s in stato_gioco.game.stato_stack]
    logger.info(f"Stack dopo cambio stato: {stack}")
    
    # Verifica che ci sia solo il nuovo stato
    assert len(stack) == 1, f"Lo stack dovrebbe contenere 1 stato, ne contiene {len(stack)}"
    assert stack[0] == "MercatoState", f"Lo stato dovrebbe essere MercatoState, è {stack[0]}"
    
    return stato_gioco

def test_transizioni_complete():
    """Testa un flusso completo di transizioni tra stati"""
    stato_gioco = test_inizializzazione_stato()
    
    # Aggiungi diversi stati in sequenza
    stato_gioco.game.push_stato(TavernaState(stato_gioco.game))
    stato_gioco.game.push_stato(MappaState())
    stato_gioco.game.push_stato(MercatoState(stato_gioco.game))
    
    # Verifica lo stack
    stack = [type(s).__name__ for s in stato_gioco.game.stato_stack]
    logger.info(f"Stack dopo sequenza di push: {stack}")
    
    # Verifica la sequenza corretta
    assert len(stack) == 4, f"Lo stack dovrebbe contenere 4 stati, ne contiene {len(stack)}"
    assert stack[0] == "SceltaMappaState", f"Primo stato dovrebbe essere SceltaMappaState, è {stack[0]}"
    assert stack[3] == "MercatoState", f"Ultimo stato dovrebbe essere MercatoState, è {stack[3]}"
    
    # Rimuovi gli stati uno per uno
    for i in range(3):
        stato_gioco.game.pop_stato()
        stack = [type(s).__name__ for s in stato_gioco.game.stato_stack]
        logger.info(f"Stack dopo pop {i+1}: {stack}")
    
    # Verifica che sia rimasto solo lo stato iniziale
    assert len(stack) == 1, f"Lo stack dovrebbe contenere 1 stato, ne contiene {len(stack)}"
    assert stack[0] == "SceltaMappaState", f"Ultimo stato dovrebbe essere SceltaMappaState, è {stack[0]}"
    
    return stato_gioco

if __name__ == "__main__":
    print("=== Test di inizializzazione dello stato ===")
    test_inizializzazione_stato()
    
    print("\n=== Test di push stato ===")
    test_push_stato()
    
    print("\n=== Test di pop stato ===")
    test_pop_stato()
    
    print("\n=== Test di cambio stato ===")
    test_cambia_stato()
    
    print("\n=== Test di transizioni complete ===")
    test_transizioni_complete()
    
    print("\nTutti i test sono stati eseguiti con successo!") 
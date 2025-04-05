from states.base_state import BaseState
from util.funzioni_utili import avanti

class GestioneInventarioState(BaseState):
    def __init__(self, stato_precedente=None):
        self.stato_precedente = stato_precedente
    
    def esegui(self, gioco):
        gioco.io.mostra_messaggio("\n--- GESTIONE INVENTARIO ---")
        
        if not gioco.giocatore.inventario:
            gioco.io.mostra_messaggio("Il tuo inventario è vuoto.")
            gioco.io.richiedi_input("Premi INVIO per tornare indietro...")
            gioco.pop_stato()
            return
        
        # Mostra gli oggetti nell'inventario
        gioco.io.mostra_messaggio(f"\nOro: {gioco.giocatore.oro}")
        gioco.io.mostra_messaggio("\nOggetti:")
        for i, item in enumerate(gioco.giocatore.inventario, 1):
            gioco.io.mostra_messaggio(f"{i}. {item.nome} - {item.tipo} - {item.descrizione}")
        
        if gioco.giocatore.arma:
            gioco.io.mostra_messaggio(f"\nArma equipaggiata: {gioco.giocatore.arma.nome}")
        if gioco.giocatore.armatura:
            gioco.io.mostra_messaggio(f"\nArmatura equipaggiata: {gioco.giocatore.armatura.nome}")
        
        gioco.io.mostra_messaggio("\nCosa vuoi fare?")
        gioco.io.mostra_messaggio("1. Usa un oggetto")
        gioco.io.mostra_messaggio("2. Equipaggia un oggetto")
        gioco.io.mostra_messaggio("3. Rimuovi equipaggiamento")
        gioco.io.mostra_messaggio("4. Esamina un oggetto")
        gioco.io.mostra_messaggio("5. Torna indietro")
        
        scelta = gioco.io.richiedi_input("Scelta: ")
        
        if scelta == "1":
            self._usa_oggetto(gioco)
        elif scelta == "2":
            self._equipaggia_oggetto(gioco)
        elif scelta == "3":
            self._rimuovi_equipaggiamento(gioco)
        elif scelta == "4":
            self._esamina_oggetto(gioco)
        elif scelta == "5":
            gioco.pop_stato()
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")
    
    def _usa_oggetto(self, gioco):
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi usare?")
        for i, item in enumerate(gioco.giocatore.inventario, 1):
            gioco.io.mostra_messaggio(f"{i}. {item.nome}")
        gioco.io.mostra_messaggio(f"{len(gioco.giocatore.inventario) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(gioco.giocatore.inventario):
                oggetto = gioco.giocatore.inventario[scelta - 1]
                oggetto.usa(gioco.giocatore)
            elif scelta == len(gioco.giocatore.inventario) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        avanti(gioco)
    
    def _equipaggia_oggetto(self, gioco):
        equipaggiabili = [item for item in gioco.giocatore.inventario 
                         if item.tipo in ["arma", "armatura", "accessorio"]]
        
        if not equipaggiabili:
            gioco.io.mostra_messaggio("Non hai oggetti equipaggiabili.")
            avanti(gioco)
            return
        
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi equipaggiare?")
        for i, item in enumerate(equipaggiabili, 1):
            gioco.io.mostra_messaggio(f"{i}. {item.nome} ({item.tipo})")
        gioco.io.mostra_messaggio(f"{len(equipaggiabili) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(equipaggiabili):
                oggetto = equipaggiabili[scelta - 1]
                oggetto.equipaggia(gioco.giocatore)
            elif scelta == len(equipaggiabili) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        avanti(gioco)
    
    def _rimuovi_equipaggiamento(self, gioco):
        gioco.io.mostra_messaggio("\nCosa vuoi rimuovere?")
        opzioni = []
        
        if gioco.giocatore.arma:
            opzioni.append(("arma", gioco.giocatore.arma))
        if gioco.giocatore.armatura:
            opzioni.append(("armatura", gioco.giocatore.armatura))
        for i, acc in enumerate(gioco.giocatore.accessori):
            opzioni.append((f"accessorio {i+1}", acc))
        
        if not opzioni:
            gioco.io.mostra_messaggio("Non hai nessun equipaggiamento da rimuovere.")
            avanti(gioco)
            return
        
        for i, (tipo, item) in enumerate(opzioni, 1):
            gioco.io.mostra_messaggio(f"{i}. {tipo.capitalize()}: {item.nome}")
        gioco.io.mostra_messaggio(f"{len(opzioni) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(opzioni):
                _, oggetto = opzioni[scelta - 1]
                oggetto.rimuovi(gioco.giocatore)
            elif scelta == len(opzioni) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        avanti(gioco)
    
    def _esamina_oggetto(self, gioco):
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi esaminare?")
        for i, item in enumerate(gioco.giocatore.inventario, 1):
            gioco.io.mostra_messaggio(f"{i}. {item.nome}")
        gioco.io.mostra_messaggio(f"{len(gioco.giocatore.inventario) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(gioco.giocatore.inventario):
                oggetto = gioco.giocatore.inventario[scelta - 1]
                gioco.io.mostra_messaggio(f"\nNome: {oggetto.nome}")
                gioco.io.mostra_messaggio(f"Tipo: {oggetto.tipo}")
                gioco.io.mostra_messaggio(f"Descrizione: {oggetto.descrizione}")
                gioco.io.mostra_messaggio(f"Valore: {oggetto.valore} oro")
                
                if oggetto.effetto:
                    gioco.io.mostra_messaggio("Effetti:")
                    for stat, valore in oggetto.effetto.items():
                        gioco.io.mostra_messaggio(f"  - {stat}: {valore}")
            elif scelta == len(gioco.giocatore.inventario) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        avanti(gioco)

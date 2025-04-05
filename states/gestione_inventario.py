from states.base_state import BaseState
from util.funzioni_utili import avanti

class GestioneInventarioState(BaseState):
    def __init__(self, stato_precedente=None):
        self.stato_precedente = stato_precedente
        self.fase = "menu_principale"  # Fase iniziale
        self.ultimo_input = None
        self.equipaggiabili = []  # Cache per oggetti equipaggiabili
        self.opzioni_rimozione = []  # Cache per opzioni di rimozione
    
    def esegui(self, gioco):
        # Gestione di inventario vuoto
        if self.fase == "menu_principale" and not gioco.giocatore.inventario:
            gioco.io.mostra_messaggio("\n--- GESTIONE INVENTARIO ---")
            gioco.io.mostra_messaggio("Il tuo inventario è vuoto.")
            gioco.io.richiedi_input("Premi INVIO per tornare indietro...")
            if gioco.stato_corrente():
                gioco.pop_stato()
            return
            
        # Processo le fasi in sequenza
        if self.fase == "menu_principale":
            self._mostra_menu_principale(gioco)
        elif self.fase == "processa_menu_principale":
            self._processa_menu_principale(gioco)
        elif self.fase == "usa_oggetto":
            self._mostra_usa_oggetto(gioco)
        elif self.fase == "processa_usa_oggetto":
            self._processa_usa_oggetto(gioco)
        elif self.fase == "equipaggia_oggetto":
            self._mostra_equipaggia_oggetto(gioco)
        elif self.fase == "processa_equipaggia_oggetto":
            self._processa_equipaggia_oggetto(gioco)
        elif self.fase == "rimuovi_equipaggiamento":
            self._mostra_rimuovi_equipaggiamento(gioco)
        elif self.fase == "processa_rimuovi_equipaggiamento":
            self._processa_rimuovi_equipaggiamento(gioco)
        elif self.fase == "esamina_oggetto":
            self._mostra_esamina_oggetto(gioco)
        elif self.fase == "processa_esamina_oggetto":
            self._processa_esamina_oggetto(gioco)
        elif self.fase == "attendi_conferma":
            self._attendi_conferma(gioco)
    
    def _mostra_menu_principale(self, gioco):
        gioco.io.mostra_messaggio("\n--- GESTIONE INVENTARIO ---")
        
        # Mostra gli oggetti nell'inventario
        gioco.io.mostra_messaggio(f"\nOro: {gioco.giocatore.oro}")
        gioco.io.mostra_messaggio("\nOggetti:")
        for i, item in enumerate(gioco.giocatore.inventario, 1):
            if isinstance(item, str):
                gioco.io.mostra_messaggio(f"{i}. {item}")
            else:
                gioco.io.mostra_messaggio(f"{i}. {item.nome} - {item.tipo} - {item.descrizione}")
        
        if gioco.giocatore.arma:
            if isinstance(gioco.giocatore.arma, str):
                gioco.io.mostra_messaggio(f"\nArma equipaggiata: {gioco.giocatore.arma}")
            else:
                gioco.io.mostra_messaggio(f"\nArma equipaggiata: {gioco.giocatore.arma.nome}")
                
        if gioco.giocatore.armatura:
            if isinstance(gioco.giocatore.armatura, str):
                gioco.io.mostra_messaggio(f"\nArmatura equipaggiata: {gioco.giocatore.armatura}")
            else:
                gioco.io.mostra_messaggio(f"\nArmatura equipaggiata: {gioco.giocatore.armatura.nome}")
        
        gioco.io.mostra_messaggio("\nCosa vuoi fare?")
        gioco.io.mostra_messaggio("1. Usa un oggetto")
        gioco.io.mostra_messaggio("2. Equipaggia un oggetto")
        gioco.io.mostra_messaggio("3. Rimuovi equipaggiamento")
        gioco.io.mostra_messaggio("4. Esamina un oggetto")
        gioco.io.mostra_messaggio("5. Torna indietro")
        
        self.ultimo_input = gioco.io.richiedi_input("Scelta: ")
        self.fase = "processa_menu_principale"
    
    def _processa_menu_principale(self, gioco):
        scelta = self.ultimo_input
        
        if scelta == "1":
            self.fase = "usa_oggetto"
        elif scelta == "2":
            self.fase = "equipaggia_oggetto"
        elif scelta == "3":
            self.fase = "rimuovi_equipaggiamento"
        elif scelta == "4":
            self.fase = "esamina_oggetto"
        elif scelta == "5":
            if gioco.stato_corrente():
                gioco.pop_stato()
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")
            self.fase = "menu_principale"  # Torna al menu principale
    
    def _mostra_usa_oggetto(self, gioco):
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi usare?")
        for i, item in enumerate(gioco.giocatore.inventario, 1):
            if isinstance(item, str):
                gioco.io.mostra_messaggio(f"{i}. {item}")
            else:
                gioco.io.mostra_messaggio(f"{i}. {item.nome}")
        gioco.io.mostra_messaggio(f"{len(gioco.giocatore.inventario) + 1}. Annulla")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
        self.fase = "processa_usa_oggetto"
    
    def _processa_usa_oggetto(self, gioco):
        try:
            scelta = int(self.ultimo_input)
            if 1 <= scelta <= len(gioco.giocatore.inventario):
                oggetto = gioco.giocatore.inventario[scelta - 1]
                if isinstance(oggetto, str):
                    gioco.io.mostra_messaggio(f"Non puoi usare {oggetto} direttamente.")
                else:
                    oggetto.usa(gioco.giocatore)
                    gioco.io.mostra_messaggio(f"Hai usato: {oggetto.nome}")
            elif scelta == len(gioco.giocatore.inventario) + 1:
                self.fase = "menu_principale"
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        self.fase = "attendi_conferma"
    
    def _mostra_equipaggia_oggetto(self, gioco):
        self.equipaggiabili = [item for item in gioco.giocatore.inventario 
                             if not isinstance(item, str) and hasattr(item, 'tipo') and item.tipo in ["arma", "armatura", "accessorio"]]
        
        if not self.equipaggiabili:
            gioco.io.mostra_messaggio("Non hai oggetti equipaggiabili.")
            self.fase = "attendi_conferma"
            return
        
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi equipaggiare?")
        for i, item in enumerate(self.equipaggiabili, 1):
            gioco.io.mostra_messaggio(f"{i}. {item.nome} ({item.tipo})")
        gioco.io.mostra_messaggio(f"{len(self.equipaggiabili) + 1}. Annulla")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
        self.fase = "processa_equipaggia_oggetto"
    
    def _processa_equipaggia_oggetto(self, gioco):
        try:
            scelta = int(self.ultimo_input)
            if 1 <= scelta <= len(self.equipaggiabili):
                oggetto = self.equipaggiabili[scelta - 1]
                oggetto.equipaggia(gioco.giocatore)
                gioco.io.mostra_messaggio(f"Hai equipaggiato: {oggetto.nome}")
            elif scelta == len(self.equipaggiabili) + 1:
                self.fase = "menu_principale"
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        self.fase = "attendi_conferma"
    
    def _mostra_rimuovi_equipaggiamento(self, gioco):
        gioco.io.mostra_messaggio("\nCosa vuoi rimuovere?")
        self.opzioni_rimozione = []
        
        if gioco.giocatore.arma and not isinstance(gioco.giocatore.arma, str):
            self.opzioni_rimozione.append(("arma", gioco.giocatore.arma))
        if gioco.giocatore.armatura and not isinstance(gioco.giocatore.armatura, str):
            self.opzioni_rimozione.append(("armatura", gioco.giocatore.armatura))
        for i, acc in enumerate(gioco.giocatore.accessori):
            if not isinstance(acc, str):
                self.opzioni_rimozione.append((f"accessorio {i+1}", acc))
        
        if not self.opzioni_rimozione:
            gioco.io.mostra_messaggio("Non hai nessun equipaggiamento da rimuovere.")
            self.fase = "attendi_conferma"
            return
        
        for i, (tipo, item) in enumerate(self.opzioni_rimozione, 1):
            gioco.io.mostra_messaggio(f"{i}. {tipo.capitalize()}: {item.nome}")
        gioco.io.mostra_messaggio(f"{len(self.opzioni_rimozione) + 1}. Annulla")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
        self.fase = "processa_rimuovi_equipaggiamento"
    
    def _processa_rimuovi_equipaggiamento(self, gioco):
        try:
            scelta = int(self.ultimo_input)
            if 1 <= scelta <= len(self.opzioni_rimozione):
                tipo, oggetto = self.opzioni_rimozione[scelta - 1]
                oggetto.rimuovi(gioco.giocatore)
                gioco.io.mostra_messaggio(f"Hai rimosso: {oggetto.nome}")
            elif scelta == len(self.opzioni_rimozione) + 1:
                self.fase = "menu_principale"
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        self.fase = "attendi_conferma"
    
    def _mostra_esamina_oggetto(self, gioco):
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi esaminare?")
        for i, item in enumerate(gioco.giocatore.inventario, 1):
            if isinstance(item, str):
                gioco.io.mostra_messaggio(f"{i}. {item}")
            else:
                gioco.io.mostra_messaggio(f"{i}. {item.nome}")
        gioco.io.mostra_messaggio(f"{len(gioco.giocatore.inventario) + 1}. Annulla")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
        self.fase = "processa_esamina_oggetto"
    
    def _processa_esamina_oggetto(self, gioco):
        try:
            scelta = int(self.ultimo_input)
            if 1 <= scelta <= len(gioco.giocatore.inventario):
                oggetto = gioco.giocatore.inventario[scelta - 1]
                if isinstance(oggetto, str):
                    gioco.io.mostra_messaggio(f"\nNome: {oggetto}")
                    gioco.io.mostra_messaggio("Tipo: Generico")
                    gioco.io.mostra_messaggio("Descrizione: Non disponibile")
                    gioco.io.mostra_messaggio("Valore: Sconosciuto")
                else:
                    gioco.io.mostra_messaggio(f"\nNome: {oggetto.nome}")
                    gioco.io.mostra_messaggio(f"Tipo: {oggetto.tipo}")
                    gioco.io.mostra_messaggio(f"Descrizione: {oggetto.descrizione}")
                    gioco.io.mostra_messaggio(f"Valore: {oggetto.valore} oro")
                    
                    if hasattr(oggetto, 'effetto') and oggetto.effetto:
                        gioco.io.mostra_messaggio("Effetti:")
                        for stat, valore in oggetto.effetto.items():
                            gioco.io.mostra_messaggio(f"  - {stat}: {valore}")
            elif scelta == len(gioco.giocatore.inventario) + 1:
                self.fase = "menu_principale"
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
        
        self.fase = "attendi_conferma"
    
    def _attendi_conferma(self, gioco):
        gioco.io.richiedi_input("Premi INVIO per continuare...")
        self.fase = "menu_principale"

# I vecchi metodi non sono più necessari perché ora abbiamo versioni separate per ogni fase
# def _usa_oggetto(self, gioco): ...
# def _equipaggia_oggetto(self, gioco): ...
# def _rimuovi_equipaggiamento(self, gioco): ...
# def _esamina_oggetto(self, gioco): ...

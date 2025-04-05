from states.base_state import BaseState
from util.dado import Dado
from entities.npg import NPG
from items.oggetto_interattivo import OggettoInterattivo
from items.oggetto import Oggetto
from entities.giocatore import Giocatore
from entities.entita import ABILITA_ASSOCIATE


class ProvaAbilitaState(BaseState):
    def __init__(self, contesto=None):
        """
        Inizializza lo stato di prova di abilità.
        
        Args:
            contesto (dict, optional): Contesto opzionale per la prova (es. oggetto associato)
        """
        self.contesto = contesto or {}
        
    def esegui(self, gioco):
        gioco.io.mostra_messaggio("\n=== PROVA DI ABILITÀ ===")
        gioco.io.mostra_messaggio("Quale abilità vuoi mettere alla prova?")
        gioco.io.mostra_messaggio("1. Forza")
        gioco.io.mostra_messaggio("2. Destrezza")
        gioco.io.mostra_messaggio("3. Costituzione")
        gioco.io.mostra_messaggio("4. Intelligenza")
        gioco.io.mostra_messaggio("5. Saggezza")
        gioco.io.mostra_messaggio("6. Carisma")
        gioco.io.mostra_messaggio("7. Prova su abilità specifica (es. Percezione, Persuasione)")
        gioco.io.mostra_messaggio("8. Torna indietro")
        
        abilita = {
            "1": "forza",
            "2": "destrezza",
            "3": "costituzione",
            "4": "intelligenza",
            "5": "saggezza",
            "6": "carisma"
        }
        
        scelta = gioco.io.richiedi_input("\nScegli: ")
        if scelta in abilita:
            abilita_scelta = abilita[scelta]
            
            # Richiedi la modalità di prova
            gioco.io.mostra_messaggio("\nScegli la modalità di prova:")
            gioco.io.mostra_messaggio("1. Prova base (contro difficoltà)")
            gioco.io.mostra_messaggio("2. Prova contro un personaggio non giocante (NPG)")
            gioco.io.mostra_messaggio("3. Prova con un oggetto interattivo")
            gioco.io.mostra_messaggio("4. Torna indietro")
            
            modalita = gioco.io.richiedi_input("\nScegli modalità: ")
            
            if modalita == "1":
                # Prova base (il codice esistente)
                self._prova_base(gioco, abilita_scelta)
            elif modalita == "2":
                # Prova contro NPG
                self._prova_npg(gioco, abilita_scelta)
            elif modalita == "3":
                # Prova con oggetto interattivo
                self._prova_oggetto(gioco, abilita_scelta)
            elif modalita == "4":
                # Torna al menu abilità (richiama esegui)
                self.esegui(gioco)
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self.esegui(gioco)
                return
        elif scelta == "7":
            # Prova di abilità specifica
            self._prova_abilita_specifica(gioco)
            return
        elif scelta == "8":
            gioco.pop_stato()
            return
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")
            self.esegui(gioco)
            return
        
        gioco.io.richiedi_input("\nPremi Enter per continuare...")
        gioco.pop_stato()
    
    def _prova_base(self, gioco, abilita):
        """Esegue una prova base contro una difficoltà"""
        try:
            difficolta = int(gioco.io.richiedi_input("Inserisci la difficoltà (5-20): "))
            difficolta = max(5, min(20, difficolta))  # Limita tra 5 e 20
            
            dado = Dado(20)
            tiro = dado.tira()
            
            # Usa direttamente getattr, che prenderà il valore del modificatore
            # sia che usi il sistema vecchio (attributo diretto) sia quello nuovo (attraverso la proprietà)
            modificatore = getattr(gioco.giocatore, abilita)
            risultato = tiro + modificatore
            
            # Se disponibile, mostra anche il valore base dell'abilità
            if hasattr(gioco.giocatore, f"{abilita}_base"):
                valore_base = getattr(gioco.giocatore, f"{abilita}_base")
                gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} ha {abilita.capitalize()} {valore_base} (modificatore: {modificatore})")
            
            gioco.io.mostra_messaggio(f"{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
            
            if risultato >= difficolta:
                gioco.io.mostra_messaggio(f"Hai superato la prova di {abilita}!")
                self._gestisci_successo(gioco, abilita)
            else:
                gioco.io.mostra_messaggio(f"Hai fallito la prova di {abilita}.")
                self._gestisci_fallimento(gioco, abilita)
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero per la difficoltà.")
    
    def _prova_npg(self, gioco, abilita):
        """Esegue una prova contro un NPG"""
        # Ottieni il penultimo stato nella pila (lo stato che ha invocato questo)
        stato_precedente = gioco.stato_stack[-2] if len(gioco.stato_stack) > 1 else None
        
        if not stato_precedente or not hasattr(stato_precedente, 'npg_presenti'):
            gioco.io.mostra_messaggio("Non ci sono personaggi non giocanti nelle vicinanze.")
            return
        
        gioco.io.mostra_messaggio("\nScegli il personaggio contro cui effettuare la prova:")
        
        # Gestione sia per dizionari che per liste
        if isinstance(stato_precedente.npg_presenti, dict):
            for i, nome in enumerate(stato_precedente.npg_presenti.keys(), 1):
                gioco.io.mostra_messaggio(f"{i}. {nome}")
            
            try:
                scelta = int(gioco.io.richiedi_input("\nScegli NPG: "))
                if 1 <= scelta <= len(stato_precedente.npg_presenti):
                    npg_nome = list(stato_precedente.npg_presenti.keys())[scelta - 1]
                    npg = stato_precedente.npg_presenti[npg_nome]
                    
                    # Prima definisci il modificatore
                    modificatore = getattr(gioco.giocatore, abilita)
                    
                    
                    if hasattr(gioco.giocatore, f"{abilita}_base") and hasattr(npg, f"{abilita}_base"):
                        g_valore = getattr(gioco.giocatore, f"{abilita}_base")
                        n_valore = getattr(npg, f"{abilita}_base")
                        gioco.io.mostra_messaggio(f"{gioco.giocatore.nome}: {abilita.capitalize()} {g_valore} (mod: {modificatore})")
                    
                    # Determina la difficoltà in base all'abilità
                    if abilita in ["forza", "destrezza", "costituzione"]:
                        # Prova fisica - confronta con lo stesso attributo dell'NPG
                        difficolta = getattr(npg, abilita, 3) + 10  # Base 10 + mod NPG
                    elif abilita in ["intelligenza", "saggezza", "carisma"]:
                        # Prova sociale/mentale
                        difficolta = getattr(npg, abilita, 3) + 8   # Base 8 + mod NPG
                    
                    dado = Dado(20)
                    tiro = dado.tira()
                    risultato = tiro + modificatore
                    
                    gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
                    gioco.io.mostra_messaggio(f"Difficoltà contro {npg.nome}: {difficolta}")
                    
                    if risultato >= difficolta:
                        gioco.io.mostra_messaggio(f"Hai superato la prova di {abilita} contro {npg.nome}!")
                        self._gestisci_successo_npg(gioco, abilita, npg)
                    else:
                        gioco.io.mostra_messaggio(f"Hai fallito la prova di {abilita} contro {npg.nome}.")
                        self._gestisci_fallimento_npg(gioco, abilita, npg)
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
        else:
            # Gestione per liste
            for i, npg in enumerate(stato_precedente.npg_presenti, 1):
                gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
            
            try:
                scelta = int(gioco.io.richiedi_input("\nScegli NPG: "))
                if 1 <= scelta <= len(stato_precedente.npg_presenti):
                    npg = stato_precedente.npg_presenti[scelta - 1]
                    
                    # Prima definisci il modificatore
                    modificatore = getattr(gioco.giocatore, abilita)
                    
                  
                    if hasattr(gioco.giocatore, f"{abilita}_base") and hasattr(npg, f"{abilita}_base"):
                        g_valore = getattr(gioco.giocatore, f"{abilita}_base")
                        n_valore = getattr(npg, f"{abilita}_base")
                        gioco.io.mostra_messaggio(f"{gioco.giocatore.nome}: {abilita.capitalize()} {g_valore} (mod: {modificatore})")
                    
                    # Determina la difficoltà in base all'abilità
                    if abilita in ["forza", "destrezza", "costituzione"]:
                        # Prova fisica - confronta con lo stesso attributo dell'NPG
                        difficolta = getattr(npg, abilita, 3) + 10  # Base 10 + mod NPG
                    elif abilita in ["intelligenza", "saggezza", "carisma"]:
                        # Prova sociale/mentale
                        difficolta = getattr(npg, abilita, 3) + 8   # Base 8 + mod NPG
                    
                    dado = Dado(20)
                    tiro = dado.tira()
                    risultato = tiro + modificatore
                    
                    gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
                    gioco.io.mostra_messaggio(f"Difficoltà contro {npg.nome}: {difficolta}")
                    
                    if risultato >= difficolta:
                        gioco.io.mostra_messaggio(f"Hai superato la prova di {abilita} contro {npg.nome}!")
                        self._gestisci_successo_npg(gioco, abilita, npg)
                    else:
                        gioco.io.mostra_messaggio(f"Hai fallito la prova di {abilita} contro {npg.nome}.")
                        self._gestisci_fallimento_npg(gioco, abilita, npg)
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
    
    def _prova_oggetto(self, gioco, abilita):
        """Esegue una prova con un oggetto interattivo"""
        # Ottieni il penultimo stato nella pila (lo stato che ha invocato questo)
        stato_precedente = gioco.stato_stack[-2] if len(gioco.stato_stack) > 1 else None
        
        if not stato_precedente or not hasattr(stato_precedente, 'oggetti_interattivi'):
            gioco.io.mostra_messaggio("Non ci sono oggetti interattivi nelle vicinanze.")
            return
        
        gioco.io.mostra_messaggio("\nScegli l'oggetto con cui interagire:")
        
        # Gestione sia per dizionari che per liste
        if isinstance(stato_precedente.oggetti_interattivi, dict):
            for i, nome in enumerate(stato_precedente.oggetti_interattivi.keys(), 1):
                oggetto = stato_precedente.oggetti_interattivi[nome]
                gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
            
            # Aggiungi l'opzione "Torna indietro" DOPO gli oggetti
            num_opzione_torna = len(stato_precedente.oggetti_interattivi) + 1
            gioco.io.mostra_messaggio(f"{num_opzione_torna}. Torna indietro")
            
            try:
                scelta = int(gioco.io.richiedi_input("\nScegli oggetto: "))
                if 1 <= scelta <= len(stato_precedente.oggetti_interattivi):
                    oggetto_nome = list(stato_precedente.oggetti_interattivi.keys())[scelta - 1]
                    oggetto = stato_precedente.oggetti_interattivi[oggetto_nome]
                    
                    # Visualizza i valori base se disponibili
                    if hasattr(gioco.giocatore, f"{abilita}_base"):
                        valore_base = getattr(gioco.giocatore, f"{abilita}_base")
                        gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} ha {abilita.capitalize()} {valore_base} (modificatore: {modificatore})")
                    
                    # Determina la difficoltà in base al tipo di oggetto e all'abilità
                    if isinstance(oggetto, OggettoInterattivo):
                        if abilita == "forza" and hasattr(oggetto, "forza_richiesta"):
                            difficolta = oggetto.forza_richiesta + 8
                        elif abilita == "destrezza" and hasattr(oggetto, "difficolta_salvezza"):
                            difficolta = oggetto.difficolta_salvezza
                        else:
                            difficolta = 12  # Difficoltà standard
                    else:
                        difficolta = 10  # Oggetto generico
                    
                    dado = Dado(20)
                    tiro = dado.tira()
                    modificatore = getattr(gioco.giocatore, abilita)
                    risultato = tiro + modificatore
                    
                    gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
                    gioco.io.mostra_messaggio(f"Difficoltà per {oggetto.nome}: {difficolta}")
                    
                    self.contesto["tipo"] = "oggetto"
                    self.contesto["oggetto"] = oggetto
                    
                    if risultato >= difficolta:
                        gioco.io.mostra_messaggio(f"Hai superato la prova di {abilita} con {oggetto.nome}!")
                        self._gestisci_successo(gioco, abilita)
                        
                        # Attiva l'interazione specifica con l'oggetto
                        if abilita == "forza" and hasattr(oggetto, "stato") and oggetto.stato == "integro":
                            gioco.io.mostra_messaggio(f"Grazie alla tua forza, puoi interagire efficacemente con {oggetto.nome}!")
                            oggetto.interagisci(gioco.giocatore)
                    else:
                        gioco.io.mostra_messaggio(f"Hai fallito la prova di {abilita} con {oggetto.nome}.")
                        self._gestisci_fallimento(gioco, abilita)
                elif scelta == num_opzione_torna:
                    return  # Torna al menu precedente
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
        else:
            # Gestione per liste
            for i, oggetto in enumerate(stato_precedente.oggetti_interattivi, 1):
                gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
            
            # Aggiungi l'opzione "Torna indietro" DOPO gli oggetti
            num_opzione_torna = len(stato_precedente.oggetti_interattivi) + 1
            gioco.io.mostra_messaggio(f"{num_opzione_torna}. Torna indietro")
            
            try:
                scelta = int(gioco.io.richiedi_input("\nScegli oggetto: "))
                if 1 <= scelta <= len(stato_precedente.oggetti_interattivi):
                    oggetto = stato_precedente.oggetti_interattivi[scelta - 1]
                    
                    # Visualizza i valori base se disponibili
                    if hasattr(gioco.giocatore, f"{abilita}_base"):
                        valore_base = getattr(gioco.giocatore, f"{abilita}_base")
                        gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} ha {abilita.capitalize()} {valore_base} (modificatore: {modificatore})")
                    
                    # Determina la difficoltà in base al tipo di oggetto e all'abilità
                    if isinstance(oggetto, OggettoInterattivo):
                        if abilita == "forza" and hasattr(oggetto, "forza_richiesta"):
                            difficolta = oggetto.forza_richiesta + 8
                        elif abilita == "destrezza" and hasattr(oggetto, "difficolta_salvezza"):
                            difficolta = oggetto.difficolta_salvezza
                        else:
                            difficolta = 12  # Difficoltà standard
                    else:
                        difficolta = 10  # Oggetto generico
                    
                    dado = Dado(20)
                    tiro = dado.tira()
                    modificatore = getattr(gioco.giocatore, abilita)
                    risultato = tiro + modificatore
                    
                    gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({abilita}) = {risultato}")
                    gioco.io.mostra_messaggio(f"Difficoltà per {oggetto.nome}: {difficolta}")
                    
                    self.contesto["tipo"] = "oggetto"
                    self.contesto["oggetto"] = oggetto
                    
                    if risultato >= difficolta:
                        gioco.io.mostra_messaggio(f"Hai superato la prova di {abilita} con {oggetto.nome}!")
                        self._gestisci_successo(gioco, abilita)
                        
                        # Attiva l'interazione specifica con l'oggetto
                        if abilita == "forza" and hasattr(oggetto, "stato") and oggetto.stato == "integro":
                            gioco.io.mostra_messaggio(f"Grazie alla tua forza, puoi interagire efficacemente con {oggetto.nome}!")
                            oggetto.interagisci(gioco.giocatore)
                    else:
                        gioco.io.mostra_messaggio(f"Hai fallito la prova di {abilita} con {oggetto.nome}.")
                        self._gestisci_fallimento(gioco, abilita)
                elif scelta == num_opzione_torna:
                    return  # Torna al menu precedente
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
    
    def _gestisci_successo_npg(self, gioco, abilita, npg):
        """Gestisce gli effetti del successo nella prova contro un NPG"""
        gioco.io.mostra_messaggio(f"L'interazione con {npg.nome} ha avuto successo!")
        
        # Comportamento diverso in base all'abilità
        if abilita in ABILITA_ASSOCIATE:
            # Abilità specifiche
            if abilita == "persuasione":
                gioco.io.mostra_messaggio(f"Sei riuscito a persuadere {npg.nome}!")
                if hasattr(npg, "stato_corrente"):
                    npg.cambia_stato("persuaso")
            elif abilita == "intimidire":
                gioco.io.mostra_messaggio(f"Sei riuscito a intimidire {npg.nome}!")
                if hasattr(npg, "stato_corrente"):
                    npg.cambia_stato("intimidito")
            elif abilita == "inganno":
                gioco.io.mostra_messaggio(f"Sei riuscito a ingannare {npg.nome}!")
                if hasattr(npg, "stato_corrente"):
                    npg.cambia_stato("ingannato")
            elif abilita == "percezione" or abilita == "indagare":
                gioco.io.mostra_messaggio(f"Hai notato qualcosa di importante su {npg.nome}!")
        else:
            # Caratteristiche base (codice esistente)
            if abilita == "forza":
                gioco.io.mostra_messaggio(f"Hai impressionato {npg.nome} con la tua forza!")
            elif abilita == "destrezza":
                gioco.io.mostra_messaggio(f"{npg.nome} è colpito dalla tua agilità!")
            elif abilita == "carisma":
                gioco.io.mostra_messaggio(f"{npg.nome} è affascinato dalla tua presenza!")
                if hasattr(npg, "stato_corrente"):
                    npg.cambia_stato("amichevole")
        
        # Ricompensa base
        exp = 8
        if gioco.giocatore.guadagna_esperienza(exp):
            gioco.io.mostra_messaggio(f"Hai guadagnato {exp} punti esperienza e sei salito di livello!")
        else:
            gioco.io.mostra_messaggio(f"Hai guadagnato {exp} punti esperienza.")
    
    def _gestisci_fallimento_npg(self, gioco, abilita, npg):
        """Gestisce gli effetti del fallimento nella prova contro un NPG"""
        gioco.io.mostra_messaggio(f"L'interazione con {npg.nome} non è andata bene.")
        
        # Comportamento diverso in base all'abilità
        if abilita == "forza":
            gioco.io.mostra_messaggio(f"{npg.nome} non sembra impressionato dalla tua forza.")
        elif abilita == "destrezza":
            gioco.io.mostra_messaggio(f"{npg.nome} ha notato la tua goffaggine.")
        elif abilita == "carisma":
            gioco.io.mostra_messaggio(f"{npg.nome} sembra infastidito dal tuo approccio.")
            if hasattr(npg, "stato_corrente"):
                npg.cambia_stato("diffidente")
        
    def _gestisci_successo(self, gioco, abilita):
        """Gestisce gli effetti del successo nella prova"""
        if self.contesto.get("tipo") == "oggetto":
            oggetto = self.contesto.get("oggetto")
            if oggetto:
                gioco.io.mostra_messaggio(f"Sei riuscito a interagire correttamente con {oggetto.nome}!")
                
        # Piccola ricompensa per il successo
        exp = 5
        if gioco.giocatore.guadagna_esperienza(exp):
            gioco.io.mostra_messaggio(f"Hai guadagnato {exp} punti esperienza e sei salito di livello!")
        else:
            gioco.io.mostra_messaggio(f"Hai guadagnato {exp} punti esperienza.")
    
    def _gestisci_fallimento(self, gioco, abilita):
        """Gestisce gli effetti del fallimento nella prova"""
        if self.contesto.get("tipo") == "oggetto":
            oggetto = self.contesto.get("oggetto")
            if oggetto:
                gioco.io.mostra_messaggio(f"Non sei riuscito a interagire correttamente con {oggetto.nome}.")
                
                # Se c'è una penalità, applicarla
                if self.contesto.get("penalita"):
                    danno = self.contesto.get("penalita")
                    gioco.giocatore.subisci_danno(danno)
                    gioco.io.mostra_messaggio(f"Subisci {danno} danni!")
    
    def _prova_abilita_specifica(self, gioco):
        """Gestisce la prova di un'abilità specifica come Percezione, Persuasione, ecc."""
        gioco.io.mostra_messaggio("\nScegli l'abilità da provare:")
        for i, abilita in enumerate(ABILITA_ASSOCIATE.keys(), 1):
            # Mostra se il giocatore ha competenza
            competenza = " [Competente]" if gioco.giocatore.abilita_competenze.get(abilita.lower()) else ""
            gioco.io.mostra_messaggio(f"{i}. {abilita.capitalize()}{competenza}")
        
        scelta = gioco.io.richiedi_input("\nScegli: ")
        try:
            idx = int(scelta) - 1
            nome_abilita = list(ABILITA_ASSOCIATE.keys())[idx]
            
            # Chiedi la modalità di prova
            gioco.io.mostra_messaggio("\nScegli la modalità di prova:")
            gioco.io.mostra_messaggio("1. Prova base (contro difficoltà)")
            gioco.io.mostra_messaggio("2. Prova contro un personaggio non giocante (NPG)")
            gioco.io.mostra_messaggio("3. Prova con un oggetto interattivo")
            gioco.io.mostra_messaggio("4. Torna indietro")
            
            modalita = gioco.io.richiedi_input("\nScegli modalità: ")
            
            if modalita == "1":
                self._prova_abilita_base(gioco, nome_abilita)
            elif modalita == "2":
                self._prova_abilita_npg(gioco, nome_abilita)
            elif modalita == "3":
                self._prova_abilita_oggetto(gioco, nome_abilita)
            elif modalita == "4":
                self._prova_abilita_specifica(gioco)
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self._prova_abilita_specifica(gioco)
                return
                
            gioco.io.richiedi_input("\nPremi Enter per continuare...")
            gioco.pop_stato()
        except (IndexError, ValueError):
            gioco.io.mostra_messaggio("Scelta non valida.")
            self._prova_abilita_specifica(gioco)
    
    def _prova_abilita_base(self, gioco, nome_abilita):
        """Esegue una prova base di abilità specifica contro una difficoltà"""
        try:
            difficolta = int(gioco.io.richiedi_input("Inserisci la difficoltà (5-25): "))
            difficolta = max(5, min(25, difficolta))  # Limita tra 5 e 25
            
            dado = Dado(20)
            tiro = dado.tira()
            
            caratteristica = ABILITA_ASSOCIATE.get(nome_abilita)
            modificatore = gioco.giocatore.modificatore_abilita(nome_abilita)
            modificatore_base = getattr(gioco.giocatore, f"modificatore_{caratteristica}")
            competenza = gioco.giocatore.abilita_competenze.get(nome_abilita, False)
            bonus_comp = gioco.giocatore.bonus_competenza if competenza else 0
            
            risultato = tiro + modificatore
            
            gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} ha {caratteristica.capitalize()} {getattr(gioco.giocatore, f'{caratteristica}_base')} (mod: {modificatore_base})")
            if competenza:
                gioco.io.mostra_messaggio(f"Ha competenza in {nome_abilita.capitalize()} (bonus: +{bonus_comp})")
            gioco.io.mostra_messaggio(f"Tira un {tiro} + {modificatore_base} (mod) {'+' + str(bonus_comp) if bonus_comp else ''} = {risultato}")
            
            if risultato >= difficolta:
                gioco.io.mostra_messaggio(f"Hai superato la prova di {nome_abilita}!")
                self._gestisci_successo(gioco, nome_abilita)
            else:
                gioco.io.mostra_messaggio(f"Hai fallito la prova di {nome_abilita}.")
                self._gestisci_fallimento(gioco, nome_abilita)
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero per la difficoltà.")
    
    def _prova_abilita_npg(self, gioco, nome_abilita):
        """Esegue una prova di abilità specifica contro un NPG"""
        stato_precedente = gioco.stato_stack[-2] if len(gioco.stato_stack) > 1 else None
        
        if not stato_precedente or not hasattr(stato_precedente, 'npg_presenti'):
            gioco.io.mostra_messaggio("Non ci sono personaggi non giocanti nelle vicinanze.")
            return
        
        gioco.io.mostra_messaggio("\nScegli il personaggio contro cui effettuare la prova:")
        
        # Gestione sia per dizionari che per liste
        if isinstance(stato_precedente.npg_presenti, dict):
            for i, nome in enumerate(stato_precedente.npg_presenti.keys(), 1):
                gioco.io.mostra_messaggio(f"{i}. {nome}")
            
            try:
                scelta = int(gioco.io.richiedi_input("\nScegli NPG: "))
                if 1 <= scelta <= len(stato_precedente.npg_presenti):
                    npg_nome = list(stato_precedente.npg_presenti.keys())[scelta - 1]
                    npg = stato_precedente.npg_presenti[npg_nome]
                    
                    # Calcola la difficoltà in base al tipo di abilità
                    caratteristica = ABILITA_ASSOCIATE.get(nome_abilita)
                    difficolta = 10  # Difficoltà base
                    
                    # Aggiusta la difficoltà in base al tipo di abilità
                    if nome_abilita in ["furtività", "percezione", "intuito"]:
                        difficolta += getattr(npg, "saggezza", 0)
                    elif nome_abilita in ["persuasione", "intimidire", "inganno"]:
                        difficolta += getattr(npg, "carisma", 0)
                    
                    dado = Dado(20)
                    tiro = dado.tira()
                    modificatore = gioco.giocatore.modificatore_abilita(nome_abilita)
                    risultato = tiro + modificatore
                    
                    # Mostra dettagli della prova
                    caratteristica_base = getattr(gioco.giocatore, f"{caratteristica}_base")
                    mod_caratteristica = getattr(gioco.giocatore, f"modificatore_{caratteristica}")
                    competenza = gioco.giocatore.abilita_competenze.get(nome_abilita, False)
                    bonus_comp = gioco.giocatore.bonus_competenza if competenza else 0
                    
                    gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} usa {nome_abilita.capitalize()} ({caratteristica}, valore: {caratteristica_base}, mod: {mod_caratteristica})")
                    if competenza:
                        gioco.io.mostra_messaggio(f"Con competenza (+{bonus_comp})")
                    gioco.io.mostra_messaggio(f"Tira un {tiro} + {modificatore} = {risultato}")
                    gioco.io.mostra_messaggio(f"Difficoltà contro {npg.nome}: {difficolta}")
                    
                    if risultato >= difficolta:
                        gioco.io.mostra_messaggio(f"Hai superato la prova di {nome_abilita} contro {npg.nome}!")
                        self._gestisci_successo_npg(gioco, nome_abilita, npg)
                    else:
                        gioco.io.mostra_messaggio(f"Hai fallito la prova di {nome_abilita} contro {npg.nome}.")
                        self._gestisci_fallimento_npg(gioco, nome_abilita, npg)
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
        else:
            # Implementazione per liste simile a quella sopra
            gioco.io.mostra_messaggio("Funzionalità per liste di NPG non ancora implementata completamente.")
    
    def _prova_abilita_oggetto(self, gioco, nome_abilita):
        """Esegue una prova di abilità specifica con un oggetto interattivo"""
        stato_precedente = gioco.stato_stack[-2] if len(gioco.stato_stack) > 1 else None
        
        if not stato_precedente or not hasattr(stato_precedente, 'oggetti_interattivi'):
            gioco.io.mostra_messaggio("Non ci sono oggetti interattivi nelle vicinanze.")
            return
        
        gioco.io.mostra_messaggio("\nScegli l'oggetto con cui interagire:")
        
        # Gestione sia per dizionari che per liste
        if isinstance(stato_precedente.oggetti_interattivi, dict):
            for i, nome in enumerate(stato_precedente.oggetti_interattivi.keys(), 1):
                oggetto = stato_precedente.oggetti_interattivi[nome]
                gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
            
            # Aggiungi l'opzione "Torna indietro" DOPO gli oggetti
            num_opzione_torna = len(stato_precedente.oggetti_interattivi) + 1
            gioco.io.mostra_messaggio(f"{num_opzione_torna}. Torna indietro")
            
            try:
                scelta = int(gioco.io.richiedi_input("\nScegli oggetto: "))
                if 1 <= scelta <= len(stato_precedente.oggetti_interattivi):
                    oggetto_nome = list(stato_precedente.oggetti_interattivi.keys())[scelta - 1]
                    oggetto = stato_precedente.oggetti_interattivi[oggetto_nome]
                    
                    # Determina la difficoltà
                    if nome_abilita in oggetto.difficolta_abilita:
                        difficolta = oggetto.difficolta_abilita[nome_abilita]
                    else:
                        difficolta = 12  # Default
                    
                    # Tiro dell'abilità
                    dado = Dado(20)
                    tiro = dado.tira()
                    modificatore = gioco.giocatore.modificatore_abilita(nome_abilita)
                    risultato = tiro + modificatore
                    
                    # Mostra dettagli della prova
                    caratteristica = ABILITA_ASSOCIATE.get(nome_abilita)
                    caratteristica_base = getattr(gioco.giocatore, f"{caratteristica}_base")
                    mod_caratteristica = getattr(gioco.giocatore, f"modificatore_{caratteristica}")
                    competenza = gioco.giocatore.abilita_competenze.get(nome_abilita, False)
                    bonus_comp = gioco.giocatore.bonus_competenza if competenza else 0
                    
                    gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} usa {nome_abilita.capitalize()} ({caratteristica}, valore: {caratteristica_base}, mod: {mod_caratteristica})")
                    if competenza:
                        gioco.io.mostra_messaggio(f"Con competenza (+{bonus_comp})")
                    gioco.io.mostra_messaggio(f"Tira un {tiro} + {modificatore} = {risultato}")
                    gioco.io.mostra_messaggio(f"Difficoltà per {oggetto.nome}: {difficolta}")
                    
                    self.contesto["tipo"] = "oggetto"
                    self.contesto["oggetto"] = oggetto
                    
                    if risultato >= difficolta:
                        gioco.io.mostra_messaggio(f"Hai superato la prova di {nome_abilita} con {oggetto.nome}!")
                        self._gestisci_successo(gioco, nome_abilita)
                        
                        # Usa il nuovo sistema di interazione specifica
                        oggetto.interagisci_specifico(gioco.giocatore, nome_abilita, gioco)
                    else:
                        gioco.io.mostra_messaggio(f"Hai fallito la prova di {nome_abilita} con {oggetto.nome}.")
                        self._gestisci_fallimento(gioco, nome_abilita)
                elif scelta == num_opzione_torna:
                    return  # Torna al menu precedente
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
        else:
            # Implementazione per liste simile a quella sopra
            gioco.io.mostra_messaggio("Funzionalità per liste di oggetti non ancora implementata completamente.")

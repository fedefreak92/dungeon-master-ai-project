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
        self.fase = "scegli_abilita"  # Fase iniziale
        self.ultimo_input = None  # Per memorizzare l'ultimo input dell'utente
        self.abilita_scelta = None  # L'abilità scelta dall'utente
        self.dati_contestuali = {}  # Per memorizzare dati tra più fasi
        
    def esegui(self, gioco):
        gioco.io.mostra_messaggio("\n=== PROVA DI ABILITÀ ===")
        
        # Gestione basata sulla fase corrente
        if self.fase == "scegli_abilita":
            self._mostra_menu_abilita(gioco)
        elif self.fase == "elabora_scelta_abilita":
            self._elabora_scelta_abilita(gioco)
        elif self.fase == "scegli_modalita":
            self._mostra_menu_modalita(gioco)
        elif self.fase == "elabora_modalita":
            self._elabora_modalita(gioco)
        elif self.fase == "prova_base":
            self._esegui_prova_base(gioco)
        elif self.fase == "prova_npg":
            self._esegui_prova_npg(gioco)
        elif self.fase == "prova_oggetto":
            self._esegui_prova_oggetto(gioco)
        elif self.fase == "abilita_specifica":
            self._esegui_prova_abilita_specifica(gioco)
        elif self.fase == "elabora_scelta_abilita_specifica":
            self._elabora_scelta_abilita_specifica(gioco)
        elif self.fase == "conclusione":
            self._concludi_prova(gioco)
        else:
            # Fase non riconosciuta, torna al menu principale
            self.fase = "scegli_abilita"
            self.esegui(gioco)
    
    def _mostra_menu_abilita(self, gioco):
        gioco.io.mostra_messaggio("Quale abilità vuoi mettere alla prova?")
        gioco.io.mostra_messaggio("1. Forza")
        gioco.io.mostra_messaggio("2. Destrezza")
        gioco.io.mostra_messaggio("3. Costituzione")
        gioco.io.mostra_messaggio("4. Intelligenza")
        gioco.io.mostra_messaggio("5. Saggezza")
        gioco.io.mostra_messaggio("6. Carisma")
        gioco.io.mostra_messaggio("7. Prova su abilità specifica (es. Percezione, Persuasione)")
        gioco.io.mostra_messaggio("8. Torna indietro")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
        self.fase = "elabora_scelta_abilita"
    
    def _elabora_scelta_abilita(self, gioco):
        abilita = {
            "1": "forza",
            "2": "destrezza",
            "3": "costituzione",
            "4": "intelligenza",
            "5": "saggezza",
            "6": "carisma"
        }
        
        scelta = self.ultimo_input
        
        if scelta in abilita:
            self.abilita_scelta = abilita[scelta]
            self.fase = "scegli_modalita"
        elif scelta == "7":
            self.fase = "abilita_specifica"
        elif scelta == "8":
            if gioco.stato_corrente():
                gioco.pop_stato()
        else:
            gioco.io.messaggio_errore("Scelta non valida.")
            self.fase = "scegli_abilita"
    
    def _mostra_menu_modalita(self, gioco):
        gioco.io.mostra_messaggio("\nScegli la modalità di prova:")
        gioco.io.mostra_messaggio("1. Prova base (contro difficoltà)")
        gioco.io.mostra_messaggio("2. Prova contro un personaggio non giocante (NPG)")
        gioco.io.mostra_messaggio("3. Prova con un oggetto interattivo")
        gioco.io.mostra_messaggio("4. Torna indietro")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli modalità: ")
        self.fase = "elabora_modalita"
    
    def _elabora_modalita(self, gioco):
        modalita = self.ultimo_input
        
        if modalita == "1":
            # Prova base
            self.fase = "prova_base"
        elif modalita == "2":
            # Prova contro NPG
            self.fase = "prova_npg"
        elif modalita == "3":
            # Prova con oggetto interattivo
            self.fase = "prova_oggetto"
        elif modalita == "4":
            # Torna al menu abilità
            self.fase = "scegli_abilita"
        else:
            gioco.io.messaggio_errore("Scelta non valida.")
            self.fase = "scegli_modalita"
    
    def _esegui_prova_base(self, gioco):
        if "difficolta" not in self.dati_contestuali:
            try:
                difficolta_input = gioco.io.richiedi_input("Inserisci la difficoltà (5-20): ")
                difficolta = int(difficolta_input)
                difficolta = max(5, min(20, difficolta))  # Limita tra 5 e 20
                self.dati_contestuali["difficolta"] = difficolta
            except ValueError:
                gioco.io.messaggio_errore("Devi inserire un numero per la difficoltà.")
                self.fase = "scegli_modalita"
                return
        
        # Effettua la prova
        difficolta = self.dati_contestuali["difficolta"]
        dado = Dado(20)
        tiro = dado.tira()
        
        # Ottieni il modificatore in base al tipo di abilità
        if self.abilita_scelta in ABILITA_ASSOCIATE:
            # Per abilità specifiche, usa il metodo modificatore_abilita
            modificatore = gioco.giocatore.modificatore_abilita(self.abilita_scelta)
        else:
            # Per caratteristiche base, usa l'attributo diretto
            modificatore = getattr(gioco.giocatore, self.abilita_scelta)
            
        risultato = tiro + modificatore
        
        # Se disponibile, mostra anche il valore base dell'abilità
        if hasattr(gioco.giocatore, f"{self.abilita_scelta}_base"):
            valore_base = getattr(gioco.giocatore, f"{self.abilita_scelta}_base")
            gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} ha {self.abilita_scelta.capitalize()} {valore_base} (modificatore: {modificatore})")
        
        gioco.io.mostra_messaggio(f"{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({self.abilita_scelta}) = {risultato}")
        
        if risultato >= difficolta:
            gioco.io.mostra_messaggio(f"Hai superato la prova di {self.abilita_scelta}!")
            self._gestisci_successo(gioco, self.abilita_scelta)
        else:
            gioco.io.mostra_messaggio(f"Hai fallito la prova di {self.abilita_scelta}.")
            self._gestisci_fallimento(gioco, self.abilita_scelta)
            
        # Attendi conferma e torna al menu principale
        gioco.io.richiedi_input("\nPremi Enter per continuare...")
        if gioco.stato_corrente():
            gioco.pop_stato()
    
    def _esegui_prova_npg(self, gioco):
        """Esegue una prova contro un NPG"""
        # Fase: lista NPG
        if "fase_npg" not in self.dati_contestuali:
            # Ottieni il penultimo stato nella pila (lo stato che ha invocato questo)
            stato_precedente = gioco.stato_stack[-2] if len(gioco.stato_stack) > 1 else None
            
            if not stato_precedente or not hasattr(stato_precedente, 'npg_presenti'):
                gioco.io.mostra_messaggio("Non ci sono personaggi non giocanti nelle vicinanze.")
                self.fase = "scegli_modalita"
                return
            
            gioco.io.mostra_messaggio("\nScegli il personaggio contro cui effettuare la prova:")
            
            # Gestione sia per dizionari che per liste
            if isinstance(stato_precedente.npg_presenti, dict):
                for i, nome in enumerate(stato_precedente.npg_presenti.keys(), 1):
                    gioco.io.mostra_messaggio(f"{i}. {nome}")
                
                self.dati_contestuali["fase_npg"] = "scelta_npg"
                self.dati_contestuali["tipo_lista"] = "dizionario"
                self.dati_contestuali["stato_precedente"] = stato_precedente
                self.ultimo_input = gioco.io.richiedi_input("\nScegli NPG: ")
                return
            else:
                # Gestione per liste
                for i, npg in enumerate(stato_precedente.npg_presenti, 1):
                    gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
                
                self.dati_contestuali["fase_npg"] = "scelta_npg"
                self.dati_contestuali["tipo_lista"] = "lista"
                self.dati_contestuali["stato_precedente"] = stato_precedente
                self.ultimo_input = gioco.io.richiedi_input("\nScegli NPG: ")
                return
        
        # Fase: elabora scelta NPG
        if self.dati_contestuali["fase_npg"] == "scelta_npg":
            try:
                scelta = int(self.ultimo_input)
                stato_precedente = self.dati_contestuali["stato_precedente"]
                
                if self.dati_contestuali["tipo_lista"] == "dizionario":
                    if 1 <= scelta <= len(stato_precedente.npg_presenti):
                        npg_nome = list(stato_precedente.npg_presenti.keys())[scelta - 1]
                        npg = stato_precedente.npg_presenti[npg_nome]
                        self.dati_contestuali["npg"] = npg
                        self.dati_contestuali["fase_npg"] = "effettua_prova"
                    else:
                        gioco.io.messaggio_errore("Scelta non valida.")
                        self.fase = "scegli_modalita"
                        return
                else:  # lista
                    if 1 <= scelta <= len(stato_precedente.npg_presenti):
                        npg = stato_precedente.npg_presenti[scelta - 1]
                        self.dati_contestuali["npg"] = npg
                        self.dati_contestuali["fase_npg"] = "effettua_prova"
                    else:
                        gioco.io.messaggio_errore("Scelta non valida.")
                        self.fase = "scegli_modalita"
                        return
            except ValueError:
                gioco.io.messaggio_errore("Devi inserire un numero.")
                self.fase = "scegli_modalita"
                return
        
        # Fase: effettua la prova
        npg = self.dati_contestuali["npg"]
        
        # Ottieni il modificatore in base al tipo di abilità
        if self.abilita_scelta in ABILITA_ASSOCIATE:
            # Per abilità specifiche, usa il metodo modificatore_abilita
            modificatore = gioco.giocatore.modificatore_abilita(self.abilita_scelta)
        else:
            # Per caratteristiche base, usa l'attributo diretto
            modificatore = getattr(gioco.giocatore, self.abilita_scelta)
        
        if hasattr(gioco.giocatore, f"{self.abilita_scelta}_base") and hasattr(npg, f"{self.abilita_scelta}_base"):
            g_valore = getattr(gioco.giocatore, f"{self.abilita_scelta}_base")
            n_valore = getattr(npg, f"{self.abilita_scelta}_base")
            gioco.io.mostra_messaggio(f"{gioco.giocatore.nome}: {self.abilita_scelta.capitalize()} {g_valore} (mod: {modificatore})")
        
        # Determina la difficoltà in base all'abilità
        if self.abilita_scelta in ["forza", "destrezza", "costituzione"]:
            # Prova fisica - confronta con lo stesso attributo dell'NPG
            difficolta = getattr(npg, self.abilita_scelta, 3) + 10  # Base 10 + mod NPG
        elif self.abilita_scelta in ["intelligenza", "saggezza", "carisma"]:
            # Prova sociale/mentale
            difficolta = getattr(npg, self.abilita_scelta, 3) + 8   # Base 8 + mod NPG
        else:
            # Abilità specifiche - difficoltà standard
            difficolta = 12
        
        dado = Dado(20)
        tiro = dado.tira()
        risultato = tiro + modificatore
        
        gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({self.abilita_scelta}) = {risultato}")
        gioco.io.mostra_messaggio(f"Difficoltà contro {npg.nome}: {difficolta}")
        
        if risultato >= difficolta:
            gioco.io.mostra_messaggio(f"Hai superato la prova di {self.abilita_scelta} contro {npg.nome}!")
            self._gestisci_successo_npg(gioco, self.abilita_scelta, npg)
        else:
            gioco.io.mostra_messaggio(f"Hai fallito la prova di {self.abilita_scelta} contro {npg.nome}.")
            self._gestisci_fallimento_npg(gioco, self.abilita_scelta, npg)
        
        # Attendi conferma e torna al menu principale
        gioco.io.richiedi_input("\nPremi Enter per continuare...")
        if gioco.stato_corrente():
            gioco.pop_stato()
    
    def _esegui_prova_oggetto(self, gioco):
        """Esegue una prova con un oggetto interattivo"""
        # Fase: lista oggetti
        if "fase_oggetto" not in self.dati_contestuali:
            # Ottieni il penultimo stato nella pila (lo stato che ha invocato questo)
            stato_precedente = gioco.stato_stack[-2] if len(gioco.stato_stack) > 1 else None
            
            if not stato_precedente or not hasattr(stato_precedente, 'oggetti_interattivi'):
                gioco.io.mostra_messaggio("Non ci sono oggetti interattivi nelle vicinanze.")
                self.fase = "scegli_modalita"
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
                
                self.dati_contestuali["fase_oggetto"] = "scelta_oggetto"
                self.dati_contestuali["tipo_lista"] = "dizionario"
                self.dati_contestuali["stato_precedente"] = stato_precedente
                self.ultimo_input = gioco.io.richiedi_input("\nScegli oggetto: ")
                return
            else:
                # Gestione per liste
                for i, oggetto in enumerate(stato_precedente.oggetti_interattivi, 1):
                    gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
                
                # Aggiungi l'opzione "Torna indietro"
                num_opzione_torna = len(stato_precedente.oggetti_interattivi) + 1
                gioco.io.mostra_messaggio(f"{num_opzione_torna}. Torna indietro")
                
                self.dati_contestuali["fase_oggetto"] = "scelta_oggetto"
                self.dati_contestuali["tipo_lista"] = "lista"
                self.dati_contestuali["stato_precedente"] = stato_precedente
                self.ultimo_input = gioco.io.richiedi_input("\nScegli oggetto: ")
                return
        
        # Fase: elabora scelta oggetto
        if self.dati_contestuali["fase_oggetto"] == "scelta_oggetto":
            try:
                scelta = int(self.ultimo_input)
                stato_precedente = self.dati_contestuali["stato_precedente"]
                
                if self.dati_contestuali["tipo_lista"] == "dizionario":
                    num_opzione_torna = len(stato_precedente.oggetti_interattivi) + 1
                    if 1 <= scelta <= len(stato_precedente.oggetti_interattivi):
                        oggetto_nome = list(stato_precedente.oggetti_interattivi.keys())[scelta - 1]
                        oggetto = stato_precedente.oggetti_interattivi[oggetto_nome]
                        self.dati_contestuali["oggetto"] = oggetto
                        self.dati_contestuali["fase_oggetto"] = "effettua_prova"
                    elif scelta == num_opzione_torna:
                        self.fase = "scegli_modalita"
                        return
                    else:
                        gioco.io.messaggio_errore("Scelta non valida.")
                        self.fase = "scegli_modalita"
                        return
                else:  # lista
                    num_opzione_torna = len(stato_precedente.oggetti_interattivi) + 1
                    if 1 <= scelta <= len(stato_precedente.oggetti_interattivi):
                        oggetto = stato_precedente.oggetti_interattivi[scelta - 1]
                        self.dati_contestuali["oggetto"] = oggetto
                        self.dati_contestuali["fase_oggetto"] = "effettua_prova"
                    elif scelta == num_opzione_torna:
                        self.fase = "scegli_modalita"
                        return
                    else:
                        gioco.io.messaggio_errore("Scelta non valida.")
                        self.fase = "scegli_modalita"
                        return
            except ValueError:
                gioco.io.messaggio_errore("Devi inserire un numero.")
                self.fase = "scegli_modalita"
                return
        
        # Fase: effettua la prova
        oggetto = self.dati_contestuali["oggetto"]
        
        # Ottieni il modificatore in base al tipo di abilità
        if self.abilita_scelta in ABILITA_ASSOCIATE:
            # Per abilità specifiche, usa il metodo modificatore_abilita
            modificatore = gioco.giocatore.modificatore_abilita(self.abilita_scelta)
        else:
            # Per caratteristiche base, usa l'attributo diretto
            modificatore = getattr(gioco.giocatore, self.abilita_scelta)
        
        # Visualizza i valori base se disponibili
        if hasattr(gioco.giocatore, f"{self.abilita_scelta}_base"):
            valore_base = getattr(gioco.giocatore, f"{self.abilita_scelta}_base")
            gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} ha {self.abilita_scelta.capitalize()} {valore_base} (modificatore: {modificatore})")
        
        # Determina la difficoltà in base al tipo di oggetto e all'abilità
        if isinstance(oggetto, OggettoInterattivo):
            if self.abilita_scelta == "forza" and hasattr(oggetto, "forza_richiesta"):
                difficolta = oggetto.forza_richiesta + 8
            elif self.abilita_scelta == "destrezza" and hasattr(oggetto, "difficolta_salvezza"):
                difficolta = oggetto.difficolta_salvezza
            else:
                difficolta = 12  # Difficoltà standard
        else:
            difficolta = 10  # Oggetto generico
        
        dado = Dado(20)
        tiro = dado.tira()
        risultato = tiro + modificatore
        
        gioco.io.mostra_messaggio(f"\n{gioco.giocatore.nome} tira un {tiro} + {modificatore} ({self.abilita_scelta}) = {risultato}")
        gioco.io.mostra_messaggio(f"Difficoltà per {oggetto.nome}: {difficolta}")
        
        self.contesto["tipo"] = "oggetto"
        self.contesto["oggetto"] = oggetto
        
        if risultato >= difficolta:
            gioco.io.mostra_messaggio(f"Hai superato la prova di {self.abilita_scelta} con {oggetto.nome}!")
            self._gestisci_successo(gioco, self.abilita_scelta)
            
            # Attiva l'interazione specifica con l'oggetto
            if self.abilita_scelta == "forza" and hasattr(oggetto, "stato") and oggetto.stato == "integro":
                gioco.io.mostra_messaggio(f"Grazie alla tua forza, puoi interagire efficacemente con {oggetto.nome}!")
                oggetto.interagisci(gioco.giocatore)
        else:
            gioco.io.mostra_messaggio(f"Hai fallito la prova di {self.abilita_scelta} con {oggetto.nome}.")
            self._gestisci_fallimento(gioco, self.abilita_scelta)
        
        # Attendi conferma e torna al menu principale
        gioco.io.richiedi_input("\nPremi Enter per continuare...")
        if gioco.stato_corrente():
            gioco.pop_stato()
    
    def _esegui_prova_abilita_specifica(self, gioco):
        """Gestisce la prova di un'abilità specifica come Percezione, Persuasione, ecc."""
        gioco.io.mostra_messaggio("\nScegli l'abilità da provare:")
        for i, abilita in enumerate(ABILITA_ASSOCIATE.keys(), 1):
            # Mostra se il giocatore ha competenza
            competenza = " [Competente]" if gioco.giocatore.abilita_competenze.get(abilita.lower()) else ""
            gioco.io.mostra_messaggio(f"{i}. {abilita.capitalize()}{competenza}")
        
        self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
        self.fase = "elabora_scelta_abilita_specifica"
    
    def _elabora_scelta_abilita_specifica(self, gioco):
        try:
            idx = int(self.ultimo_input) - 1
            if 0 <= idx < len(ABILITA_ASSOCIATE):
                self.abilita_scelta = list(ABILITA_ASSOCIATE.keys())[idx].lower()
                self.dati_contestuali["abilita_scelta"] = self.abilita_scelta
                self.fase = "scegli_modalita"
            else:
                gioco.io.messaggio_errore("Scelta non valida.")
                self.fase = "abilita_specifica"
        except (IndexError, ValueError):
            gioco.io.messaggio_errore("Scelta non valida.")
            self.fase = "abilita_specifica"
    
    def _concludi_prova(self, gioco):
        gioco.io.richiedi_input("\nPremi Enter per continuare...")
        if gioco.stato_corrente():
            gioco.pop_stato()
            
    # Metodi di gestione degli effetti (rimangono invariati)
    
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

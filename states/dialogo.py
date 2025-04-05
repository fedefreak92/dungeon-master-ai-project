from states.base_state import BaseState
from entities.npg import NPG

class DialogoState(BaseState):
    def __init__(self, npg, stato_iniziale="inizio"):
        """
        Inizializza uno stato di dialogo con un NPG.
        
        Args:
            npg (NPG): Il personaggio non giocante con cui dialogare
            stato_iniziale (str): Lo stato iniziale della conversazione
        """
        self.npg = npg
        self.stato_corrente = stato_iniziale
        self.conversazione = npg.ottieni_conversazione(stato_iniziale)
        self.in_dialogo = True
        self.scelte_fatte = {}  # Memorizza le scelte fatte dall'utente
        self.fase = "mostra_testo"  # Fasi: mostra_testo, attendi_input, elabora_input, conclusione
        self.ultima_input = None  # Memorizza l'ultimo input dell'utente
        
    def esegui(self, gioco):
        """Esegue il dialogo, gestendo una fase alla volta"""
        if not self.in_dialogo or self.conversazione is None:
            if gioco.stato_corrente():
                gioco.pop_stato()
            return
        
        # Gestione basata sulla fase corrente
        if self.fase == "mostra_testo":
            self._mostra_testo_dialogo(gioco)
            self.fase = "applica_effetto" if 'effetto' in self.conversazione else "mostra_opzioni"
            
        elif self.fase == "applica_effetto":
            self._applica_effetto(gioco, self.conversazione['effetto'])
            self.fase = "mostra_opzioni"
            
        elif self.fase == "mostra_opzioni":
            opzioni = self.conversazione.get('opzioni', [])
            if not opzioni:
                # Se non ci sono opzioni, prepara per la conclusione
                self.fase = "conclusione"
                return
                
            # Mostra opzioni disponibili
            gioco.io.mostra_messaggio("\nOpzioni disponibili:")
            for i, (testo, _) in enumerate(opzioni, 1):
                gioco.io.mostra_messaggio(f"{i}. {testo}")
                
            # Prepara per l'input nella prossima chiamata
            self.fase = "attendi_input"
            
        elif self.fase == "attendi_input":
            opzioni = self.conversazione.get('opzioni', [])
            if not opzioni:
                self.fase = "conclusione"
                return
                
            # Richiede input dall'utente
            self.ultima_input = gioco.io.richiedi_input("\nScegli un'opzione (1-{}): ".format(len(opzioni)))
            # Passa alla fase di elaborazione
            self.fase = "elabora_input"
            
        elif self.fase == "elabora_input":
            opzioni = self.conversazione.get('opzioni', [])
            if self._elabora_scelta(gioco, opzioni):
                # La fase viene aggiornata all'interno di _elabora_scelta
                pass
            else:
                # Se c'è stato un errore, torna ad attendere input
                self.fase = "attendi_input"
                
        elif self.fase == "conclusione":
            if not self.conversazione.get('opzioni', []):
                # Non ci sono opzioni, è un semplice messaggio, attendiamo un Enter per continuare
                self.ultima_input = gioco.io.richiedi_input("\nPremi Enter per continuare...")
            
            # Termina il dialogo
            self.in_dialogo = False
            if gioco.stato_corrente():
                gioco.pop_stato()
                
    def _mostra_testo_dialogo(self, gioco):
        """Mostra il testo del dialogo corrente"""
        gioco.io.mostra_messaggio("\n" + "="*50)
        gioco.io.mostra_messaggio(f"{self.npg.nome}: {self.conversazione['testo']}")
        gioco.io.mostra_messaggio("="*50)
            
    def _elabora_scelta(self, gioco, opzioni):
        """
        Elabora la scelta dell'utente
        
        Returns:
            bool: True se la scelta è valida, False altrimenti
        """
        scelta_input = self.ultima_input
        
        try:
            # Prova a convertire in intero
            if scelta_input.isdigit():
                scelta = int(scelta_input)
            else:
                # Se l'input non è numerico, cerca di abbinarlo a un'opzione
                scelta = self._trova_opzione_da_testo(scelta_input, opzioni)
                
            if scelta is not None and 1 <= scelta <= len(opzioni):
                testo_scelta, prossimo_stato = opzioni[scelta-1]
                
                # Salva la scelta fatta
                self.scelte_fatte[self.stato_corrente] = scelta
                
                if prossimo_stato is None:
                    # Fine dialogo
                    self.fase = "conclusione"
                else:
                    self.conversazione = self.npg.ottieni_conversazione(prossimo_stato)
                    if self.conversazione is None:
                        gioco.io.mostra_messaggio(f"Stato di dialogo '{prossimo_stato}' non trovato per {self.npg.nome}")
                        self.fase = "conclusione"
                    else:
                        self.stato_corrente = prossimo_stato
                        # Ricomincia il ciclo con il nuovo dialogo
                        self.fase = "mostra_testo"
                return True
            else:
                gioco.io.mostra_messaggio(f"Scelta non valida: '{scelta_input}'.")
                return False
        except (ValueError, TypeError):
            gioco.io.mostra_messaggio(f"Input non valido: '{scelta_input}'. Usa un numero o il testo di un'opzione.")
            return False
    
    def _trova_opzione_da_testo(self, testo_input, opzioni):
        """
        Cerca di abbinare l'input testuale a un'opzione di dialogo
        
        Args:
            testo_input (str): Il testo inserito dall'utente
            opzioni (list): Lista di opzioni di dialogo
            
        Returns:
            int or None: L'indice dell'opzione corrispondente + 1, o None se non trovata
        """
        testo_input = testo_input.lower().strip()
        
        # Cerca una corrispondenza esatta o parziale con un'opzione
        for i, (testo_opzione, _) in enumerate(opzioni, 1):
            if testo_input == testo_opzione.lower() or testo_input in testo_opzione.lower():
                return i
                
        # Se non trova una corrispondenza diretta, cerca parole chiave
        for i, (testo_opzione, _) in enumerate(opzioni, 1):
            # Dividi il testo dell'opzione in parole
            parole = set(testo_opzione.lower().split())
            # Se almeno una parola dell'input utente è anche nel testo dell'opzione
            if any(parola in parole for parola in testo_input.split()):
                return i
                
        return None
    
    def _applica_effetto(self, gioco, effetto):
        """Applica effetti speciali in base al tipo di effetto"""
        if isinstance(effetto, str):
            # Gestione effetti semplici
            if effetto == "riposo":
                gioco.giocatore.cura(5)
                gioco.io.mostra_messaggio("\n*Hai riposato e recuperato 5 HP*")
            elif effetto == "cura_leggera":
                gioco.giocatore.cura(3)
                gioco.io.mostra_messaggio("\n*L'unguento di Violetta ti cura per 3 HP*")
        elif isinstance(effetto, dict):
            # Gestione effetti complessi
            tipo = effetto.get("tipo", "")
            
            if tipo == "consegna_oro":
                quantita = effetto.get("quantita", 10)
                self.npg.trasferisci_oro(gioco.giocatore, quantita)
                gioco.io.mostra_messaggio(f"\n*{self.npg.nome} ti ha dato {quantita} monete d'oro*")
                
            elif tipo == "aggiungi_item":
                oggetto = effetto.get("oggetto")
                if oggetto and self.npg.rimuovi_item(oggetto):
                    gioco.giocatore.aggiungi_item(oggetto)
                    gioco.io.mostra_messaggio(f"\n*Hai ricevuto {oggetto} da {self.npg.nome}*")
                    
            elif tipo == "rimuovi_item":
                oggetto = effetto.get("oggetto")
                if oggetto and gioco.giocatore.rimuovi_item(oggetto):
                    self.npg.aggiungi_item(oggetto)
                    gioco.io.mostra_messaggio(f"\n*Hai dato {oggetto} a {self.npg.nome}*")
                    
            elif tipo == "scambio":
                oggetto_nome = effetto.get("oggetto")
                costo = effetto.get("costo", 0)
                
                # Trova l'oggetto nell'inventario dell'NPC
                oggetto_trovato = None
                for item in self.npg.inventario:
                    if item.nome == oggetto_nome:
                        oggetto_trovato = item
                        break
                
                if gioco.giocatore.oro >= costo and oggetto_trovato is not None:
                    gioco.giocatore.oro -= costo
                    self.npg.oro += costo
                    self.npg.rimuovi_item(oggetto_nome)
                    gioco.giocatore.aggiungi_item(oggetto_trovato)
                    gioco.io.mostra_messaggio(f"\n*Hai acquistato {oggetto_nome} da {self.npg.nome} per {costo} monete d'oro*")
                else:
                    if gioco.giocatore.oro < costo:
                        gioco.io.mostra_messaggio(f"\n*Non hai abbastanza oro per acquistare {oggetto_nome}*")
                    else:
                        gioco.io.mostra_messaggio(f"\n*{self.npg.nome} non ha più {oggetto_nome} disponibile*")

    def pausa(self, gioco):
        """
        Quando il dialogo viene messo in pausa
        salviamo lo stato corrente del dialogo
        """
        gioco.io.mostra_messaggio(f"\nIl dialogo con {self.npg.nome} rimane in sospeso...")
        
    def riprendi(self, gioco):
        """
        Quando il dialogo riprende dopo una pausa
        mostriamo un messaggio di ripresa
        """
        gioco.io.mostra_messaggio(f"\nRiprendi il dialogo con {self.npg.nome}...")
        
    def esci(self, gioco):
        """
        Quando si esce dal dialogo
        puliamo lo stato
        """
        self.in_dialogo = False
        gioco.io.mostra_messaggio(f"\nConcludi il dialogo con {self.npg.nome}...")
        
    def ha_fatto_scelta(self, stato, scelta=None):
        """
        Verifica se il giocatore ha fatto una particolare scelta durante il dialogo
        
        Args:
            stato (str): Lo stato del dialogo
            scelta (int, optional): La scelta specifica da verificare
            
        Returns:
            bool: True se la scelta è stata fatta, False altrimenti
        """
        if stato not in self.scelte_fatte:
            return False
            
        if scelta is None:
            return True
            
        return self.scelte_fatte[stato] == scelta

    def to_dict(self):
        """
        Converte lo stato del dialogo in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dello stato in formato dizionario
        """
        # Ottieni il dizionario base
        data = super().to_dict()
        
        # Aggiungi attributi specifici
        data.update({
            "stato_corrente": self.stato_corrente,
            "stato_precedente": self.stato_precedente,
            "scelte_fatte": self.scelte_fatte,
            "ultimo_input": self.ultimo_input
        })
        
        # Salva le informazioni sul NPG
        if self.npg:
            if hasattr(self.npg, 'to_dict'):
                data["npg"] = self.npg.to_dict()
            else:
                data["npg"] = {"nome": self.npg.nome}
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di DialogoState da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            
        Returns:
            DialogoState: Nuova istanza di DialogoState
        """
        # Per creare un dialogo serve un NPG
        from entities.npg import NPG
        
        # Recupera o crea l'NPG
        npg_data = data.get("npg", {})
        if isinstance(npg_data, dict):
            if hasattr(NPG, 'from_dict'):
                npg = NPG.from_dict(npg_data)
            else:
                npg = NPG(npg_data.get("nome", "NPC Sconosciuto"))
        else:
            npg = NPG("NPC Sconosciuto")
            
        # Crea lo stato con l'NPG
        state = cls(npg, stato_iniziale=data.get("stato_corrente", "inizio"))
        
        # Ripristina attributi
        state.stato_precedente = data.get("stato_precedente")
        state.scelte_fatte = data.get("scelte_fatte", {})
        state.ultimo_input = data.get("ultimo_input")
        
        return state
        
    def __getstate__(self):
        """
        Metodo speciale per la serializzazione con pickle.
        
        Returns:
            dict: Stato serializzabile dell'oggetto
        """
        state = self.__dict__.copy()
        
        # Rimuovi eventuali riferimenti ciclici o non serializzabili
        # Le variabili specifiche al dialogo sono già primitive
        
        return state
    
    def __setstate__(self, state):
        """
        Metodo speciale per la deserializzazione con pickle.
        
        Args:
            state (dict): Stato dell'oggetto da ripristinare
        """
        self.__dict__.update(state)

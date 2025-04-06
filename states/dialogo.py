from states.base_state import BaseState
from entities.npg import NPG

class DialogoState(BaseState):
    """Stato che gestisce il dialogo con un NPG"""
    
    def __init__(self, npg=None, stato_ritorno=None):
        """
        Costruttore dello stato di dialogo
        
        Args:
            npg (NPG, optional): L'NPG con cui dialogare
            stato_ritorno (str, optional): Nome dello stato in cui tornare dopo il dialogo
        """
        self.fase = "conversazione"
        self.ultimo_input = None
        self.npg = npg
        self.stato_corrente = "inizio"
        self.stato_ritorno = stato_ritorno
        self.dati_contestuali = {}  # Per memorizzare dati tra più fasi
        
    def esegui(self, gioco):
        """
        Esegue la fase di dialogo
        
        Args:
            gioco (Gioco): Il gioco in cui si sta svolgendo il dialogo
            
        Returns:
            str: il prossimo stato
        """
        # Controlla se c'è un NPG valido
        if not self.npg:
            gioco.io.mostra_messaggio("Non c'è nessuno con cui parlare qui.")
            gioco.io.richiedi_input("\nPremi Invio per continuare...")
            gioco.pop_stato()  # Esce dallo stato corrente
            return self.stato_ritorno or "mappa"
        
        # Ottieni l'interfaccia di input/output
        io = gioco.io
        
        # Ottieni i dati della conversazione per lo stato corrente
        dati_conversazione = self.npg.ottieni_conversazione(self.stato_corrente)
        
        # Se i dati non esistono, torna al menu principale
        if not dati_conversazione:
            io.mostra_messaggio(f"{self.npg.nome} non ha nulla da dirti.")
            io.richiedi_input("\nPremi Invio per continuare...")
            gioco.pop_stato()  # Esce dallo stato corrente
            return self.stato_ritorno or "mappa"
        
        # Gestisce gli effetti legati allo stato della conversazione
        if "effetto" in dati_conversazione:
            self._gestisci_effetto(dati_conversazione["effetto"], gioco)
        
        # Mostra il testo della conversazione
        io.mostra_messaggio(f"{self.npg.nome}: {dati_conversazione['testo']}")
        
        # Se la conversazione non ha opzioni, torna allo stato di ritorno
        if not dati_conversazione.get("opzioni"):
            io.richiedi_input("\nPremi Invio per continuare...")
            gioco.pop_stato()  # Esce dallo stato corrente
            return self.stato_ritorno or "mappa"
        
        # Mostra le opzioni di dialogo
        io.mostra_messaggio("\nOpzioni:")
        
        for i, (testo, _) in enumerate(dati_conversazione["opzioni"], 1):
            io.mostra_messaggio(f"{i}. {testo}")
        
        # Ottieni la scelta dell'utente
        scelta_input = io.richiedi_input("\nScegli un'opzione: ")
        
        # Converti l'input in un numero
        try:
            scelta = int(scelta_input)
            if scelta < 1 or scelta > len(dati_conversazione["opzioni"]):
                io.mostra_messaggio("Scelta non valida.")
                io.richiedi_input("\nPremi Invio per continuare...")
                return "dialogo"  # Rimani nello stesso stato
                
            # Ottieni la destinazione (stato successivo) della scelta
            _, destinazione = dati_conversazione["opzioni"][scelta - 1]
            
            # Se la destinazione è None, torna allo stato di ritorno
            if destinazione is None:
                # Aggiungi una pausa per leggere il messaggio
                io.richiedi_input("\nPremi Invio per continuare...")
                gioco.pop_stato()  # Esce dallo stato corrente
                return self.stato_ritorno or "mappa"
            
            # Altrimenti, passa allo stato successivo della conversazione
            self.stato_corrente = destinazione
            return "dialogo"
        except ValueError:
            io.mostra_messaggio("Per favore, inserisci un numero valido.")
            io.richiedi_input("\nPremi Invio per continuare...")
            return "dialogo"
    
    def _gestisci_effetto(self, effetto, gioco):
        """Applica effetti speciali in base al tipo di effetto"""
        if isinstance(effetto, str):
            # Gestione effetti semplici
            if effetto == "riposo":
                gioco.giocatore.cura(5, gioco)
                gioco.io.mostra_messaggio("\n*Hai riposato e recuperato 5 HP*")
            elif effetto == "cura_leggera":
                gioco.giocatore.cura(3, gioco)
                gioco.io.mostra_messaggio("\n*L'unguento di Violetta ti cura per 3 HP*")
        elif isinstance(effetto, dict):
            # Gestione effetti complessi
            tipo = effetto.get("tipo", "")
            
            if tipo == "consegna_oro":
                quantita = effetto.get("quantita", 10)
                self.npg.trasferisci_oro(gioco.giocatore, quantita, gioco)
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
        self.fase = "conversazione"
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
        if stato not in self.dati_contestuali:
            return False
            
        if scelta is None:
            return True
            
        return self.dati_contestuali[stato] == scelta

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
            "stato_ritorno": self.stato_ritorno,
            "dati_contestuali": self.dati_contestuali,
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
        state = cls(npg, stato_ritorno=data.get("stato_ritorno"))
        
        # Ripristina attributi
        state.dati_contestuali = data.get("dati_contestuali", {})
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

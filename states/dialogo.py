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
        
    def esegui(self, gioco):
        """Esegue il dialogo, mostrando il testo e gestendo le scelte"""
        if not self.in_dialogo or self.conversazione is None:
            gioco.pop_stato()
            return
            
        # Mostra il testo del dialogo
        gioco.io.mostra_messaggio("\n" + "="*50)
        gioco.io.mostra_messaggio(f"{self.npg.nome}: {self.conversazione['testo']}")
        gioco.io.mostra_messaggio("="*50)
        
        # Verifica se c'è un effetto da applicare
        if 'effetto' in self.conversazione:
            self._applica_effetto(gioco, self.conversazione['effetto'])
        
        # Mostra le opzioni
        opzioni = self.conversazione.get('opzioni', [])
        if opzioni:
            gioco.io.mostra_messaggio("\nOpzioni disponibili:")
            for i, (testo, _) in enumerate(opzioni, 1):
                gioco.io.mostra_messaggio(f"{i}. {testo}")
                
            # Gestione input
            gioco.io.mostra_messaggio("\nScegli un'opzione (1-{}): ".format(len(opzioni)))
            try:
                scelta = int(gioco.io.richiedi_input())
                if 1 <= scelta <= len(opzioni):
                    testo_scelta, prossimo_stato = opzioni[scelta-1]
                    
                    # Salva la scelta fatta
                    self.scelte_fatte[self.stato_corrente] = scelta
                    
                    if prossimo_stato is None:
                        self.in_dialogo = False
                        gioco.pop_stato()
                    else:
                        self.conversazione = self.npg.ottieni_conversazione(prossimo_stato)
                        if self.conversazione is None:
                            gioco.io.mostra_messaggio(f"Stato di dialogo '{prossimo_stato}' non trovato per {self.npg.nome}")
                            self.in_dialogo = False
                            gioco.pop_stato()
                        else:
                            self.stato_corrente = prossimo_stato
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Input non valido. Usa un numero.")
        else:
            # Se non ci sono opzioni, aspetta un input per continuare
            gioco.io.richiedi_input("\nPremi Enter per continuare...")
            self.in_dialogo = False
            gioco.pop_stato()
    
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

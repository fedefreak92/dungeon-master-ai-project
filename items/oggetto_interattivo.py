from util.dado import Dado

class OggettoInterattivo:
    def __init__(self, nome, descrizione="", stato="chiuso", contenuto=None, posizione=None, token="O"):
        """
        Inizializza un oggetto interattivo nel mondo di gioco.
        
        Args:
            nome: Nome dell'oggetto
            descrizione: Descrizione testuale dell'oggetto
            stato: Stato attuale dell'oggetto (es. "chiuso", "aperto", "attivo", "rotto")
            contenuto: Lista di oggetti contenuti (se applicabile)
            posizione: Posizione dell'oggetto nel mondo di gioco (es. "taverna", "mercato", o coordinate)
            token: Token per la rappresentazione sulla mappa
        """
        self.nome = nome
        self.descrizione = descrizione
        self.stato = stato
        self.contenuto = contenuto or []  # Lista di oggetti contenuti
        self.oggetti_collegati = {}  # Dizionario di oggetti che possono essere influenzati da questo
        self.posizione = posizione  # Posizione dell'oggetto nel mondo
        self.token = token  # Token per la rappresentazione sulla mappa
        
        # Nuovi attributi
        self.descrizioni_stati = {stato: descrizione}  # Descrizioni per ogni stato
        self.stati_possibili = {}  # Dizionario delle transizioni possibili
        self.abilita_richieste = {}  # Abilità necessarie per interazioni specifiche
        self.difficolta_abilita = {}  # Difficoltà per ogni abilità
        self.messaggi_interazione = {}  # Feedback narrativi per interazioni
        self.eventi = {}  # Eventi da attivare al cambiamento di stato
    
    def __getstate__(self):
        """
        Prepara l'oggetto per la serializzazione con pickle.
        
        Returns:
            dict: Stato dell'oggetto da serializzare
        """
        # Crea una copia del dizionario dello stato
        state = self.__dict__.copy()
        
        # Rimuove attributi non serializzabili (come funzioni)
        if 'eventi' in state:
            del state['eventi']
        
        # Rimuove altri elementi non serializzabili
        non_serializzabili = []
        for key, value in state.items():
            if callable(value) or key.startswith('__'):
                non_serializzabili.append(key)
        
        for key in non_serializzabili:
            del state[key]
        
        return state

    def __setstate__(self, state):
        """
        Ripristina lo stato dell'oggetto dopo la deserializzazione.
        
        Args:
            state: Stato deserializzato da ripristinare
        """
        # Inizializza eventi vuoti
        state['eventi'] = {}
        
        # Aggiorna lo stato dell'oggetto
        self.__dict__.update(state)
    
    def interagisci(self, giocatore, gioco=None):
        """
        Metodo principale di interazione. Dovrebbe essere sovrascritto nelle sottoclassi.
        """
        if gioco:
            gioco.io.mostra_messaggio(f"Non succede nulla con {self.nome}...")
    
    def descrivi(self, gioco=None):
        """
        Mostra la descrizione dell'oggetto e il suo stato attuale.
        """
        if gioco:
            gioco.io.mostra_messaggio(f"{self.nome}: {self.descrizione} [{self.stato}]")
            if self.posizione:
                gioco.io.mostra_messaggio(f"Si trova in: {self.posizione}")
    
    def collega_oggetto(self, nome_collegamento, oggetto):
        """
        Collega un altro oggetto interattivo a questo (es. una leva a una porta).
        """
        self.oggetti_collegati[nome_collegamento] = oggetto
    
    def sposta(self, nuova_posizione, gioco=None):
        """
        Sposta l'oggetto in una nuova posizione.
        """
        self.posizione = nuova_posizione
        if gioco:
            gioco.io.mostra_messaggio(f"{self.nome} è stato spostato in: {nuova_posizione}")
        
    def interagisci_specifico(self, giocatore, abilita, gioco=None):
        """
        Gestisce interazioni basate su abilità specifiche.
        """
        if abilita not in self.abilita_richieste:
            if gioco:
                gioco.io.mostra_messaggio(f"Non puoi usare {abilita} con {self.nome} in questo momento.")
            return False
            
        # Ottieni messaggio narrativo se disponibile
        if abilita in self.messaggi_interazione and gioco:
            gioco.io.mostra_messaggio(self.messaggi_interazione[abilita])
        
        # Transizione di stato se necessaria
        if abilita in self.abilita_richieste:
            nuovo_stato = self.abilita_richieste[abilita]
            if nuovo_stato in self.stati_possibili.get(self.stato, []):
                self.cambia_stato(nuovo_stato, gioco)
                return True
        
        return False
    
    def cambia_stato(self, nuovo_stato, gioco=None):
        """
        Cambia lo stato dell'oggetto e attiva eventi nel mondo.
        """
        vecchio_stato = self.stato
        if nuovo_stato in self.stati_possibili.get(vecchio_stato, []):
            self.stato = nuovo_stato
            
            # Mostra descrizione del nuovo stato
            if gioco:
                if nuovo_stato in self.descrizioni_stati:
                    gioco.io.mostra_messaggio(self.descrizioni_stati[nuovo_stato])
                else:
                    gioco.io.mostra_messaggio(f"{self.nome} è ora {nuovo_stato}.")
            
            # Attiva eventi nel mondo
            if gioco and nuovo_stato in self.eventi:
                for evento in self.eventi[nuovo_stato]:
                    evento(gioco)
            
            return True
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"Impossibile cambiare {self.nome} da {vecchio_stato} a {nuovo_stato}.")
            return False
    
    def aggiungi_transizione(self, stato_corrente, stato_nuovo):
        """
        Definisce una transizione possibile tra stati.
        """
        if stato_corrente not in self.stati_possibili:
            self.stati_possibili[stato_corrente] = []
        
        if stato_nuovo not in self.stati_possibili[stato_corrente]:
            self.stati_possibili[stato_corrente].append(stato_nuovo)
    
    def imposta_descrizione_stato(self, stato, descrizione):
        """
        Definisce una descrizione per uno stato specifico.
        """
        self.descrizioni_stati[stato] = descrizione
    
    def richiedi_abilita(self, abilita, stato_risultante, difficolta=10, messaggio=None):
        """
        Definisce un'abilità che può essere usata con questo oggetto.
        """
        self.abilita_richieste[abilita] = stato_risultante
        self.difficolta_abilita[abilita] = difficolta
        
        if messaggio:
            self.messaggi_interazione[abilita] = messaggio
    
    def collega_evento(self, stato, evento):
        """
        Collega un evento da attivare quando l'oggetto entra in un certo stato.
        """
        if stato not in self.eventi:
            self.eventi[stato] = []
        
        self.eventi[stato].append(evento)
        
    def to_dict(self):
        """
        Converte l'oggetto interattivo in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dell'oggetto in formato dizionario
        """
        # Serializza solo gli attributi fondamentali
        return {
            "nome": self.nome,
            "descrizione": self.descrizione,
            "stato": self.stato,
            "contenuto": [obj.to_dict() if hasattr(obj, 'to_dict') else obj.nome for obj in self.contenuto],
            "posizione": self.posizione,
            "token": self.token,
            "descrizioni_stati": self.descrizioni_stati,
            "stati_possibili": self.stati_possibili,
            "abilita_richieste": self.abilita_richieste,
            "difficolta_abilita": self.difficolta_abilita,
            "messaggi_interazione": self.messaggi_interazione,
            # Gli eventi non sono serializzabili direttamente
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di OggettoInterattivo da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dell'oggetto
            
        Returns:
            OggettoInterattivo: Nuova istanza di OggettoInterattivo
        """
        from items.oggetto import Oggetto
        
        oggetto = cls(
            nome=data.get("nome", ""),
            descrizione=data.get("descrizione", ""),
            stato=data.get("stato", "chiuso"),
            posizione=data.get("posizione"),
            token=data.get("token", "O")
        )
        
        # Impostazione del contenuto
        contenuto_raw = data.get("contenuto", [])
        contenuto = []
        
        for item in contenuto_raw:
            if isinstance(item, dict):
                contenuto.append(Oggetto.from_dict(item))
            elif isinstance(item, str):
                # Crea un oggetto generico se solo il nome è disponibile
                contenuto.append(Oggetto(item, "comune"))
        
        oggetto.contenuto = contenuto
        
        # Caricamento delle altre proprietà
        oggetto.descrizioni_stati = data.get("descrizioni_stati", {oggetto.stato: oggetto.descrizione})
        oggetto.stati_possibili = data.get("stati_possibili", {})
        oggetto.abilita_richieste = data.get("abilita_richieste", {})
        oggetto.difficolta_abilita = data.get("difficolta_abilita", {})
        oggetto.messaggi_interazione = data.get("messaggi_interazione", {})
        
        return oggetto


class Baule(OggettoInterattivo):
    def __init__(self, nome, descrizione="", stato="chiuso", contenuto=None, richiede_chiave=False, posizione=None, token="C"):
        super().__init__(nome, descrizione, stato, contenuto, posizione, token)
        self.richiede_chiave = richiede_chiave
    
    def interagisci(self, giocatore, gioco=None):
        if self.stato == "chiuso":
            if self.richiede_chiave:
                # Verifica se il giocatore ha una chiave
                chiave_trovata = False
                for item in giocatore.inventario:
                    if isinstance(item, str):
                        nome_item = item
                    else:
                        nome_item = item.nome
                    
                    if "chiave" in nome_item.lower():
                        chiave_trovata = True
                        break
                
                if not chiave_trovata:
                    if gioco:
                        gioco.io.mostra_messaggio("Il baule è chiuso a chiave. Ti serve una chiave per aprirlo.")
                    return
                if gioco:
                    gioco.io.mostra_messaggio("Usi la chiave per aprire il baule...")
            
            if gioco:
                gioco.io.mostra_messaggio(f"Apri il {self.nome}...")
            self.stato = "aperto"
            if self.contenuto:
                if gioco:
                    gioco.io.mostra_messaggio("Dentro trovi:")
                    for oggetto in self.contenuto:
                        gioco.io.mostra_messaggio(f"- {oggetto.nome}")
                giocatore.aggiungi_item(oggetto)
                self.contenuto = []
            else:
                if gioco:
                    gioco.io.mostra_messaggio("È vuoto.")
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"Il {self.nome} è già aperto.")


class Porta(OggettoInterattivo):
    def __init__(self, nome, descrizione="", stato="chiusa", richiede_chiave=False, posizione=None, posizione_destinazione=None, token="D"):
        super().__init__(nome, descrizione, stato, None, posizione, token)
        self.richiede_chiave = richiede_chiave
        self.posizione_destinazione = posizione_destinazione  # Dove porta questa porta
    
    def interagisci(self, giocatore, gioco=None):
        if self.stato == "chiusa":
            if self.richiede_chiave:
                # Verifica se il giocatore ha una chiave
                chiave_trovata = False
                for item in giocatore.inventario:
                    if isinstance(item, str):
                        nome_item = item
                    else:
                        nome_item = item.nome
                    
                    if "chiave" in nome_item.lower():
                        chiave_trovata = True
                        break
                
                if not chiave_trovata:
                    if gioco:
                        gioco.io.mostra_messaggio("La porta è chiusa a chiave. Ti serve una chiave per aprirla.")
                    return
                if gioco:
                    gioco.io.mostra_messaggio("Usi la chiave per aprire la porta...")
            
            if gioco:
                gioco.io.mostra_messaggio(f"Apri la {self.nome}...")
            self.stato = "aperta"
            if self.posizione_destinazione and gioco:
                gioco.io.mostra_messaggio(f"Puoi andare verso: {self.posizione_destinazione}")
        elif self.stato == "aperta":
            if gioco:
                gioco.io.mostra_messaggio(f"Chiudi la {self.nome}...")
            self.stato = "chiusa"
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"La {self.nome} è {self.stato}.")


class Leva(OggettoInterattivo):
    def __init__(self, nome, descrizione="", stato="disattivata", posizione=None, token="L"):
        super().__init__(nome, descrizione, stato, None, posizione, token)
    
    def interagisci(self, giocatore, gioco=None):
        if self.stato == "disattivata":
            if gioco:
                gioco.io.mostra_messaggio(f"Attivi la {self.nome}...")
            self.stato = "attivata"
            
            # Attiva/disattiva oggetti collegati
            for nome, oggetto in self.oggetti_collegati.items():
                if oggetto.stato == "chiuso" or oggetto.stato == "chiusa":
                    if gioco:
                        gioco.io.mostra_messaggio(f"La {self.nome} sblocca {oggetto.nome}!")
                    oggetto.stato = "aperto" if oggetto.nome.lower() == "baule" else "aperta"
                elif oggetto.stato == "attiva":
                    if gioco:
                        gioco.io.mostra_messaggio(f"La {self.nome} disattiva {oggetto.nome}!")
                    oggetto.stato = "disattivata"
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"Disattivi la {self.nome}...")
            self.stato = "disattivata"
            
            # Ripristina lo stato degli oggetti collegati
            for nome, oggetto in self.oggetti_collegati.items():
                if oggetto.stato == "aperto" or oggetto.stato == "aperta":
                    if gioco:
                        gioco.io.mostra_messaggio(f"La {self.nome} blocca {oggetto.nome}!")
                    oggetto.stato = "chiuso" if oggetto.nome.lower() == "baule" else "chiusa"
                elif oggetto.stato == "disattivata":
                    if gioco:
                        gioco.io.mostra_messaggio(f"La {self.nome} attiva {oggetto.nome}!")
                    oggetto.stato = "attiva"


class Trappola(OggettoInterattivo):
    def __init__(self, nome, descrizione="", stato="attiva", danno=10, posizione=None, difficolta_salvezza=10, token="T"):
        super().__init__(nome, descrizione, stato, None, posizione, token)
        self.danno = danno
        self.difficolta_salvezza = difficolta_salvezza
    
    def interagisci(self, giocatore, gioco=None):
        if self.stato == "attiva":
            if gioco:
                gioco.io.mostra_messaggio(f"Hai attivato la {self.nome}!")
            dado = Dado(20)
            tiro = dado.tira()
            modificatore = giocatore.destrezza  # Supponiamo che il tiro salvezza sia basato sulla destrezza
            risultato = tiro + modificatore
            if gioco:
                gioco.io.mostra_messaggio(f"Tiro salvezza: {tiro} + {modificatore} = {risultato}")
            if risultato < self.difficolta_salvezza:
                if gioco:
                    gioco.io.mostra_messaggio(f"Subisci {self.danno} danni!")
                giocatore.subisci_danno(self.danno)
            else:
                if gioco:
                    gioco.io.mostra_messaggio("Hai evitato la trappola!")
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"La {self.nome} è disattivata.")
    
    def disattiva(self, gioco=None):
        if self.stato == "attiva":
            if gioco:
                gioco.io.mostra_messaggio(f"Disattivi la {self.nome}.")
            self.stato = "disattivata"
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"La {self.nome} è già disattivata.")


class OggettoRompibile(OggettoInterattivo):
    def __init__(self, nome, descrizione="", stato="integro", materiali=None, forza_richiesta=5, posizione=None):
        super().__init__(nome, descrizione, stato, None, posizione)
        self.materiali = materiali or []  # Lista di oggetti che si ottengono rompendo
        self.forza_richiesta = forza_richiesta
    
    def interagisci(self, giocatore, gioco=None):
        if self.stato == "integro":
            if hasattr(giocatore, 'forza') and giocatore.forza >= self.forza_richiesta:
                if gioco:
                    gioco.io.mostra_messaggio(f"Rompi {self.nome}!")
                self.stato = "rotto"
                if self.materiali:
                    if gioco:
                        gioco.io.mostra_messaggio("Ottieni:")
                        for oggetto in self.materiali:
                            gioco.io.mostra_messaggio(f"- {oggetto.nome}")
                    giocatore.aggiungi_item(oggetto)
            else:
                if gioco:
                    gioco.io.mostra_messaggio(f"Non sei abbastanza forte per rompere {self.nome}.")
        else:
            if gioco:
                gioco.io.mostra_messaggio(f"{self.nome} è già rotto.")

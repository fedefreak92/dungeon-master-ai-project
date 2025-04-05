class BaseState:
    """
    Classe base per tutti gli stati del gioco.
    Ogni stato specifico deve ereditare da questa classe e implementare il metodo esegui().
    """
    def esegui(self, gioco):
        """
        Metodo principale che viene chiamato quando lo stato è attivo.
        Deve essere implementato da ogni classe figlia.
        
        Args:
            gioco: L'istanza del gioco che contiene lo stato corrente e il giocatore
        """
        raise NotImplementedError("Ogni stato deve implementare esegui()")
    
    def entra(self, gioco):
        """
        Metodo chiamato quando si entra nello stato.
        Può essere sovrascritto per inizializzare lo stato.
        
        Args:
            gioco: L'istanza del gioco
        """
        pass
    
    def esci(self, gioco):
        """
        Metodo chiamato quando si esce dallo stato.
        Può essere sovrascritto per pulire o salvare dati.
        
        Args:
            gioco: L'istanza del gioco
        """
        pass

    def pausa(self, gioco):
        """
        Metodo chiamato quando lo stato viene temporaneamente sospeso
        perché un nuovo stato viene messo sopra di esso.
        Può essere sovrascritto per gestire la sospensione temporanea.
        
        Args:
            gioco: L'istanza del gioco
        """
        pass

    def riprendi(self, gioco):
        """
        Metodo chiamato quando lo stato torna ad essere attivo
        dopo essere stato in pausa.
        Può essere sovrascritto per gestire la ripresa dello stato.
        
        Args:
            gioco: L'istanza del gioco
        """
        pass
        
    # Metodi di utilità per le mappe
    
    def ottieni_mappa_corrente(self, gioco):
        """
        Ottiene la mappa corrente dove si trova il giocatore.
        
        Args:
            gioco: L'istanza del gioco
            
        Returns:
            Mappa: L'oggetto mappa attuale o None se non disponibile
        """
        if gioco.giocatore.mappa_corrente:
            return gioco.gestore_mappe.ottieni_mappa(gioco.giocatore.mappa_corrente)
        return None
    
    def ottieni_oggetti_vicini(self, gioco, raggio=1):
        """
        Ottiene gli oggetti vicini al giocatore entro un certo raggio.
        
        Args:
            gioco: L'istanza del gioco
            raggio (int): Raggio di ricerca
            
        Returns:
            dict: Dizionario di oggetti vicini o dict vuoto se non disponibili
        """
        if not gioco.giocatore.mappa_corrente:
            return {}
            
        return gioco.giocatore.ottieni_oggetti_vicini(gioco.gestore_mappe, raggio)
    
    def ottieni_npg_vicini(self, gioco, raggio=1):
        """
        Ottiene gli NPG vicini al giocatore entro un certo raggio.
        
        Args:
            gioco: L'istanza del gioco
            raggio (int): Raggio di ricerca
            
        Returns:
            dict: Dizionario di NPG vicini o dict vuoto se non disponibili
        """
        if not gioco.giocatore.mappa_corrente:
            return {}
            
        return gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe, raggio)
    
    def muovi_giocatore(self, gioco, direzione):
        """
        Muove il giocatore in una direzione.
        
        Args:
            gioco: L'istanza del gioco
            direzione (str): Una delle direzioni "nord", "sud", "est", "ovest"
            
        Returns:
            bool: True se il movimento è avvenuto, False altrimenti
        """
        return gioco.muovi_giocatore(direzione)
    
    def interagisci_con_oggetto_adiacente(self, gioco):
        """
        Fa interagire il giocatore con un oggetto adiacente.
        
        Args:
            gioco: L'istanza del gioco
            
        Returns:
            bool: True se l'interazione è avvenuta, False altrimenti
        """
        if not gioco.giocatore.mappa_corrente:
            return False
            
        return gioco.giocatore.interagisci_con_oggetto_adiacente(gioco.gestore_mappe)
    
    def interagisci_con_npg_adiacente(self, gioco):
        """
        Fa interagire il giocatore con un NPG adiacente.
        
        Args:
            gioco: L'istanza del gioco
            
        Returns:
            bool: True se l'interazione è avvenuta, False altrimenti
        """
        if not gioco.giocatore.mappa_corrente:
            return False
            
        return gioco.giocatore.interagisci_con_npg_adiacente(gioco.gestore_mappe, gioco)
    
    def visualizza_mappa(self, gioco):
        """
        Visualizza la mappa corrente.
        
        Args:
            gioco: L'istanza del gioco
            
        Returns:
            str: Rappresentazione ASCII della mappa o None se non disponibile
        """
        mappa = self.ottieni_mappa_corrente(gioco)
        if mappa:
            return mappa.genera_rappresentazione_ascii((gioco.giocatore.x, gioco.giocatore.y))
        return None
    
    def cambia_mappa(self, gioco, mappa_dest, x=None, y=None):
        """
        Cambia la mappa corrente del giocatore.
        
        Args:
            gioco: L'istanza del gioco
            mappa_dest (str): Nome della mappa di destinazione
            x, y (int, optional): Coordinate di destinazione
            
        Returns:
            bool: True se il cambio mappa è avvenuto, False altrimenti
        """
        return gioco.cambia_mappa(mappa_dest, x, y)

    def to_dict(self):
        """
        Converte lo stato in un dizionario per la serializzazione.
        Salva automaticamente gli attributi base e permette l'estensione nelle sottoclassi.
        
        Returns:
            dict: Rappresentazione dello stato in formato dizionario
        """
        # Salva il tipo dello stato per la ricostruzione
        data = {
            "type": self.__class__.__name__
        }
        
        # Aggiungi automaticamente tutti gli attributi serializzabili
        for attr_name, attr_value in self.__dict__.items():
            # Ignora attributi privati o funzioni
            if attr_name.startswith('_') or callable(attr_value):
                continue
                
            # Gestisci tipi base serializzabili
            if isinstance(attr_value, (str, int, float, bool, type(None))):
                data[attr_name] = attr_value
            # Gestisci oggetti con to_dict()
            elif hasattr(attr_value, 'to_dict') and callable(getattr(attr_value, 'to_dict')):
                try:
                    data[attr_name] = attr_value.to_dict()
                except:
                    # Se il to_dict() fallisce, ignora questo attributo
                    pass
            # Gestisci liste di oggetti
            elif isinstance(attr_value, list):
                serialized_list = []
                try:
                    for item in attr_value:
                        if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                            serialized_list.append(item.to_dict())
                        elif isinstance(item, (str, int, float, bool, type(None))):
                            serialized_list.append(item)
                        # Ignora gli elementi che non possono essere serializzati
                    if serialized_list:  # Aggiungi solo se la lista non è vuota
                        data[attr_name] = serialized_list
                except:
                    # Se c'è un errore di serializzazione, ignora questo attributo
                    pass
            # Gestisci dizionari di oggetti
            elif isinstance(attr_value, dict):
                serialized_dict = {}
                try:
                    for key, value in attr_value.items():
                        # Converti la chiave a stringa per assicurare compatibilità JSON
                        str_key = str(key)
                        if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                            serialized_dict[str_key] = value.to_dict()
                        elif isinstance(value, (str, int, float, bool, type(None))):
                            serialized_dict[str_key] = value
                        # Ignora i valori che non possono essere serializzati
                    if serialized_dict:  # Aggiungi solo se il dict non è vuoto
                        data[attr_name] = serialized_dict
                except:
                    # Se c'è un errore di serializzazione, ignora questo attributo
                    pass
            # Gestisci tuple (convertendole in liste)
            elif isinstance(attr_value, tuple):
                try:
                    data[attr_name] = list(attr_value)
                except:
                    pass
        
        return data
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di stato da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            
        Returns:
            BaseState: Nuova istanza di stato o istanza di base in caso di errore
        """
        # Se c'è un tipo specifico, crea l'istanza appropriata
        state_type = data.get("type")
        if state_type != cls.__name__:
            # Importazione dinamica dello stato corretto
            import importlib
            import traceback
            
            try:
                # Cerca in tutti i moduli states
                # Correzione: mappatura esplicita dei nomi delle classi ai moduli
                state_module_map = {
                    "TavernaState": "taverna",
                    "MercatoState": "mercato",
                    "CombattimentoState": "combattimento",
                    "DialogoState": "dialogo",
                    "GestioneInventarioState": "gestione_inventario",
                    "ProvaAbilitaState": "prova_abilita",
                    "MappaState": "mappa_state",
                    "MenuState": "menu"
                }
                
                # Usa la mappatura se disponibile, altrimenti fallback al nome in minuscolo
                module_suffix = state_module_map.get(state_type, state_type.lower())
                module_name = f"states.{module_suffix}"
                
                module = importlib.import_module(module_name)
                state_class = getattr(module, state_type)
                
                # Crea l'istanza usando il metodo from_dict della classe
                if hasattr(state_class, 'from_dict'):
                    return state_class.from_dict(data)
                else:
                    # Se non ha un metodo from_dict, crea un'istanza di default
                    return state_class()
            except (ImportError, AttributeError) as e:
                # Log dell'errore per debug
                print(f"Errore durante il caricamento dello stato {state_type}: {e}")
                print(traceback.format_exc())
                # Fallback a un'istanza base invece di None
                return cls()
            except Exception as e:
                # Cattura qualsiasi altro errore imprevisto
                print(f"Errore imprevisto durante il caricamento dello stato: {e}")
                print(traceback.format_exc())
                return cls()
        
        # Istanza base
        return cls()
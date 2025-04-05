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
        if hasattr(gioco, 'gestore_mappe') and gioco.giocatore.mappa_corrente:
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
        if not hasattr(gioco, 'gestore_mappe') or not gioco.giocatore.mappa_corrente:
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
        if not hasattr(gioco, 'gestore_mappe') or not gioco.giocatore.mappa_corrente:
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
        if not hasattr(gioco, 'gestore_mappe') or not gioco.giocatore.mappa_corrente:
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
        if not hasattr(gioco, 'gestore_mappe') or not gioco.giocatore.mappa_corrente:
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
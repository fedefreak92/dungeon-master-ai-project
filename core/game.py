from world.gestore_mappe import GestitoreMappe
from core.io_interface import TerminalIO
import json


class Game:
    def __init__(self, giocatore, stato_iniziale, e_temporaneo=False):
        """
        Inizializza il gioco con un giocatore e uno stato iniziale
        
        Args:
            giocatore: L'oggetto giocatore
            stato_iniziale: Lo stato iniziale del gioco
            e_temporaneo: Se True, indica che è un'istanza temporanea solo per caricamento
        """
        self.giocatore = giocatore
        self.stato_stack = []  # Stack degli stati
        self.attivo = True
        self.io = TerminalIO()
        
        # Inizializza il gestore delle mappe
        self.gestore_mappe = GestitoreMappe()
        
        # Imposta la mappa iniziale del giocatore (taverna per default)
        # Solo se il giocatore è già stato creato
        if self.giocatore is not None:
            self.imposta_mappa_iniziale()
        
        # Non aggiungere lo stato iniziale se è None o se è un'istanza temporanea
        if stato_iniziale is not None and not e_temporaneo:
            self.push_stato(stato_iniziale)

    def imposta_mappa_iniziale(self, mappa_nome="taverna"):
        """
        Imposta la mappa iniziale per il giocatore
        
        Args:
            mappa_nome (str): Nome della mappa iniziale (default: "taverna")
        """
        mappa = self.gestore_mappe.ottieni_mappa(mappa_nome)
        if mappa:
            self.gestore_mappe.imposta_mappa_attuale(mappa_nome)
            x, y = mappa.pos_iniziale_giocatore
            self.giocatore.imposta_posizione(mappa_nome, x, y)
            return True
        return False

    def cambia_mappa(self, mappa_nome, x=None, y=None):
        """
        Cambia la mappa corrente del giocatore
        
        Args:
            mappa_nome (str): Nome della mappa di destinazione
            x (int, optional): Posizione X di destinazione
            y (int, optional): Posizione Y di destinazione
            
        Returns:
            bool: True se il cambio mappa è avvenuto, False altrimenti
        """
        return self.gestore_mappe.cambia_mappa_giocatore(self.giocatore, mappa_nome, x, y)

    def stato_corrente(self):
        """
        Restituisce lo stato corrente in modo sicuro
        
        Returns:
            Lo stato corrente o None se lo stack è vuoto
        """
        try:
            return self.stato_stack[-1] if self.stato_stack else None
        except IndexError:
            return None

    def push_stato(self, nuovo_stato):
        """
        Inserisce un nuovo stato sopra quello corrente
        
        Args:
            nuovo_stato: Il nuovo stato da aggiungere
        """
        try:
            # Verifica che lo stato non sia None
            if nuovo_stato is None:
                self.io.mostra_messaggio("Errore: tentativo di aggiungere uno stato nullo.")
                return
                
            if self.stato_corrente():
                self.stato_corrente().pausa(self)  # Mette in pausa lo stato corrente
            self.stato_stack.append(nuovo_stato)
            nuovo_stato.entra(self)
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il push dello stato: {e}")
            self.attivo = False

    def pop_stato(self):
        """
        Rimuove lo stato corrente e torna al precedente
        """
        try:
            if not self.stato_stack:
                self.io.mostra_messaggio("Nessuno stato da rimuovere.")
                return
                
            stato_corrente = self.stato_stack[-1]
            if stato_corrente is None:
                # Rimuovi stato nullo senza chiamare metodi su di esso
                self.io.mostra_messaggio("Rimozione di uno stato non valido.")
                self.stato_stack.pop()
            else:
                # Procedi normalmente
                stato_corrente.esci(self)
                self.stato_stack.pop()
                
            # Riprende lo stato precedente se esiste
            if self.stato_corrente():
                if self.stato_corrente() is not None:
                    self.stato_corrente().riprendi(self)
                else:
                    # Rimuovi anche questo stato se è None
                    self.io.mostra_messaggio("Stato precedente non valido, verrà rimosso.")
                    self.stato_stack.pop()
            
            # Se non ci sono più stati, termina il gioco
            if not self.stato_stack:
                self.attivo = False  # Nessuno stato rimasto
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il pop dello stato: {e}")
            # In caso di errore critico, rimuovi lo stato comunque
            if self.stato_stack:
                self.stato_stack.pop()
            if not self.stato_stack:
                self.attivo = False

    def cambia_stato(self, nuovo_stato):
        """
        Sostituisce lo stato corrente con uno nuovo
        
        Args:
            nuovo_stato: Il nuovo stato che sostituirà quello corrente
        """
        try:
            if self.stato_corrente():
                self.stato_corrente().esci(self)
                self.stato_stack.pop()
            self.stato_stack.append(nuovo_stato)
            nuovo_stato.entra(self)
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il cambio di stato: {e}")
            self.attivo = False

    def esegui(self):
        """
        Esegue il loop principale del gioco
        """
        while self.attivo and self.stato_corrente():
            try:
                self.stato_corrente().esegui(self)
            except Exception as e:
                self.io.mostra_messaggio(f"Errore durante l'esecuzione dello stato: {e}")
                self.pop_stato()  # Gestione automatica degli errori
                if not self.stato_stack:
                    self.attivo = False

    def termina(self):
        """
        Termina il gioco in modo pulito
        """
        while self.stato_stack:
            self.pop_stato()
            
        self.attivo = False

    def sblocca_area(self, area_id):
        """
        Gestisce lo sblocco di un'area nel mondo.
        
        Args:
            area_id (str): Identificatore dell'area da sbloccare
        """
        self.io.mostra_messaggio(f"L'area {area_id} è stata sbloccata!")
        # Logica per sbloccare l'area
        
        # Se l'area è una mappa, possiamo attivarla
        if area_id in self.gestore_mappe.mappe:
            self.io.mostra_messaggio(f"La mappa {area_id} è ora accessibile!")
        
    def attiva_trappola(self, trappola_id, danno=0):
        """
        Attiva una trappola nel mondo.
        
        Args:
            trappola_id (str): Identificatore della trappola
            danno (int): Quantità di danno da infliggere
        """
        self.io.mostra_messaggio(f"Una trappola si attiva!")
        if danno > 0:
            self.giocatore.subisci_danno(danno)
        
    def modifica_ambiente(self, ambiente_id, nuovo_stato):
        """
        Modifica un ambiente del mondo.
        
        Args:
            ambiente_id (str): Identificatore dell'ambiente
            nuovo_stato (str): Nuovo stato dell'ambiente
        """
        self.io.mostra_messaggio(f"L'ambiente {ambiente_id} cambia: {nuovo_stato}")
        # Logica per modificare l'ambiente

    def ottieni_posizione_giocatore(self):
        """
        Restituisce informazioni sulla posizione corrente del giocatore
        
        Returns:
            dict: Informazioni sulla posizione corrente
        """
        if not self.giocatore.mappa_corrente:
            return None
            
        mappa = self.gestore_mappe.ottieni_mappa(self.giocatore.mappa_corrente)
        if not mappa:
            return None
            
        return {
            "mappa": self.giocatore.mappa_corrente,
            "x": self.giocatore.x,
            "y": self.giocatore.y,
            "oggetti_vicini": self.giocatore.ottieni_oggetti_vicini(self.gestore_mappe),
            "npg_vicini": self.giocatore.ottieni_npg_vicini(self.gestore_mappe)
        }
        
    def muovi_giocatore(self, direzione):
        """
        Muove il giocatore in una direzione specifica
        
        Args:
            direzione (str): Una delle direzioni "nord", "sud", "est", "ovest"
            
        Returns:
            bool: True se il movimento è avvenuto, False altrimenti
        """
        direzioni = {
            "nord": (0, -1),
            "sud": (0, 1),
            "est": (1, 0),
            "ovest": (-1, 0)
        }
        
        if direzione not in direzioni:
            return False
            
        dx, dy = direzioni[direzione]
        spostamento = self.giocatore.muovi(dx, dy, self.gestore_mappe)
        
        if not spostamento:
            self.io.mostra_messaggio("Non puoi muoverti in quella direzione!")
            
        return spostamento

    def salva(self, file_path="salvataggio.json"):
        """
        Salva lo stato corrente del gioco in un file JSON
        
        Args:
            file_path (str): Percorso del file di salvataggio
        """
        # Ottieni dati serializzabili del giocatore
        if hasattr(self.giocatore, 'to_dict'):
            giocatore_data = self.giocatore.to_dict()
        else:
            # Fallback al salvataggio base
            inventario_data = []
            for oggetto in self.giocatore.inventario:
                if hasattr(oggetto, 'to_dict') and callable(getattr(oggetto, 'to_dict')):
                    inventario_data.append(oggetto.to_dict())
                else:
                    # Salva tutti gli attributi dell'oggetto
                    oggetto_data = {
                        "nome": getattr(oggetto, 'nome', 'Oggetto sconosciuto'),
                        "tipo": getattr(oggetto, 'tipo', 'vario'),
                        "descrizione": getattr(oggetto, 'descrizione', ''),
                        "valore": getattr(oggetto, 'valore', 0),
                        "effetto": getattr(oggetto, 'effetto', {}),
                    }
                    inventario_data.append(oggetto_data)
                    
            # Serializza arma equipaggiata
            arma_data = None
            if hasattr(self.giocatore, 'arma') and self.giocatore.arma:
                if hasattr(self.giocatore.arma, 'to_dict'):
                    arma_data = self.giocatore.arma.to_dict()
                else:
                    arma_data = {
                        "nome": getattr(self.giocatore.arma, 'nome', 'Arma sconosciuta'),
                        "tipo": "arma",
                        "descrizione": getattr(self.giocatore.arma, 'descrizione', ''),
                        "valore": getattr(self.giocatore.arma, 'valore', 0),
                        "effetto": getattr(self.giocatore.arma, 'effetto', {}),
                    }
            
            # Serializza armatura equipaggiata
            armatura_data = None
            if hasattr(self.giocatore, 'armatura') and self.giocatore.armatura:
                if hasattr(self.giocatore.armatura, 'to_dict'):
                    armatura_data = self.giocatore.armatura.to_dict()
                else:
                    armatura_data = {
                        "nome": getattr(self.giocatore.armatura, 'nome', 'Armatura sconosciuta'),
                        "tipo": "armatura",
                        "descrizione": getattr(self.giocatore.armatura, 'descrizione', ''),
                        "valore": getattr(self.giocatore.armatura, 'valore', 0),
                        "effetto": getattr(self.giocatore.armatura, 'effetto', {}),
                    }
                    
            # Serializza accessori
            accessori_data = []
            if hasattr(self.giocatore, 'accessori'):
                for acc in self.giocatore.accessori:
                    if hasattr(acc, 'to_dict'):
                        accessori_data.append(acc.to_dict())
                    else:
                        acc_data = {
                            "nome": getattr(acc, 'nome', 'Accessorio sconosciuto'),
                            "tipo": "accessorio",
                            "descrizione": getattr(acc, 'descrizione', ''),
                            "valore": getattr(acc, 'valore', 0),
                            "effetto": getattr(acc, 'effetto', {}),
                        }
                        accessori_data.append(acc_data)
                    
            giocatore_data = {
                "nome": self.giocatore.nome,
                "classe": self.giocatore.classe,
                "hp": self.giocatore.hp,
                "hp_max": getattr(self.giocatore, 'hp_max', self.giocatore.hp),
                "mappa": self.giocatore.mappa_corrente,
                "posizione": [self.giocatore.x, self.giocatore.y],
                "oro": getattr(self.giocatore, 'oro', 0),
                "inventario": inventario_data,
                "arma": arma_data,
                "armatura": armatura_data,
                "accessori": accessori_data,
                "forza_base": getattr(self.giocatore, 'forza_base', 10),
                "destrezza_base": getattr(self.giocatore, 'destrezza_base', 10),
                "costituzione_base": getattr(self.giocatore, 'costituzione_base', 10),
                "intelligenza_base": getattr(self.giocatore, 'intelligenza_base', 10),
                "saggezza_base": getattr(self.giocatore, 'saggezza_base', 10),
                "carisma_base": getattr(self.giocatore, 'carisma_base', 10),
                "livello": getattr(self.giocatore, 'livello', 1),
                "esperienza": getattr(self.giocatore, 'esperienza', 0),
            }
            
        # Serializza lo stack degli stati
        stati_data = []
        for stato in self.stato_stack:
            if hasattr(stato, 'to_dict'):
                stati_data.append(stato.to_dict())
            else:
                # Fallback per stati che non hanno to_dict
                stati_data.append({"type": stato.__class__.__name__})
        
        # Componi il dizionario completo
        data = {
            "giocatore": giocatore_data,
            "stati": stati_data,
            "attivo": self.attivo,
            "mappa_corrente": self.giocatore.mappa_corrente,
            "versione_gioco": "0.1.0",  # Aggiungiamo versione per compatibilità
            "timestamp": __import__('time').time()  # Quando è stato fatto il salvataggio
        }
        
        # Serializza e salva su file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
    
    def carica(self, file_path="salvataggio.json"):
        """
        Carica uno stato di gioco da un file JSON
        
        Args:
            file_path (str): Percorso del file di salvataggio
            
        Returns:
            bool: True se il caricamento è riuscito, False altrimenti
        """
        try:
            # Importa tutti i moduli di stato
            import states.taverna
            import states.dialogo
            import states.combattimento
            import states.mercato
            import states.gestione_inventario
            from entities.giocatore import Giocatore
            from entities.npg import NPG
            from items.oggetto import Oggetto
            from items.oggetto_interattivo import OggettoInterattivo
            
            # Mappa i nomi delle classi ai moduli corretti
            moduli_stati = {
                "TavernaState": states.taverna,
                "DialogoState": states.dialogo,
                "CombattimentoState": states.combattimento,
                "MercatoState": states.mercato,
                "GestioneInventarioState": states.gestione_inventario
            }

            # Leggi il file di salvataggio
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Ricrea il giocatore
            self.giocatore = Giocatore.from_dict(data["giocatore"])

            # Ricrea lo stack degli stati
            self.stato_stack = []
            for stato_dato in data["stati"]:
                # Supporta sia "type" (usato nel salva) che "tipo" (per compatibilità)
                nome_classe = stato_dato.get("type", stato_dato.get("tipo"))
                if nome_classe:
                    # Usa il modulo corretto invece del nome classe in lowercase
                    if nome_classe in moduli_stati:
                        modulo = moduli_stati[nome_classe]
                        classe_stato = getattr(modulo, nome_classe, None)
                        if classe_stato and hasattr(classe_stato, 'from_dict'):
                            # Supporto sia "dati" che il formato diretto
                            dati = stato_dato.get("dati", stato_dato)
                            istanza = classe_stato.from_dict(dati)
                            self.stato_stack.append(istanza)
                        else:
                            self.io.mostra_messaggio(f"Avviso: la classe {nome_classe} non ha il metodo from_dict")
                    else:
                        self.io.mostra_messaggio(f"Avviso: modulo per {nome_classe} non disponibile")

            # Ricrea NPC nelle mappe
            for mappa_nome, npcs in data.get("npcs", {}).items():
                mappa = self.gestore_mappe.ottieni_mappa(mappa_nome)
                if mappa:
                    for pos_str, npg_data in npcs.items():
                        pos = eval(pos_str)
                        npg = NPG.from_dict(npg_data)
                        mappa.npg[pos] = npg
                        
            # Imposta la mappa corrente
            mappa_corrente = data.get("mappa_corrente", "taverna")
            self.gestore_mappe.imposta_mappa_attuale(mappa_corrente)
            
            # Imposta lo stato attivo
            self.attivo = data.get("attivo", True)
            
            self.io.mostra_messaggio(f"Partita di {self.giocatore.nome} caricata con successo!")
            return True
            
        except Exception as e:
            self.io.mostra_messaggio(f"Errore durante il caricamento: {e}")
            return False

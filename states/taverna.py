from states.base_state import BaseState
from util.funzioni_utili import avanti, mostra_inventario, mostra_statistiche
from states.mercato import MercatoState
from states.dialogo import DialogoState
from entities.npg import NPG
from states.gestione_inventario import GestioneInventarioState
from items.oggetto_interattivo import OggettoInterattivo, Baule, Porta, Leva, Trappola
from items.oggetto import Oggetto
from states.prova_abilita import ProvaAbilitaState
from world.mappa import Mappa
from world.gestore_mappe import GestitoreMappe


class TavernaState(BaseState):
    def __init__(self):
        self.ultima_scelta = None  # Per ricordare l'ultima scelta fatta
        self.prima_visita = True  # Flag per la prima visita
        self.fase = "menu_principale"  # Fase corrente per operazioni asincrone
        self.ultimo_input = None  # Memorizza l'ultimo input dell'utente
        self.dati_contestuali = {}  # Per memorizzare dati tra più fasi
        
        # Dizionario degli NPG presenti nella taverna
        self.npg_presenti = {
            "Durnan": NPG("Durnan"),
            "Elminster": NPG("Elminster"),
            "Mirt": NPG("Mirt")
        }
        
        # Oggetti interattivi nella taverna
        self.oggetti_interattivi = {
            "bancone": OggettoInterattivo("Bancone", "Un lungo bancone di legno lucido dove vengono servite le bevande.", "pulito", posizione="taverna"),
            "camino": OggettoInterattivo("Camino", "Un grande camino in pietra con un fuoco scoppiettante.", "acceso", posizione="taverna"),
            "baule_nascondiglio": Baule("Baule nascosto", "Un piccolo baule nascosto sotto una tavola del pavimento.", 
                                     contenuto=[Oggetto("Chiave rugginosa", "chiave", {}, 2, "Una vecchia chiave arrugginita.")], 
                                     posizione="taverna"),
            "porta_cantina": Porta("Porta della cantina", "Una robusta porta che conduce alla cantina.", 
                                  stato="chiusa", richiede_chiave=True, posizione="taverna", 
                                  posizione_destinazione="cantina"),
            "trappola_pavimento": Trappola("Trappola nel pavimento", "Una parte del pavimento sembra instabile.", 
                                         danno=5, posizione="taverna", difficolta_salvezza=10)
        }
        
        # Colleghiamo alcuni oggetti tra loro per creare interazioni
        leva_segreta = Leva("Leva segreta", "Una leva nascosta dietro un quadro.", posizione="taverna")
        self.oggetti_interattivi["leva_segreta"] = leva_segreta
        leva_segreta.collega_oggetto("trappola", self.oggetti_interattivi["trappola_pavimento"])

        # Esempio di altare magico
        altare = OggettoInterattivo("Altare magico", "Un antico altare con simboli misteriosi.", stato="inattivo")
        altare.imposta_descrizione_stato("inattivo", "Un antico altare con simboli misteriosi che sembrano spenti.")
        altare.imposta_descrizione_stato("attivo", "L'altare emette una luce blu intensa e i simboli brillano.")
        altare.imposta_descrizione_stato("esaminato", "Noti che l'altare ha delle rune che formano un incantesimo antico.")

        # Aggiungi transizioni possibili
        altare.aggiungi_transizione("inattivo", "esaminato")
        altare.aggiungi_transizione("inattivo", "attivo")
        altare.aggiungi_transizione("esaminato", "attivo")
        altare.aggiungi_transizione("attivo", "inattivo")

        # Collega abilità 
        altare.richiedi_abilita("percezione", "esaminato", 12, 
                            "Scrutando attentamente l'altare, noti delle incisioni nascoste.")
        altare.richiedi_abilita("arcano", "attivo", 15, 
                            "Utilizzando la tua conoscenza arcana, attivi l'antico potere dell'altare.")

        # Collega eventi al mondo
        altare.collega_evento("attivo", lambda gioco: gioco.sblocca_area("cripta_magica"))

        # Aggiungi l'oggetto alla taverna
        self.oggetti_interattivi["altare_magico"] = altare
        
        # Attributo per tenere traccia della visualizzazione mappa
        self.mostra_mappa = False
        
        # Direzioni di movimento
        self.direzioni = {
            "nord": (0, -1),
            "sud": (0, 1),
            "est": (1, 0),
            "ovest": (-1, 0)
        }

    def esegui(self, gioco):
        if self.prima_visita:
            gioco.io.mostra_messaggio(f"Benvenuto {gioco.giocatore.nome} sei appena arrivato nella Taverna Il Portale Spalancato a Waterdeep. Sei di ritrono da un lungo viaggio che ti ha permesso di ottenere molti tesori ma anche molte cicatrici. Entri con passo svelto e ti dirigi verso la tua prossima avventura")
            self.prima_visita = False
            
            # Imposta la posizione iniziale del giocatore sulla mappa della taverna
            mappa = gioco.gestore_mappe.ottieni_mappa("taverna")
            if mappa:
                gioco.gestore_mappe.imposta_mappa_attuale("taverna")
                x, y = mappa.pos_iniziale_giocatore
                gioco.giocatore.imposta_posizione("taverna", x, y)
                # Popola la mappa con gli oggetti interattivi e gli NPG
                gioco.gestore_mappe.trasferisci_oggetti_da_stato("taverna", self)

        # Gestione asincrona basata sulla fase corrente
        if self.fase == "menu_principale":
            self._mostra_menu_principale(gioco)
        elif self.fase == "elabora_scelta":
            self._elabora_scelta(gioco)
        elif self.fase == "parla_npg":
            self._parla_con_npg(gioco)
        elif self.fase == "combatti_npg":
            self._combatti_con_npg(gioco)
        elif self.fase == "esplora_oggetti":
            self._esplora_oggetti(gioco)
        elif self.fase == "visualizza_mappa":
            self._visualizza_mappa(gioco)
        elif self.fase == "muovi_mappa":
            self._muovi_sulla_mappa(gioco)
        elif self.fase == "interagisci_ambiente":
            self._interagisci_ambiente(gioco)
        elif self.fase == "salva_partita":
            self._salva_partita(gioco)
        else:
            # Fase non riconosciuta, torna al menu principale
            self.fase = "menu_principale"
            self.esegui(gioco)
    
    def _mostra_menu_principale(self, gioco):
        gioco.io.mostra_messaggio("\nTi trovi nella taverna. Cosa vuoi fare?")
        gioco.io.mostra_messaggio("1. Parla con qualcuno")
        gioco.io.mostra_messaggio("2. Vai al mercato")        
        gioco.io.mostra_messaggio("3. Mostra statistiche")
        gioco.io.mostra_messaggio("4. Combatti con un nemico")
        gioco.io.mostra_messaggio("5. Sfida un NPC")
        gioco.io.mostra_messaggio("6. Esplora oggetti nella taverna")
        gioco.io.mostra_messaggio("7. Mostra inventario")
        gioco.io.mostra_messaggio("8. Prova abilità")
        gioco.io.mostra_messaggio("9. Visualizza mappa")
        gioco.io.mostra_messaggio("10. Muoviti sulla mappa")
        gioco.io.mostra_messaggio("11. Interagisci con l'ambiente")
        gioco.io.mostra_messaggio("12. Salva partita")
        gioco.io.mostra_messaggio("13. Esci dal gioco")
       
        # Ottiene il comando dall'input e lo memorizza
        self.ultimo_input = gioco.io.richiedi_input("Scelta: ")
        self.fase = "elabora_scelta"
    
    def _elabora_scelta(self, gioco):
        # Salviamo la scelta
        scelta = self.ultimo_input
        self.ultima_scelta = scelta
        
        # Supporta sia input numerico che testuale
        scelta_originale = scelta
        if not scelta.isdigit():
            scelta = self._elabora_comando(scelta)

        if scelta == "1":
            self.fase = "parla_npg"
            self.dati_contestuali.clear()
        elif scelta == "2":
            gioco.push_stato(MercatoState())  # Usiamo push_stato per il mercato
            self.fase = "menu_principale"
        elif scelta == "3":
            mostra_statistiche(gioco.giocatore, gioco)
            avanti(gioco)
            self.fase = "menu_principale"
        elif scelta == "4":
            from states.combattimento import CombattimentoState
            from entities.nemico import Nemico
            nemico = Nemico("Goblin", 10, 3)
            gioco.push_stato(CombattimentoState(nemico=nemico))  # Usiamo push_stato per il combattimento
            self.fase = "menu_principale"
        elif scelta == "5":
            self.fase = "combatti_npg"
            self.dati_contestuali.clear()
        elif scelta == "6":
            self.fase = "esplora_oggetti"
            self.dati_contestuali.clear()
        elif scelta == "7":
            gioco.push_stato(GestioneInventarioState())
            self.fase = "menu_principale"
        elif scelta == "8":
            gioco.push_stato(ProvaAbilitaState())
            self.fase = "menu_principale"
        elif scelta == "9":
            self.fase = "visualizza_mappa"
        elif scelta == "10":
            self.fase = "muovi_mappa"
        elif scelta == "11":
            self.fase = "interagisci_ambiente"
        elif scelta == "12":
            self.fase = "salva_partita"
        elif scelta == "13":
            gioco.attivo = False          
        else:
            gioco.io.mostra_messaggio(f"Non capisco cosa vuoi fare con '{scelta_originale}'.")
            self.fase = "menu_principale"
    
    def _elabora_comando(self, cmd):
        cmd = cmd.lower().strip()
        
        # Mappatura comandi di testo ai numeri
        if any(parola in cmd for parola in ["parla", "dialoga", "conversa"]):
            return "1"
        elif any(parola in cmd for parola in ["mercato", "compra", "negozio"]):
            return "2"
        elif any(parola in cmd for parola in ["statistiche", "stat", "status"]):
            return "3"
        elif any(parola in cmd for parola in ["combatti", "attacca", "lotta"]):
            return "4"
        elif any(parola in cmd for parola in ["sfida", "duello"]):
            return "5"
        elif any(parola in cmd for parola in ["esplora", "cerca", "oggetti"]):
            return "6"
        elif any(parola in cmd for parola in ["inventario", "zaino", "oggetti"]):
            return "7"
        elif any(parola in cmd for parola in ["prova", "abilità", "skill"]):
            return "8"
        elif any(parola in cmd for parola in ["mappa", "guarda mappa", "visualizza"]):
            return "9"
        elif any(parola in cmd for parola in ["muovi", "vai", "sposta"]):
            return "10"
        elif any(parola in cmd for parola in ["interagisci", "usa", "ambiente"]):
            return "11"
        elif any(parola in cmd for parola in ["salva", "save"]):
            return "12"
        elif any(parola in cmd for parola in ["esci", "quit", "exit"]):
            return "13"
        else:
            return cmd  # ritorna il comando originale se non corrisponde a nessuna azione
    
    def _parla_con_npg(self, gioco):
        # Verifica se abbiamo già mostrato la lista degli NPG
        if "npg_lista_mostrata" not in self.dati_contestuali:
            # Proviamo a usare gli NPG sulla mappa
            if gioco.giocatore.mappa_corrente:
                npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)
                if npg_vicini:
                    gioco.io.mostra_messaggio("\nCon chi vuoi parlare?")
                    npg_lista = list(npg_vicini.values())
                    for i, npg in enumerate(npg_lista, 1):
                        gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
                    gioco.io.mostra_messaggio(f"{len(npg_lista) + 1}. Torna indietro")
                    
                    self.dati_contestuali["npg_lista_mostrata"] = True
                    self.dati_contestuali["tipo_lista"] = "mappa"
                    self.dati_contestuali["npg_lista"] = npg_lista
                    self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
                    return
                    
            # Fallback al metodo originale se non ci sono NPG vicini o non usiamo il gestore mappe
            gioco.io.mostra_messaggio("\nCon chi vuoi parlare?")
            for i, nome in enumerate(self.npg_presenti.keys(), 1):
                gioco.io.mostra_messaggio(f"{i}. {nome}")
            gioco.io.mostra_messaggio(f"{len(self.npg_presenti) + 1}. Torna indietro")
            
            self.dati_contestuali["npg_lista_mostrata"] = True
            self.dati_contestuali["tipo_lista"] = "locale"
            self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
            return
            
        # Elabora la scelta dell'NPG  
        try:
            scelta = int(self.ultimo_input)
            
            if self.dati_contestuali["tipo_lista"] == "mappa":
                npg_lista = self.dati_contestuali["npg_lista"]
                if 1 <= scelta <= len(npg_lista):
                    npg = npg_lista[scelta - 1]
                    gioco.push_stato(DialogoState(npg))
                elif scelta == len(npg_lista) + 1:
                    # Torna al menu principale
                    pass
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            else:  # tipo_lista == "locale"
                if 1 <= scelta <= len(self.npg_presenti):
                    npg_nome = list(self.npg_presenti.keys())[scelta - 1]
                    npg = self.npg_presenti[npg_nome]
                    gioco.push_stato(DialogoState(npg))
                elif scelta == len(self.npg_presenti) + 1:
                    # Torna al menu principale
                    pass
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
                    
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            
        # Alla fine, ripristina lo stato
        self.fase = "menu_principale"
        self.dati_contestuali.clear()
            
    def _combatti_con_npg(self, gioco):
        # Verifica se abbiamo già mostrato la lista degli NPG
        if "npg_lista_mostrata" not in self.dati_contestuali:
            # Proviamo a usare gli NPG sulla mappa
            if gioco.giocatore.mappa_corrente:
                npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)
                if npg_vicini:
                    gioco.io.mostra_messaggio("\nCon chi vuoi combattere?")
                    npg_lista = list(npg_vicini.values())
                    for i, npg in enumerate(npg_lista, 1):
                        gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
                    gioco.io.mostra_messaggio(f"{len(npg_lista) + 1}. Torna indietro")
                    
                    self.dati_contestuali["npg_lista_mostrata"] = True
                    self.dati_contestuali["tipo_lista"] = "mappa"
                    self.dati_contestuali["npg_lista"] = npg_lista
                    self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
                    return
            
            # Fallback al metodo originale
            gioco.io.mostra_messaggio("\nCon chi vuoi combattere?")
            for i, nome in enumerate(self.npg_presenti.keys(), 1):
                gioco.io.mostra_messaggio(f"{i}. {nome}")
            gioco.io.mostra_messaggio(f"{len(self.npg_presenti) + 1}. Torna indietro")
            
            self.dati_contestuali["npg_lista_mostrata"] = True
            self.dati_contestuali["tipo_lista"] = "locale"
            self.ultimo_input = gioco.io.richiedi_input("\nScegli: ")
            return
        
        # Se abbiamo mostrato la lista ma non abbiamo ancora chiesto conferma
        if "npg_scelto" not in self.dati_contestuali:
            try:
                scelta = int(self.ultimo_input)
                
                if self.dati_contestuali["tipo_lista"] == "mappa":
                    npg_lista = self.dati_contestuali["npg_lista"]
                    if 1 <= scelta <= len(npg_lista):
                        npg = npg_lista[scelta - 1]
                        self.dati_contestuali["npg_scelto"] = npg
                        # Conferma prima di attaccare
                        gioco.io.mostra_messaggio(f"Sei sicuro di voler attaccare {npg.nome}?")
                        self.ultimo_input = gioco.io.richiedi_input("(s/n): ")
                        return
                    elif scelta == len(npg_lista) + 1:
                        # Torna al menu principale
                        self.fase = "menu_principale"
                        self.dati_contestuali.clear()
                        return
                    else:
                        gioco.io.mostra_messaggio("Scelta non valida.")
                        self.fase = "menu_principale"
                        self.dati_contestuali.clear()
                        return
                else:  # tipo_lista == "locale"
                    if 1 <= scelta <= len(self.npg_presenti):
                        npg_nome = list(self.npg_presenti.keys())[scelta - 1]
                        npg = self.npg_presenti[npg_nome]
                        self.dati_contestuali["npg_scelto"] = npg
                        self.dati_contestuali["npg_nome"] = npg_nome
                        # Conferma prima di attaccare
                        gioco.io.mostra_messaggio(f"Sei sicuro di voler attaccare {npg_nome}?")
                        self.ultimo_input = gioco.io.richiedi_input("(s/n): ")
                        return
                    elif scelta == len(self.npg_presenti) + 1:
                        # Torna al menu principale
                        self.fase = "menu_principale"
                        self.dati_contestuali.clear()
                        return
                    else:
                        gioco.io.mostra_messaggio("Scelta non valida.")
                        self.fase = "menu_principale"
                        self.dati_contestuali.clear()
                        return
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
                self.fase = "menu_principale"
                self.dati_contestuali.clear()
                return
        
        # Se abbiamo un NPG scelto, verifichiamo la conferma
        if self.dati_contestuali.get("npg_scelto"):
            npg = self.dati_contestuali["npg_scelto"]
            conferma = self.ultimo_input.lower()
            if conferma == "s":
                from states.combattimento import CombattimentoState
                gioco.push_stato(CombattimentoState(npg_ostile=npg))
            else:
                gioco.io.mostra_messaggio("Hai deciso di non combattere.")
        
        # Alla fine, ripristina lo stato
        self.fase = "menu_principale"
        self.dati_contestuali.clear()
            
    def _esplora_oggetti(self, gioco):
        # Verifica se abbiamo già mostrato la lista degli oggetti
        if "oggetti_lista_mostrata" not in self.dati_contestuali:
            # Proviamo a usare gli oggetti sulla mappa
            if gioco.giocatore.mappa_corrente:
                oggetti_vicini = gioco.giocatore.ottieni_oggetti_vicini(gioco.gestore_mappe)
                if oggetti_vicini:
                    gioco.io.mostra_messaggio("\nOggetti nelle vicinanze:")
                    oggetti_lista = []
                    for pos, obj in oggetti_vicini.items():
                        oggetti_lista.append((pos, obj))
                        x, y = pos
                        gioco.io.mostra_messaggio(f"{len(oggetti_lista)}. {obj.nome} [{obj.stato}] a ({x}, {y})")
                    gioco.io.mostra_messaggio(f"{len(oggetti_lista) + 1}. Torna indietro")
                    
                    self.dati_contestuali["oggetti_lista_mostrata"] = True
                    self.dati_contestuali["tipo_lista"] = "mappa"
                    self.dati_contestuali["oggetti_lista"] = oggetti_lista
                    self.ultimo_input = gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? ")
                    return
            
            # Fallback al metodo originale
            gioco.io.mostra_messaggio("\nOggetti nella taverna:")
            for i, nome in enumerate(self.oggetti_interattivi.keys(), 1):
                oggetto = self.oggetti_interattivi[nome]
                gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
            gioco.io.mostra_messaggio(f"{len(self.oggetti_interattivi) + 1}. Torna indietro")
            
            self.dati_contestuali["oggetti_lista_mostrata"] = True
            self.dati_contestuali["tipo_lista"] = "locale"
            self.ultimo_input = gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? ")
            return
            
        # Elabora la scelta dell'oggetto  
        try:
            scelta = int(self.ultimo_input)
            
            if self.dati_contestuali["tipo_lista"] == "mappa":
                oggetti_lista = self.dati_contestuali["oggetti_lista"]
                if 1 <= scelta <= len(oggetti_lista):
                    _, oggetto = oggetti_lista[scelta - 1]
                    oggetto.descrivi()
                    oggetto.interagisci(gioco.giocatore)
                elif scelta == len(oggetti_lista) + 1:
                    # Torna al menu principale
                    pass
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            else:  # tipo_lista == "locale"
                if 1 <= scelta <= len(self.oggetti_interattivi):
                    oggetto_nome = list(self.oggetti_interattivi.keys())[scelta - 1]
                    oggetto = self.oggetti_interattivi[oggetto_nome]
                    oggetto.descrivi()
                    oggetto.interagisci(gioco.giocatore)
                elif scelta == len(self.oggetti_interattivi) + 1:
                    # Torna al menu principale
                    pass
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
                    
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            
        # Alla fine, ripristina lo stato
        self.fase = "menu_principale"
        self.dati_contestuali.clear()
    
    def _visualizza_mappa(self, gioco):
        """Visualizza la mappa della taverna"""
        from states.mappa_state import MappaState
        
        # Se c'è già un'istanza del map state, la usiamo
        map_state = next((s for s in gioco.stato_stack if isinstance(s, MappaState)), None)
        if map_state:
            map_state.apri(self)
        else:
            gioco.push_stato(MappaState(stato_origine=self))
            
        # Torna al menu principale
        self.fase = "menu_principale"
    
    def _muovi_sulla_mappa(self, gioco):
        """Permette al giocatore di muoversi sulla mappa"""
        from states.mappa_state import MappaState
        
        # Se c'è già un'istanza del map state, la usiamo
        map_state = next((s for s in gioco.stato_stack if isinstance(s, MappaState)), None)
        if map_state:
            map_state.muovi(gioco)
        else:
            gioco.io.mostra_messaggio("Sistema di movimento non disponibile!")
            avanti(gioco)
            
        # Torna al menu principale
        self.fase = "menu_principale"
            
    def _interagisci_ambiente(self, gioco):
        """Permette al giocatore di interagire con l'ambiente circostante"""
        from states.mappa_state import MappaState
        
        # Se c'è già un'istanza del map state, la usiamo
        map_state = next((s for s in gioco.stato_stack if isinstance(s, MappaState)), None)
        if map_state:
            map_state.interagisci(gioco)
        else:
            gioco.io.mostra_messaggio("Sistema di interazione non disponibile!")
            avanti(gioco)
            
        # Torna al menu principale
        self.fase = "menu_principale"

    def _salva_partita(self, gioco):
        """Salva la partita corrente"""
        gioco.salva()
        gioco.io.mostra_messaggio("Partita salvata!")
        avanti(gioco)
        
        # Torna al menu principale
        self.fase = "menu_principale"
            
    def pausa(self, gioco):
        """
        Quando la taverna viene messa in pausa (es. durante un dialogo)
        salviamo lo stato corrente
        """
        gioco.io.mostra_messaggio("\nLa taverna rimane in attesa...")
        
    def riprendi(self, gioco):
        """
        Quando la taverna riprende dopo una pausa
        mostriamo un messaggio di ripresa
        """
        gioco.io.mostra_messaggio("\nTorni alla taverna...")
        # Quando riprendiamo, torniamo sempre al menu principale
        self.fase = "menu_principale"

    def to_dict(self):
        """
        Converte lo stato della taverna in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dello stato in formato dizionario
        """
        # Ottieni il dizionario base
        data = super().to_dict()
        
        # Rimuovi il dizionario npg_presenti prima, dato che verrà serializzato separatamente
        if "npg_presenti" in data:
            del data["npg_presenti"]
            
        # Serializza manualmente gli NPG per evitare problemi di serializzazione
        npg_dict = {}
        try:
            for nome, npg in self.npg_presenti.items():
                if hasattr(npg, 'to_dict') and callable(getattr(npg, 'to_dict')):
                    npg_dict[nome] = npg.to_dict()
        except:
            # In caso di errore, salviamo solo i nomi degli NPG
            npg_dict = {nome: {"nome": nome} for nome in self.npg_presenti.keys()}
            
        # Aggiungi attributi specifici
        data.update({
            "fase": self.fase,
            "ultimo_input": self.ultimo_input,
            "ultima_scelta": self.ultima_scelta,
            "npg_nomi": list(self.npg_presenti.keys())  # Salva solo i nomi degli NPG
            # Non serializzare oggetti_interattivi poiché sono generati dinamicamente
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di TavernaState da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            
        Returns:
            TavernaState: Nuova istanza di TavernaState
        """
        state = cls()
        
        # Ripristina attributi
        state.fase = data.get("fase", "menu_principale")
        state.ultimo_input = data.get("ultimo_input")
        state.ultima_scelta = data.get("ultima_scelta")
        
        # Ricrea gli NPG dai nomi
        npg_nomi = data.get("npg_nomi", ["Durnan", "Elminster", "Mirt"])
        for nome in npg_nomi:
            if nome not in state.npg_presenti:
                from entities.npg import NPG
                state.npg_presenti[nome] = NPG(nome)
        
        # Gli oggetti_interattivi vengono generati dal costruttore
        
        return state
        
    def __getstate__(self):
        """
        Metodo speciale per la serializzazione con pickle.
        
        Returns:
            dict: Stato serializzabile dell'oggetto
        """
        state = self.__dict__.copy()
        
        # Rimuovi eventuali riferimenti ciclici o non serializzabili
        if 'dati_contestuali' in state:
            # Filtra solo i dati serializzabili
            dati_contestuali_safe = {}
            for k, v in state['dati_contestuali'].items():
                if isinstance(v, (str, int, float, bool, list, dict, tuple)):
                    dati_contestuali_safe[k] = v
            state['dati_contestuali'] = dati_contestuali_safe
        
        return state
    
    def __setstate__(self, state):
        """
        Metodo speciale per la deserializzazione con pickle.
        
        Args:
            state (dict): Stato dell'oggetto da ripristinare
        """
        self.__dict__.update(state)
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
            if hasattr(gioco, 'gestore_mappe'):
                mappa = gioco.gestore_mappe.ottieni_mappa("taverna")
                if mappa:
                    gioco.gestore_mappe.imposta_mappa_attuale("taverna")
                    x, y = mappa.pos_iniziale_giocatore
                    gioco.giocatore.imposta_posizione("taverna", x, y)
                    # Popola la mappa con gli oggetti interattivi e gli NPG
                    gioco.gestore_mappe.trasferisci_oggetti_da_stato("taverna", self)

        gioco.io.mostra_messaggio("\nTi trovi nella taverna. Cosa vuoi fare?")
        gioco.io.mostra_messaggio("1. Parla con qualcuno")
        gioco.io.mostra_messaggio("2. Vai al mercato")        
        gioco.io.mostra_messaggio("3. Mostra statistiche")
        gioco.io.mostra_messaggio("4. Combatti con un nemico")
        gioco.io.mostra_messaggio("5. Sfida un NPC")
        gioco.io.mostra_messaggio("6. Esplora oggetti nella taverna")
        gioco.io.mostra_messaggio("7. Mostra inventario")
        gioco.io.mostra_messaggio("8. Prova abilità")
        gioco.io.mostra_messaggio("9. Visualizza mappa")  # Nuova opzione
        gioco.io.mostra_messaggio("10. Muoviti sulla mappa")  # Nuova opzione
        gioco.io.mostra_messaggio("11. Interagisci con l'ambiente")  # Nuova opzione
        gioco.io.mostra_messaggio("12. Salva partita")  # Nuova opzione
        gioco.io.mostra_messaggio("13. Esci dal gioco")
       
        scelta = gioco.io.richiedi_input("Scelta: ")
        self.ultima_scelta = scelta  # Salviamo la scelta

        if scelta == "1":
            self._parla_con_npg(gioco)
        elif scelta == "2":
            gioco.push_stato(MercatoState())  # Usiamo push_stato per il mercato
        elif scelta == "3":
            mostra_statistiche(gioco.giocatore, gioco)
            avanti(gioco)
        elif scelta == "4":
            from test_state.stati.combattimento import CombattimentoState
            from test_state.nemico import Nemico
            nemico = Nemico("Goblin", 10, 3)
            gioco.push_stato(CombattimentoState(nemico=nemico))  # Usiamo push_stato per il combattimento
        elif scelta == "5":
            self._combatti_con_npg(gioco)
        elif scelta == "6":
            self._esplora_oggetti(gioco)
        elif scelta == "7":
            gioco.push_stato(GestioneInventarioState())
        elif scelta == "8":
            gioco.push_stato(ProvaAbilitaState())
        elif scelta == "9":
            self._visualizza_mappa(gioco)
        elif scelta == "10":
            self._muovi_sulla_mappa(gioco)
        elif scelta == "11":
            self._interagisci_ambiente(gioco)
        elif scelta == "12":
            gioco.salva()
            gioco.io.mostra_messaggio("Partita salvata!")
            avanti(gioco)
        elif scelta == "13":
            gioco.attivo = False          
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")
    
    def _parla_con_npg(self, gioco):
        # Se abbiamo il gestore mappe, proviamo a usare la posizione
        if hasattr(gioco, 'gestore_mappe') and gioco.giocatore.mappa_corrente:
            npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)
            if npg_vicini:
                gioco.io.mostra_messaggio("\nCon chi vuoi parlare?")
                npg_lista = list(npg_vicini.values())
                for i, npg in enumerate(npg_lista, 1):
                    gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
                gioco.io.mostra_messaggio(f"{len(npg_lista) + 1}. Torna indietro")
                
                try:
                    scelta = int(gioco.io.richiedi_input("\nScegli: "))
                    if 1 <= scelta <= len(npg_lista):
                        npg = npg_lista[scelta - 1]
                        gioco.push_stato(DialogoState(npg))
                    elif scelta == len(npg_lista) + 1:
                        return
                    else:
                        gioco.io.mostra_messaggio("Scelta non valida.")
                except ValueError:
                    gioco.io.mostra_messaggio("Devi inserire un numero.")
                return
                
        # Fallback al metodo originale se non ci sono NPG vicini o non usiamo il gestore mappe
        gioco.io.mostra_messaggio("\nCon chi vuoi parlare?")
        for i, nome in enumerate(self.npg_presenti.keys(), 1):
            gioco.io.mostra_messaggio(f"{i}. {nome}")
        gioco.io.mostra_messaggio(f"{len(self.npg_presenti) + 1}. Torna indietro")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(self.npg_presenti):
                npg_nome = list(self.npg_presenti.keys())[scelta - 1]
                npg = self.npg_presenti[npg_nome]
                
                # Avvia il dialogo con l'NPG scelto
                gioco.push_stato(DialogoState(npg))
            elif scelta == len(self.npg_presenti) + 1:
                return  # Torna al menu principale
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            
    def _combatti_con_npg(self, gioco):
        # Se abbiamo il gestore mappe, proviamo a usare la posizione
        if hasattr(gioco, 'gestore_mappe') and gioco.giocatore.mappa_corrente:
            npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)
            if npg_vicini:
                gioco.io.mostra_messaggio("\nCon chi vuoi combattere?")
                npg_lista = list(npg_vicini.values())
                for i, npg in enumerate(npg_lista, 1):
                    gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
                gioco.io.mostra_messaggio(f"{len(npg_lista) + 1}. Torna indietro")
                
                try:
                    scelta = int(gioco.io.richiedi_input("\nScegli: "))
                    if 1 <= scelta <= len(npg_lista):
                        npg = npg_lista[scelta - 1]
                        
                        # Conferma prima di attaccare
                        conferma = gioco.io.richiedi_input(f"Sei sicuro di voler attaccare {npg.nome}? (s/n): ").lower()
                        if conferma == "s":
                            from test_state.stati.combattimento import CombattimentoState
                            gioco.push_stato(CombattimentoState(npg_ostile=npg))
                        else:
                            gioco.io.mostra_messaggio("Hai deciso di non combattere.")
                    elif scelta == len(npg_lista) + 1:
                        return
                    else:
                        gioco.io.mostra_messaggio("Scelta non valida.")
                except ValueError:
                    gioco.io.mostra_messaggio("Devi inserire un numero.")
                return
        
        # Fallback al metodo originale
        gioco.io.mostra_messaggio("\nCon chi vuoi combattere?")
        for i, nome in enumerate(self.npg_presenti.keys(), 1):
            gioco.io.mostra_messaggio(f"{i}. {nome}")
        gioco.io.mostra_messaggio(f"{len(self.npg_presenti) + 1}. Torna indietro")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(self.npg_presenti):
                npg_nome = list(self.npg_presenti.keys())[scelta - 1]
                npg_ostile = self.npg_presenti[npg_nome]
                
                # Conferma prima di attaccare
                conferma = gioco.io.richiedi_input(f"Sei sicuro di voler attaccare {npg_nome}? (s/n): ").lower()
                if conferma == "s":
                    from test_state.stati.combattimento import CombattimentoState
                    gioco.push_stato(CombattimentoState(npg_ostile=npg_ostile))
                else:
                    gioco.io.mostra_messaggio("Hai deciso di non combattere.")
            elif scelta == len(self.npg_presenti) + 1:
                return  # Torna al menu principale
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            
    def _esplora_oggetti(self, gioco):
        # Se abbiamo il gestore mappe, proviamo a usare la posizione
        if hasattr(gioco, 'gestore_mappe') and gioco.giocatore.mappa_corrente:
            oggetti_vicini = gioco.giocatore.ottieni_oggetti_vicini(gioco.gestore_mappe)
            if oggetti_vicini:
                gioco.io.mostra_messaggio("\nOggetti nelle vicinanze:")
                oggetti_lista = []
                for pos, obj in oggetti_vicini.items():
                    oggetti_lista.append((pos, obj))
                    x, y = pos
                    gioco.io.mostra_messaggio(f"{len(oggetti_lista)}. {obj.nome} [{obj.stato}] a ({x}, {y})")
                gioco.io.mostra_messaggio(f"{len(oggetti_lista) + 1}. Torna indietro")
                
                try:
                    scelta = int(gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? "))
                    if 1 <= scelta <= len(oggetti_lista):
                        _, oggetto = oggetti_lista[scelta - 1]
                        oggetto.descrivi()
                        oggetto.interagisci(gioco.giocatore)
                    elif scelta == len(oggetti_lista) + 1:
                        return
                    else:
                        gioco.io.mostra_messaggio("Scelta non valida.")
                except ValueError:
                    gioco.io.mostra_messaggio("Devi inserire un numero.")
                return
        
        # Fallback al metodo originale
        gioco.io.mostra_messaggio("\nOggetti nella taverna:")
        for i, nome in enumerate(self.oggetti_interattivi.keys(), 1):
            oggetto = self.oggetti_interattivi[nome]
            gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
        gioco.io.mostra_messaggio(f"{len(self.oggetti_interattivi) + 1}. Torna indietro")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? "))
            if 1 <= scelta <= len(self.oggetti_interattivi):
                oggetto_nome = list(self.oggetti_interattivi.keys())[scelta - 1]
                oggetto = self.oggetti_interattivi[oggetto_nome]
                oggetto.descrivi()
                oggetto.interagisci(gioco.giocatore)
            elif scelta == len(self.oggetti_interattivi) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
    
    def _visualizza_mappa(self, gioco):
        """Apre lo stato mappa"""
        if not hasattr(gioco, 'gestore_mappe'):
            gioco.io.mostra_messaggio("Sistema mappa non ancora implementato!")
            avanti(gioco)
            return
        
        # Importiamo localmente per evitare dipendenze circolari
        from test_state.stati.mappa_state import MappaState
        gioco.push_stato(MappaState(stato_origine=self))
    
    def _muovi_sulla_mappa(self, gioco):
        """Permette al giocatore di muoversi sulla mappa"""
        if not hasattr(gioco, 'gestore_mappe') or not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema di movimento non disponibile!")
            avanti(gioco)
            return
        
        # Usa direttamente lo stato mappa
        from test_state.stati.mappa_state import MappaState
        gioco.push_stato(MappaState(stato_origine=self))
            
    def _interagisci_ambiente(self, gioco):
        """Permette al giocatore di interagire con l'ambiente circostante"""
        if not hasattr(gioco, 'gestore_mappe') or not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema di interazione non disponibile!")
            avanti(gioco)
            return
            
        # Usa direttamente lo stato mappa
        from test_state.stati.mappa_state import MappaState
        gioco.push_stato(MappaState(stato_origine=self))
            
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
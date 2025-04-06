from states.base_state import BaseGameState
from util.funzioni_utili import avanti
from entities.npg import NPG
from states.dialogo import DialogoState
from entities.giocatore import Giocatore
from states.gestione_inventario import GestioneInventarioState
from items.oggetto_interattivo import Baule, Leva, Porta, OggettoInterattivo, Trappola, OggettoRompibile
from items.oggetto import Oggetto  # Assicurati che questa importazione sia corretta
from states.prova_abilita import ProvaAbilitaState
from world.mappa import Mappa
from world.gestore_mappe import GestitoreMappe
from core.io_interface import GameIO  # Importazione corretta per l'interfaccia IO
from util.data_manager import get_data_manager
import logging


class MercatoState(BaseGameState):
    """Classe che rappresenta lo stato del mercato"""
    
    def __init__(self, game):
        super().__init__(game)
        self.nome_stato = "mercato"
        # Carica gli NPC specifici del mercato
        self.npg_presenti = {
            "Araldo": NPG("Araldo"),
            "Violetta": NPG("Violetta"),
            "Gundren": NPG("Gundren")
        }
        self.nome_npg_attivo = None
        self.stato_conversazione = "inizio"
        self.stato_precedente = None
        
        # Inizializza menu e comandi
        self._init_commands()
        
        # Attributi per gestione asincrona
        self.fase = "menu_principale"
        self.ultimo_input = None
        self.dati_contestuali = {}  # Per memorizzare dati tra più fasi
        
        # Aggiungiamo gli oggetti interattivi del mercato
        self.oggetti_interattivi = {
            "bancarella": OggettoInterattivo("Bancarella", "Una bancarella di oggetti usati.", "aperta", posizione="mercato"),
            "baule_mercante": Baule("Baule del mercante", "Un baule di ferro con serratura robusta.", 
                                   contenuto=[Oggetto("Amuleto", "accessorio", {"fortuna": 1}, 10)],
                                   richiede_chiave=True, posizione="mercato"),
            "porta_magazzino": Porta("Porta del magazzino", "Una porta che conduce al magazzino del mercato.", 
                                    stato="chiusa", richiede_chiave=True, posizione="mercato", 
                                    posizione_destinazione="magazzino"),
            "leva_segreta": Leva("Leva nascosta", "Una leva nascosta sotto il bancone.", posizione="mercato")
        }
        
        # Colleghiamo la leva alla porta del magazzino
        self.oggetti_interattivi["leva_segreta"].collega_oggetto("porta", self.oggetti_interattivi["porta_magazzino"])
        
        # NUOVO OGGETTO 1: Statua Antica con diverse abilità richieste
        statua_antica = OggettoInterattivo("Statua Antica", "Una statua di pietra raffigurante un mercante. Sembra molto vecchia.", stato="normale", posizione="mercato")
        
        # Configura descrizioni per vari stati
        statua_antica.imposta_descrizione_stato("normale", "Una statua di pietra raffigurante un mercante. Sembra molto vecchia.")
        statua_antica.imposta_descrizione_stato("esaminata", "Guardando attentamente, noti simboli strani incisi sulla base della statua.")
        statua_antica.imposta_descrizione_stato("decifrata", "I simboli sulla statua sembrano indicare la posizione di un tesoro nascosto.")
        statua_antica.imposta_descrizione_stato("ruotata", "La statua è stata ruotata. Si sente un click provenire dal pavimento.")
        
        # Definisci le transizioni possibili
        statua_antica.aggiungi_transizione("normale", "esaminata")
        statua_antica.aggiungi_transizione("esaminata", "decifrata")
        statua_antica.aggiungi_transizione("decifrata", "ruotata")
        statua_antica.aggiungi_transizione("ruotata", "normale")
        
        # Collega abilità alle transizioni
        statua_antica.richiedi_abilita("percezione", "esaminata", 12, 
                                      "Osservi attentamente la statua e noti dei piccoli simboli incisi sulla base.")
        statua_antica.richiedi_abilita("storia", "decifrata", 15, 
                                      "Grazie alla tua conoscenza storica, comprendi che i simboli raccontano di un tesoro nascosto.")
        statua_antica.richiedi_abilita("forza", "ruotata", 14, 
                                      "Con uno sforzo notevole, riesci a ruotare la pesante statua rivelando una piccola fessura nel pavimento.")
        
        # Collega un evento di gioco allo stato "ruotata"
        statua_antica.collega_evento("ruotata", lambda gioco: gioco.sblocca_area("cripta_mercante"))
        
        # Aggiungi la statua al mercato
        self.oggetti_interattivi["statua_antica"] = statua_antica
        
        # NUOVO OGGETTO 2: Scaffale con merce speciale
        scaffale_merce = OggettoInterattivo("Scaffale di Merce", "Uno scaffale pieno di merci esotiche.", stato="intatto", posizione="mercato")
        
        # Configura descrizioni per vari stati
        scaffale_merce.imposta_descrizione_stato("intatto", "Uno scaffale pieno di merci esotiche dai vari paesi.")
        scaffale_merce.imposta_descrizione_stato("ispezionato", "Tra le varie merci, noti un piccolo cofanetto nascosto dietro alcune stoffe.")
        scaffale_merce.imposta_descrizione_stato("spostato", "Hai spostato alcuni oggetti rivelando un cofanetto decorato.")
        scaffale_merce.imposta_descrizione_stato("aperto", "Il cofanetto è aperto, rivelando una mappa di un luogo sconosciuto.")
        
        # Definisci le transizioni possibili
        scaffale_merce.aggiungi_transizione("intatto", "ispezionato")
        scaffale_merce.aggiungi_transizione("ispezionato", "spostato")
        scaffale_merce.aggiungi_transizione("spostato", "aperto")
        
        # Collega abilità alle transizioni
        scaffale_merce.richiedi_abilita("percezione", "ispezionato", 10, 
                                        "Guardando tra le merci esposte, noti qualcosa di insolito...")
        scaffale_merce.richiedi_abilita("indagare", "spostato", 12, 
                                        "Sposti con attenzione alcuni oggetti, rivelando un piccolo cofanetto decorato.")
        scaffale_merce.richiedi_abilita("destrezza", "aperto", 13, 
                                        "Con le tue dita agili riesci ad aprire il meccanismo di chiusura del cofanetto.")
        
        # Definisci un evento quando il cofanetto viene aperto
        def ricompensa_mappa(gioco):
            mappa = Oggetto("Mappa del tesoro", "mappa", {}, 50, "Una mappa che mostra la posizione di un tesoro nascosto.")
            gioco.giocatore.aggiungi_item(mappa)
            gioco.io.mostra_messaggio("Hai ottenuto una Mappa del tesoro!")
        
        scaffale_merce.collega_evento("aperto", ricompensa_mappa)
        
        # Aggiungi lo scaffale al mercato
        self.oggetti_interattivi["scaffale_merce"] = scaffale_merce
        
        # NUOVO OGGETTO 3: Fontana Magica
        fontana = OggettoInterattivo("Fontana Magica", "Una piccola fontana decorativa al centro del mercato.", stato="inattiva", posizione="mercato")
        
        # Configura descrizioni per vari stati
        fontana.imposta_descrizione_stato("inattiva", "Una piccola fontana decorativa che sembra non funzionare da tempo.")
        fontana.imposta_descrizione_stato("esaminata", "Noti dei simboli arcani incisi sul bordo della fontana.")
        fontana.imposta_descrizione_stato("attivata", "La fontana si illumina e l'acqua inizia a fluire, emanando un bagliore azzurro.")
        fontana.imposta_descrizione_stato("purificata", "L'acqua della fontana emana un bagliore dorato e sembra avere proprietà curative.")
        
        # Definisci le transizioni possibili
        fontana.aggiungi_transizione("inattiva", "esaminata")
        fontana.aggiungi_transizione("esaminata", "attivata")
        fontana.aggiungi_transizione("attivata", "purificata")
        fontana.aggiungi_transizione("purificata", "inattiva")
        
        # Collega abilità alle transizioni
        fontana.richiedi_abilita("arcano", "esaminata", 13, 
                                "Studiando la fontana, riconosci antichi simboli arcani di acqua ed energia.")
        fontana.richiedi_abilita("intelligenza", "attivata", 14, 
                                "Ricordando un antico incantesimo, pronunci le parole che attivano la fontana.")
        fontana.richiedi_abilita("religione", "purificata", 15, 
                                "Con una preghiera di purificazione, l'acqua della fontana cambia colore diventando dorata.")
        
        # Definisci eventi per i vari stati
        def bevi_acqua_guaritrice(gioco):
            gioco.io.mostra_messaggio("Bevi l'acqua dalla fontana e ti senti rivitalizzato!")
            gioco.giocatore.cura(10)
        
        fontana.collega_evento("purificata", bevi_acqua_guaritrice)
        
        # Aggiungi la fontana al mercato
        self.oggetti_interattivi["fontana_magica"] = fontana
        
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
        # Se è la prima visita al mercato, inizializza la posizione e popola la mappa
        if not hasattr(self, 'prima_visita_completata'):
            mappa = gioco.gestore_mappe.ottieni_mappa("mercato")
            if mappa:
                gioco.gestore_mappe.imposta_mappa_attuale("mercato")
                x, y = mappa.pos_iniziale_giocatore
                gioco.giocatore.imposta_posizione("mercato", x, y)
                # Popola la mappa con gli oggetti interattivi e gli NPG
                gioco.gestore_mappe.trasferisci_oggetti_da_stato("mercato", self)
            self.prima_visita_completata = True
            
        # Gestione asincrona basata sulla fase corrente
        if self.fase == "menu_principale":
            self._mostra_menu_principale(gioco)
        elif self.fase == "compra_pozione":
            self._compra_pozione(gioco)
        elif self.fase == "vendi_oggetto_lista":
            self._vendi_oggetto_lista(gioco)
        elif self.fase == "vendi_oggetto_conferma":
            self._vendi_oggetto_conferma(gioco)
        elif self.fase == "parla_npg_lista":
            self._parla_npg_lista(gioco)
        elif self.fase == "combatti_npg_lista":
            self._combatti_npg_lista(gioco)
        elif self.fase == "combatti_npg_conferma":
            self._combatti_npg_conferma(gioco)
        elif self.fase == "esplora_oggetti_lista":
            self._esplora_oggetti_lista(gioco)
        elif self.fase == "interagisci_oggetto":
            self._interagisci_oggetto(gioco)
        elif self.fase.startswith("prova_abilita"):
            # Gestione delegata a ProvaAbilitaState
            gioco.push_stato(ProvaAbilitaState())
            self.fase = "menu_principale"  # Torna al menu dopo
        elif self.fase == "visualizza_mappa":
            self._visualizza_mappa(gioco)
        elif self.fase == "muovi_mappa":
            self._muovi_sulla_mappa(gioco)
        elif self.fase == "interagisci_ambiente":
            self._interagisci_ambiente(gioco)
        else:
            # Fase non riconosciuta, torna al menu principale
            self.fase = "menu_principale"
            self.esegui(gioco)
    
    def _mostra_menu_principale(self, gioco):
        gioco.io.mostra_messaggio("\n=== MERCATO ===")
        gioco.io.mostra_messaggio("1. Compra pozione (5 oro)")
        gioco.io.mostra_messaggio("2. Vendi oggetto")
        gioco.io.mostra_messaggio("3. Parla con un mercante")
        gioco.io.mostra_messaggio("4. Sfida un mercante")
        gioco.io.mostra_messaggio("5. Gestisci inventario")
        gioco.io.mostra_messaggio("6. Esplora oggetti nel mercato")
        gioco.io.mostra_messaggio("7. Prova abilità")
        gioco.io.mostra_messaggio("8. Visualizza mappa")
        gioco.io.mostra_messaggio("9. Muoviti sulla mappa")
        gioco.io.mostra_messaggio("10. Interagisci con l'ambiente")
        gioco.io.mostra_messaggio("11. Viaggia verso un'altra zona")
        
        scelta_input = gioco.io.richiedi_input("\nCosa vuoi fare? ")
        self.ultimo_input = scelta_input
        
        # Elabora il comando
        if not scelta_input.isdigit():
            scelta = self._elabora_comando_mercato(scelta_input)
        else:
            scelta = scelta_input
        
        # Imposta la fase successiva in base alla scelta
        if scelta == "1":
            self.fase = "compra_pozione"
        elif scelta == "2":
            self.fase = "vendi_oggetto_lista"
        elif scelta == "3":
            self.fase = "parla_npg_lista"
        elif scelta == "4":
            self.fase = "combatti_npg_lista"
        elif scelta == "5":
            gioco.push_stato(GestioneInventarioState())
            # Rimaniamo nel menu principale al ritorno
        elif scelta == "6":
            self.fase = "esplora_oggetti_lista"
        elif scelta == "7":
            self.fase = "prova_abilita"
        elif scelta == "8":
            self.fase = "visualizza_mappa"
        elif scelta == "9":
            self.fase = "muovi_mappa"
        elif scelta == "10":
            self.fase = "interagisci_ambiente"
        elif scelta == "11":
            from states.scelta_mappa_state import SceltaMappaState
            gioco.push_stato(SceltaMappaState(gioco))
        else:
            gioco.io.mostra_messaggio(f"Non capisco cosa vuoi fare con '{scelta_input}'.")
            avanti(gioco)
            return
        
        # Se non abbiamo cambiato stato, esegui subito la prossima fase
        if self.fase != "menu_principale" and gioco.stato_corrente() == self:
            self.esegui(gioco)
    
    def _elabora_comando_mercato(self, cmd):
        cmd = cmd.lower().strip()
        
        # Mappatura comandi di testo alle azioni
        if any(x in cmd for x in ["compra", "pozione", "acquista"]):
            return "1"
        elif any(x in cmd for x in ["vendi", "vende", "vendere"]):
            return "2"
        elif any(x in cmd for x in ["parla", "mercante", "conversare"]):
            return "3"
        elif any(x in cmd for x in ["sfida", "combatti", "duello"]):
            return "4"
        elif any(x in cmd for x in ["inventario", "zaino", "gestisci"]):
            return "5"
        elif any(x in cmd for x in ["esplora", "cerca", "oggetti"]):
            return "6"
        elif any(x in cmd for x in ["prova", "abilità", "skill"]):
            return "7"
        elif any(x in cmd for x in ["mappa", "visualizza"]):
            return "8"
        elif any(x in cmd for x in ["muovi", "movimento", "vai"]):
            return "9"
        elif any(x in cmd for x in ["interagisci", "ambiente", "interazione"]):
            return "10"
        elif any(x in cmd for x in ["viaggia", "zona", "cambio", "mappa"]):
            return "11"
        else:
            return cmd  # ritorna il comando originale se non corrisponde a nessuna azione
    
    def _compra_pozione(self, gioco):
        if gioco.giocatore.oro >= 5:
            gioco.giocatore.oro -= 5
            gioco.giocatore.aggiungi_item("Pozione di cura")
            gioco.io.mostra_messaggio("Hai comprato una pozione di cura!")
        else:
            gioco.io.mostra_messaggio("Non hai abbastanza oro!")
        
        self.fase = "menu_principale"
        avanti(gioco)
    
    def _vendi_oggetto_lista(self, gioco):
        if len(gioco.giocatore.inventario) == 0:
            gioco.io.mostra_messaggio("Non hai oggetti da vendere!")
            self.fase = "menu_principale"
            avanti(gioco)
            return
        
        # Mostra la lista degli oggetti
        gioco.io.mostra_messaggio("\nI tuoi oggetti:")
        for i, oggetto in enumerate(gioco.giocatore.inventario, 1):
            if isinstance(oggetto, str):
                gioco.io.mostra_messaggio(f"{i}. {oggetto}")
            else:
                # Mostra anche il tipo e il valore dell'oggetto se disponibili
                tipo_str = f" - {oggetto.tipo}" if hasattr(oggetto, 'tipo') else ""
                valore_str = f" (Valore: {oggetto.valore} oro)" if hasattr(oggetto, 'valore') else ""
                gioco.io.mostra_messaggio(f"{i}. {oggetto.nome}{tipo_str}{valore_str}")
        gioco.io.mostra_messaggio(f"0. Torna indietro")
        
        idx_input = gioco.io.richiedi_input("\nQuale oggetto vuoi vendere? ")
        self.ultimo_input = idx_input
        
        # Torna al menu se richiesto
        if idx_input == "0":
            self.fase = "menu_principale"
            self.esegui(gioco)
            return
            
        # Trova l'oggetto per nome o indice
        idx = -1
        if idx_input.isdigit():
            idx = int(idx_input) - 1
        else:
            # Cerca di trovare l'oggetto per nome
            nome_oggetto = idx_input.lower().strip()
            for i, ogg in enumerate(gioco.giocatore.inventario):
                ogg_nome = ogg.nome.lower() if hasattr(ogg, 'nome') else str(ogg).lower()
                if nome_oggetto in ogg_nome:
                    idx = i
                    break
        
        # Controlla se l'oggetto è stato trovato
        if 0 <= idx < len(gioco.giocatore.inventario):
            # Memorizza l'indice dell'oggetto nei dati contestuali
            self.dati_contestuali["idx_oggetto_da_vendere"] = idx
            self.fase = "vendi_oggetto_conferma"
            self.esegui(gioco)  # Esegui subito la fase di conferma
        else:
            gioco.io.mostra_messaggio("Oggetto non trovato nell'inventario.")
            self.fase = "menu_principale"
            avanti(gioco)
    
    def _vendi_oggetto_conferma(self, gioco):
        idx = self.dati_contestuali.get("idx_oggetto_da_vendere", -1)
        if idx < 0 or idx >= len(gioco.giocatore.inventario):
            gioco.io.mostra_messaggio("Errore: l'oggetto selezionato non è più disponibile.")
            self.fase = "menu_principale"
            avanti(gioco)
            return
        
        oggetto = gioco.giocatore.inventario[idx]
        
        # Calcola il prezzo di vendita
        prezzo_vendita = 3  # Prezzo base
        if hasattr(oggetto, 'valore'):
            prezzo_vendita = max(1, oggetto.valore // 2)  # Metà del valore originale
        
        gioco.io.mostra_messaggio(f"Stai per vendere {oggetto} per {prezzo_vendita} monete d'oro.")
        conferma = gioco.io.richiedi_input("Confermi la vendita? (s/n): ")
        self.ultimo_input = conferma
        
        if conferma.lower() == "s":
            oggetto = gioco.giocatore.inventario.pop(idx)
            gioco.giocatore.oro += prezzo_vendita
            gioco.io.mostra_messaggio(f"Hai venduto {oggetto} per {prezzo_vendita} monete d'oro!")
        else:
            gioco.io.mostra_messaggio("Vendita annullata.")
        
        self.fase = "menu_principale"
        avanti(gioco)
    
    def _parla_npg_lista(self, gioco):
        # Prima controlla se ci sono NPG sulla mappa
        npg_vicini = {}
        if gioco.giocatore.mappa_corrente:
            npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)
        
        # Se non ci sono NPG sulla mappa, usa quelli definiti nello stato
        if not npg_vicini:
            npg_lista = list(self.npg_presenti.values())
        else:
            npg_lista = list(npg_vicini.values())
        
        gioco.io.mostra_messaggio("\nCon chi vuoi parlare?")
        for i, npg in enumerate(npg_lista, 1):
            gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
        gioco.io.mostra_messaggio(f"0. Torna indietro")
        
        scelta = gioco.io.richiedi_input("\nScegli: ")
        self.ultimo_input = scelta
        
        if scelta == "0":
            self.fase = "menu_principale"
            self.esegui(gioco)
            return
            
        try:
            idx = int(scelta) - 1
            if 0 <= idx < len(npg_lista):
                npg = npg_lista[idx]
                # Avvia il dialogo con l'NPG scelto
                gioco.push_stato(DialogoState(npg))
                # Dopo il dialogo, torna al menu principale
                self.fase = "menu_principale"
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self.fase = "menu_principale"
                avanti(gioco)
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            self.fase = "menu_principale"
            avanti(gioco)
    
    def _combatti_npg_lista(self, gioco):
        # Prima controlla se ci sono NPG sulla mappa
        npg_vicini = {}
        if gioco.giocatore.mappa_corrente:
            npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)
        
        # Se non ci sono NPG sulla mappa, usa quelli definiti nello stato
        if not npg_vicini:
            npg_lista = list(self.npg_presenti.values())
        else:
            npg_lista = list(npg_vicini.values())
        
        gioco.io.mostra_messaggio("\nCon chi vuoi combattere?")
        for i, npg in enumerate(npg_lista, 1):
            gioco.io.mostra_messaggio(f"{i}. {npg.nome}")
        gioco.io.mostra_messaggio(f"0. Torna indietro")
        
        scelta = gioco.io.richiedi_input("\nScegli: ")
        self.ultimo_input = scelta
        
        if scelta == "0":
            self.fase = "menu_principale"
            self.esegui(gioco)
            return
            
        try:
            idx = int(scelta) - 1
            if 0 <= idx < len(npg_lista):
                # Memorizza l'NPG scelto nei dati contestuali
                self.dati_contestuali["npg_combattimento"] = npg_lista[idx]
                self.fase = "combatti_npg_conferma"
                self.esegui(gioco)  # Esegui subito la fase di conferma
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self.fase = "menu_principale"
                avanti(gioco)
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            self.fase = "menu_principale"
            avanti(gioco)
    
    def _combatti_npg_conferma(self, gioco):
        npg = self.dati_contestuali.get("npg_combattimento")
        if not npg:
            gioco.io.mostra_messaggio("Errore: l'NPG selezionato non è più disponibile.")
            self.fase = "menu_principale"
            avanti(gioco)
            return
        
        gioco.io.mostra_messaggio(f"Sei sicuro di voler attaccare {npg.nome}?")
        conferma = gioco.io.richiedi_input("Conferma (s/n): ")
        self.ultimo_input = conferma
        
        if conferma.lower() == "s":
            from states.combattimento import CombattimentoState
            gioco.push_stato(CombattimentoState(npg_ostile=npg))
            # Dopo il combattimento, torna al menu principale
            self.fase = "menu_principale"
        else:
            gioco.io.mostra_messaggio("Hai deciso di non combattere.")
            self.fase = "menu_principale"
            avanti(gioco)
    
    def _esplora_oggetti_lista(self, gioco):
        # Prima controlla se ci sono oggetti sulla mappa
        oggetti_vicini = {}
        if gioco.giocatore.mappa_corrente:
            oggetti_vicini = gioco.giocatore.ottieni_oggetti_vicini(gioco.gestore_mappe)
        
        # Prepara la lista degli oggetti da mostrare
        if not oggetti_vicini:
            # Usa gli oggetti definiti nello stato
            gioco.io.mostra_messaggio("\nOggetti nel mercato:")
            oggetti_lista = []
            for nome, obj in self.oggetti_interattivi.items():
                oggetti_lista.append(obj)
                gioco.io.mostra_messaggio(f"{len(oggetti_lista)}. {obj.nome} [{obj.stato}]")
        else:
            # Usa gli oggetti sulla mappa
            gioco.io.mostra_messaggio("\nOggetti nelle vicinanze:")
            oggetti_lista = []
            for pos, obj in oggetti_vicini.items():
                oggetti_lista.append(obj)
                x, y = pos
                gioco.io.mostra_messaggio(f"{len(oggetti_lista)}. {obj.nome} [{obj.stato}] a ({x}, {y})")
        
        gioco.io.mostra_messaggio(f"0. Torna indietro")
        
        scelta = gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? ")
        self.ultimo_input = scelta
        
        if scelta == "0":
            self.fase = "menu_principale"
            self.esegui(gioco)
            return
            
        try:
            idx = int(scelta) - 1
            if 0 <= idx < len(oggetti_lista):
                oggetto = oggetti_lista[idx]
                self.dati_contestuali["oggetto_interazione"] = oggetto
                self.fase = "interagisci_oggetto"
                self.esegui(gioco)
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self.fase = "menu_principale"
                avanti(gioco)
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            self.fase = "menu_principale"
            avanti(gioco)
    
    def _interagisci_oggetto(self, gioco):
        oggetto = self.dati_contestuali.get("oggetto_interazione")
        if not oggetto:
            gioco.io.mostra_messaggio("Errore: l'oggetto selezionato non è più disponibile.")
            self.fase = "menu_principale"
            avanti(gioco)
            return
            
        oggetto.descrivi()
        oggetto.interagisci(gioco.giocatore)
        
        self.fase = "menu_principale"
        avanti(gioco)
    
    def _visualizza_mappa(self, gioco):
        """Visualizza la mappa del mercato"""
        from states.mappa_state import MappaState
        
        # Se c'è già un'istanza del map state, la usiamo
        map_state = next((s for s in gioco.stato_stack if isinstance(s, MappaState)), None)
        if map_state:
            map_state.esegui(gioco)
        else:
            gioco.push_stato(MappaState(stato_origine=self))
        
        # Dopo aver visualizzato la mappa, torneremo al menu principale
        self.fase = "menu_principale"
    
    def _muovi_sulla_mappa(self, gioco):
        """Permette al giocatore di muoversi sulla mappa"""
        from states.mappa_state import MappaState
        
        if not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema di movimento non disponibile!")
            self.fase = "menu_principale"
            avanti(gioco)
            return
        
        # Se c'è già un'istanza del map state, la usiamo
        map_state = next((s for s in gioco.stato_stack if isinstance(s, MappaState)), None)
        if map_state:
            map_state.esegui(gioco)
        else:
            gioco.push_stato(MappaState(stato_origine=self))
        
        # Dopo il movimento, torneremo al menu principale
        self.fase = "menu_principale"
    
    def _interagisci_ambiente(self, gioco):
        """Permette al giocatore di interagire con l'ambiente circostante"""
        from states.mappa_state import MappaState
        
        if not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema di interazione non disponibile!")
            self.fase = "menu_principale"
            avanti(gioco)
            return
        
        # Se c'è già un'istanza del map state, la usiamo
        map_state = next((s for s in gioco.stato_stack if isinstance(s, MappaState)), None)
        if map_state:
            map_state.esegui(gioco)
        else:
            gioco.push_stato(MappaState(stato_origine=self))
        
        # Dopo l'interazione, torneremo al menu principale
        self.fase = "menu_principale"
    
    def _init_commands(self):
        """Inizializza i comandi e le loro mappature per questo stato"""
        # Questo è un metodo temporaneo che può essere implementato completamente in futuro
        # Per ora è vuoto per consentire l'esecuzione del gioco
        pass
        
    def to_dict(self):
        """
        Converte lo stato del mercato in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dello stato in formato dizionario
        """
        # Ottieni il dizionario base
        data = super().to_dict()
        
        # Aggiungi attributi specifici
        data.update({
            "fase": self.fase,
            "ultimo_input": self.ultimo_input,
            # Non serializzare mercanti, scorte, oggetti_interattivi poiché sono generati dinamicamente
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data, game=None):
        """
        Crea un'istanza di MercatoState da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            game: Istanza del gioco (opzionale)
            
        Returns:
            MercatoState: Nuova istanza di MercatoState
        """
        # Otteniamo innanzitutto uno stato di base attraverso la classe padre
        state = super().from_dict(data, game)
        
        # Inizializziamo manualmente gli attributi specifici di MercatoState
        state.nome_stato = "mercato"
        state.game = game
        state.fase = data.get("fase", "menu_principale")
        state.ultimo_input = data.get("ultimo_input")
        state.dati_contestuali = {}
        state.prima_visita_completata = False
        
        # Inizializza gli NPC del mercato
        state.npg_presenti = {
            "Araldo": NPG("Araldo"),
            "Violetta": NPG("Violetta"),
            "Gundren": NPG("Gundren")
        }
        state.nome_npg_attivo = None
        state.stato_conversazione = "inizio"
        state.stato_precedente = None
        
        # Inizializza gli oggetti interattivi vuoti (verranno caricati dal sistema JSON)
        state.oggetti_interattivi = {}
        state.mostra_mappa = False
        
        # Direzioni di movimento
        state.direzioni = {
            "nord": (0, -1),
            "sud": (0, 1),
            "est": (1, 0),
            "ovest": (-1, 0)
        }
        
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
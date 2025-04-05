from states.base_state import BaseState
from util.funzioni_utili import avanti
from entities.npg import NPG
from states.dialogo import DialogoState
from entities.giocatore import Giocatore
from states.gestione_inventario import GestioneInventarioState
from items.oggetto_interattivo import (
    Baule,
    Leva,
    Porta,
    OggettoInterattivo,
    Trappola,
    OggettoRompibile,
)
from items.oggetto import Oggetto  # Assicurati che questa importazione sia corretta
from states.prova_abilita import ProvaAbilitaState
from world.mappa import Mappa
from world.gestore_mappe import GestitoreMappe
from core.io_interface import GameIO  # Importazione corretta per l'interfaccia IO


class MercatoState(BaseState):
    def __init__(self):
        # Creiamo NPG specifici del mercato
        self.npg_presenti = {
            "Araldo": NPG("Araldo"),
            "Violetta": NPG("Violetta"),
            "Gundren": NPG("Gundren"),
        }

        # Aggiungiamo gli oggetti interattivi del mercato
        self.oggetti_interattivi = {
            "bancarella": OggettoInterattivo(
                "Bancarella",
                "Una bancarella di oggetti usati.",
                "aperta",
                posizione="mercato",
            ),
            "baule_mercante": Baule(
                "Baule del mercante",
                "Un baule di ferro con serratura robusta.",
                contenuto=[Oggetto("Amuleto", "accessorio", {"fortuna": 1}, 10)],
                richiede_chiave=True,
                posizione="mercato",
            ),
            "porta_magazzino": Porta(
                "Porta del magazzino",
                "Una porta che conduce al magazzino del mercato.",
                stato="chiusa",
                richiede_chiave=True,
                posizione="mercato",
                posizione_destinazione="magazzino",
            ),
            "leva_segreta": Leva(
                "Leva nascosta",
                "Una leva nascosta sotto il bancone.",
                posizione="mercato",
            ),
        }

        # Colleghiamo la leva alla porta del magazzino
        self.oggetti_interattivi["leva_segreta"].collega_oggetto(
            "porta", self.oggetti_interattivi["porta_magazzino"]
        )

        # NUOVO OGGETTO 1: Statua Antica con diverse abilità richieste
        statua_antica = OggettoInterattivo(
            "Statua Antica",
            "Una statua di pietra raffigurante un mercante. Sembra molto vecchia.",
            stato="normale",
            posizione="mercato",
        )

        # Configura descrizioni per vari stati
        statua_antica.imposta_descrizione_stato(
            "normale",
            "Una statua di pietra raffigurante un mercante. Sembra molto vecchia.",
        )
        statua_antica.imposta_descrizione_stato(
            "esaminata",
            "Guardando attentamente, noti simboli strani incisi sulla base della statua.",
        )
        statua_antica.imposta_descrizione_stato(
            "decifrata",
            "I simboli sulla statua sembrano indicare la posizione di un tesoro nascosto.",
        )
        statua_antica.imposta_descrizione_stato(
            "ruotata",
            "La statua è stata ruotata. Si sente un click provenire dal pavimento.",
        )

        # Definisci le transizioni possibili
        statua_antica.aggiungi_transizione("normale", "esaminata")
        statua_antica.aggiungi_transizione("esaminata", "decifrata")
        statua_antica.aggiungi_transizione("decifrata", "ruotata")
        statua_antica.aggiungi_transizione("ruotata", "normale")

        # Collega abilità alle transizioni
        statua_antica.richiedi_abilita(
            "percezione",
            "esaminata",
            12,
            "Osservi attentamente la statua e noti dei piccoli simboli incisi sulla base.",
        )
        statua_antica.richiedi_abilita(
            "storia",
            "decifrata",
            15,
            "Grazie alla tua conoscenza storica, comprendi che i simboli raccontano di un tesoro nascosto.",
        )
        statua_antica.richiedi_abilita(
            "forza",
            "ruotata",
            14,
            "Con uno sforzo notevole, riesci a ruotare la pesante statua rivelando una piccola fessura nel pavimento.",
        )

        # Collega un evento di gioco allo stato "ruotata"
        statua_antica.collega_evento(
            "ruotata", lambda gioco: gioco.sblocca_area("cripta_mercante")
        )

        # Aggiungi la statua al mercato
        self.oggetti_interattivi["statua_antica"] = statua_antica

        # NUOVO OGGETTO 2: Scaffale con merce speciale
        scaffale_merce = OggettoInterattivo(
            "Scaffale di Merce",
            "Uno scaffale pieno di merci esotiche.",
            stato="intatto",
            posizione="mercato",
        )

        # Configura descrizioni per vari stati
        scaffale_merce.imposta_descrizione_stato(
            "intatto", "Uno scaffale pieno di merci esotiche dai vari paesi."
        )
        scaffale_merce.imposta_descrizione_stato(
            "ispezionato",
            "Tra le varie merci, noti un piccolo cofanetto nascosto dietro alcune stoffe.",
        )
        scaffale_merce.imposta_descrizione_stato(
            "spostato", "Hai spostato alcuni oggetti rivelando un cofanetto decorato."
        )
        scaffale_merce.imposta_descrizione_stato(
            "aperto",
            "Il cofanetto è aperto, rivelando una mappa di un luogo sconosciuto.",
        )

        # Definisci le transizioni possibili
        scaffale_merce.aggiungi_transizione("intatto", "ispezionato")
        scaffale_merce.aggiungi_transizione("ispezionato", "spostato")
        scaffale_merce.aggiungi_transizione("spostato", "aperto")

        # Collega abilità alle transizioni
        scaffale_merce.richiedi_abilita(
            "percezione",
            "ispezionato",
            10,
            "Guardando tra le merci esposte, noti qualcosa di insolito...",
        )
        scaffale_merce.richiedi_abilita(
            "indagare",
            "spostato",
            12,
            "Sposti con attenzione alcuni oggetti, rivelando un piccolo cofanetto decorato.",
        )
        scaffale_merce.richiedi_abilita(
            "destrezza",
            "aperto",
            13,
            "Con le tue dita agili riesci ad aprire il meccanismo di chiusura del cofanetto.",
        )

        # Definisci un evento quando il cofanetto viene aperto
        def ricompensa_mappa(gioco):
            mappa = Oggetto(
                "Mappa del tesoro",
                "mappa",
                {},
                50,
                "Una mappa che mostra la posizione di un tesoro nascosto.",
            )
            gioco.giocatore.aggiungi_item(mappa)
            gioco.io.mostra_messaggio("Hai ottenuto una Mappa del tesoro!")

        scaffale_merce.collega_evento("aperto", ricompensa_mappa)

        # Aggiungi lo scaffale al mercato
        self.oggetti_interattivi["scaffale_merce"] = scaffale_merce

        # NUOVO OGGETTO 3: Fontana Magica
        fontana = OggettoInterattivo(
            "Fontana Magica",
            "Una piccola fontana decorativa al centro del mercato.",
            stato="inattiva",
            posizione="mercato",
        )

        # Configura descrizioni per vari stati
        fontana.imposta_descrizione_stato(
            "inattiva",
            "Una piccola fontana decorativa che sembra non funzionare da tempo.",
        )
        fontana.imposta_descrizione_stato(
            "esaminata", "Noti dei simboli arcani incisi sul bordo della fontana."
        )
        fontana.imposta_descrizione_stato(
            "attivata",
            "La fontana si illumina e l'acqua inizia a fluire, emanando un bagliore azzurro.",
        )
        fontana.imposta_descrizione_stato(
            "purificata",
            "L'acqua della fontana emana un bagliore dorato e sembra avere proprietà curative.",
        )

        # Definisci le transizioni possibili
        fontana.aggiungi_transizione("inattiva", "esaminata")
        fontana.aggiungi_transizione("esaminata", "attivata")
        fontana.aggiungi_transizione("attivata", "purificata")
        fontana.aggiungi_transizione("purificata", "inattiva")

        # Collega abilità alle transizioni
        fontana.richiedi_abilita(
            "arcano",
            "esaminata",
            13,
            "Studiando la fontana, riconosci antichi simboli arcani di acqua ed energia.",
        )
        fontana.richiedi_abilita(
            "intelligenza",
            "attivata",
            14,
            "Ricordando un antico incantesimo, pronunci le parole che attivano la fontana.",
        )
        fontana.richiedi_abilita(
            "religione",
            "purificata",
            15,
            "Con una preghiera di purificazione, l'acqua della fontana cambia colore diventando dorata.",
        )

        # Definisci eventi per i vari stati
        def bevi_acqua_guaritrice(gioco):
            gioco.io.mostra_messaggio(
                "Bevi l'acqua dalla fontana e ti senti rivitalizzato!"
            )
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
            "ovest": (-1, 0),
        }

    def esegui(self, gioco):
        # Se è la prima visita al mercato, inizializza la posizione e popola la mappa
        if not hasattr(self, "prima_visita_completata"):
            if hasattr(gioco, "gestore_mappe"):
                if mappa := gioco.gestore_mappe.ottieni_mappa("mercato"):
                    gioco.gestore_mappe.imposta_mappa_attuale("mercato")
                    x, y = mappa.pos_iniziale_giocatore
                    gioco.giocatore.imposta_posizione("mercato", x, y)
                    # Popola la mappa con gli oggetti interattivi e gli NPG
                    gioco.gestore_mappe.trasferisci_oggetti_da_stato("mercato", self)
            self.prima_visita_completata = True

        gioco.io.mostra_messaggio("\n=== MERCATO ===")
        gioco.io.mostra_messaggio("1. Compra pozione (5 oro)")
        gioco.io.mostra_messaggio("2. Vendi oggetto")
        gioco.io.mostra_messaggio("3. Parla con un mercante")
        gioco.io.mostra_messaggio("4. Sfida un mercante")
        gioco.io.mostra_messaggio("5. Gestisci inventario")
        gioco.io.mostra_messaggio("6. Esplora oggetti nel mercato")
        gioco.io.mostra_messaggio("7. Prova abilità")
        gioco.io.mostra_messaggio("8. Visualizza mappa")  # Nuova opzione
        gioco.io.mostra_messaggio("9. Muoviti sulla mappa")  # Nuova opzione
        gioco.io.mostra_messaggio("10. Interagisci con l'ambiente")  # Nuova opzione
        gioco.io.mostra_messaggio("11. Torna alla taverna")

        scelta = gioco.io.richiedi_input("\nCosa vuoi fare? ")

        if scelta == "1":
            if gioco.giocatore.oro >= 5:
                gioco.giocatore.oro -= 5
                gioco.giocatore.aggiungi_item("Pozione")
                gioco.io.mostra_messaggio("Hai comprato una pozione!")
            else:
                gioco.io.mostra_messaggio("Non hai abbastanza oro!")
        elif scelta == "2":
            if len(gioco.giocatore.inventario) == 0:
                gioco.io.mostra_messaggio("Non hai oggetti da vendere!")
            else:
                gioco.io.mostra_messaggio("\nI tuoi oggetti:")
                for i, oggetto in enumerate(gioco.giocatore.inventario, 1):
                    gioco.io.mostra_messaggio(f"{i}. {oggetto}")
                try:
                    idx = (
                        int(
                            gioco.io.richiedi_input(
                                "\nQuale oggetto vuoi vendere? (0 per annullare) "
                            )
                        )
                        - 1
                    )
                    if 0 <= idx < len(gioco.giocatore.inventario):
                        oggetto = gioco.giocatore.inventario.pop(idx)
                        gioco.giocatore.oro += 3
                        gioco.io.mostra_messaggio(
                            f"Hai venduto {oggetto} per 3 monete d'oro!"
                        )
                except ValueError:
                    gioco.io.mostra_messaggio("Scelta non valida!")
        elif scelta == "3":
            self._parla_con_npg(gioco)
        elif scelta == "4":
            self._combatti_con_npg(gioco)
        elif scelta == "5":
            gioco.push_stato(GestioneInventarioState())
        elif scelta == "6":
            self._esplora_oggetti(gioco)
        elif scelta == "7":
            gioco.push_stato(ProvaAbilitaState())
        elif scelta == "8":
            self._visualizza_mappa(gioco)
        elif scelta == "9":
            self._muovi_sulla_mappa(gioco)
        elif scelta == "10":
            self._interagisci_ambiente(gioco)
        elif scelta == "11":
            gioco.pop_stato()
        else:
            gioco.io.mostra_messaggio("Scelta non valida!")

        avanti(gioco)

    def _parla_con_npg(self, gioco):
        # Se abbiamo il gestore mappe, proviamo a usare la posizione
        if hasattr(gioco, "gestore_mappe") and gioco.giocatore.mappa_corrente:
            if npg_vicini := gioco.giocatore.ottieni_npg_vicini(
                gioco.gestore_mappe
            ):
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

        # Fallback al metodo originale
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
        if hasattr(gioco, "gestore_mappe") and gioco.giocatore.mappa_corrente:
            if npg_vicini := gioco.giocatore.ottieni_npg_vicini(
                gioco.gestore_mappe
            ):
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
                        conferma = gioco.io.richiedi_input(
                            f"Sei sicuro di voler attaccare {npg.nome}? (s/n): "
                        ).lower()
                        if conferma == "s":
                            from test_state.stati.combattimento import (
                                CombattimentoState,
                            )

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
                conferma = gioco.io.richiedi_input(
                    f"Sei sicuro di voler attaccare {npg_nome}? (s/n): "
                ).lower()
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
        if hasattr(gioco, "gestore_mappe") and gioco.giocatore.mappa_corrente:
            if oggetti_vicini := gioco.giocatore.ottieni_oggetti_vicini(
                gioco.gestore_mappe
            ):
                gioco.io.mostra_messaggio("\nOggetti nelle vicinanze:")
                oggetti_lista = []
                for pos, obj in oggetti_vicini.items():
                    oggetti_lista.append((pos, obj))
                    x, y = pos
                    gioco.io.mostra_messaggio(
                        f"{len(oggetti_lista)}. {obj.nome} [{obj.stato}] a ({x}, {y})"
                    )
                gioco.io.mostra_messaggio(f"{len(oggetti_lista) + 1}. Torna indietro")

                try:
                    scelta = int(
                        gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? ")
                    )
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
        gioco.io.mostra_messaggio("\nOggetti nel mercato:")
        for i, nome in enumerate(self.oggetti_interattivi.keys(), 1):
            oggetto = self.oggetti_interattivi[nome]
            gioco.io.mostra_messaggio(f"{i}. {oggetto.nome} [{oggetto.stato}]")
        gioco.io.mostra_messaggio(
            f"{len(self.oggetti_interattivi) + 1}. Torna indietro"
        )

        try:
            scelta = int(
                gioco.io.richiedi_input("\nCon quale oggetto vuoi interagire? ")
            )
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
        if not hasattr(gioco, "gestore_mappe"):
            gioco.io.mostra_messaggio("Sistema mappa non ancora implementato!")
            avanti(gioco)
            return

        # Importiamo localmente per evitare dipendenze circolari
        from test_state.stati.mappa_state import MappaState # type: ignore

        gioco.push_stato(MappaState(stato_origine=self))

    def _muovi_sulla_mappa(self, gioco):
        """Permette al giocatore di muoversi sulla mappa"""
        if not hasattr(gioco, "gestore_mappe") or not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema di movimento non disponibile!")
            avanti(gioco)
            return

        from test_state.stati.mappa_state import MappaState # type: ignore

        gioco.push_stato(MappaState(stato_origine=self))

    def _interagisci_ambiente(self, gioco):
        """Permette al giocatore di interagire con l'ambiente circostante"""
        if not hasattr(gioco, "gestore_mappe") or not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema di interazione non disponibile!")
            avanti(gioco)
            return

        # Usa direttamente lo stato mappa
        from test_state.stati.mappa_state import MappaState # type: ignore

        gioco.push_stato(MappaState(stato_origine=self))

from states.base_state import BaseState
from util.funzioni_utili import avanti


class MappaState(BaseState):
    def __init__(self, stato_origine=None):
        """
        Inizializza lo stato mappa.

        Args:
            stato_origine: Lo stato da cui proviene (es. TavernaState o MercatoState)
        """
        self.stato_origine = stato_origine
        self.mostra_leggenda = True

        # Direzioni di movimento
        self.direzioni = {
            "nord": (0, -1),
            "sud": (0, 1),
            "est": (1, 0),
            "ovest": (-1, 0),
        }

    def esegui(self, gioco):
        if not hasattr(gioco, "gestore_mappe") or not gioco.giocatore.mappa_corrente:
            gioco.io.mostra_messaggio("Sistema mappa non disponibile!")
            gioco.pop_stato()
            return

        mappa_corrente = gioco.gestore_mappe.ottieni_mappa(
            gioco.giocatore.mappa_corrente
        )
        nome_mappa = gioco.giocatore.mappa_corrente.upper()

        gioco.io.mostra_messaggio(f"\n=== MAPPA DI {nome_mappa} ===")

        # Visualizza la mappa
        rappresentazione = mappa_corrente.genera_rappresentazione_ascii(
            (gioco.giocatore.x, gioco.giocatore.y)
        )
        gioco.io.mostra_messaggio(rappresentazione)

        if self.mostra_leggenda:
            self._mostra_leggenda(gioco)

        # Mostra informazioni sulla posizione del giocatore
        gioco.io.mostra_messaggio(
            f"\nPosizione attuale: ({gioco.giocatore.x}, {gioco.giocatore.y})"
        )

        # Mostra menù interattivo
        gioco.io.mostra_messaggio("\nCosa vuoi fare?")
        gioco.io.mostra_messaggio("1. Muoviti")
        gioco.io.mostra_messaggio("2. Interagisci con l'ambiente")
        gioco.io.mostra_messaggio("3. Mostra elementi nelle vicinanze")
        gioco.io.mostra_messaggio("4. Mostra/nascondi leggenda")
        gioco.io.mostra_messaggio("5. Torna indietro")

        scelta = gioco.io.richiedi_input("\nScelta: ")

        if scelta == "1":
            self._muovi_giocatore(gioco)
        elif scelta == "2":
            self._interagisci_ambiente(gioco)
        elif scelta == "3":
            self._mostra_elementi_vicini(gioco)
        elif scelta == "4":
            self.mostra_leggenda = not self.mostra_leggenda
            gioco.io.mostra_messaggio(
                "Leggenda " + ("attivata" if self.mostra_leggenda else "disattivata")
            )
        elif scelta == "5":
            gioco.pop_stato()
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")

        avanti(gioco)

    def _mostra_leggenda(self, gioco):
        gioco.io.mostra_messaggio("\nLegenda:")
        gioco.io.mostra_messaggio("P = Giocatore")
        gioco.io.mostra_messaggio("N = NPC generico")
        gioco.io.mostra_messaggio("O = Oggetto generico")
        gioco.io.mostra_messaggio("D = Porta")
        gioco.io.mostra_messaggio("C = Baule")
        gioco.io.mostra_messaggio("L = Leva")
        gioco.io.mostra_messaggio("T = Trappola")
        gioco.io.mostra_messaggio("M = Mostro/Nemico")
        gioco.io.mostra_messaggio("# = Muro")
        gioco.io.mostra_messaggio(". = Spazio vuoto")
        # Aggiungi altri token speciali se necessario

    def _muovi_giocatore(self, gioco):
        gioco.io.mostra_messaggio("\n=== MOVIMENTO ===")
        gioco.io.mostra_messaggio("In quale direzione vuoi muoverti?")
        gioco.io.mostra_messaggio("1. Nord")
        gioco.io.mostra_messaggio("2. Sud")
        gioco.io.mostra_messaggio("3. Est")
        gioco.io.mostra_messaggio("4. Ovest")
        gioco.io.mostra_messaggio("5. Torna indietro")

        scelta = gioco.io.richiedi_input("\nScegli direzione: ")

        if scelta == "1":
            dx, dy = self.direzioni["nord"]
        elif scelta == "2":
            dx, dy = self.direzioni["sud"]
        elif scelta == "3":
            dx, dy = self.direzioni["est"]
        elif scelta == "4":
            dx, dy = self.direzioni["ovest"]
        elif scelta == "5":
            return
        else:
            gioco.io.mostra_messaggio("Direzione non valida.")
            return

        # Mappa corrente prima del movimento
        mappa_precedente = gioco.giocatore.mappa_corrente

        # Tenta di muovere il giocatore
        if gioco.giocatore.muovi(dx, dy, gioco.gestore_mappe):
            gioco.io.mostra_messaggio(
                f"Ti sei spostato verso {list(self.direzioni.keys())[list(self.direzioni.values()).index((dx, dy))]}"
            )

            # Controlla se c'è una porta per cambiare mappa
            mappa = gioco.gestore_mappe.ottieni_mappa(gioco.giocatore.mappa_corrente)

            # Se la mappa è cambiata dopo il movimento
            if mappa_precedente != gioco.giocatore.mappa_corrente:
                gioco.io.mostra_messaggio(
                    f"Hai attraversato una porta verso {gioco.giocatore.mappa_corrente}!"
                )

                # Gestione dello stato in base al cambio di mappa
                self._gestisci_cambio_mappa(
                    gioco, mappa_precedente, gioco.giocatore.mappa_corrente
                )
        else:
            gioco.io.mostra_messaggio("Non puoi muoverti in quella direzione!")

    def _gestisci_cambio_mappa(self, gioco, mappa_origine, mappa_destinazione):
        """Gestisce il cambio di stato in base al cambio di mappa"""
        # Se il cambio mappa implica il cambio di stato
        if (
            self.stato_origine is not None
            and hasattr(self.stato_origine, "__class__")
            and self.stato_origine.__class__.__name__ == "TavernaState"
            and mappa_destinazione == "mercato"
        ):

            # Chiedi se continuare a esplorare la nuova mappa
            continua = gioco.io.richiedi_input(
                "Vuoi continuare a esplorare la mappa? (s/n): "
            ).lower()
            if continua != "s":
                # Esci dallo stato mappa
                gioco.pop_stato()
                # Passa direttamente allo stato mercato
                from test_state.stati.mercato import MercatoState # type: ignore

                gioco.push_stato(MercatoState())

        elif (
            self.stato_origine is not None
            and hasattr(self.stato_origine, "__class__")
            and self.stato_origine.__class__.__name__ == "MercatoState"
            and mappa_destinazione == "taverna"
        ):

            # Chiedi se continuare a esplorare la nuova mappa
            continua = gioco.io.richiedi_input(
                "Vuoi continuare a esplorare la mappa? (s/n): "
            ).lower()
            if continua != "s":
                # Esci dallo stato mappa e dallo stato mercato
                gioco.pop_stato()  # Rimuove MappaState
                gioco.pop_stato()  # Rimuove MercatoState

    def _interagisci_ambiente(self, gioco):
        """Permette al giocatore di interagire con l'ambiente circostante"""
        gioco.io.mostra_messaggio("\n=== INTERAZIONE ===")
        gioco.io.mostra_messaggio("1. Interagisci con un oggetto nelle vicinanze")
        gioco.io.mostra_messaggio("2. Parla con un personaggio nelle vicinanze")
        gioco.io.mostra_messaggio("3. Esamina l'area")
        gioco.io.mostra_messaggio("4. Torna indietro")

        scelta = gioco.io.richiedi_input("\nScegli: ")

        if scelta == "1":
            if not gioco.giocatore.interagisci_con_oggetto_adiacente(
                gioco.gestore_mappe
            ):
                gioco.io.mostra_messaggio(
                    "Non ci sono oggetti con cui interagire nelle vicinanze."
                )
        elif scelta == "2":
            if not gioco.giocatore.interagisci_con_npg_adiacente(
                gioco.gestore_mappe, gioco
            ):
                gioco.io.mostra_messaggio(
                    "Non ci sono personaggi con cui parlare nelle vicinanze."
                )
        elif scelta == "3":
            self._esamina_area(gioco)
        elif scelta == "4":
            return
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")

    def _esamina_area(self, gioco):
        """Esamina l'area per trovare oggetti o personaggi"""
        gioco.io.mostra_messaggio("Esamini attentamente l'area circostante...")

        # Si potrebbe implementare una meccanica di scoperta di oggetti nascosti qui
        oggetti_vicini = gioco.giocatore.ottieni_oggetti_vicini(gioco.gestore_mappe, 2)
        npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe, 2)

        if oggetti_vicini or npg_vicini:
            gioco.io.mostra_messaggio("Noti alcune cose interessanti:")

            if oggetti_vicini:
                gioco.io.mostra_messaggio("\nOggetti:")
                for pos, obj in oggetti_vicini.items():
                    x, y = pos
                    gioco.io.mostra_messaggio(f"- {obj.nome} a ({x}, {y}) da te")

            if npg_vicini:
                gioco.io.mostra_messaggio("\nPersonaggi:")
                for pos, npg in npg_vicini.items():
                    x, y = pos
                    gioco.io.mostra_messaggio(f"- {npg.nome} a ({x}, {y}) da te")
        else:
            gioco.io.mostra_messaggio("Non noti nulla di particolare.")

    def _mostra_elementi_vicini(self, gioco):
        """Mostra oggetti e NPC nelle vicinanze"""
        oggetti_vicini = gioco.giocatore.ottieni_oggetti_vicini(gioco.gestore_mappe)
        npg_vicini = gioco.giocatore.ottieni_npg_vicini(gioco.gestore_mappe)

        if not oggetti_vicini and not npg_vicini:
            gioco.io.mostra_messaggio("Non ci sono elementi nelle vicinanze.")
            return

        gioco.io.mostra_messaggio("\n=== ELEMENTI NELLE VICINANZE ===")

        if oggetti_vicini:
            gioco.io.mostra_messaggio("\nOggetti:")
            for pos, obj in oggetti_vicini.items():
                x, y = pos
                gioco.io.mostra_messaggio(f"- {obj.nome} [{obj.stato}] a ({x}, {y})")

        if npg_vicini:
            gioco.io.mostra_messaggio("\nPersonaggi:")
            for pos, npg in npg_vicini.items():
                x, y = pos
                gioco.io.mostra_messaggio(f"- {npg.nome} a ({x}, {y})")

    def salva_stato_mappa(self, gioco):
        """Salva lo stato attuale della mappa"""
        # Implementazione per il salvataggio

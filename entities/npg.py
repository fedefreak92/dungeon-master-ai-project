from entities.giocatore import Giocatore
from items.oggetto import Oggetto
from entities.entita import Entita, ABILITA_ASSOCIATE

class NPG(Entita):
    def __init__(self, nome, token="N"):
        # Chiamiamo il costruttore della classe base
        super().__init__(nome, hp=10, hp_max=10, forza_base=13, difesa=1, token=token)
        
        # Attributi specifici per NPG
        self.stato_corrente = "default"
        self.background = ""
        self.professione = ""
        
        # Inizializzazioni specifiche per NPG
        self._inizializza_attributi()
        self.conversazioni = self._inizializza_conversazioni()
        
    def _inizializza_attributi(self):
        """Inizializza attributi specifici per ogni NPG"""
        if self.nome == "Durnan":
            self.hp_max = 30
            self.hp = self.hp_max
            self.oro = 500
            self.forza_base = 16  # Valore base della forza (equivalente a mod +3)
            self.difesa = 4
            self.livello = 3
            
            # Ricalcola il modificatore
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            
            # Oggetti nell'inventario
            spada_taverna = Oggetto("Spada del taverniere", "arma", {"forza": 2}, 80, "Una spada ben tenuta")
            armatura_taverna = Oggetto("Gilet di cuoio robusto", "armatura", {"difesa": 2}, 60, "Un gilet di cuoio rinforzato")
            
            self.inventario = [
                spada_taverna,
                armatura_taverna,
                Oggetto("Chiave della cantina", "chiave", {}, 50, "Una vecchia chiave arrugginita"),
                Oggetto("Mazzo di carte", "comune", {}, 5, "Un mazzo di carte da gioco"),
                Oggetto("Pozione di cura", "cura", {"cura": 10}, 10, "Recupera 10 HP")
            ]
            
            # Equipaggia arma e armatura
            self.arma = spada_taverna
            self.armatura = armatura_taverna
            
            self.background = "Proprietario della taverna, ex-avventuriero"
            self.professione = "Taverniere"
        elif self.nome == "Elminster":
            self.hp_max = 50
            self.hp = self.hp_max
            self.oro = 1000
            self.forza_base = 14  # Valore base della forza (equivalente a mod +2)
            self.intelligenza_base = 18  # Alto valore base di intelligenza
            self.difesa = 3
            self.livello = 8
            
            # Ricalcola i modificatori
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            self.modificatore_intelligenza = self.calcola_modificatore(self.intelligenza_base)
            
            # Oggetti specifici
            bastone = Oggetto("Bastone magico", "arma", {"forza": 5}, 200, "Un potente bastone magico")
            veste = Oggetto("Veste arcana", "armatura", {"difesa": 4}, 300, "Una veste intessuta di magia protettiva")
            anello = Oggetto("Anello dell'invisibilità", "accessorio", {"invisibilità": 1}, 700, "Rende parzialmente invisibili")
            
            self.inventario = [
                bastone,
                veste,
                anello,
                Oggetto("Grimorio arcano", "magico", {}, 500, "Un libro di incantesimi")
            ]
            
            # Equipaggia
            self.arma = bastone
            self.armatura = veste
            self.accessori.append(anello)
            
            self.background = "Arcimago di fama mondiale, consigliere dei Lord di Waterdeep"
            self.professione = "Mago"
        elif self.nome == "Mirt":
            self.hp_max = 25
            self.hp = self.hp_max
            self.oro = 2000
            self.forza_base = 15  # Valore base della forza (equivalente a mod +2)
            self.destrezza_base = 14  # Buona destrezza
            self.difesa = 3
            self.livello = 4
            
            # Ricalcola i modificatori
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            self.modificatore_destrezza = self.calcola_modificatore(self.destrezza_base)
            
            # Oggetti specifici
            pugnale = Oggetto("Pugnale avvelenato", "arma", {"forza": 3, "veleno": 2}, 150, "Un pugnale con lama avvelenata")
            gilet = Oggetto("Gilet di pelle", "armatura", {"difesa": 2}, 100, "Un gilet di pelle scura")
            
            self.inventario = [
                pugnale,
                gilet,
                Oggetto("Contratto segreto", "missione", {}, 0, "Un contratto con sigillo sconosciuto"),
                Oggetto("Mappa del sottosuolo", "missione", {}, 50, "Una mappa dei sotterranei della città")
            ]
            
            # Equipaggia
            self.arma = pugnale
            self.armatura = gilet
            
            self.background = "Ex-mercenario, ora commerciante con legami oscuri"
            self.professione = "Mercante"
        elif self.nome == "Araldo":
            self.hp_max = 15
            self.hp = self.hp_max
            self.oro = 300
            self.forza_base = 14  # Valore base della forza (equivalente a mod +2)
            self.difesa = 2
            self.livello = 2
            
            # Ricalcola il modificatore
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            
            # Oggetti specifici
            spada = Oggetto("Spada corta", "arma", {"forza": 2}, 25, "Una spada corta ben bilanciata")
            cotta = Oggetto("Cotta di maglia", "armatura", {"difesa": 2}, 35, "Una cotta di maglia resistente")
            
            self.inventario = [
                spada,
                Oggetto("Arco lungo", "arma", {"forza": 3}, 40, "Un arco lungo di legno flessibile"),
                cotta
            ]
            
            # Equipaggia
            self.arma = spada
            self.armatura = cotta
            
            self.background = "Ex soldato, ora commerciante di armi"
            self.professione = "Armaiolo"
        elif self.nome == "Violetta":
            self.hp_max = 12
            self.hp = self.hp_max
            self.oro = 450
            self.forza_base = 8  # Valore base basso della forza (equivalente a mod -1)
            self.intelligenza_base = 14  # Buona intelligenza
            self.difesa = 1
            self.livello = 2
            
            # Ricalcola i modificatori
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            self.modificatore_intelligenza = self.calcola_modificatore(self.intelligenza_base)
            
            # Oggetti specifici
            bastone = Oggetto("Bastone da erborista", "arma", {"forza": 1}, 10, "Un bastone di legno per raccogliere erbe")
            veste = Oggetto("Veste da erborista", "armatura", {"difesa": 1}, 15, "Una veste leggera da lavoro")
            
            self.inventario = [
                bastone,
                veste,
                Oggetto("Pozione di cura", "cura", {"cura": 10}, 15, "Recupera 10 HP"),
                Oggetto("Antidoto", "cura", {"antidoto": 1}, 20, "Cura avvelenamento"),
                Oggetto("Erbe medicinali", "cura_leggera", {"cura_leggera": 5}, 8, "Leggero recupero di HP"),
                Oggetto("Balsamo curativo", "cura_grave", {"cura_grave": 15}, 25, "Forte recupero di HP")
            ]
            
            # Equipaggia
            self.arma = bastone
            self.armatura = veste
            
            self.background = "Erborista di fama locale"
            self.professione = "Erborista"
        elif self.nome == "Gundren":
            self.hp_max = 20
            self.hp = self.hp_max
            self.oro = 800
            self.forza_base = 14  # Valore base della forza (equivalente a mod +2)
            self.costituzione_base = 16  # Alta costituzione (tipica dei nani)
            self.difesa = 2
            self.livello = 3
            
            # Ricalcola i modificatori
            self.modificatore_forza = self.calcola_modificatore(self.forza_base)
            self.modificatore_costituzione = self.calcola_modificatore(self.costituzione_base)
            
            # Oggetti specifici
            martello = Oggetto("Martello da minatore", "arma", {"forza": 2}, 30, "Un martello pesante da minatore")
            corazza = Oggetto("Corazza decorata", "armatura", {"difesa": 2}, 65, "Una corazza decorata con motivi nanici")
            amuleto = Oggetto("Amuleto antico", "accessorio", {"difesa": 1}, 60, "Un amuleto che protegge dai danni")
            
            self.inventario = [
                martello,
                corazza,
                amuleto,
                Oggetto("Gemma di rubino", "prezioso", {}, 100, "Una gemma rossa brillante"),
                Oggetto("Pergamena magica", "magico", {}, 50, "Una pergamena con antichi simboli"),
                Oggetto("Anello d'oro", "accessorio", {"fortuna": 1}, 45, "Un semplice anello d'oro")
            ]
            
            # Equipaggia
            self.arma = martello
            self.armatura = corazza
            self.accessori.append(amuleto)
            
            self.background = "Nano mercante di gemme e oggetti rari"
            self.professione = "Gioielliere"
        
    def _inizializza_conversazioni(self):
        """Inizializza le conversazioni specifiche per ogni NPG"""
        if self.nome == "Durnan":
            return {
                "inizio": {
                    "testo": "Salve viaggiatore, cosa ti porta qui? Vedo che porti molte cicatrici, sei nel posto giusto per recuperare le energie.",
                    "opzioni": [
                        ("Vorrei una stanza per riposare", "riposo"),
                        ("Raccontami della taverna", "storia"),
                        ("Hai sentito voci interessanti?", "voci"),
                        ("Chi sei veramente?", "info"),
                        ("Posso acquistare una pozione?", "vendita_pozione"),
                        ("Arrivederci", None)
                    ]
                },
                "riposo": {
                    "testo": "La stanza è pronta per te. Riposa bene, avventuriero.",
                    "effetto": "riposo",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "storia": {
                    "testo": "Mio nonno era un grande avventuriero, proprio come te. Ha fondato questa taverna per dare un rifugio sicuro a chi viaggia per il mondo.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "voci": {
                    "testo": "Se decidi di esplorare i sotterranei, fai attenzione. Non tutti quelli che ci sono entrati sono tornati.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "info": {
                    "testo": f"Sono {self.background}. Ora gestisco questa taverna con {self.oro} monete d'oro di capitale e qualche oggetto interessante.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "vendita_pozione": {
                    "testo": "Ho una pozione di cura che potrebbe interessarti. Costa 10 monete d'oro.",
                    "opzioni": [
                        ("La compro", "acquista_pozione"),
                        ("Troppo costosa", "inizio")
                    ]
                },
                "acquista_pozione": {
                    "testo": "Eccoti la pozione. Usala con saggezza!",
                    "effetto": {
                        "tipo": "scambio",
                        "oggetto": "Pozione di cura",
                        "costo": 10
                    },
                    "opzioni": [("Grazie", "inizio")]
                }
            }
        elif self.nome == "Elminster":
            return {
                "inizio": {
                    "testo": "Ah, un altro avventuriero. Gli Elmi Lucenti mi hanno parlato di te.",
                    "opzioni": [
                        ("Mi parli della magia?", "magia"),
                        ("Avete bisogno del mio aiuto?", "aiuto"),
                        ("Chi sei veramente?", "info"),
                        ("Arrivederci", None)
                    ]
                },
                "magia": {
                    "testo": "Se vuoi apprendere la magia, cerca il mio amico alla Gilda dei Maghi.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "aiuto": {
                    "testo": "Potrei affidarti una missione importante, se sei interessato.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "info": {
                    "testo": f"Sono {self.background}. Ho con me {self.oro} monete d'oro e alcuni oggetti magici potenti.",
                    "opzioni": [("Torna indietro", "inizio")]
                }
            }
        elif self.nome == "Mirt":
            return {
                "inizio": {
                    "testo": "*Alza lo sguardo dalla sua birra* Sei nuovo da queste parti, eh?",
                    "opzioni": [
                        ("Cerco lavoro", "lavoro"),
                        ("Chi sei?", "identita"),
                        ("Posso vedere cosa vendi?", "commercio"),
                        ("Arrivederci", None)
                    ]
                },
                "lavoro": {
                    "testo": "Torna più tardi, avrò i dettagli pronti.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "identita": {
                    "testo": f"Sono {self.background}. Ho {self.oro} monete d'oro, ma non portarle via.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "commercio": {
                    "testo": f"Do un'occhiata... ho con me {', '.join([item.nome for item in self.inventario])}. Ti interessa qualcosa?",
                    "opzioni": [("Forse più tardi", "inizio")]
                }
            }
        elif self.nome == "Araldo":
            return {
                "inizio": {
                    "testo": "Benvenuto alla mia armeria! Ho le migliori armi di Waterdeep. Cosa ti serve oggi?",
                    "opzioni": [
                        ("Voglio vedere le tue armi", "mostra_armi"),
                        ("Hai qualche affare speciale?", "affare"),
                        ("Chi sei?", "info"),
                        ("Arrivederci", None)
                    ]
                },
                "mostra_armi": {
                    "testo": f"Certo! Ho {', '.join([item.nome for item in self.inventario])}. Tutte di ottima qualità!",
                    "opzioni": [
                        ("Quanto costa la spada?", "prezzo_spada"),
                        ("Torna indietro", "inizio")
                    ]
                },
                "prezzo_spada": {
                    "testo": "Per te, solo 25 monete d'oro. È un affare!",
                    "opzioni": [
                        ("La compro", "acquista_spada"),
                        ("Troppo costosa", "inizio")
                    ]
                },
                "acquista_spada": {
                    "testo": "Una scelta eccellente! Questa spada ti servirà bene.",
                    "effetto": {
                        "tipo": "scambio",
                        "oggetto": "Spada corta",
                        "costo": 25
                    },
                    "opzioni": [("Grazie", "inizio")]
                },
                "affare": {
                    "testo": "Hmm, potrei avere qualcosa di speciale nel retro... Torna più tardi.",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "info": {
                    "testo": f"Sono {self.background}. Ho combattuto in molte battaglie prima di aprire questo negozio.",
                    "opzioni": [("Torna indietro", "inizio")]
                }
            }
        elif self.nome == "Violetta":
            return {
                "inizio": {
                    "testo": "Salve, viaggiatore. Benvenuto nella mia erboristeria. Hai bisogno di cure?",
                    "opzioni": [
                        ("Che pozioni hai?", "pozioni"),
                        ("Sono ferito, puoi aiutarmi?", "cura"),
                        ("Chi sei?", "info"),
                        ("Arrivederci", None)
                    ]
                },
                "pozioni": {
                    "testo": f"Preparo tutte le mie pozioni personalmente. Ho {', '.join([item.nome for item in self.inventario])}.",
                    "opzioni": [
                        ("Quanto costa una pozione di cura?", "prezzo_pozione"),
                        ("Torna indietro", "inizio")
                    ]
                },
                "prezzo_pozione": {
                    "testo": "Una pozione di cura costa 15 monete d'oro. Funziona immediatamente!",
                    "opzioni": [
                        ("La compro", "acquista_pozione_violetta"),
                        ("Troppo costosa", "inizio")
                    ]
                },
                "acquista_pozione_violetta": {
                    "testo": "Ecco la tua pozione, preparata con le migliori erbe.",
                    "effetto": {
                        "tipo": "scambio",
                        "oggetto": "Pozione di cura",
                        "costo": 15
                    },
                    "opzioni": [("Grazie", "inizio")]
                },
                "cura": {
                    "testo": "Posso darti un unguento per le tue ferite per 5 monete d'oro.",
                    "effetto": "cura_leggera",
                    "opzioni": [("Torna indietro", "inizio")]
                },
                "info": {
                    "testo": f"Sono {self.background} e {self.professione}. La mia famiglia cura le persone di questa città da generazioni.",
                    "opzioni": [("Torna indietro", "inizio")]
                }
            }
        elif self.nome == "Gundren":
            return {
                "inizio": {
                    "testo": "*Guarda attraverso una lente* Hmm? Oh, benvenuto! Cerchi gioielli o altre rarità?",
                    "opzioni": [
                        ("Mostrami i tuoi oggetti", "mostra_oggetti"),
                        ("Cerco qualcosa di magico", "magia"),
                        ("Chi sei?", "info"),
                        ("Arrivederci", None)
                    ]
                },
                "mostra_oggetti": {
                    "testo": f"*Con orgoglio* Guarda che meraviglie! Ho {', '.join([item.nome for item in self.inventario])}.",
                    "opzioni": [
                        ("Quanto costa la gemma di rubino?", "prezzo_gemma"),
                        ("Torna indietro", "inizio")
                    ]
                },
                "prezzo_gemma": {
                    "testo": "Questa? *La fa brillare alla luce* 100 monete d'oro, non un pezzo in meno!",
                    "opzioni": [
                        ("La compro", "acquista_gemma"),
                        ("Troppo costosa", "inizio")
                    ]
                },
                "acquista_gemma": {
                    "testo": "*Sorride soddisfatto* Hai buon gusto! Questa gemma è davvero rara.",
                    "effetto": {
                        "tipo": "scambio",
                        "oggetto": "Gemma di rubino",
                        "costo": 100
                    },
                    "opzioni": [("Grazie", "inizio")]
                },
                "magia": {
                    "testo": "*Abbassa la voce* Ho questa pergamena magica... ma costa 50 monete d'oro.",
                    "opzioni": [
                        ("La compro", "acquista_pergamena"),
                        ("Troppo costosa", "inizio")
                    ]
                },
                "acquista_pergamena": {
                    "testo": "*Guarda intorno furtivamente* Usala con saggezza, contiene un potere antico.",
                    "effetto": {
                        "tipo": "scambio",
                        "oggetto": "Pergamena magica",
                        "costo": 50
                    },
                    "opzioni": [("Grazie", "inizio")]
                },
                "info": {
                    "testo": f"*Si gonfia il petto* Sono {self.background}. La mia famiglia scava nelle miniere di Gauntlgrym da generazioni.",
                    "opzioni": [("Torna indietro", "inizio")]
                }
            }
        else:
            return {
                "inizio": {
                    "testo": "Salve, sono un abitante di questa città.",
                    "opzioni": [("Arrivederci", None)]
                }
            }

    def cambia_stato(self, nuovo_stato):
        """
        Cambia lo stato del personaggio
        
        Args:
            nuovo_stato (str): Il nuovo stato del personaggio
        """
        self.stato_corrente = nuovo_stato

    def ottieni_conversazione(self, stato="inizio"):
        """
        Ottiene i dati della conversazione per lo stato specificato
        
        Args:
            stato (str): Lo stato della conversazione
            
        Returns:
            dict: Dati della conversazione o None se non esiste
        """
        return self.conversazioni.get(stato)
        
    def mostra_info(self):
        """
        Mostra le informazioni dell'NPG
        
        Returns:
            str: Informazioni formattate dell'NPG
        """
        info = f"=== {self.nome} ===\n"
        info += f"Professione: {self.professione}\n"
        info += f"Background: {self.background}\n"
        info += f"HP: {self.hp}/{self.hp_max}\n"
        info += f"Oro: {self.oro}\n"
        info += "Inventario:\n"
        for item in self.inventario:
            info += f"- {item.nome} ({item.tipo}): {item.descrizione}\n"
        return info

    def attacca(self, bersaglio, gioco=None):
        """Override del metodo attacca per retrocompatibilità"""
        # Prima prova a usare l'implementazione base
        if hasattr(bersaglio, 'subisci_danno'):
            return super().attacca(bersaglio)
        
        # Altrimenti usa il vecchio codice
        danno = self.forza 
        if gioco:
            gioco.io.mostra_messaggio(f"{self.nome} attacca {bersaglio.nome} e infligge {danno} danni!")
        
        if hasattr(bersaglio, 'ferisci'):
            bersaglio.ferisci(danno)
        else:
            bersaglio.hp -= danno

    def trasferisci_oro(self, giocatore, quantita):
        """
        Trasferisce oro dall'NPG al giocatore
        
        Args:
            giocatore (Giocatore): Il giocatore che riceve l'oro
            quantita (int): Quantità di oro da trasferire
            
        Returns:
            bool: True se il trasferimento è riuscito, False se l'NPG non ha abbastanza oro
        """
        if self.oro >= quantita:
            self.oro -= quantita
            giocatore.aggiungi_oro(quantita)
            return True
        return False

    def to_dict(self):
        """
        Converte l'NPG in un dizionario per la serializzazione.
        
        Returns:
            dict: Rappresentazione dell'NPG in formato dizionario
        """
        # Ottieni il dizionario base dalla classe genitore
        data = super().to_dict()
        
        # Aggiungi attributi specifici di NPG
        data.update({
            "stato_corrente": self.stato_corrente,
            "background": self.background,
            "professione": self.professione,
            # Le conversazioni non vengono serializzate perché vengono generate dinamicamente
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di NPG da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dell'NPG
            
        Returns:
            NPG: Nuova istanza di NPG
        """
        # Creiamo prima un'istanza di NPG con solo nome e token
        # evitando di passare hp e altri parametri che vengono gestiti in _inizializza_attributi
        npg = cls(
            nome=data.get("nome", "Sconosciuto"),
            token=data.get("token", "N")
        )
        
        # Impostiamo manualmente gli attributi che sono stati serializzati
        npg.hp = data.get("hp", 10)
        npg.hp_max = data.get("hp_max", 10)
        npg.x = data.get("x", 0)
        npg.y = data.get("y", 0)
        npg.mappa_corrente = data.get("mappa_corrente")
        npg.abilita_competenze = data.get("abilita_competenze", {})
        npg.bonus_competenza = data.get("bonus_competenza", 2)
        npg.oro = data.get("oro", 0)
        npg.esperienza = data.get("esperienza", 0)
        npg.livello = data.get("livello", 1)
        npg.difesa = data.get("difesa", 0)
        
        # Impostiamo i valori base che sono stati serializzati
        npg.forza_base = data.get("forza_base", 10)
        npg.destrezza_base = data.get("destrezza_base", 10)
        npg.costituzione_base = data.get("costituzione_base", 10)
        npg.intelligenza_base = data.get("intelligenza_base", 10)
        npg.saggezza_base = data.get("saggezza_base", 10)
        npg.carisma_base = data.get("carisma_base", 10)
        
        # Ricalcoliamo i modificatori
        npg.modificatore_forza = npg.calcola_modificatore(npg.forza_base)
        npg.modificatore_destrezza = npg.calcola_modificatore(npg.destrezza_base)
        npg.modificatore_costituzione = npg.calcola_modificatore(npg.costituzione_base)
        npg.modificatore_intelligenza = npg.calcola_modificatore(npg.intelligenza_base)
        npg.modificatore_saggezza = npg.calcola_modificatore(npg.saggezza_base)
        npg.modificatore_carisma = npg.calcola_modificatore(npg.carisma_base)
        
        # Imposta attributi specifici
        npg.stato_corrente = data.get("stato_corrente", "default")
        npg.background = data.get("background", "")
        npg.professione = data.get("professione", "")
        
        # Le conversazioni vengono reinizializzate
        npg.conversazioni = npg._inizializza_conversazioni()
        
        return npg

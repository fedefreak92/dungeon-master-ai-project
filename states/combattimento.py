from states.base_state import BaseState
from entities.nemico import Nemico
from entities.giocatore import Giocatore
from entities.npg import NPG
from util.dado import Dado

class CombattimentoState(BaseState):
    def __init__(self, nemico=None, npg_ostile=None):
        """
        Inizializza lo stato di combattimento.
        
        Args:
            nemico (Nemico, optional): Un nemico tradizionale
            npg_ostile (NPG, optional): Un NPG diventato ostile
        """
        self.nemico = nemico
        self.npg_ostile = npg_ostile
        self.turno = 1
        self.avversario = nemico if nemico else npg_ostile
        # Inizializza i dadi per vari tiri durante il combattimento
        self.dado_d20 = Dado(20)
        self.dado_d100 = Dado(100)
        # Aggiungiamo la fase per gestire il flusso asincrono
        self.fase = "scelta"
        # Per memorizzare eventuali dati temporanei tra le fasi
        self.dati_temporanei = {}
        
    def esegui(self, gioco):
        giocatore = gioco.giocatore
        
        # Mostra le statistiche del combattimento in ogni fase
        self._mostra_stato_combattimento(giocatore, gioco)
        
        # Controlla se il combattimento è finito
        if self._controlla_fine_combattimento(gioco):
            return
            
        # Gestisce il flusso in base alla fase corrente
        if self.fase == "scelta":
            self._fase_scelta(giocatore, gioco)
        elif self.fase == "esegui_azione":
            self._fase_esegui_azione(giocatore, gioco)
        elif self.fase == "attacco_nemico":
            self._fase_attacco_nemico(giocatore, gioco)
        elif self.fase == "fine_turno":
            self._fase_fine_turno(giocatore, gioco)
        elif self.fase == "usa_oggetto":
            self._fase_usa_oggetto(giocatore, gioco)
        elif self.fase == "cambia_equipaggiamento":
            self._fase_cambia_equipaggiamento(giocatore, gioco)

    def _fase_scelta(self, giocatore, gioco):
        """Fase di scelta dell'azione"""
        # Chiedi l'azione al giocatore
        gioco.io.mostra_messaggio("\nCosa vuoi fare?")
        gioco.io.mostra_messaggio("1. Attacca")
        gioco.io.mostra_messaggio("2. Usa oggetto")
        gioco.io.mostra_messaggio("3. Cambia equipaggiamento")
        gioco.io.mostra_messaggio("4. Fuggi")
        
        # Ottiene il comando dall'input (già impostato dal sistema web)
        gioco.io.richiedi_input("Scelta: ")
        
        # Passa alla fase successiva
        self.fase = "esegui_azione"
    
    def _fase_esegui_azione(self, giocatore, gioco):
        """Fase di esecuzione dell'azione scelta"""
        scelta_input = gioco.io.ultimo_input
        
        # Funzione per elaborare i comandi testuali
        def elabora_comando_combattimento(cmd):
            cmd = cmd.lower().strip()
            
            # Mappatura comandi di testo alle azioni
            if any(x in cmd for x in ["attacca", "colpisco", "1"]):
                return "1"
            elif any(x in cmd for x in ["usa", "oggetto", "pozione", "2"]):
                return "2"
            elif any(x in cmd for x in ["cambia", "equipaggiamento", "arma", "3"]):
                return "3"
            elif any(x in cmd for x in ["fuggi", "fuga", "scappa", "4"]):
                return "4"
            else:
                return None
        
        # Elabora il comando testuale o numerico
        if scelta_input.isdigit() and scelta_input in ["1", "2", "3", "4"]:
            scelta = scelta_input
        else:
            scelta = elabora_comando_combattimento(scelta_input)
        
        if scelta == "1":
            self._gestisci_attacco(giocatore, gioco)
            # Passa alla fase di attacco nemico se l'avversario è ancora vivo
            if self.avversario.hp > 0:
                self.fase = "attacco_nemico"
            else:
                self.fase = "fine_turno"
        elif scelta == "2":
            self.fase = "usa_oggetto"
            self.dati_temporanei.clear()
            return
        elif scelta == "3":
            self.fase = "cambia_equipaggiamento"
            self.dati_temporanei.clear()
            return
        elif scelta == "4":
            self._tenta_fuga(gioco)
            if gioco.stato_corrente() == self:  # Se non siamo usciti dallo stato
                # Passa alla fase di attacco nemico se l'avversario è ancora vivo
                if self.avversario.hp > 0:
                    self.fase = "attacco_nemico"
                else:
                    self.fase = "fine_turno"
        else:
            gioco.io.mostra_messaggio(f"Azione non valida: '{scelta_input}'!")
            self.fase = "scelta"  # Torna alla fase di scelta
    
    def _fase_attacco_nemico(self, giocatore, gioco):
        """Fase di attacco dell'avversario"""
        self._attacco_nemico(giocatore, gioco)
        self.fase = "fine_turno"
    
    def _fase_fine_turno(self, giocatore, gioco):
        """Fase di fine turno"""
        # Incrementa il turno
        self.turno += 1
        # Torna alla fase di scelta per il prossimo turno
        self.fase = "scelta"
        
    def _fase_usa_oggetto(self, giocatore, gioco):
        """Fase per l'uso di oggetti"""
        if not giocatore.inventario:
            gioco.io.mostra_messaggio("\nNon hai nessun oggetto da usare!")
            self.fase = "scelta"
            return
            
        if "mostra_inventario" not in self.dati_temporanei:
            # Prima chiamata: mostra l'inventario
            gioco.io.mostra_messaggio("\nQuale oggetto vuoi usare?")
            for i, item in enumerate(giocatore.inventario, 1):
                gioco.io.mostra_messaggio(f"{i}. {item}")
            gioco.io.mostra_messaggio(f"{len(giocatore.inventario) + 1}. Annulla")
            
            self.dati_temporanei["mostra_inventario"] = True
            gioco.io.richiedi_input("\nScegli: ")
            return
        
        # Seconda chiamata: elabora la scelta
        try:
            scelta = int(gioco.io.ultimo_input)
            if 1 <= scelta <= len(giocatore.inventario):
                item = giocatore.inventario[scelta - 1]
                
                # Usa il metodo usa dell'oggetto
                if hasattr(item, 'usa'):
                    item.usa(giocatore)
                else:
                    # Retrocompatibilità con stringhe
                    self._applica_effetto_oggetto(giocatore, item, gioco)
            elif scelta == len(giocatore.inventario) + 1:
                # Annulla
                self.fase = "scelta"
                self.dati_temporanei.clear()
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self.fase = "scelta"
                self.dati_temporanei.clear()
                return
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
            self.fase = "scelta"
            self.dati_temporanei.clear()
            return
            
        # Pulisci i dati temporanei
        self.dati_temporanei.clear()
        
        # Passa alla fase di attacco nemico se l'avversario è ancora vivo
        if self.avversario.hp > 0:
            self.fase = "attacco_nemico"
        else:
            self.fase = "fine_turno"
    
    def _fase_cambia_equipaggiamento(self, giocatore, gioco):
        """Fase per il cambio di equipaggiamento"""
        if "fase_equip" not in self.dati_temporanei:
            # Prima chiamata: mostra le opzioni
            gioco.io.mostra_messaggio("\nCosa vuoi cambiare?")
            gioco.io.mostra_messaggio("1. Arma")
            gioco.io.mostra_messaggio("2. Armatura")
            gioco.io.mostra_messaggio("3. Accessorio")
            gioco.io.mostra_messaggio("4. Annulla")
            
            self.dati_temporanei["fase_equip"] = "scelta_tipo"
            gioco.io.richiedi_input("Scelta: ")
            return
        
        if self.dati_temporanei["fase_equip"] == "scelta_tipo":
            # Elabora la scelta del tipo di equipaggiamento
            scelta = gioco.io.ultimo_input
            
            if scelta == "1":
                self.dati_temporanei["tipo_equip"] = "arma"
                # Filtra le armi dall'inventario
                armi = [item for item in giocatore.inventario 
                       if not isinstance(item, str) and hasattr(item, 'tipo') and item.tipo == "arma"]
                
                if not armi:
                    gioco.io.mostra_messaggio("\nNon hai altre armi nell'inventario!")
                    self.dati_temporanei.clear()
                    self.fase = "scelta"
                    return
                
                gioco.io.mostra_messaggio("\nQuale arma vuoi equipaggiare?")
                for i, arma in enumerate(armi, 1):
                    bonus = f" (Forza +{arma.effetto.get('forza', 0)})" if hasattr(arma, 'effetto') else ""
                    gioco.io.mostra_messaggio(f"{i}. {arma.nome}{bonus}")
                gioco.io.mostra_messaggio(f"{len(armi) + 1}. Annulla")
                
                self.dati_temporanei["items"] = armi
                self.dati_temporanei["fase_equip"] = "scelta_item"
                gioco.io.richiedi_input("\nScegli: ")
                return
                
            elif scelta == "2":
                self.dati_temporanei["tipo_equip"] = "armatura"
                # Filtra le armature dall'inventario
                armature = [item for item in giocatore.inventario 
                           if not isinstance(item, str) and hasattr(item, 'tipo') and item.tipo == "armatura"]
                
                if not armature:
                    gioco.io.mostra_messaggio("\nNon hai altre armature nell'inventario!")
                    self.dati_temporanei.clear()
                    self.fase = "scelta"
                    return
                
                gioco.io.mostra_messaggio("\nQuale armatura vuoi equipaggiare?")
                for i, armatura in enumerate(armature, 1):
                    bonus = f" (Difesa +{armatura.effetto.get('difesa', 0)})" if hasattr(armatura, 'effetto') else ""
                    gioco.io.mostra_messaggio(f"{i}. {armatura.nome}{bonus}")
                gioco.io.mostra_messaggio(f"{len(armature) + 1}. Annulla")
                
                self.dati_temporanei["items"] = armature
                self.dati_temporanei["fase_equip"] = "scelta_item"
                gioco.io.richiedi_input("\nScegli: ")
                return
                
            elif scelta == "3":
                self.dati_temporanei["tipo_equip"] = "accessorio"
                # Filtra gli accessori dall'inventario
                accessori = [item for item in giocatore.inventario 
                            if not isinstance(item, str) and hasattr(item, 'tipo') and item.tipo == "accessorio"]
                
                if not accessori:
                    gioco.io.mostra_messaggio("\nNon hai altri accessori nell'inventario!")
                    self.dati_temporanei.clear()
                    self.fase = "scelta"
                    return
                
                gioco.io.mostra_messaggio("\nQuale accessorio vuoi equipaggiare?")
                for i, accessorio in enumerate(accessori, 1):
                    bonus = ""
                    if hasattr(accessorio, 'effetto'):
                        bonus = " ("
                        for stat, val in accessorio.effetto.items():
                            bonus += f"{stat.capitalize()} +{val}, "
                        bonus = bonus[:-2] + ")"
                    gioco.io.mostra_messaggio(f"{i}. {accessorio.nome}{bonus}")
                gioco.io.mostra_messaggio(f"{len(accessori) + 1}. Annulla")
                
                self.dati_temporanei["items"] = accessori
                self.dati_temporanei["fase_equip"] = "scelta_item"
                gioco.io.richiedi_input("\nScegli: ")
                return
                
            elif scelta == "4":
                # Annulla
                self.dati_temporanei.clear()
                self.fase = "scelta"
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
                self.dati_temporanei.clear()
                self.fase = "scelta"
                return
                
        elif self.dati_temporanei["fase_equip"] == "scelta_item":
            # Elabora la scelta dell'item
            items = self.dati_temporanei.get("items", [])
            
            try:
                scelta = int(gioco.io.ultimo_input)
                if 1 <= scelta <= len(items):
                    item = items[scelta - 1]
                    item.equipaggia(giocatore)
                    gioco.io.mostra_messaggio(f"\nHai equipaggiato {item.nome}!")
                elif scelta == len(items) + 1:
                    # Annulla
                    pass
                else:
                    gioco.io.mostra_messaggio("Scelta non valida.")
            except ValueError:
                gioco.io.mostra_messaggio("Devi inserire un numero.")
            
            # Pulisci i dati temporanei e passa alla fase successiva
            self.dati_temporanei.clear()
            
            # Passa alla fase di attacco nemico se l'avversario è ancora vivo
            if self.avversario.hp > 0:
                self.fase = "attacco_nemico"
            else:
                self.fase = "fine_turno"
                
    def _mostra_stato_combattimento(self, giocatore, gioco):
        """Mostra lo stato attuale del combattimento"""
        gioco.io.mostra_messaggio("\n" + "="*60)
        gioco.io.mostra_messaggio(f"COMBATTIMENTO: {giocatore.nome} vs {self.avversario.nome}")
        gioco.io.mostra_messaggio(f"Turno: {self.turno}")
        gioco.io.mostra_messaggio(f"HP {giocatore.nome}: {giocatore.hp}/{giocatore.hp_max} | HP {self.avversario.nome}: {self.avversario.hp}/{self.avversario.hp_max}")
        
        # Mostra anche l'equipaggiamento attuale
        arma = giocatore.arma if isinstance(giocatore.arma, str) else (giocatore.arma.nome if giocatore.arma else "Nessuna")
        armatura = giocatore.armatura if isinstance(giocatore.armatura, str) else (giocatore.armatura.nome if giocatore.armatura else "Nessuna")
        
        # Gestione degli accessori
        accessori_nomi = []
        for acc in giocatore.accessori:
            if isinstance(acc, str):
                accessori_nomi.append(acc)
            else:
                accessori_nomi.append(acc.nome)
        accessori = ", ".join(accessori_nomi) if accessori_nomi else "Nessuno"
        
        gioco.io.mostra_messaggio(f"Arma: {arma} | Armatura: {armatura} | Accessori: {accessori}")
        gioco.io.mostra_messaggio(f"Forza: {giocatore.forza} | Difesa: {giocatore.difesa}")
        gioco.io.mostra_messaggio("="*60)
        
    def _controlla_fine_combattimento(self, gioco):
        """Controlla se il combattimento è finito"""
        giocatore = gioco.giocatore
        
        if giocatore.hp <= 0:
            gioco.io.mostra_messaggio(f"\n{self.avversario.nome} ti ha sconfitto! Sei ferito gravemente...")
            giocatore.hp = 1  # Invece di morire, il giocatore resta con 1 HP
            if gioco.stato_corrente():
                gioco.pop_stato()
            return True
            
        if self.avversario.hp <= 0:
            gioco.io.mostra_messaggio(f"\nHai sconfitto {self.avversario.nome}!")
            
            # Gestisci la ricompensa
            oro_guadagnato = min(self.avversario.oro, 20)  # Max 20 monete
            self.avversario.oro -= oro_guadagnato
            giocatore.oro += oro_guadagnato
            
            gioco.io.mostra_messaggio(f"Hai guadagnato {oro_guadagnato} monete d'oro!")
            
            # Controlla se c'è un oggetto da saccheggiare
            if hasattr(self.avversario, 'inventario') and self.avversario.inventario and len(self.avversario.inventario) > 0:
                item = self.avversario.inventario[0]  # Prendi il primo oggetto
                giocatore.aggiungi_item(item)
                gioco.io.mostra_messaggio(f"Hai ottenuto: {item.nome}")
            
            # Guadagna esperienza
            exp_guadagnata = 25 * (1 + self.avversario.livello if hasattr(self.avversario, 'livello') else 1)
            if giocatore.guadagna_esperienza(exp_guadagnata):
                gioco.io.mostra_messaggio(f"Hai guadagnato {exp_guadagnata} punti esperienza e sei salito di livello!")
            else:
                gioco.io.mostra_messaggio(f"Hai guadagnato {exp_guadagnata} punti esperienza!")
            
            if gioco.stato_corrente():
                gioco.pop_stato()
            return True
            
        return False
        
    def _gestisci_attacco(self, giocatore, gioco):
        """Gestisce l'attacco del giocatore"""
        # Usa la forza effettiva del giocatore, che include i bonus dell'arma e accessori
        danno = giocatore.forza
        
        # Calcola critici e bonus speciali usando i dadi invece di random diretto
        critico = False
        if self.dado_d100.tira() <= 10:  # 10% di probabilità di colpo critico
            danno *= 2
            critico = True
        
        # Applica il danno all'avversario
        self.avversario.ferisci(danno)
        
        if critico:
            gioco.io.mostra_messaggio(f"\nCOLPO CRITICO! Attacchi {self.avversario.nome} e infliggi {danno} danni!")
        else:
            gioco.io.mostra_messaggio(f"\nAttacchi {self.avversario.nome} e infliggi {danno} danni!")
        
    def _attacco_nemico(self, giocatore, gioco):
        """Gestisce l'attacco dell'avversario"""
        # Per NPG usiamo la loro forza, altrimenti usiamo il danno del nemico
        if self.npg_ostile:
            danno = max(1, self.npg_ostile.forza if hasattr(self.npg_ostile, 'forza') else 3)
        else:
            danno = self.nemico.forza if hasattr(self.nemico, 'forza') else self.nemico.danno
        
        # Considera la difesa del giocatore (armatura + valori base)
        danno_effettivo = max(1, danno - giocatore.difesa)
        
        gioco.io.mostra_messaggio(f"\n{self.avversario.nome} ti attacca e infligge {danno_effettivo} danni!")
        giocatore.ferisci(danno)
    
    def _applica_effetto_oggetto(self, giocatore, item, gioco):
        """Applica l'effetto di un oggetto"""
        if isinstance(item, str):
            # Gestione vecchi oggetti (stringhe)
            if "Pozione" in item:
                # Cura il giocatore
                cura = 10
                giocatore.hp = min(giocatore.hp_max, giocatore.hp + cura)
                gioco.io.mostra_messaggio(f"\nUsi {item} e recuperi {cura} HP!")
                giocatore.inventario.remove(item)
            elif "Veleno" in item:
                # Avvelena il nemico
                danno = 5
                self.avversario.ferisci(danno)
                gioco.io.mostra_messaggio(f"\nUsi {item} e infliggi {danno} danni a {self.avversario.nome}!")
                giocatore.inventario.remove(item)
            elif "Bomba" in item:
                # Danneggia gravemente il nemico
                danno = 15
                self.avversario.ferisci(danno)
                gioco.io.mostra_messaggio(f"\nUsi {item} e infliggi {danno} danni a {self.avversario.nome}!")
                giocatore.inventario.remove(item)
            else:
                gioco.io.mostra_messaggio(f"\nNon sai come usare {item} in combattimento!")
    
    def _tenta_fuga(self, gioco):
        """Gestisce il tentativo di fuga"""
        # Tira un d20 con CD 10 per la fuga
        risultato_tiro = self.dado_d20.tira()
        if risultato_tiro >= 10:
            gioco.io.mostra_messaggio(f"\nSei riuscito a fuggire! (Tiro: {risultato_tiro})")
            if gioco.stato_corrente():
                gioco.pop_stato()
        else:
            gioco.io.mostra_messaggio(f"\nNon sei riuscito a fuggire! (Tiro: {risultato_tiro})")
            
    # Metodi obsoleti, lasciati per compatibilità
    def _usa_oggetto(self, giocatore, gioco):
        """Metodo obsoleto mantenuto per compatibilità"""
        gioco.io.messaggio_errore("Metodo obsoleto, usa _fase_usa_oggetto invece")
        
    def _cambia_equipaggiamento(self, giocatore, gioco):
        """Metodo obsoleto mantenuto per compatibilità"""
        gioco.io.messaggio_errore("Metodo obsoleto, usa _fase_cambia_equipaggiamento invece")
        
    def _cambia_arma(self, giocatore, gioco):
        """Metodo obsoleto mantenuto per compatibilità"""
        gioco.io.messaggio_errore("Metodo obsoleto, usa _fase_cambia_equipaggiamento invece")
        
    def _cambia_armatura(self, giocatore, gioco):
        """Metodo obsoleto mantenuto per compatibilità"""
        gioco.io.messaggio_errore("Metodo obsoleto, usa _fase_cambia_equipaggiamento invece")
        
    def _cambia_accessorio(self, giocatore, gioco):
        """Metodo obsoleto mantenuto per compatibilità"""
        gioco.io.messaggio_errore("Metodo obsoleto, usa _fase_cambia_equipaggiamento invece")
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza di CombattimentoState da un dizionario.
        
        Args:
            data (dict): Dizionario con i dati dello stato
            
        Returns:
            CombattimentoState: Nuova istanza di CombattimentoState
        """
        from entities.nemico import Nemico
        from entities.npg import NPG
        
        stato = cls()
        
        # Ripristina l'avversario
        if "avversario" in data and data["avversario"] is not None:
            if isinstance(data["avversario"], dict):
                # Determina se l'avversario è un nemico o un NPG
                if data["avversario"].get("type") == "NPG":
                    stato.npg_ostile = NPG.from_dict(data["avversario"])
                    stato.avversario = stato.npg_ostile
                    stato.nemico = None
                else:
                    stato.nemico = Nemico.from_dict(data["avversario"])
                    stato.avversario = stato.nemico
                    stato.npg_ostile = None
        
        # Ripristina gli altri attributi
        stato.turno = data.get("turno", 1)
        stato.fase = data.get("fase", "scelta")
        stato.dati_temporanei = data.get("dati_temporanei", {})
        
        return stato
        
    def to_dict(self):
        """
        Converte l'istanza di CombattimentoState in un dizionario per il salvataggio.
        
        Returns:
            dict: Dizionario con i dati dello stato
        """
        data = {
            "turno": self.turno,
            "fase": self.fase,
            "dati_temporanei": self.dati_temporanei
        }
        
        # Salva l'avversario
        if self.avversario is not None:
            if hasattr(self.avversario, 'to_dict'):
                avversario_dict = self.avversario.to_dict()
                # Aggiungi un campo type per distinguere tra NPG e Nemico
                if self.npg_ostile is not None:
                    avversario_dict["type"] = "NPG"
                data["avversario"] = avversario_dict
        
        return data

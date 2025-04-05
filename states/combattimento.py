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
        
    def esegui(self, gioco):
        giocatore = gioco.giocatore
        
        # Mostra le statistiche del combattimento
        self._mostra_stato_combattimento(giocatore, gioco)
        
        # Controlla se il combattimento è finito
        if not self._controlla_fine_combattimento(gioco):
            # Chiedi l'azione al giocatore
            gioco.io.mostra_messaggio("\nCosa vuoi fare?")
            gioco.io.mostra_messaggio("1. Attacca")
            gioco.io.mostra_messaggio("2. Usa oggetto")
            gioco.io.mostra_messaggio("3. Cambia equipaggiamento")
            gioco.io.mostra_messaggio("4. Fuggi")
            
            scelta = gioco.io.richiedi_input("Scelta: ")
            
            if scelta == "1":
                self._gestisci_attacco(giocatore, gioco)
            elif scelta == "2":
                self._usa_oggetto(giocatore, gioco)
            elif scelta == "3":
                self._cambia_equipaggiamento(giocatore, gioco)
            elif scelta == "4":
                self._tenta_fuga(gioco)
            else:
                gioco.io.mostra_messaggio("Azione non valida!")
                
            # Se l'avversario è ancora vivo, attacca
            if self.avversario.hp > 0:
                self._attacco_nemico(giocatore, gioco)
                
            # Incrementa il turno
            self.turno += 1
        
    def _mostra_stato_combattimento(self, giocatore, gioco):
        """Mostra lo stato attuale del combattimento"""
        gioco.io.mostra_messaggio("\n" + "="*60)
        gioco.io.mostra_messaggio(f"COMBATTIMENTO: {giocatore.nome} vs {self.avversario.nome}")
        gioco.io.mostra_messaggio(f"Turno: {self.turno}")
        gioco.io.mostra_messaggio(f"HP {giocatore.nome}: {giocatore.hp}/{giocatore.hp_max} | HP {self.avversario.nome}: {self.avversario.hp}/{self.avversario.hp_max}")
        
        # Mostra anche l'equipaggiamento attuale
        arma = giocatore.arma.nome if giocatore.arma else "Nessuna"
        armatura = giocatore.armatura.nome if giocatore.armatura else "Nessuna"
        accessori = ", ".join([a.nome for a in giocatore.accessori]) if giocatore.accessori else "Nessuno"
        
        gioco.io.mostra_messaggio(f"Arma: {arma} | Armatura: {armatura} | Accessori: {accessori}")
        gioco.io.mostra_messaggio(f"Forza: {giocatore.forza} | Difesa: {giocatore.difesa}")
        gioco.io.mostra_messaggio("="*60)
        
    def _controlla_fine_combattimento(self, gioco):
        """Controlla se il combattimento è finito"""
        giocatore = gioco.giocatore
        
        if giocatore.hp <= 0:
            gioco.io.mostra_messaggio(f"\n{self.avversario.nome} ti ha sconfitto! Sei ferito gravemente...")
            giocatore.hp = 1  # Invece di morire, il giocatore resta con 1 HP
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
        
    def _usa_oggetto(self, giocatore, gioco):
        """Gestisce l'uso di un oggetto"""
        if not giocatore.inventario:
            gioco.io.mostra_messaggio("\nNon hai nessun oggetto da usare!")
            return
            
        gioco.io.mostra_messaggio("\nQuale oggetto vuoi usare?")
        for i, item in enumerate(giocatore.inventario, 1):
            gioco.io.mostra_messaggio(f"{i}. {item}")
        gioco.io.mostra_messaggio(f"{len(giocatore.inventario) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(giocatore.inventario):
                item = giocatore.inventario[scelta - 1]
                
                # Usa il metodo usa dell'oggetto
                if hasattr(item, 'usa'):
                    item.usa(giocatore)
                else:
                    # Retrocompatibilità con stringhe
                    self._applica_effetto_oggetto(giocatore, item, gioco)
            elif scelta == len(giocatore.inventario) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
    
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
    
    def _cambia_equipaggiamento(self, giocatore, gioco):
        """Permette al giocatore di cambiare equipaggiamento durante il combattimento"""
        gioco.io.mostra_messaggio("\nCosa vuoi cambiare?")
        gioco.io.mostra_messaggio("1. Arma")
        gioco.io.mostra_messaggio("2. Armatura")
        gioco.io.mostra_messaggio("3. Accessorio")
        gioco.io.mostra_messaggio("4. Annulla")
        
        scelta = gioco.io.richiedi_input("Scelta: ")
        
        if scelta == "1":
            self._cambia_arma(giocatore, gioco)
        elif scelta == "2":
            self._cambia_armatura(giocatore, gioco)
        elif scelta == "3":
            self._cambia_accessorio(giocatore, gioco)
        elif scelta == "4":
            return
        else:
            gioco.io.mostra_messaggio("Scelta non valida.")
    
    def _cambia_arma(self, giocatore, gioco):
        """Permette al giocatore di cambiare l'arma"""
        # Filtra le armi dall'inventario
        armi = [item for item in giocatore.inventario if hasattr(item, 'tipo') and item.tipo == "arma"]
        
        if not armi:
            gioco.io.mostra_messaggio("\nNon hai altre armi nell'inventario!")
            return
        
        gioco.io.mostra_messaggio("\nQuale arma vuoi equipaggiare?")
        for i, arma in enumerate(armi, 1):
            bonus = f" (Forza +{arma.effetto.get('forza', 0)})" if hasattr(arma, 'effetto') else ""
            gioco.io.mostra_messaggio(f"{i}. {arma.nome}{bonus}")
        gioco.io.mostra_messaggio(f"{len(armi) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(armi):
                arma = armi[scelta - 1]
                arma.equipaggia(giocatore)
                gioco.io.mostra_messaggio(f"\nHai equipaggiato {arma.nome}!")
            elif scelta == len(armi) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
    
    def _cambia_armatura(self, giocatore, gioco):
        """Permette al giocatore di cambiare l'armatura"""
        # Filtra le armature dall'inventario
        armature = [item for item in giocatore.inventario if hasattr(item, 'tipo') and item.tipo == "armatura"]
        
        if not armature:
            gioco.io.mostra_messaggio("\nNon hai altre armature nell'inventario!")
            return
        
        gioco.io.mostra_messaggio("\nQuale armatura vuoi equipaggiare?")
        for i, armatura in enumerate(armature, 1):
            bonus = f" (Difesa +{armatura.effetto.get('difesa', 0)})" if hasattr(armatura, 'effetto') else ""
            gioco.io.mostra_messaggio(f"{i}. {armatura.nome}{bonus}")
        gioco.io.mostra_messaggio(f"{len(armature) + 1}. Annulla")
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(armature):
                armatura = armature[scelta - 1]
                armatura.equipaggia(giocatore)
                gioco.io.mostra_messaggio(f"\nHai equipaggiato {armatura.nome}!")
            elif scelta == len(armature) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
    
    def _cambia_accessorio(self, giocatore, gioco):
        """Permette al giocatore di cambiare un accessorio"""
        # Filtra gli accessori dall'inventario
        accessori = [item for item in giocatore.inventario if hasattr(item, 'tipo') and item.tipo == "accessorio"]
        
        if not accessori:
            gioco.io.mostra_messaggio("\nNon hai altri accessori nell'inventario!")
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
        
        try:
            scelta = int(gioco.io.richiedi_input("\nScegli: "))
            if 1 <= scelta <= len(accessori):
                accessorio = accessori[scelta - 1]
                accessorio.equipaggia(giocatore)
                gioco.io.mostra_messaggio(f"\nHai equipaggiato {accessorio.nome}!")
            elif scelta == len(accessori) + 1:
                return
            else:
                gioco.io.mostra_messaggio("Scelta non valida.")
        except ValueError:
            gioco.io.mostra_messaggio("Devi inserire un numero.")
    
    def _tenta_fuga(self, gioco):
        """Gestisce il tentativo di fuga"""
        # Tira un d20 con CD 10 per la fuga
        risultato_tiro = self.dado_d20.tira()
        if risultato_tiro >= 10:
            gioco.io.mostra_messaggio(f"\nSei riuscito a fuggire! (Tiro: {risultato_tiro})")
            gioco.pop_stato()
        else:
            gioco.io.mostra_messaggio(f"\nNon sei riuscito a fuggire! (Tiro: {risultato_tiro})")

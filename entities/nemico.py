from entities.entita import Entita

class Nemico(Entita):
    def __init__(self, nome, hp, danno, token="M"):
        """Inizializza un nuovo nemico.

        Crea un'istanza della classe Nemico con nome, punti vita, danno e token specificati.
        """
        # Chiamiamo il costruttore della classe base
        super().__init__(nome, hp=hp, hp_max=hp, forza=danno, difesa=0)
        
        # Attributi specifici per nemici
        self.danno = danno  # Manteniamo anche danno per retrocompatibilità
        self.oro = 10       # Oro base che il nemico può lasciare
        self.token = token
    
    def attacca(self, giocatore, gioco=None):
        """Override del metodo attacca per retrocompatibilità"""
        # Prima prova a usare l'implementazione base
        if hasattr(giocatore, 'subisci_danno'):
            return super().attacca(giocatore)

        # Altrimenti usa il vecchio codice
        messaggio = f"{self.nome} ti attacca e ti infligge {self.danno} danni!"
        gioco.io.mostra_messaggio(messaggio)
        if hasattr(giocatore, 'ferisci'):
            giocatore.ferisci(self.danno)
        else:
            giocatore.hp -= self.danno

from entities.entita import Entita

class Nemico(Entita):
    def __init__(self, nome, hp, danno, token="M"):  # M per Monster
        # Chiamiamo il costruttore della classe base con forza_base calcolata
        super().__init__(nome, hp=hp, hp_max=hp, forza_base=10+danno*2, difesa=0, token=token)
        
        # Rimuoviamo danno come attributo separato, usiamo il modificatore di forza
        # self.danno = danno  # Non più necessario
        self.oro = 10       # Oro base che il nemico può lasciare
    
    def attacca(self, giocatore, gioco=None):
        """Override del metodo attacca per retrocompatibilità"""
        # Prima prova a usare l'implementazione base
        if hasattr(giocatore, 'subisci_danno'):
            return super().attacca(giocatore)
        
        # Altrimenti usa il vecchio codice
        messaggio = f"{self.nome} ti attacca e ti infligge {self.modificatore_forza} danni!"
        if gioco:
            gioco.io.mostra_messaggio(messaggio)
        else:
            from entities.entita import io
            io.mostra_messaggio(messaggio)  # Fallback se gioco non è fornito
        
        if hasattr(giocatore, 'ferisci'):
            giocatore.ferisci(self.modificatore_forza)
        else:
            giocatore.hp -= self.modificatore_forza

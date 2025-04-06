from entities.entita import Entita

class Nemico(Entita):
    def __init__(self, nome, hp, danno, token="M"):  # M per Monster
        # Chiamiamo il costruttore della classe base con forza_base calcolata
        super().__init__(nome, hp=hp, hp_max=hp, forza_base=10+danno*2, difesa=0, token=token)
        
        # Rimuoviamo danno come attributo separato, usiamo il modificatore di forza
        # self.danno = danno  # Non più necessario
        self.oro = 10       # Oro base che il nemico può lasciare
    
    def attacca(self, giocatore, gioco=None):
        """Attacca il giocatore utilizzando il metodo unificato"""
        # Ottieni l'interfaccia I/O da gioco se disponibile
        io_interface = gioco.io if gioco else None
        
        # Usa il metodo della classe base per gestire l'attacco
        return super().attacca(giocatore, io_interface)

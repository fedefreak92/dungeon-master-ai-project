import random

class Dado:
    """
    Classe che rappresenta un dado a N facce utilizzabile per tiri in stile D&D.
    Supporta i tiri di dado singoli, multipli e con vantaggio/svantaggio.
    """
    def __init__(self, facce):
        """Inizializza un dado con il numero specificato di facce."""
        self.facce = facce
    
    def tira(self):
        """Esegue un singolo tiro di dado."""
        return random.randint(1, self.facce)
    
    def tiri_multipli(self, numero_tiri):
        """Esegue più tiri di dado e restituisce una lista dei risultati."""
        return [self.tira() for _ in range(numero_tiri)]
    
    def tira_con_vantaggio(self):
        """Esegue due tiri di dado e restituisce il risultato migliore (vantaggio in D&D)."""
        tiro1 = self.tira()
        tiro2 = self.tira()
        return max(tiro1, tiro2), tiro1, tiro2
    
    def tira_con_svantaggio(self):
        """Esegue due tiri di dado e restituisce il risultato peggiore (svantaggio in D&D)."""
        tiro1 = self.tira()
        tiro2 = self.tira()
        return min(tiro1, tiro2), tiro1, tiro2

def tira_dadi(formula):
    """
    Esegue un tiro di dadi secondo una formula, ad esempio "2d6+3" o "1d20-1".
    
    Args:
        formula (str): La formula del tiro di dadi (es. "2d6+3")
    
    Returns:
        tuple: (risultato_totale, lista_tiri, modificatore)
    """
    # Analizza la formula
    if "+" in formula:
        formula_dadi, mod_str = formula.split("+")
        modificatore = int(mod_str)
    elif "-" in formula:
        formula_dadi, mod_str = formula.split("-")
        modificatore = -int(mod_str)
    else:
        formula_dadi = formula
        modificatore = 0
    
    # Estrai il numero e il tipo di dadi
    if "d" in formula_dadi:
        num_dadi, facce = formula_dadi.split("d")
        num_dadi = int(num_dadi) if num_dadi else 1
        facce = int(facce)
    else:
        # Se non c'è 'd', assumiamo sia solo un numero
        return int(formula_dadi) + modificatore, [], modificatore
    
    # Esegui i tiri
    dado = Dado(facce)
    tiri = dado.tiri_multipli(num_dadi)
    risultato_totale = sum(tiri) + modificatore
    
    return risultato_totale, tiri, modificatore

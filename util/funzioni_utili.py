def avanti(gioco):
    gioco.io.richiedi_input("Premi Invio per continuare...")

def mostra_statistiche(g, gioco):
    try:
        gioco.io.mostra_messaggio("\n=== LE TUE STATISTICHE ===")
        gioco.io.mostra_messaggio(f"Nome: {g.nome}")
        if hasattr(g, 'classe'):
            gioco.io.mostra_messaggio(f"Classe: {g.classe}")
        gioco.io.mostra_messaggio(f"Livello: {g.livello if hasattr(g, 'livello') else 1}")
        gioco.io.mostra_messaggio(f"HP: {g.hp}/{g.hp_max if hasattr(g, 'hp_max') else g.hp}")
        gioco.io.mostra_messaggio(f"Oro: {g.oro}")
        
        # Mostra sia i valori base che i modificatori
        if hasattr(g, 'forza_base'):
            gioco.io.mostra_messaggio(f"Forza: {g.forza_base} (mod: {g.forza})")
        elif hasattr(g, 'forza'):
            gioco.io.mostra_messaggio(f"Forza: {g.forza}")
            
        if hasattr(g, 'destrezza_base'):
            gioco.io.mostra_messaggio(f"Destrezza: {g.destrezza_base} (mod: {g.destrezza})")
        elif hasattr(g, 'destrezza'):
            gioco.io.mostra_messaggio(f"Destrezza: {g.destrezza}")
            
        if hasattr(g, 'costituzione_base'):
            gioco.io.mostra_messaggio(f"Costituzione: {g.costituzione_base} (mod: {g.costituzione})")
        elif hasattr(g, 'costituzione'):
            gioco.io.mostra_messaggio(f"Costituzione: {g.costituzione}")
            
        if hasattr(g, 'intelligenza_base'):
            gioco.io.mostra_messaggio(f"Intelligenza: {g.intelligenza_base} (mod: {g.intelligenza})")
        elif hasattr(g, 'intelligenza'):
            gioco.io.mostra_messaggio(f"Intelligenza: {g.intelligenza}")
            
        if hasattr(g, 'saggezza_base'):
            gioco.io.mostra_messaggio(f"Saggezza: {g.saggezza_base} (mod: {g.saggezza})")
        elif hasattr(g, 'saggezza'):
            gioco.io.mostra_messaggio(f"Saggezza: {g.saggezza}")
            
        if hasattr(g, 'carisma_base'):
            gioco.io.mostra_messaggio(f"Carisma: {g.carisma_base} (mod: {g.carisma})")
        elif hasattr(g, 'carisma'):
            gioco.io.mostra_messaggio(f"Carisma: {g.carisma}")
            
        if hasattr(g, 'difesa'):
            gioco.io.mostra_messaggio(f"Difesa: {g.difesa}")
            
        # Mostra esperienza se esiste
        if hasattr(g, 'esperienza'):
            gioco.io.mostra_messaggio(f"Esperienza: {g.esperienza}")
            
    except Exception as e:
        gioco.io.mostra_messaggio(f"Errore nel mostrare le statistiche: {str(e)}")
        gioco.io.mostra_messaggio(f"Tipo di g: {type(g)}")
        attributi = [attr for attr in dir(g) if not attr.startswith('_')]
        gioco.io.mostra_messaggio(f"Attributi disponibili: {', '.join(attributi)}")

def mostra_inventario(g, gioco):
    gioco.io.mostra_messaggio("\n=== IL TUO INVENTARIO ===")
    if len(g.inventario) == 0:
        gioco.io.mostra_messaggio("Il tuo inventario è vuoto!")
    else:
        for oggetto in g.inventario:
            gioco.io.mostra_messaggio(f"- {oggetto}")

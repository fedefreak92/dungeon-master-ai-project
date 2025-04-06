def avanti(gioco=None):
    """
    Funzione di utilità per attendere l'input dell'utente per avanzare.
    Utile per dare tempo all'utente di leggere i messaggi sullo schermo.
    
    Args:
        gioco: L'istanza del gioco (opzionale se non richiesto)
    """
    # Usa il contesto di gioco se disponibile
    if gioco:
        gioco.io.richiedi_input("Premi Invio per continuare...")
    else:
        input("Premi Invio per continuare...")

def mostra_statistiche(entita, gioco=None):
    """
    Mostra le statistiche di un'entità.
    
    Args:
        entita: L'entità di cui mostrare le statistiche
        gioco: L'istanza del gioco (opzionale se il contesto è memorizzato nell'entità)
    """
    # Usa il contesto di gioco dell'entità se disponibile
    game_ctx = gioco
    if not game_ctx and hasattr(entita, 'gioco') and entita.gioco:
        game_ctx = entita.gioco
        
    if game_ctx:
        game_ctx.io.mostra_messaggio(f"Nome: {entita.nome}")
        game_ctx.io.mostra_messaggio(f"HP: {entita.hp}/{entita.hp_max}")
        game_ctx.io.mostra_messaggio(f"FOR: {entita.forza_base} ({entita.modificatore_forza:+d})")
        game_ctx.io.mostra_messaggio(f"DES: {entita.destrezza_base} ({entita.modificatore_destrezza:+d})")
        game_ctx.io.mostra_messaggio(f"COS: {entita.costituzione_base} ({entita.modificatore_costituzione:+d})")
        game_ctx.io.mostra_messaggio(f"INT: {entita.intelligenza_base} ({entita.modificatore_intelligenza:+d})")
        game_ctx.io.mostra_messaggio(f"SAG: {entita.saggezza_base} ({entita.modificatore_saggezza:+d})")
        game_ctx.io.mostra_messaggio(f"CAR: {entita.carisma_base} ({entita.modificatore_carisma:+d})")
        game_ctx.io.mostra_messaggio(f"Difesa: {entita.difesa}")
        if hasattr(entita, 'livello'):
            game_ctx.io.mostra_messaggio(f"Livello: {entita.livello}")
        if hasattr(entita, 'oro'):
            game_ctx.io.mostra_messaggio(f"Oro: {entita.oro}")
        if hasattr(entita, 'esperienza'):
            game_ctx.io.mostra_messaggio(f"Esperienza: {entita.esperienza}/{100 * entita.livello}")
    else:
        # Fallback se non c'è contesto di gioco
        print(f"Nome: {entita.nome}")
        print(f"HP: {entita.hp}/{entita.hp_max}")
        print(f"FOR: {entita.forza_base} ({entita.modificatore_forza:+d})")
        print(f"DES: {entita.destrezza_base} ({entita.modificatore_destrezza:+d})")
        print(f"COS: {entita.costituzione_base} ({entita.modificatore_costituzione:+d})")
        print(f"INT: {entita.intelligenza_base} ({entita.modificatore_intelligenza:+d})")
        print(f"SAG: {entita.saggezza_base} ({entita.modificatore_saggezza:+d})")
        print(f"CAR: {entita.carisma_base} ({entita.modificatore_carisma:+d})")
        print(f"Difesa: {entita.difesa}")
        if hasattr(entita, 'livello'):
            print(f"Livello: {entita.livello}")
        if hasattr(entita, 'oro'):
            print(f"Oro: {entita.oro}")
        if hasattr(entita, 'esperienza'):
            print(f"Esperienza: {entita.esperienza}/{100 * entita.livello}")

def mostra_inventario(entita, gioco=None):
    """
    Mostra l'inventario di un'entità.
    
    Args:
        entita: L'entità di cui mostrare l'inventario
        gioco: L'istanza del gioco (opzionale se il contesto è memorizzato nell'entità)
    """
    # Usa il contesto di gioco dell'entità se disponibile
    game_ctx = gioco
    if not game_ctx and hasattr(entita, 'gioco') and entita.gioco:
        game_ctx = entita.gioco
    
    if not hasattr(entita, 'inventario'):
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"{entita.nome} non ha un inventario.")
        else:
            print(f"{entita.nome} non ha un inventario.")
        return
        
    if len(entita.inventario) == 0:
        if game_ctx:
            game_ctx.io.mostra_messaggio(f"L'inventario di {entita.nome} è vuoto.")
        else:
            print(f"L'inventario di {entita.nome} è vuoto.")
        return
    
    if game_ctx:
        game_ctx.io.mostra_messaggio(f"\n=== INVENTARIO DI {entita.nome.upper()} ===")
        
        for i, item in enumerate(entita.inventario, 1):
            # Gestisci diversi tipi di item
            if isinstance(item, str):
                game_ctx.io.mostra_messaggio(f"{i}. {item}")
            elif hasattr(item, 'nome'):
                descrizione = f"{item.nome}"
                
                if hasattr(item, 'descrizione') and item.descrizione:
                    descrizione += f" - {item.descrizione}"
                
                if hasattr(item, 'valore') and item.valore:
                    descrizione += f" (Valore: {item.valore} oro)"
                    
                if hasattr(item, 'equipaggiato') and item.equipaggiato:
                    descrizione += " [Equipaggiato]"
                    
                game_ctx.io.mostra_messaggio(f"{i}. {descrizione}")
            else:
                game_ctx.io.mostra_messaggio(f"{i}. {str(item)}")
                
        if hasattr(entita, 'oro'):
            game_ctx.io.mostra_messaggio(f"\nOro: {entita.oro}")
    else:
        # Fallback se non c'è contesto di gioco
        print(f"\n=== INVENTARIO DI {entita.nome.upper()} ===")
        
        for i, item in enumerate(entita.inventario, 1):
            # Gestisci diversi tipi di item
            if isinstance(item, str):
                print(f"{i}. {item}")
            elif hasattr(item, 'nome'):
                descrizione = f"{item.nome}"
                
                if hasattr(item, 'descrizione') and item.descrizione:
                    descrizione += f" - {item.descrizione}"
                
                if hasattr(item, 'valore') and item.valore:
                    descrizione += f" (Valore: {item.valore} oro)"
                    
                if hasattr(item, 'equipaggiato') and item.equipaggiato:
                    descrizione += " [Equipaggiato]"
                    
                print(f"{i}. {descrizione}")
            else:
                print(f"{i}. {str(item)}")
                
        if hasattr(entita, 'oro'):
            print(f"\nOro: {entita.oro}")

"""
Test per il caricamento esterno dei dati NPC
"""
from entities.npg import NPG
from util.data_manager import get_data_manager

def test_npg_data():
    """Testa il caricamento dei dati degli NPC"""
    npc_names = ["Durnan", "Elminster", "Mirt", "Araldo", "Violetta", "Gundren"]
    
    # Carica i dati di ogni NPC
    for name in npc_names:
        npc = NPG(name)
        print(f"\n=== Informazioni su {name} ===")
        print(npc.mostra_info())
        
        # Mostra informazioni sulla conversazione
        conv = npc.ottieni_conversazione("inizio")
        if conv:
            print(f"\nConversazione iniziale con {name}:")
            print(f"Testo: {conv['testo']}")
            print("Opzioni:")
            for i, (testo, destinazione) in enumerate(conv['opzioni'], 1):
                print(f"{i}. {testo} -> {destinazione}")
        else:
            print(f"\nNessuna conversazione trovata per {name}")

if __name__ == "__main__":
    test_npg_data() 
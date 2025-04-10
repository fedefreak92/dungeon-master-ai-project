/**
 * Definizioni delle API del gioco RPG
 * Questo file contiene le definizioni di tutte le API disponibili nel sistema,
 * inclusi metodi, endpoint, parametri e risposte.
 */

// Base URL per tutte le API
const API_BASE_URL = '/api';

/**
 * Definizione di tutti gli endpoint API disponibili nel sistema
 * NOTA: i path non devono includere il prefisso /api/ poiché è già configurato in Axios
 */
const API_ENDPOINTS = {
  // Gestione della sessione e dello stato
  INIZIA_GIOCO: {
    path: '/inizia',
    method: 'POST',
    description: 'Crea una nuova partita',
    params: {
      nome: 'Nome del personaggio',
      classe: 'Classe del personaggio (guerriero, mago, ladro, chierico, ...)'
    },
    response: {
      id_sessione: 'Identificativo univoco della sessione di gioco',
      messaggio: 'Messaggio di conferma',
      stato: 'Stato iniziale del gioco',
      stato_nome: 'Nome dello stato corrente'
    }
  },
  
  COMANDO: {
    path: '/comando',
    method: 'POST',
    description: 'Invia un comando alla partita',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      comando: 'Comando da eseguire'
    },
    response: {
      output: 'Output strutturato del comando',
      stato: 'Stato aggiornato del gioco',
      stato_nome: 'Nome dello stato corrente',
      fine: 'Booleano che indica se il gioco è terminato'
    }
  },
  
  STATO: {
    path: '/stato',
    method: 'GET',
    description: 'Ottieni lo stato attuale della partita',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      // Lo stato completo del gioco, struttura variabile
    }
  },
  
  // Gestione dei salvataggi
  SALVA: {
    path: '/salva',
    method: 'POST',
    description: 'Salva la partita corrente',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      nome_file: 'Nome del file di salvataggio (opzionale)'
    },
    response: {
      messaggio: 'Messaggio di conferma'
    }
  },
  
  CARICA: {
    path: '/carica',
    method: 'POST',
    description: 'Carica una partita esistente',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      nome_file: 'Nome del file di salvataggio da caricare'
    },
    response: {
      messaggio: 'Messaggio di conferma',
      giocatore: 'Informazioni sul giocatore caricato'
    }
  },
  
  SALVATAGGI: {
    path: '/salvataggi',
    method: 'GET',
    description: 'Ottieni la lista dei salvataggi disponibili',
    params: {},
    response: {
      // Array di oggetti con informazioni sui salvataggi
      // Ogni oggetto contiene: nome_file, nome_personaggio, classe, livello, data_salvataggio
    }
  },
  
  ELIMINA_SALVATAGGIO: {
    path: '/elimina_salvataggio',
    method: 'POST',
    description: 'Elimina un salvataggio',
    params: {
      nome_file: 'Nome del file di salvataggio da eliminare'
    },
    response: {
      messaggio: 'Messaggio di conferma'
    }
  },
  
  ESPORTA_SALVATAGGIO: {
    path: '/esporta_salvataggio',
    method: 'POST',
    description: 'Esporta un salvataggio come file',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      nome_file: 'Nome del file di salvataggio (opzionale)'
    },
    response: {
      // File di salvataggio come download
    }
  },
  
  IMPORTA_SALVATAGGIO: {
    path: '/importa_salvataggio',
    method: 'POST',
    description: 'Importa un salvataggio da file',
    params: {
      file: 'File di salvataggio da importare (multipart/form-data)'
    },
    response: {
      id_sessione: 'Nuovo identificativo della sessione di gioco',
      messaggio: 'Messaggio di conferma',
      stato: 'Stato iniziale del gioco importato'
    }
  },
  
  LISTA_SALVATAGGI: {
    path: '/lista_salvataggi',
    method: 'GET',
    description: 'Restituisce la lista dei salvataggi disponibili con dettagli',
    params: {},
    response: {
      salvataggi: [
        // Array di oggetti con informazioni dettagliate sui salvataggi
        // file, giocatore, livello, classe, mappa, data, versione
      ]
    }
  },
  
  // Gestione della mappa e dello spostamento
  MAPPA: {
    path: '/mappa',
    method: 'GET',
    description: 'Ottieni informazioni sulla mappa attuale',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      // Informazioni sulla mappa e sulla posizione del giocatore
    }
  },
  
  MUOVI: {
    path: '/muovi',
    method: 'POST',
    description: 'Muovi il giocatore nella direzione specificata',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      direzione: 'Direzione in cui muoversi (nord, sud, est, ovest)'
    },
    response: {
      spostamento: 'Risultato dello spostamento',
      stato: 'Stato aggiornato del gioco'
    }
  },
  
  POSIZIONE: {
    path: '/posizione',
    method: 'GET',
    description: 'Ottieni la posizione attuale del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      // Informazioni sulla posizione del giocatore
    }
  },
  
  ESPLORA: {
    path: '/esplora',
    method: 'POST',
    description: 'Esplora l\'ambiente circostante',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      output: 'Output strutturato dell\'esplorazione',
      stato: 'Stato aggiornato del gioco',
      oggetti: 'Oggetti presenti nell\'ambiente',
      uscite: 'Uscite disponibili',
      npc: 'NPC presenti nella zona'
    }
  },
  
  DESTINAZIONI: {
    path: '/destinazioni',
    method: 'GET',
    description: 'Ottieni le destinazioni disponibili per il viaggio',
    params: {
      id_sessione: 'Identificativo della sessione di gioco (opzionale)'
    },
    response: [
      // Array di oggetti destinazione con id, nome, descrizione
    ]
  },
  
  MAPPE_DISPONIBILI: {
    path: '/mappe_disponibili',
    method: 'GET',
    description: 'Ottieni informazioni sulle mappe disponibili',
    params: {
      id: 'ID della mappa specifica (opzionale)'
    },
    response: {
      // Informazioni sulle mappe disponibili
    }
  },
  
  // Gestione dell'inventario e degli oggetti
  INVENTARIO: {
    path: '/inventario',
    method: 'GET',
    description: 'Ottieni l\'inventario del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      inventario: 'Array di oggetti nell\'inventario',
      equipaggiamento: 'Oggetti equipaggiati'
    }
  },
  
  OGGETTO: {
    path: '/oggetto',
    method: 'POST',
    description: 'Interagisci con un oggetto nell\'inventario o nell\'ambiente',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      oggetto: 'Nome o ID dell\'oggetto',
      azione: 'Azione da eseguire (usa, esamina, ...)'
    },
    response: {
      output: 'Output strutturato dell\'interazione',
      stato: 'Stato aggiornato del gioco'
    }
  },
  
  EQUIPAGGIAMENTO: {
    path: '/equipaggiamento',
    method: 'POST',
    description: 'Gestisci l\'equipaggiamento del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      azione: 'Azione da eseguire (equip, unequip, examine)',
      oggetto: 'Nome o ID dell\'oggetto',
      slot: 'Slot in cui equipaggiare l\'oggetto (opzionale)'
    },
    response: {
      output: 'Output strutturato dell\'operazione',
      stato: 'Stato aggiornato del gioco',
      equipaggiamento: 'Stato aggiornato dell\'equipaggiamento'
    }
  },
  
  OGGETTO_DETTAGLI: {
    path: '/oggetto_dettagli',
    method: 'GET',
    description: 'Ottieni dettagli su un oggetto specifico',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      id_oggetto: 'ID dell\'oggetto (alternativo a nome_oggetto)',
      nome_oggetto: 'Nome dell\'oggetto (alternativo a id_oggetto)'
    },
    response: {
      // Dettagli completi sull'oggetto, inclusi asset e utilizzi possibili
    }
  },
  
  OGGETTI: {
    path: '/oggetti',
    method: 'GET',
    description: 'Ottieni informazioni sugli oggetti disponibili',
    params: {
      categoria: 'Categoria di oggetti (opzionale)'
    },
    response: {
      // Informazioni sugli oggetti disponibili
    }
  },
  
  // Gestione del personaggio
  STATISTICHE: {
    path: '/statistiche',
    method: 'GET',
    description: 'Ottieni le statistiche del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      nome: 'Nome del personaggio',
      classe: 'Classe del personaggio',
      hp: 'Punti vita attuali',
      max_hp: 'Punti vita massimi',
      statistiche: 'Statistiche dettagliate del personaggio'
    }
  },
  
  // Gestione delle classi
  CLASSI: {
    path: '/classi',
    method: 'GET',
    description: 'Ottieni informazioni sulle classi di personaggio disponibili',
    params: {},
    response: {
      // Informazioni sulle classi di personaggio disponibili
    }
  },
  
  MISSIONI: {
    path: '/missioni',
    method: 'GET',
    description: 'Ottieni l\'elenco delle missioni attive e completate del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      attive: 'Array di missioni attive',
      completate: 'Array di missioni completate'
    }
  },
  
  ABILITA: {
    path: '/abilita',
    method: 'GET',
    description: 'Ottieni le abilità del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      abilita: 'Array di abilità',
      mana_attuale: 'Mana attuale',
      mana_massimo: 'Mana massimo'
    }
  },
  
  USA_ABILITA: {
    path: '/usa_abilita',
    method: 'POST',
    description: 'Usa un\'abilità del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      id_abilita: 'ID dell\'abilità da usare',
      nome_abilita: 'Nome dell\'abilità (alternativo a id_abilita)',
      bersaglio: 'Bersaglio dell\'abilità (opzionale)'
    },
    response: {
      output: 'Output strutturato dell\'uso dell\'abilità',
      stato: 'Stato aggiornato del gioco',
      mana_attuale: 'Mana attuale dopo l\'uso dell\'abilità',
      uso_riuscito: 'Booleano che indica se l\'uso dell\'abilità è riuscito'
    }
  },
  
  ACHIEVEMENTS: {
    path: '/achievements',
    method: 'GET',
    description: 'Ottieni gli achievement del giocatore',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      achievements: 'Array di achievement',
      totale: 'Numero totale di achievement',
      sbloccati: 'Numero di achievement sbloccati'
    }
  },
  
  // Gestione di combattimento e NPC
  COMBATTIMENTO: {
    path: '/combattimento',
    method: 'GET',
    description: 'Ottieni lo stato del combattimento attuale',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      in_combattimento: 'Booleano che indica se il giocatore è in combattimento',
      round: 'Round corrente del combattimento',
      turno_di: 'Chi ha il turno attuale',
      nemici: 'Array di nemici presenti',
      azioni_disponibili: 'Array di azioni disponibili'
    }
  },
  
  AZIONE_COMBATTIMENTO: {
    path: '/azione_combattimento',
    method: 'POST',
    description: 'Esegui un\'azione di combattimento',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      azione: 'Azione da eseguire',
      bersaglio: 'Bersaglio dell\'azione (opzionale)',
      parametri: 'Parametri aggiuntivi dell\'azione (opzionale)'
    },
    response: {
      output: 'Output strutturato dell\'azione',
      stato: 'Stato aggiornato del gioco',
      combattimento: 'Stato aggiornato del combattimento'
    }
  },
  
  NPC: {
    path: '/npc',
    method: 'GET',
    description: 'Ottieni informazioni sugli NPC nella posizione attuale o su un NPC specifico',
    params: {
      id_sessione: 'Identificativo della sessione di gioco (opzionale se specificato id)',
      id: 'ID dell\'NPC specifico (opzionale)'
    },
    response: {
      // Se id specificato: dettagli completi sull'NPC
      // Altrimenti: array di NPC nella posizione corrente
    }
  },
  
  DIALOGO: {
    path: '/dialogo',
    method: 'POST',
    description: 'Gestisci il dialogo con un NPC',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      npc: 'Nome o ID dell\'NPC',
      opzione: 'Opzione di dialogo (opzionale)'
    },
    response: {
      output: 'Output strutturato del dialogo',
      stato: 'Stato aggiornato del gioco',
      opzioni_dialogo: 'Opzioni di dialogo disponibili'
    }
  },
  
  MOSTRI: {
    path: '/mostri',
    method: 'GET',
    description: 'Ottieni informazioni sui mostri',
    params: {
      id: 'ID del mostro specifico (opzionale)'
    },
    response: {
      // Informazioni sui mostri
    }
  },
  
  // Gestione del sistema
  AZIONI_DISPONIBILI: {
    path: '/azioni_disponibili',
    method: 'GET',
    description: 'Ottieni le azioni disponibili nel contesto attuale',
    params: {
      id_sessione: 'Identificativo della sessione di gioco'
    },
    response: {
      azioni: 'Array di azioni disponibili',
      bersagli: 'Possibili bersagli per le azioni',
      contesto: 'Contesto attuale (nome dello stato)'
    }
  },
  
  LOG: {
    path: '/log',
    method: 'GET',
    description: 'Ottieni il log degli eventi recenti',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      max: 'Numero massimo di eventi da restituire (opzionale)'
    },
    response: {
      eventi: 'Array di eventi recenti'
    }
  },
  
  PREFERENZE: {
    path: '/preferenze',
    method: 'POST',
    description: 'Salva le preferenze dell\'utente',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      preferenze: 'Oggetto con le preferenze da salvare'
    },
    response: {
      messaggio: 'Messaggio di conferma'
    }
  },
  
  NOTIFICHE: {
    path: '/notifiche',
    method: 'GET',
    description: 'Ottieni le notifiche per la sessione corrente',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      solo_non_lette: 'Booleano per filtrare solo le notifiche non lette (opzionale)',
      tipo: 'Tipo di notifiche da filtrare (opzionale)',
      limite: 'Numero massimo di notifiche da restituire (opzionale)'
    },
    response: {
      notifiche: 'Array di notifiche',
      totale_non_lette: 'Numero totale di notifiche non lette'
    }
  },
  
  LEGGI_NOTIFICA: {
    path: '/leggi_notifica',
    method: 'POST',
    description: 'Segna una notifica come letta',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      id_notifica: 'ID della notifica da segnare come letta (opzionale se tutte=true)',
      tutte: 'Booleano per segnare tutte le notifiche come lette (opzionale)'
    },
    response: {
      messaggio: 'Messaggio di conferma'
    }
  },
  
  // Gestione di asset e tutorial
  ASSET: {
    path: '/asset/:nome_file',
    method: 'GET',
    description: 'Ottieni un asset grafico',
    params: {
      nome_file: 'Nome del file dell\'asset'
    },
    response: {
      // File dell'asset
    }
  },
  
  ASSETS_INFO: {
    path: '/assets_info',
    method: 'GET',
    description: 'Ottieni informazioni sugli asset disponibili',
    params: {
      tipo: 'Tipo di asset (personaggio, ambiente, oggetto, nemico)'
    },
    response: {
      assets: 'Informazioni sugli asset disponibili'
    }
  },
  
  TUTORIAL: {
    path: '/tutorial',
    method: 'GET',
    description: 'Ottieni informazioni sui tutorial disponibili',
    params: {
      id_sessione: 'Identificativo della sessione di gioco',
      tipo: 'Tipo di tutorial (opzionale)'
    },
    response: {
      // Se tipo specificato: tutorial specifico
      // Altrimenti: tutti i tutorial disponibili
    }
  },
  
  // Endpoint di verifica stato del server
  HEALTH: {
    path: '/health',
    method: 'GET',
    description: 'Verifica lo stato di salute del server',
    params: {},
    response: {
      success: 'Booleano che indica se il server è disponibile',
      data: 'Dati sullo stato del server (status, timestamp, version)',
      messaggio: 'Messaggio informativo'
    }
  }
};

/**
 * Costruisce un URL completo per un endpoint con parametri di query opzionali
 */
const buildUrl = (endpoint, queryParams = {}) => {
  // Assicurati che l'endpoint inizi con una barra
  const formattedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Se non ci sono parametri di query, restituisci l'endpoint
  if (Object.keys(queryParams).length === 0) {
    return formattedEndpoint;
  }
  
  // Costruisci la stringa di query
  const queryString = Object.entries(queryParams)
    .map(([key, value]) => {
      // Gestisci i valori booleani convertendoli in stringhe
      if (typeof value === 'boolean') {
        return `${encodeURIComponent(key)}=${value ? 'true' : 'false'}`;
      }
      return `${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
    })
    .join('&');
  
  // Restituisci l'URL completo
  return `${formattedEndpoint}?${queryString}`;
};

export { API_ENDPOINTS, buildUrl }; 
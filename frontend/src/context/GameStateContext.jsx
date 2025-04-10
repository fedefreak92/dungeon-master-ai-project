import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { getStatoGioco, getMappa, inviaComando, iniziaGioco, getClassi, viaggiaVerso } from '../services/api';

// Stato iniziale
const initialState = {
  giocatore: {
    nome: '',
    classe: '',
    hp: 0,
    max_hp: 0,
    mana: 0,
    mana_max: 0,
    inventario: [],
    equipaggiamento: {},
    statistiche: {}
  },
  mappa: {
    nome: '',
    griglia: [],
    oggetti: [],
    npg: []
  },
  posizione: {
    mappa: '',
    x: 0,
    y: 0
  },
  stato_corrente: null,
  stato_nome: null,
  messaggi: [],
  ultima_azione: null,
  loading: false,
  error: null,
  sessione_attiva: false,
  classiDisponibili: {},
  loadingClassi: false
};

// Reducer per gestire le transizioni di stato
function gameStateReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'UPDATE_GAME_STATE':
      return { ...state, ...action.payload };
    case 'UPDATE_MAP':
      return { ...state, mappa: action.payload };
    case 'SET_ACTIVE_SESSION':
      return { ...state, sessione_attiva: action.payload };
    case 'SET_AVAILABLE_CLASSES':
      return { ...state, classiDisponibili: action.payload, loadingClassi: false };
    case 'SET_LOADING_CLASSES':
      return { ...state, loadingClassi: action.payload };
    case 'ADD_MESSAGE': {
      // Verifica se è un messaggio duplicato recente, specialmente per messaggi di sistema
      const nuoviMessaggi = [...state.messaggi];
      const nuovoMessaggio = action.payload;
      
      // Se ci sono messaggi precedenti, controlla se è un duplicato
      if (nuoviMessaggi.length > 0) {
        const ultimoMsg = nuoviMessaggi[nuoviMessaggi.length - 1];
        
        // Confronta i messaggi per contenuto e tipo
        const isStessoContenuto = (ultimoMsg.testo === nuovoMessaggio.testo);
        const isStessoTipo = (ultimoMsg.tipo === nuovoMessaggio.tipo);
        
        // Se è un messaggio di sistema o errore duplicato, non aggiungerlo
        if (isStessoContenuto && isStessoTipo && (nuovoMessaggio.tipo === 'sistema' || nuovoMessaggio.tipo === 'errore')) {
          // Non aggiungere questo messaggio duplicato
          return state;
        }
      }
      
      // Aggiungi il messaggio
      nuoviMessaggi.push(nuovoMessaggio);
      
      // Limita la lunghezza della cronologia dei messaggi a massimo 100
      if (nuoviMessaggi.length > 100) {
        nuoviMessaggi.shift(); // Rimuovi il messaggio più vecchio
      }
      
      return { ...state, messaggi: nuoviMessaggi };
    }
    case 'CLEAR_MESSAGES':
      return { ...state, messaggi: [] };
    case 'RESET_STATE':
      return initialState;
    default:
      return state;
  }
}

// Creazione del Context
const GameStateContext = createContext();

// Provider
export function GameStateProvider({ children }) {
  const [state, dispatch] = useReducer(gameStateReducer, initialState);

  // Carica lo stato iniziale se esiste una sessione
  useEffect(() => {
    const sessionId = localStorage.getItem('sessionId');
    if (sessionId) {
      dispatch({ type: 'SET_ACTIVE_SESSION', payload: true });
      refreshGameState();
    }
    
    // Carica le classi disponibili
    loadClassi();
  }, []);

  // Carica le classi disponibili
  const loadClassi = async (forceRefresh = false) => {
    try {
      dispatch({ type: 'SET_LOADING_CLASSES', payload: true });
      // Passa il parametro forceRefresh per forzare un aggiornamento dalla cache se necessario
      const data = await getClassi(forceRefresh);
      dispatch({ type: 'SET_AVAILABLE_CLASSES', payload: data });
    } catch (err) {
      console.error('Errore nel caricamento delle classi:', err);
      // In caso di errore, aggiungiamo un messaggio per informare l'utente
      dispatch({ 
        type: 'ADD_MESSAGE', 
        payload: { 
          tipo: 'errore', 
          testo: `Errore nel caricamento delle classi: ${err.message}` 
        } 
      });
    } finally {
      dispatch({ type: 'SET_LOADING_CLASSES', payload: false });
    }
  };

  // Funzione per aggiornare lo stato del gioco
  const refreshGameState = async (force = false) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      const gameStateData = await getStatoGioco();
      
      // Trasforma i dati per adattarli alla struttura del nostro stato
      const mappedState = {
        giocatore: {
          nome: gameStateData.nome,
          classe: gameStateData.classe,
          hp: gameStateData.hp,
          max_hp: gameStateData.max_hp,
          mana: gameStateData.mana || 0,
          mana_max: gameStateData.mana_max || 0,
          inventario: gameStateData.inventario || [],
          equipaggiamento: gameStateData.equipaggiamento || {},
          statistiche: gameStateData.statistiche || {}
        },
        posizione: gameStateData.posizione || state.posizione,
        stato_corrente: gameStateData,
        stato_nome: gameStateData.stato
      };
      
      dispatch({ type: 'UPDATE_GAME_STATE', payload: mappedState });
      
      // Carica anche i dati della mappa
      try {
        const mapData = await getMappa();
        if (mapData) {
          dispatch({ type: 'UPDATE_MAP', payload: mapData });
        }
      } catch (err) {
        console.error('Errore nel caricare la mappa:', err);
      }
      
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (err) {
      console.error('Errore nel refreshState:', err);
      dispatch({ type: 'SET_ERROR', payload: 'Errore nel caricamento dello stato del gioco' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Gestione comandi verso il backend
  const executeCommand = async (command) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'ADD_MESSAGE', payload: { tipo: 'comando', testo: `> ${command}` } });
      
      // Gestione speciale per il comando "viaggia" per evitare l'interazione con l'interfaccia testuale
      if (command.startsWith('viaggia ')) {
        // Estrai la destinazione dal comando
        const destinazione = command.replace('viaggia ', '').trim();
        
        if (destinazione) {
          console.log(`Gestione speciale per viaggia verso ${destinazione}`);
          
          try {
            // Utilizziamo direttamente l'API viaggiaVerso invece di inviaComando
            const viaggioResponse = await viaggiaVerso(destinazione);
            console.log("Risposta viaggio diretto:", viaggioResponse);
            
            // Aggiungi solo una notifica dell'avvenuto spostamento
            dispatch({ 
              type: 'ADD_MESSAGE', 
              payload: { 
                tipo: 'narrativo', 
                testo: `Ti sei spostato verso ${destinazione}`
              } 
            });
            
            // Aggiorna lo stato con più tentativi per assicurarsi che il cambio stato sia completo
            await forceRefreshGameState();
            
            return viaggioResponse;
          } catch (viggioError) {
            console.error(`Errore nel viaggio diretto verso ${destinazione}:`, viggioError);
            throw viggioError;
          }
        }
      }
      
      // Gestione normale per gli altri comandi
      const response = await inviaComando(command);
      
      // Aggiungi i messaggi di risposta, ma filtra quelli della console backend
      if (response.output && Array.isArray(response.output)) {
        // Pattern da escludere - messaggi dell'interfaccia backend da non mostrare nel frontend
        const patternsDaEscludere = [
          /=== SELEZIONE DESTINAZIONE ===/,
          /Dove desideri andare\?/,
          /\d+\.\s+(Cantina|Mercato|Taverna|Torna indietro)/,
          /Scegli una destinazione:/,
          /Inserisci un numero valido/,
          /Premi Invio per continuare.../,
          /La taverna rimane in attesa.../,
          /Ti trovi nella taverna. Cosa vuoi fare\?/,
          /\d+\.\s+(Parla|Viaggia|Mostra|Combatti|Sfida|Esplora|Prova|Visualizza|Muoviti|Interagisci|Salva|Esci)/,
          /Scelta:/,
          /Ti dirigi verso .+\.\.\./,
          /Sei arrivato a .+\./
        ];
        
        // Filtra i messaggi prima di aggiungerli
        response.output.forEach(msg => {
          // Controlla se il messaggio è una stringa
          if (typeof msg === 'string') {
            // Verifica se il messaggio corrisponde a uno dei pattern da escludere
            const daEscludere = patternsDaEscludere.some(pattern => pattern.test(msg));
            if (!daEscludere) {
              dispatch({ type: 'ADD_MESSAGE', payload: { tipo: 'narrativo', testo: msg } });
            }
          } 
          // Se il messaggio è un oggetto, controlla il testo
          else if (msg && typeof msg === 'object' && msg.testo) {
            const daEscludere = patternsDaEscludere.some(pattern => pattern.test(msg.testo));
            if (!daEscludere) {
              dispatch({ type: 'ADD_MESSAGE', payload: msg });
            }
          }
          // Altrimenti aggiungi il messaggio così com'è
          else {
            dispatch({ type: 'ADD_MESSAGE', payload: msg });
          }
        });
      }
      
      // Aggiorna lo stato del gioco
      await refreshGameState();
      
      return response;
    } catch (err) {
      console.error('Errore nell\'esecuzione del comando:', err);
      dispatch({ type: 'ADD_MESSAGE', payload: { tipo: 'errore', testo: `Errore: ${err.message}` } });
      dispatch({ type: 'SET_ERROR', payload: err.message });
      throw err;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Gestione inizio partita
  const startGame = async (nome, classe) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_MESSAGES' });
      
      const response = await iniziaGioco(nome, classe);
      
      if (response.id_sessione) {
        dispatch({ type: 'SET_ACTIVE_SESSION', payload: true });
        
        // Aggiungi il messaggio di benvenuto
        if (response.stato && response.stato.output) {
          dispatch({ type: 'ADD_MESSAGE', payload: { tipo: 'narrativo', testo: response.stato.output } });
        }
        
        // Forza un refresh completo dello stato
        await forceRefreshGameState();
      }
      
      return response;
    } catch (err) {
      console.error('Errore nell\'iniziare il gioco:', err);
      dispatch({ type: 'SET_ERROR', payload: `Errore nell'iniziare il gioco: ${err.message}` });
      throw err;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Funzione per forzare un refresh completo dello stato
  const forceRefreshGameState = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Pulisci la cache del localStorage
      localStorage.removeItem('gameStateCache');
      
      // Forza un refresh immediato
      await refreshGameState(true);
      
      // Forza un secondo refresh dopo un breve delay
      setTimeout(async () => {
        await refreshGameState(true);
      }, 500);
      
      // Forza un terzo refresh dopo un delay più lungo
      setTimeout(async () => {
        await refreshGameState(true);
      }, 2000);
      
    } catch (err) {
      console.error('Errore nel force refresh:', err);
      dispatch({ type: 'SET_ERROR', payload: 'Errore nel refresh forzato dello stato' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Valore fornito dal context
  const value = {
    state,
    dispatch,
    refreshGameState,
    forceRefreshGameState,
    executeCommand,
    startGame,
    loadClassi,
    addMessage: (text, tipo = 'narrativo') => {
      dispatch({ type: 'ADD_MESSAGE', payload: { tipo, testo: text } });
    },
    clearMessages: () => {
      dispatch({ type: 'CLEAR_MESSAGES' });
    },
    resetState: () => {
      dispatch({ type: 'RESET_STATE' });
      localStorage.removeItem('sessionId');
      localStorage.removeItem('gameStateCache');
    }
  };

  return (
    <GameStateContext.Provider value={value}>
      {children}
    </GameStateContext.Provider>
  );
}

// Hook custom per utilizzare il context
export function useGameState() {
  const context = useContext(GameStateContext);
  if (!context) {
    throw new Error('useGameState deve essere utilizzato all\'interno di un GameStateProvider');
  }
  return context;
} 
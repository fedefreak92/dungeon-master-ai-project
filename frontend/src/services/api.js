import axios from 'axios';
import { API_ENDPOINTS, buildUrl } from '../api/api-definitions';

// Impostazioni base per il debug
const DEBUG = true;

// Configurazione di base axios con retry
const api = axios.create({
  baseURL: '/api',  // Usa sempre il prefisso /api/
  timeout: 15000, // Aumentato a 15 secondi per gestire risposte lente
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest' // Impedisce che le risposte siano trattate come HTML
  }
});

// Funzione di debug per logging
const logDebug = (message, data) => {
  if (DEBUG) {
    console.log(`[API Debug] ${message}`, data !== undefined ? data : '');
  }
};

// Gestione sessione
let sessionId = localStorage.getItem('sessionId');

// Contatore di tentativi per richieste fallite
const retryMap = new Map();
const MAX_RETRY = 3;
const RETRY_DELAY = 1000; // 1 secondo di attesa tra i tentativi

// Funzione per gestire automaticamente i retry delle richieste
const handleRetry = async (error, instance) => {
  const { config } = error;
  
  // Se non c'è configurazione, non possiamo fare retry
  if (!config) return Promise.reject(error);
  
  // Genera una chiave unica per questa richiesta
  const requestKey = `${config.method}:${config.url}`;
  
  // Ottieni il contatore corrente o inizializza a 0
  const retryCount = retryMap.get(requestKey) || 0;
  
  // Se abbiamo raggiunto il limite massimo di tentativi, restituisci l'errore
  if (retryCount >= MAX_RETRY) {
    retryMap.delete(requestKey); // Pulisci il contatore
    return Promise.reject(error);
  }
  
  // Incrementa il contatore dei tentativi
  retryMap.set(requestKey, retryCount + 1);
  
  // Solo per errori di rete, timeout o 5xx
  if (!error.response || error.code === 'ECONNABORTED' || 
      (error.response && error.response.status >= 500)) {
    console.log(`Tentativo di riconnessione ${retryCount + 1}/${MAX_RETRY} per ${requestKey}`);
    
    // Attendi RETRY_DELAY millisecondi prima di riprovare
    return new Promise(resolve => {
      setTimeout(() => resolve(instance(config)), RETRY_DELAY);
    });
  }
  
  return Promise.reject(error);
};

// Imposta timeout più lunghi specificamente per l'endpoint di inizializzazione
api.interceptors.request.use(config => {
  // Per l'endpoint /inizia che può richiedere più tempo, aumenta il timeout
  if (config.url === API_ENDPOINTS.INIZIA_GIOCO.path) {
    config.timeout = 30000; // 30 secondi per iniziare il gioco
  }
  
  logDebug(`Invio richiesta ${config.method.toUpperCase()} a ${config.url}`, config.data);
  
  // Imposta sessionId per tutte le richieste
  if (sessionId) {
    // Per le richieste GET, aggiungi alla query string
    if (config.method === 'get') {
      config.params = { ...config.params, id_sessione: sessionId };
    } 
    // Per le altre richieste, aggiungi al body
    else if (config.data) {
      config.data = { ...config.data, id_sessione: sessionId };
    } else {
      config.data = { id_sessione: sessionId };
    }
  }
  return config;
});

// Intercettore per gestire errori comuni
api.interceptors.response.use(
  response => {
    // In caso di successo, azzera il contatore dei tentativi
    const requestKey = `${response.config.method}:${response.config.url}`;
    retryMap.delete(requestKey);
    
    // Log contenuto risposta in debug
    logDebug(`Risposta ricevuta da ${response.config.url}`, response.data);
    
    return response;
  },
  error => {
    if (error.response) {
      // Visualizza il contenuto della risposta di errore in modo dettagliato
      try {
        const responseData = error.response.data;
        console.error('Errore API:', error.response.status, responseData);
        
        // Se la risposta è HTML invece di JSON, è un segnale di errore di configurazione
        if (typeof responseData === 'string' && (responseData.includes('<!doctype html>') || responseData.includes('<!DOCTYPE html>'))) {
          console.error('Ricevuta risposta HTML invece di JSON. Probabile errore di configurazione del proxy.');
          console.error('URL richiesta:', error.config.url);
          console.error('Metodo:', error.config.method);
        }
      } catch (e) {
        console.error('Errore nel parsing della risposta:', e);
      }
      
      // Se riceviamo un 401 (Non autorizzato) o 404 (Non trovato) sulla sessione
      if (error.response.status === 401 || 
         (error.response.status === 404 && error.response.data?.errore?.includes('sessione'))) {
        console.warn('Sessione non valida, reindirizzamento alla pagina iniziale');
        // Rimuovi l'ID sessione non valido
        localStorage.removeItem('sessionId');
        sessionId = null;
        
        // Invia evento personalizzato per notificare l'app della sessione scaduta
        const event = new CustomEvent('sessioneScaduta');
        window.dispatchEvent(event);
      }
      
      // Non ritentare per errori 4xx, solo per errori 5xx
      if (error.response.status >= 500) {
        return handleRetry(error, api);
      }
    } else if (error.request) {
      console.error('Nessuna risposta ricevuta dal server:', error.request);
      
      // Tenta di riconnettersi per errori di rete
      const retryResponse = handleRetry(error, api);
      
      // Se abbiamo raggiunto il limite massimo di tentativi
      if (retryResponse === Promise.reject(error)) {
        // Invia evento personalizzato per notificare l'app della connessione persa
        const event = new CustomEvent('connessionePersa');
        window.dispatchEvent(event);
      }
      
      return retryResponse;
    } else {
      console.error('Errore di configurazione della richiesta:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export const iniziaGioco = async (nome, classe) => {
  try {
    // Prima di avviare il gioco, verifica che il server sia disponibile
    const healthCheck = await checkHealth().catch(err => {
      console.warn("Impossibile contattare il server:", err);
      throw new Error("Il server non è raggiungibile. Riprova più tardi.");
    });
    
    console.log("Stato di salute del server:", healthCheck);
    
    // Se il server è disponibile, procedi con l'avvio del gioco
    const data = {
      nome: nome,
      classe: classe 
    };
    
    logDebug('Richiesta inizia gioco', data);
    
    // Assicurati di usare l'URL completo con /api/
    const response = await api.post(API_ENDPOINTS.INIZIA_GIOCO.path, data);
    
    // Verifica che la risposta contenga l'ID sessione
    if (!response.data.id_sessione) {
      throw new Error("Risposta del server non valida: manca l'ID sessione");
    }
    
    sessionId = response.data.id_sessione;
    localStorage.setItem('sessionId', sessionId);
    return response.data;
  } catch (error) {
    console.error('Errore nell\'iniziare il gioco:', error);
    throw error;
  }
};

export const inviaComando = async (comando) => {
  try {
    const response = await api.post(API_ENDPOINTS.COMANDO.path, { comando });
    return response.data;
  } catch (error) {
    console.error('Errore nell\'inviare il comando:', error);
    throw error;
  }
};

export const getMappa = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.MAPPA.path);
    
    // Trasforma i dati della mappa per renderli utilizzabili dal frontend
    const mappaData = response.data;
    
    // Aggiungi informazioni sulla posizione corrente del giocatore
    const statoResponse = await api.get(API_ENDPOINTS.STATO.path);
    if (statoResponse.data && statoResponse.data.posizione) {
      mappaData.posizione_giocatore = {
        x: statoResponse.data.posizione.x,
        y: statoResponse.data.posizione.y
      };
    }
    
    return mappaData;
  } catch (error) {
    console.error('Errore nel recuperare la mappa:', error);
    throw error;
  }
};

export const muoviGiocatore = async (direzione) => {
  try {
    // Prima controlla se siamo in uno stato che potrebbe richiedere interazione testuale
    const statoAttuale = await getStatoGioco();
    const nomeStato = (statoAttuale.stato || "").toLowerCase();
    
    // Se siamo in uno stato di selezione mappa, non permettere il movimento
    if (nomeStato.includes("sceltamappa") || nomeStato === "scelta_mappa") {
      console.warn("Impossibile muoversi durante la selezione della mappa");
      return { 
        spostamento: false, 
        messaggio: "Non puoi muoverti in questa fase. Seleziona prima una destinazione." 
      };
    }
    
    // Usa una variabile per il tracciamento del tentativo
    let tentativo = 0;
    const maxTentativi = 2;
    
    // Funzione per eseguire la richiesta di movimento
    const eseguiRichiesta = async () => {
      tentativo++;
      
      try {
        // Esegui la richiesta API normale
        const response = await api.post(API_ENDPOINTS.MUOVI.path, { direzione });
        
        // Se la risposta contiene l'inizio del menu di selezione, siamo bloccati
        if (response.data && response.data.output) {
          const output = Array.isArray(response.data.output) 
            ? response.data.output.join(' ')
            : String(response.data.output);
            
          // Controlla se l'output contiene il menu di selezione delle destinazioni
          if (output.includes("SELEZIONE DESTINAZIONE") || 
              output.includes("Dove desideri andare?")) {
            
            // Se siamo ancora nei tentativi, prova con un approccio diverso
            if (tentativo < maxTentativi) {
              console.warn(`Rilevato menu selezione destinazione, tentativo alternativo ${tentativo}`);
              
              // Prova a usare l'endpoint comando direttamente per sbloccarci
              const comandoResponse = await api.post(API_ENDPOINTS.COMANDO.path, { 
                comando: "no" // Usiamo "no" per uscire dal dialogo
              });
              
              // Attendi un breve momento
              await new Promise(resolve => setTimeout(resolve, 500));
              
              // Riprova la richiesta di movimento
              return await eseguiRichiesta();
            } else {
              // Troppi tentativi, restituisci un errore "pulito"
              console.error("Impossibile muoversi, troppi tentativi falliti");
              return { 
                spostamento: false, 
                messaggio: `Non puoi muoverti verso ${direzione} in questo momento.`
              };
            }
          }
        }
        
        // Se la risposta è valida e non contiene il menu, restituisci i dati
        return response.data;
        
      } catch (error) {
        console.error(`Errore nel tentativo ${tentativo} di spostamento:`, error);
        // Se abbiamo ancora tentativi, riprova
        if (tentativo < maxTentativi) {
          console.warn("Nuovo tentativo...");
          return await eseguiRichiesta();
        }
        throw error;
      }
    };
    
    // Avvia la richiesta con il meccanismo di retry
    return await eseguiRichiesta();
    
  } catch (error) {
    console.error('Errore nello spostamento:', error);
    throw error;
  }
};

export const getStatoGioco = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.STATO.path);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare lo stato:', error);
    throw error;
  }
};

export const salvaPartita = async (nomeFile) => {
  try {
    const response = await api.post(API_ENDPOINTS.SALVA.path, { nome_file: nomeFile });
    return response.data;
  } catch (error) {
    console.error('Errore nel salvare la partita:', error);
    throw error;
  }
};

export const caricaPartita = async (nomeFile) => {
  try {
    const response = await api.post(API_ENDPOINTS.CARICA.path, { nome_file: nomeFile });
    return response.data;
  } catch (error) {
    console.error('Errore nel caricare la partita:', error);
    throw error;
  }
};

export const getInventario = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.INVENTARIO.path);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare l\'inventario:', error);
    throw error;
  }
};

export const getSalvataggi = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.SALVATAGGI.path);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare i salvataggi:', error);
    throw error;
  }
};

export const getStatistiche = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.STATISTICHE.path);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare le statistiche:', error);
    throw error;
  }
};

export const getAzioniDisponibili = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.AZIONI_DISPONIBILI.path);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare le azioni disponibili:', error);
    throw error;
  }
};

export const getDestinazioniDisponibili = async () => {
  try {
    console.log("Invio richiesta per ottenere destinazioni disponibili...");
    // Ottieni il sessionId
    const sessionId = localStorage.getItem('sessionId');
    console.log("Session ID per richiesta destinazioni:", sessionId);
    
    // Costruisci l'URL con il parametro id_sessione
    let url = API_ENDPOINTS.DESTINAZIONI.path;
    
    // Verifica che l'interceptor sia in funzione mostrando l'URL effettivo
    console.log("URL endpoint destinazioni:", url);
    
    const response = await api.get(url);
    console.log("Risposta destinazioni ricevuta:", response.data);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare le destinazioni disponibili:', error);
    console.error('Dettagli errore:', error.response ? error.response.data : 'Nessun dettaglio disponibile');
    // Se c'è un errore, restituisci un array vuoto per consentire l'uso dei valori predefiniti nel componente
    return [];
  }
};

export const esploraAmbiente = async () => {
  try {
    const response = await api.post(API_ENDPOINTS.ESPLORA.path);
    return response.data;
  } catch (error) {
    console.error('Errore nell\'esplorare l\'ambiente:', error);
    throw error;
  }
};

export const getNotifiche = async (soloNonLette = true, tipo = null, limite = 50) => {
  try {
    let url = `${API_ENDPOINTS.NOTIFICHE.path}?solo_non_lette=${soloNonLette}`;
    if (tipo) url += `&tipo=${tipo}`;
    if (limite) url += `&limite=${limite}`;
    
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Errore nel recuperare le notifiche:', error);
    throw error;
  }
};

export const leggiNotifica = async (idNotifica) => {
  try {
    const response = await api.post(API_ENDPOINTS.LEGGI_NOTIFICA.path, { id_notifica: idNotifica });
    return response.data;
  } catch (error) {
    console.error('Errore nel segnare la notifica come letta:', error);
    throw error;
  }
};

export const leggiTutteLeNotifiche = async () => {
  try {
    const response = await api.post(API_ENDPOINTS.LEGGI_NOTIFICA.path, { tutte: true });
    return response.data;
  } catch (error) {
    console.error('Errore nel segnare tutte le notifiche come lette:', error);
    throw error;
  }
};

export const gestisciEquipaggiamento = async (azione, oggetto, slot = null) => {
  try {
    const payload = { azione, oggetto };
    if (slot) payload.slot = slot;
    
    const response = await api.post(API_ENDPOINTS.EQUIPAGGIAMENTO.path, payload);
    return response.data;
  } catch (error) {
    console.error('Errore nella gestione dell\'equipaggiamento:', error);
    throw error;
  }
};

export const interagisciOggetto = async (oggetto, azione = 'usa') => {
  try {
    const response = await api.post(API_ENDPOINTS.OGGETTO.path, { oggetto, azione });
    return response.data;
  } catch (error) {
    console.error('Errore nell\'interagire con l\'oggetto:', error);
    throw error;
  }
};

export const gestisciDialogo = async (npc, opzione = '') => {
  try {
    const payload = { npc };
    if (opzione) payload.opzione = opzione;
    
    const response = await api.post(API_ENDPOINTS.DIALOGO.path, payload);
    return response.data;
  } catch (error) {
    console.error('Errore nella gestione del dialogo:', error);
    throw error;
  }
};

export const usaAbilita = async (idAbilita, bersaglio = '') => {
  try {
    const payload = { id_abilita: idAbilita };
    if (bersaglio) payload.bersaglio = bersaglio;
    
    const response = await api.post(API_ENDPOINTS.USA_ABILITA.path, payload);
    return response.data;
  } catch (error) {
    console.error('Errore nell\'usare l\'abilità:', error);
    throw error;
  }
};

export const eliminaSalvataggio = async (nomeFile) => {
  try {
    const response = await api.post(API_ENDPOINTS.ELIMINA_SALVATAGGIO.path, { nome_file: nomeFile });
    return response.data;
  } catch (error) {
    console.error('Errore nell\'eliminare il salvataggio:', error);
    throw error;
  }
};

// Funzione per terminare la sessione di gioco (logout)
export const terminaSessione = () => {
  sessionId = null;
  localStorage.removeItem('sessionId');
};

// Funzione specifica per viaggiare verso una destinazione
export const viaggiaVerso = async (destinazione) => {
  try {
    console.log(`Iniziando viaggio verso ${destinazione}...`);
    
    // 1. Eseguiamo la chiamata API con il comando di viaggio
    const response = await api.post(API_ENDPOINTS.COMANDO.path, { comando: `viaggia ${destinazione}` });
    
    // 2. Per garantire il cambio di stato, aspettiamo un breve momento
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 3. Otteniamo lo stato corrente per verificare se siamo ancora in modalità "scelta mappa"
    const statoCorrente = await getStatoGioco();
    console.log(`Stato dopo prima chiamata viaggio: ${statoCorrente.stato}`);
    
    // 4. Se siamo ancora in stato di scelta mappa, dobbiamo completare il processo
    if (statoCorrente.stato === 'SceltaMappaState' || 
        statoCorrente.stato === 'scelta_mappa' || 
        statoCorrente.stato?.toLowerCase().includes('sceltamappa')) {
      
      console.log("Siamo ancora in modalità scelta mappa, tentiamo di completare il processo...");
      
      // Otteniamo le destinazioni disponibili per trovare l'indice corretto
      const destinazioni = await getDestinazioniDisponibili();
      
      // Troviamo l'indice della destinazione selezionata
      let selezioneIdx = -1;
      for (let i = 0; i < destinazioni.length; i++) {
        if (destinazioni[i].id === destinazione) {
          selezioneIdx = i + 1; // +1 perché gli indici nelle selezioni solitamente partono da 1
          break;
        }
      }
      
      // Se non troviamo l'indice, usiamo 1 come fallback solo per tentare di procedere
      if (selezioneIdx === -1) {
        console.warn(`Destinazione ${destinazione} non trovata nelle destinazioni disponibili`);
        selezioneIdx = 1;
      }
      
      // Invia la scelta numerica come comando diretto
      console.log(`Inviando selezione numerica: ${selezioneIdx}`);
      const completaResponse = await api.post(API_ENDPOINTS.COMANDO.path, { 
        comando: `${selezioneIdx}` 
      });
      
      console.log("Risposta dopo completamento:", completaResponse.data);
      
      // Attendiamo ancora per dare tempo al backend di processare
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Controlliamo di nuovo lo stato
      const statoFinale = await getStatoGioco();
      console.log(`Stato finale dopo completamento: ${statoFinale.stato}`);
      
      // Restituiamo la risposta più recente
      return completaResponse.data;
    }
    
    // Se il cambio di stato è già avvenuto, restituiamo la risposta originale
    return response.data;
  } catch (error) {
    console.error(`Errore nel viaggiare verso ${destinazione}:`, error);
    throw error;
  }
};

// Cache per le classi
let classiCache = null;

export const getClassi = async (forceRefresh = false) => {
  // Se abbiamo già i dati in cache e non è richiesto un refresh, usiamo la cache
  if (classiCache && !forceRefresh) {
    console.log("Utilizzo classi dalla cache locale");
    return classiCache;
  }

  try {
    console.log("Richiesta classi inviata al server...");
    
    // Usa axios direttamente per avere più controllo
    const response = await axios({
      method: 'GET',
      url: '/api/classi',  // Usa il percorso completo con /api/
      timeout: 5000,
      headers: {
        'Cache-Control': 'no-cache',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      responseType: 'text'  // Usa text per processare manualmente il JSON
    });
    
    console.log("Status risposta classi:", response.status);
    
    let classi;
    
    // Se è una stringa, potrebbe essere JSON o HTML
    if (typeof response.data === 'string') {
      // Controlla se è HTML
      if (response.data.includes('<!DOCTYPE html>') || response.data.includes('<!doctype html>')) {
        console.warn("Ricevuto HTML invece di JSON dalla richiesta classi");
        // Usa le classi predefinite
        classi = getClassiPredefinite();
      } else {
        // Prova a parsare come JSON
        try {
          classi = JSON.parse(response.data);
          console.log("Dati classi parserati con successo:", Object.keys(classi));
        } catch (e) {
          console.error("Errore nel parsare la risposta classi come JSON:", e);
          classi = getClassiPredefinite();
        }
      }
    } else {
      // Se non è una stringa, usa direttamente
      classi = response.data;
    }
    
    // Se la risposta è valida e non vuota, usa i dati ricevuti
    if (classi && typeof classi === 'object' && Object.keys(classi).length > 0) {
      console.log("Utilizzo classi dal server:", Object.keys(classi));
      // Salva in cache
      classiCache = classi;
      return classi;
    } else {
      console.warn("Risposta classi vuota o non valida dal server. Uso dati predefiniti.");
      const classiPredefinite = getClassiPredefinite();
      // Salva in cache le classi predefinite
      classiCache = classiPredefinite;
      return classiPredefinite;
    }
  } catch (error) {
    console.error('Errore nel recuperare le classi:', error);
    console.error('Dettagli errore:', error.response ? error.response.data : 'Nessuna risposta');
    const classiPredefinite = getClassiPredefinite();
    // Salva in cache le classi predefinite in caso di errore
    classiCache = classiPredefinite;
    return classiPredefinite;
  }
};

// Funzione helper per ottenere classi predefinite più complete
const getClassiPredefinite = () => {
  console.log("Utilizzo classi predefinite");
  return {
    "guerriero": {
      "nome": "Guerriero",
      "descrizione": "Un combattente specializzato nell'uso delle armi e delle armature pesanti",
      "statistiche_base": {
        "forza": 15,
        "destrezza": 10,
        "costituzione": 14,
        "intelligenza": 8,
        "saggezza": 10,
        "carisma": 9
      }
    },
    "mago": {
      "nome": "Mago",
      "descrizione": "Un incantatore che ha imparato a manipolare la magia attraverso lo studio",
      "statistiche_base": {
        "forza": 6,
        "destrezza": 10,
        "costituzione": 8,
        "intelligenza": 16,
        "saggezza": 12,
        "carisma": 10
      }
    },
    "ladro": {
      "nome": "Ladro", 
      "descrizione": "Un abile furfante specializzato nella furtività e nelle serrature",
      "statistiche_base": {
        "forza": 8,
        "destrezza": 16,
        "costituzione": 10,
        "intelligenza": 12,
        "saggezza": 10,
        "carisma": 12
      }
    },
    "chierico": {
      "nome": "Chierico",
      "descrizione": "Un sacerdote che canalizza la potenza divina",
      "statistiche_base": {
        "forza": 10,
        "destrezza": 8,
        "costituzione": 12,
        "intelligenza": 10,
        "saggezza": 16,
        "carisma": 12
      }
    }
  };
};

// Funzione per verificare la salute del server
export const checkHealth = async () => {
  try {
    console.log("Controllo salute del server iniziato...");
    // Assicurati di usare il percorso completo con /api/ e aggiungi parametro per evitare caching
    const response = await axios({
      method: 'GET',
      url: `/api/health?t=${Date.now()}`,
      timeout: 8000, // Aumentato a 8 secondi per consentire risposte più lente
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      responseType: 'text',  // Usa text per processare manualmente il JSON
    });
    
    console.log("Risposta salute server ricevuta:", response.status);
    
    // Controlla il Content-Type della risposta
    const contentType = response.headers['content-type'];
    const responseData = response.data;
    
    console.log(`Content-Type ricevuto: ${contentType || 'non specificato'}`);
    
    let jsonData;
    
    // Se è una stringa, potrebbe essere JSON o HTML
    if (typeof responseData === 'string') {
      // Controlla se è HTML
      if (responseData.includes('<!DOCTYPE html>') || responseData.includes('<!doctype html>')) {
        console.warn("Ricevuto HTML invece di JSON:", responseData.substring(0, 100));
        // Segnala un errore invece di continuare silenziosamente
        jsonData = { 
          success: false, 
          errore: 'Risposta HTML ricevuta dal server', 
          dettagli: 'Il server potrebbe essere non disponibile o ci sono problemi di configurazione'
        };
      } else {
        // Prova a parsare come JSON
        try {
          jsonData = JSON.parse(responseData);
          console.log("JSON parserato con successo");
        } catch (e) {
          console.error("Errore nel parsare la risposta come JSON:", e);
          // Segnala l'errore di parsing
          jsonData = { 
            success: false, 
            errore: 'Errore nel parsare la risposta JSON', 
            dettagli: e.message 
          };
        }
      }
    } else {
      // Se non è una stringa, usa direttamente
      jsonData = responseData;
    }
    
    // Verifica se abbiamo ricevuto una risposta di errore
    if (!jsonData || typeof jsonData !== 'object' || !jsonData.success) {
      console.warn("Risposta non standard ricevuta:", jsonData);
      
      // Se è già un oggetto di errore con il flag success: false, usalo
      if (jsonData && jsonData.success === false) {
        return jsonData;
      }
      
      // Altrimenti crea un oggetto di errore generico
      return { 
        success: false, 
        errore: 'Risposta non standard dal server', 
        dettagli: 'Il server ha risposto ma il formato non è quello atteso'
      };
    }
    
    return jsonData;
  } catch (error) {
    console.error('Errore nel controllo di salute:', error);
    // Restituisci un oggetto di errore dettagliato
    return { 
      success: false, 
      errore: 'Errore di connessione al server', 
      dettagli: error.message,
      timeout: error.code === 'ECONNABORTED' 
    };
  }
};

// Funzione per monitorare periodicamente la salute del server
export const startHealthMonitor = (intervalMs = 30000) => {
  let monitorId = null;
  let consecutiveFailures = 0;
  
  const checkServerHealth = async () => {
    try {
      const healthResponse = await checkHealth();
      
      // Ora controlliamo il flag success per determinare se il controllo è riuscito
      if (healthResponse.success === false) {
        consecutiveFailures++;
        console.warn(`Controllo di salute fallito ${consecutiveFailures} volte consecutive`);
        console.warn(`Motivo: ${healthResponse.errore} - ${healthResponse.dettagli || ''}`);
        
        // Se fallisce più di 3 volte consecutive, notifica l'utente
        if (consecutiveFailures >= 3) {
          const event = new CustomEvent('connessionePersa', { 
            detail: { 
              errore: healthResponse.errore,
              dettagli: healthResponse.dettagli
            } 
          });
          window.dispatchEvent(event);
        }
      } else {
        if (consecutiveFailures > 0) {
          console.log('Connessione al server ristabilita');
        }
        consecutiveFailures = 0; // Reset del contatore degli errori
      }
    } catch (error) {
      consecutiveFailures++;
      console.warn(`Errore imprevisto nel controllo di salute ${consecutiveFailures} volte consecutive:`, error);
      
      // Se fallisce più di 3 volte consecutive, notifica l'utente
      if (consecutiveFailures >= 3) {
        const event = new CustomEvent('connessionePersa');
        window.dispatchEvent(event);
      }
    }
  };
  
  // Avvia il monitoraggio periodico
  monitorId = setInterval(checkServerHealth, intervalMs);
  
  // Prima verifica immediata
  checkServerHealth();
  
  // Ritorna una funzione per interrompere il monitoraggio
  return () => {
    if (monitorId) {
      clearInterval(monitorId);
    }
  };
};

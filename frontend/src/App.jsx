import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useGameState } from './context/GameStateContext';
import { muoviGiocatore, startHealthMonitor, getDestinazioniDisponibili, viaggiaVerso } from './services/api';
import { useNavigate } from 'react-router-dom';

import Grid from './components/Grid';
import CommandPanel from './components/CommandPanel';
import StatusBar from './components/StatusBar';
import DialogBox from './components/DialogBox';
import ActionButtons from './components/ActionButtons';
import NotificationPanel from './components/NotificationPanel';
import SceltaMappa from './components/SceltaMappa';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #111;
  color: #fff;
  font-family: monospace;
`;

const MainContainer = styled.div`
  display: flex;
  flex: 1;
`;

const GameContainer = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 10px;
`;

const GameHeader = styled.div`
  background-color: #222;
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #444;
`;

const GameTitle = styled.h1`
  margin: 0;
  color: #FFFF00;
`;

const StartGameForm = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
  margin: 0 auto;
  max-width: 400px;
`;

const HeroTitle = styled.h1`
  color: #FFFF00;
  margin-bottom: 30px;
  text-align: center;
  font-size: 28px;
`;

const FormInput = styled.input`
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  padding: 12px;
  margin: 10px 0;
  width: 100%;
  font-family: monospace;
  font-size: 16px;
  
  &:focus {
    border-color: #FFFF00;
    outline: none;
  }
`;

const FormSelect = styled.select`
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  padding: 12px;
  margin: 10px 0;
  width: 100%;
  font-family: monospace;
  font-size: 16px;
  
  &:focus {
    border-color: #FFFF00;
    outline: none;
  }
`;

const FormButton = styled.button`
  background-color: #444;
  color: #FFFF00;
  border: 1px solid #555;
  padding: 15px 25px;
  margin-top: 30px;
  cursor: pointer;
  font-family: monospace;
  font-size: 18px;
  font-weight: bold;
  transition: all 0.3s ease;
  
  &:hover {
    background-color: #555;
    transform: scale(1.05);
  }
  
  &:active {
    background-color: #666;
  }
`;

const ErrorMessage = styled.div`
  color: #FF4444;
  margin-top: 10px;
  font-size: 14px;
  text-align: center;
`;

const ClassDescription = styled.p`
  color: #AAA;
  font-size: 14px;
  margin: 5px 0 15px 0;
  text-align: center;
`;

const ContentContainer = styled.div`
  display: flex;
  flex: 1;
`;

const MainSectionContainer = styled.div`
  display: flex;
  flex: 1;
  background-color: #111;
`;

const MainGameArea = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const GameGridContainer = styled.div`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  background-color: #222;
  border: 1px solid #444;
  margin: 10px;
`;

const DialogContainer = styled.div`
  height: 250px;
  margin: 10px;
  overflow-y: auto;
  background-color: #222;
  border: 1px solid #444;
  padding: 10px;
  font-family: monospace;
  font-size: 14px;
  color: #ddd;
`;

const App = () => {
  const { 
    state, 
    executeCommand, 
    startGame, 
    refreshGameState, 
    addMessage,
    forceRefreshGameState
  } = useGameState();
  
  const [playerName, setPlayerName] = useState('');
  const [playerClass, setPlayerClass] = useState('guerriero');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSceltaMappa, setShowSceltaMappa] = useState(false);
  const [connessionePersa, setConnessionePersa] = useState(false);
  const [sessioneScaduta, setSessioneScaduta] = useState(false);
  const navigate = useNavigate();
  const [mostraSceltaMappa, setMostraSceltaMappa] = useState(false);
  const [chiaveSceltaMappa, setChiaveSceltaMappa] = useState(0);

  // Estrai i dati dallo stato globale
  const { 
    giocatore, 
    stato_nome, 
    messaggi, 
    loading, 
    error,
    sessione_attiva,
    classiDisponibili,
    loadingClassi
  } = state;

  // Imposta la classe del personaggio quando vengono caricate le classi
  useEffect(() => {
    if (classiDisponibili && Object.keys(classiDisponibili).length > 0 && !playerClass) {
      setPlayerClass(Object.keys(classiDisponibili)[0]);
    }
    
    // Log per debug
    console.log("Classi disponibili:", classiDisponibili);
  }, [classiDisponibili, playerClass]);

  // Effetto per mostrare automaticamente la mappa di scelta dopo l'inizio del gioco
  useEffect(() => {
    const statiMappaValidi = ["sceltamappastate", "scelta_mappa", "sceltamappa"];
    const statoCorrente = (stato_nome || "").toLowerCase();
    const isMapSelection = sessione_attiva && (
      statiMappaValidi.some(s => statoCorrente.includes(s)) ||
      statoCorrente === "scelta_mappa"
    );
    
    if (isMapSelection && !showSceltaMappa) {
      setShowSceltaMappa(true);
      addMessage("Scegli la mappa su cui vuoi giocare");
      
      // Forza un refresh dello stato quando si mostra la scelta mappa
      forceRefreshGameState();
    }
  }, [sessione_attiva, stato_nome, addMessage, showSceltaMappa, forceRefreshGameState]);

  // Gestisce i tasti freccia per il movimento
  useEffect(() => {
    const handleKeyDown = async (e) => {
      if (!sessione_attiva) return;
      
      let direction = null;
      
      switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
          direction = 'nord';
          break;
        case 'ArrowDown':
        case 's':
        case 'S':
          direction = 'sud';
          break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
          direction = 'ovest';
          break;
        case 'ArrowRight':
        case 'd':
        case 'D':
          direction = 'est';
          break;
        default:
          return; // Altri tasti non ci interessano
      }
      
      if (direction) {
        try {
          // Verifica se siamo nello stato di SceltaMappaState
          const statoAttuale = (stato_nome || "").toLowerCase();
          if (statoAttuale.includes("sceltamappa") || statoAttuale === "scelta_mappa") {
            console.log("Movimento bloccato in stato di selezione mappa");
            return; // Non permettere movimenti in stato di selezione mappa
          }
          
          // Visualizza il comando ma senza eseguirlo realmente
          addMessage(`> muovi ${direction}`, 'comando');
          
          // Prepara un oggetto mappa fittizio per le risposte in caso di errore
          const mappaAttuale = state.mappa && state.mappa.nome ? state.mappa.nome : "sconosciuta";
          
          try {
            // Usa l'API direttamente, evitando l'interfaccia testuale
            const response = await muoviGiocatore(direction);
            
            // Gestisci la risposta e ignora l'interfaccia testuale
            if (response && response.spostamento) {
              if (response.spostamento === true) {
                // Movimento riuscito
                addMessage(`Ti sposti verso ${direction}`, 'narrativo');
              } else if (typeof response.spostamento === 'string') {
                // Messaggio specifico
                addMessage(response.spostamento, 'narrativo');
              } else {
                // Nessun messaggio specifico, aggiungi uno predefinito
                addMessage(`Hai provato a muoverti verso ${direction}`, 'narrativo');
              }
            } else {
              // Nessun dato di spostamento nella risposta
              addMessage(`Non puoi andare in quella direzione`, 'narrativo');
            }
            
            // Forza un aggiornamento dello stato
            refreshGameState();
          } catch (err) {
            console.error('Errore nel movimento:', err);
            // Aggiungi un messaggio di errore senza mostrare i dettagli dell'interfaccia testuale
            addMessage(`Non puoi muoverti verso ${direction} ora`, 'errore');
          }
        } catch (err) {
          console.error('Errore durante il movimento:', err);
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sessione_attiva, refreshGameState, addMessage, stato_nome, state.mappa]);

  // Funzione per gestire le azioni dei pulsanti
  const handleAction = async (action) => {
    console.log(`Azione richiesta: ${action}`);
    
    switch (action) {
      case 'viaggia':
        // Usa la nuova funzione per mostrare la mappa
        mostraMappa();
        break;
      case 'pg':
        executeCommand('stato');
        break;
      case 'inventario':
        executeCommand('inventario');
        break;
      case 'scelta_mappa':
        setShowSceltaMappa(true);
        break;
      case 'attacco':
        executeCommand('attacca');
        break;
      case 'tiro_dadi':
        executeCommand('tira_dadi');
        break;
      case 'compra':
        executeCommand('compra pozione');
        break;
      case 'vendi':
        executeCommand('vendi');
        break;
      case 'parla_mercante':
      case 'parla_taverna':
        executeCommand('parla');
        break;
      case 'riposa':
        executeCommand('aspetta');
        break;
      case 'riposa_ore':
        executeCommand('riposa 8');
        break;
      case 'medita':
        executeCommand('medita 4');
        break;
      case 'vedi_orario':
        executeCommand('tempo');
        break;
      case 'esplora':
        executeCommand('esplora');
        break;
      case 'interagisci':
        executeCommand('interagisci');
        break;
      case 'abilita':
        executeCommand('abilita');
        break;
      case 'mappa':
        executeCommand('mappa');
        break;
      case 'difesa':
        executeCommand('difendi');
        break;
      case 'usa_pozione':
        executeCommand('usa pozione');
        break;
      case 'fuggi':
        executeCommand('fuggi');
        break;
      case 'salva':
        executeCommand('salva');
        break;
      default:
        addMessage(`Azione non riconosciuta: ${action}`, 'errore');
    }
  };

  // Funzione per gestire la selezione della destinazione
  const handleSelectDestination = async (destinazione) => {
    try {
      addMessage(`Hai scelto di viaggiare verso: ${destinazione}`, 'narrativo');
      
      // Nascondi il componente SceltaMappa
      setShowSceltaMappa(false);
      
      // Memorizza lo stato iniziale per confronto
      const statoIniziale = stato_nome;
      console.log(`Stato iniziale prima del viaggio: ${statoIniziale}`);
      
      // Usa direttamente viaggiaVerso invece di executeCommand
      const { viaggiaVerso } = await import('./services/api');
      const risultatoViaggio = await viaggiaVerso(destinazione);
      console.log("Risultato viaggio diretto:", risultatoViaggio);
      
      // Aggiungi messaggio di conferma
      addMessage(`Ti sei spostato verso ${destinazione}`, 'narrativo');
      
      // Attendi un momento e poi forza un refresh dello stato
      setTimeout(async () => {
        console.log("Forzando refresh dello stato dopo il viaggio");
        await forceRefreshGameState();
        
        // Verifica se lo stato è cambiato rispetto a quello iniziale
        if (state.stato_nome === statoIniziale || 
            state.stato_nome === 'SceltaMappaState' || 
            (state.stato_nome || '').toLowerCase().includes('sceltamappa')) {
          
          console.warn(`ATTENZIONE: Stato non cambiato (${state.stato_nome}), avvio procedura di recupero...`);
          
          // Prova un approccio più diretto
          try {
            // Notifica l'utente
            addMessage(`Finalizzando viaggio verso ${destinazione}...`, 'sistema');
            
            // Invia direttamente un numero basato sulla destinazione
            let indiceDestinazione = 1; // Default per cantina
            if (destinazione.toLowerCase() === 'taverna') indiceDestinazione = 3;
            if (destinazione.toLowerCase() === 'mercato') indiceDestinazione = 2;
            
            console.log(`Invio selezione numerica: ${indiceDestinazione}`);
            
            // Usa direttamente l'API per inviare la selezione numerica
            await executeCommand(indiceDestinazione.toString());
            
            // Attendi un momento e poi verifica di nuovo
            setTimeout(async () => {
              await forceRefreshGameState();
              
              if (state.stato_nome !== statoIniziale) {
                console.log(`Recupero riuscito! Nuovo stato: ${state.stato_nome}`);
                addMessage(`Sei arrivato a ${destinazione}`, 'narrativo');
              } else {
                console.error("Impossibile cambiare stato anche dopo il recupero");
                addMessage(`Problemi nel completare il viaggio. Riprova.`, 'errore');
              }
            }, 1000);
          } catch (err) {
            console.error("Errore nel tentativo di recupero:", err);
          }
        } else {
          console.log(`Cambio stato riuscito: da ${statoIniziale} a ${state.stato_nome}`);
        }
      }, 2000);
    } catch (err) {
      console.error("Errore nel viaggio:", err);
      addMessage(`Errore nel viaggio: ${err.message}`, 'errore');
    }
  };

  // Funzione per mostrare la mappa con force refresh
  const mostraMappa = () => {
    setChiaveSceltaMappa(prevKey => prevKey + 1); // Incrementa la chiave per forzare il refresh
    setMostraSceltaMappa(true);
  };

  // Funzione per gestire i messaggi dal componente SceltaMappa
  const handleMessageUpdate = (messaggio, tipo = 'sistema') => {
    console.log(`App: handleMessageUpdate chiamata con messaggio "${messaggio}" di tipo "${tipo}"`);
    if (typeof addMessage === 'function') {
      addMessage(messaggio, tipo);
    } else {
      console.error("Errore: addMessage non è una funzione disponibile");
    }
  };

  // Renderizza il form di inizio gioco
  const renderStartGameForm = () => {
    // Assicurati che ci siano sempre classi disponibili, anche vuote
    const classiVisualizzabili = classiDisponibili && Object.keys(classiDisponibili).length > 0 
      ? classiDisponibili 
      : { "guerriero": { nome: "Guerriero", descrizione: "Un combattente valoroso" } };
      
    return (
      <StartGameForm>
        <HeroTitle>🧙‍ Dungeon Master AI 🏰</HeroTitle>
        
        <FormInput
          type="text"
          placeholder="Il tuo nome"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
        />
        
        <FormSelect
          value={playerClass}
          onChange={(e) => setPlayerClass(e.target.value)}
          disabled={loadingClassi}
        >
          {Object.keys(classiVisualizzabili).map(classe => (
            <option key={classe} value={classe}>
              {classiVisualizzabili[classe].nome || classe}
            </option>
          ))}
        </FormSelect>
        
        {playerClass && classiVisualizzabili[playerClass] && (
          <ClassDescription>
            {classiVisualizzabili[playerClass].descrizione || "Nessuna descrizione disponibile."}
          </ClassDescription>
        )}
        
        <FormButton onClick={handleStartGame} disabled={loading}>
          Inizia l'avventura
        </FormButton>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
      </StartGameForm>
    );
  };

  // Funzione per avviare il gioco
  const handleStartGame = async () => {
    if (!playerName || !playerClass) {
      addMessage("Inserisci nome e classe prima di iniziare.", 'errore');
      return;
    }
    
    try {
      await startGame(playerName, playerClass);
    } catch (err) {
      console.error("Errore nell'avvio del gioco:", err);
    }
  };

  // Gestori eventi per problemi di connessione
  useEffect(() => {
    const handleConnessionePersa = (event) => {
      // Estrai i dettagli dell'errore se disponibili
      const erroreDettagli = event.detail ? 
        `${event.detail.errore}: ${event.detail.dettagli || ''}` : 
        'Connessione al server persa';
      
      console.error('Problema di connessione:', erroreDettagli);
      
      // Imposta lo stato per mostrare l'errore
      setConnessionePersa(true);
      
      // Aggiungi il messaggio al log di gioco
      addMessage({
        tipo: 'errore',
        testo: `Problema di connessione al server: ${erroreDettagli}. Tentativo di riconnessione in corso...`
      });
      
      // Tenta di riconnettersi dopo 5 secondi
      setTimeout(() => {
        window.location.reload();
      }, 5000);
    };
    
    const handleSessioneScaduta = () => {
      setSessioneScaduta(true);
      // Reindirizza alla pagina iniziale
      navigate('/');
      setTimeout(() => {
        setSessioneScaduta(false);
      }, 3000);
    };
    
    window.addEventListener('connessionePersa', handleConnessionePersa);
    window.addEventListener('sessioneScaduta', handleSessioneScaduta);
    
    return () => {
      window.removeEventListener('connessionePersa', handleConnessionePersa);
      window.removeEventListener('sessioneScaduta', handleSessioneScaduta);
    };
  }, [navigate, addMessage]);

  // Aggiungo un useEffect per rilevare lo stato SceltaMappaState
  useEffect(() => {
    // Quando lo stato cambia a SceltaMappaState o scelta_mappa, mostra il componente SceltaMappa
    if (stato_nome === 'SceltaMappaState') {
      console.log("Rilevato stato SceltaMappaState, mostro la mappa");
      mostraMappa();
    }
  }, [stato_nome]);

  // Avvia il monitoraggio dello stato del server
  useEffect(() => {
    // Avvia il monitoraggio con controllo ogni 30 secondi
    const stopHealthMonitor = startHealthMonitor(30000);
    
    // Pulisci il monitoraggio quando il componente viene smontato
    return () => {
      stopHealthMonitor();
    };
  }, []);

  // Se non c'è una sessione attiva, mostra il form di inizio gioco
  if (!sessione_attiva) {
    return (
      <AppContainer>
        <GameHeader>
          <GameTitle>Dungeon Master AI</GameTitle>
        </GameHeader>
        {renderStartGameForm()}
      </AppContainer>
    );
  }

  // Layout principale del gioco
  return (
    <AppContainer>
      <GameHeader>
        <GameTitle>Dungeon Master AI</GameTitle>
        {giocatore.nome && (
          <StatusBar giocatore={giocatore} stato={stato_nome} />
        )}
      </GameHeader>
      
      <MainContainer>
        {/* Layout principale a tre colonne */}
        <MainSectionContainer>
          {/* Colonna sinistra - Pulsanti di azione */}
          <ActionButtons 
            onAction={handleAction} 
            currentState={stato_nome}
          />
          
          {/* Colonna centrale - Area di gioco principale */}
          <MainGameArea>
            {/* Visualizzazione griglia della mappa */}
            <GameGridContainer>
              <Grid 
                mapData={state.mappa} 
                gameState={{
                  x: state.posizione ? state.posizione.x : 0,
                  y: state.posizione ? state.posizione.y : 0
                }}
              />
            </GameGridContainer>
            
            {/* Area messaggi di testo */}
            <DialogContainer>
              <DialogBox 
                messages={messaggi} 
                loading={loading}
                onExecuteCommand={executeCommand}
              />
            </DialogContainer>
          </MainGameArea>
          
          {/* Colonna destra - Comandi e informazioni */}
          <CommandPanel />
        </MainSectionContainer>
      </MainContainer>
      
      {/* Notifiche e altri overlay */}
      {showNotifications && (
        <NotificationPanel 
          onClose={() => setShowNotifications(false)} 
        />
      )}
      
      {/* Overlay per la scelta della mappa */}
      {mostraSceltaMappa && (
        <SceltaMappa
          key={chiaveSceltaMappa}
          isOpen={mostraSceltaMappa}
          onClose={() => setMostraSceltaMappa(false)}
          onSelectDestination={handleSelectDestination}
          onMessageUpdate={handleMessageUpdate}
          onForceRefresh={forceRefreshGameState}
        />
      )}
      
      {/* Notifiche di errore di connessione */}
      {connessionePersa && (
        <div className="error-notification" style={{
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: '#FF4444',
          color: 'white',
          padding: '15px 20px',
          borderRadius: '5px',
          boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
          zIndex: 1000,
          fontFamily: 'monospace',
          fontWeight: 'bold',
          textAlign: 'center',
          maxWidth: '80%'
        }}>
          Connessione al server persa. Tentativo di riconnessione in corso...
        </div>
      )}
      
      {sessioneScaduta && (
        <div className="error-notification" style={{
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: '#FF4444',
          color: 'white',
          padding: '15px 20px',
          borderRadius: '5px',
          boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
          zIndex: 1000,
          fontFamily: 'monospace',
          fontWeight: 'bold',
          textAlign: 'center',
          maxWidth: '80%'
        }}>
          Sessione scaduta. Verrai reindirizzato alla pagina iniziale.
        </div>
      )}
    </AppContainer>
  );
};

export default App;

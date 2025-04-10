import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { getDestinazioniDisponibili, viaggiaVerso, getStatoGioco } from '../services/api';

const MappaContainer = styled.div`
  background-color: rgba(0, 0, 0, 0.8);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999 !important; /* Assicura che sia sopra a tutto */
`;

const MappaPanel = styled.div`
  background-color: #222;
  border: 1px solid #444;
  padding: 20px;
  max-width: 500px;
  width: 90%;
  color: #fff;
  font-family: monospace;
`;

const Title = styled.h2`
  color: #FFFF00;
  text-align: center;
  margin-top: 0;
`;

const Subtitle = styled.p`
  text-align: center;
  margin-bottom: 20px;
  color: #AAA;
`;

const DestinazioneList = styled.div`
  margin-top: 20px;
`;

const DestinazioneButton = styled.button`
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  padding: 15px;
  margin: 8px 0;
  cursor: pointer;
  width: 100%;
  text-align: left;
  font-family: monospace;
  font-size: 16px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  
  &:hover {
    background-color: #444;
    border-color: #FFFF00;
  }
  
  &:active {
    background-color: #555;
  }
`;

const DestinationIcon = styled.span`
  margin-right: 10px;
  font-size: 18px;
`;

const CloseButton = styled.button`
  background-color: #444;
  color: #fff;
  border: 1px solid #555;
  padding: 10px 15px;
  margin-top: 20px;
  cursor: pointer;
  width: 100%;
  font-family: monospace;
  
  &:hover {
    background-color: #555;
  }
`;

const LoadingText = styled.div`
  text-align: center;
  padding: 20px;
`;

const ErrorText = styled.div`
  color: #FF6666;
  text-align: center;
  padding: 20px;
`;

// Icone per le destinazioni
const getIcon = (destinationId) => {
  switch(destinationId) {
    case 'taverna': return '🍺';
    case 'mercato': return '🛒';
    case 'cantina': return '🍷';
    default: return '🗺️';
  }
};

const SceltaMappa = ({ isOpen = true, onClose, onSelectDestination, onMessageUpdate, onForceRefresh }) => {
  console.log("SceltaMappa riceve props:", { isOpen, hasOnMessageUpdate: !!onMessageUpdate });
  
  // Funzione di supporto per gestire in sicurezza onMessageUpdate
  const notifyMessage = (messaggio, tipo = 'sistema') => {
    if (onMessageUpdate && typeof onMessageUpdate === 'function') {
      console.log(`SceltaMappa: invio messaggio "${messaggio}" di tipo "${tipo}"`);
      onMessageUpdate(messaggio, tipo);
    } else {
      console.warn(`SceltaMappa: impossibile inviare messaggio - onMessageUpdate non disponibile`);
    }
  };
  
  const [destinazioni, setDestinazioni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("SceltaMappa montato - caricamento destinazioni");
    loadDestinazioni();
  }, []);

  const loadDestinazioni = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("Chiamata API getDestinazioniDisponibili");
      
      // Tenta di caricare le destinazioni dall'API
      try {
        const apiDestinazioni = await getDestinazioniDisponibili();
        console.log("Risposta API destinazioni:", apiDestinazioni);
        
        if (apiDestinazioni && Array.isArray(apiDestinazioni) && apiDestinazioni.length > 0) {
          console.log(`Caricate ${apiDestinazioni.length} destinazioni dall'API`);
          setDestinazioni(apiDestinazioni);
          
          // Notifica l'utente che le destinazioni sono state caricate
          notifyMessage("Destinazioni disponibili caricate con successo.", "sistema");
        } else {
          console.warn("API ha restituito una lista vuota o invalida");
          setDestinazioni([]);
          
          // Imposta l'errore ma mostra comunque le destinazioni
          setError("Nessuna destinazione disponibile. Il server potrebbe non essere raggiungibile.");
          
          // Notifica l'utente
          notifyMessage("Nessuna destinazione disponibile. Verifica la connessione al server.", "errore");
        }
      } catch (err) {
        console.error('Errore API destinazioni:', err);
        setDestinazioni([]);
        setError(`Errore di comunicazione col server. Dettagli: ${err.message}`);
        
        // Notifica l'utente dell'errore
        notifyMessage("Errore nella comunicazione con il server. Impossibile caricare le destinazioni.", "errore");
      }
      
    } catch (err) {
      console.error('Errore generale nel caricare le destinazioni:', err);
      setError("Si è verificato un errore. Riprova più tardi.");
      setDestinazioni([]);
      
      // Notifica l'utente dell'errore
      notifyMessage("Si è verificato un errore nel caricamento delle destinazioni.", "errore");
    } finally {
      // In ogni caso, terminiamo lo stato di caricamento
      setLoading(false);
    }
  };

  const handleSelectDestination = async (destinazione) => {
    try {
      // Ottieni l'ID della destinazione
      const destinazioneId = typeof destinazione === 'string' ? destinazione : destinazione.id;
      const destinazioneNome = typeof destinazione === 'string' ? destinazione : destinazione.nome;
      
      // Aggiorna i messaggi con l'azione intrapresa
      notifyMessage(`Hai scelto di viaggiare verso ${destinazioneNome}`);
      
      // Chiudi il modale
      onClose();
      
      // Esegui l'azione di viaggio direttamente con l'API
      console.log(`Avvio viaggio verso ${destinazioneNome}...`);
      
      // Monitoriamo lo stato precedente per confronto
      let statoIniziale;
      try {
        statoIniziale = await getStatoGioco();
        console.log("Stato iniziale:", statoIniziale.stato);
      } catch (err) {
        console.warn("Impossibile ottenere lo stato iniziale");
      }
      
      // Esegui l'azione di viaggio
      let risultato;
      if (onSelectDestination) {
        risultato = await onSelectDestination(destinazioneId);
      } else {
        // Usa l'API direttamente
        risultato = await viaggiaVerso(destinazioneId);
      }
      
      console.log("Risultato viaggio diretto:", risultato);
      
      // Attendiamo più a lungo (3 secondi) per dare tempo al backend di completare il cambio di stato
      setTimeout(async () => {
        try {
          // Forza un aggiornamento dello stato
          if (onForceRefresh && typeof onForceRefresh === 'function') {
            console.log("Forzando aggiornamento stato dopo viaggio");
            await onForceRefresh();
          }
          
          // Ottieni il nuovo stato e verifica che sia cambiato
          const statoAggiornato = await getStatoGioco();
          console.log("Stato aggiornato:", statoAggiornato);
          
          if (statoAggiornato.stato === 'SceltaMappaState' || 
              statoAggiornato.stato === statoIniziale.stato ||
              statoAggiornato.stato?.toLowerCase().includes('sceltamappa')) {
            
            console.warn("Il cambio di stato non è avvenuto, tentativo di recupero...");
            
            // Tenta di forzare nuovamente il viaggio
            try {
              const secondoTentativo = await viaggiaVerso(destinazioneId);
              console.log("Risultato secondo tentativo:", secondoTentativo);
              
              // Forza di nuovo l'aggiornamento
              if (onForceRefresh) await onForceRefresh();
              
              // Notifica l'utente
              notifyMessage(`Ti sei spostato a ${destinazioneNome}`, "narrativo");
            } catch (err) {
              console.error("Errore nel secondo tentativo:", err);
              notifyMessage(`Problemi nel viaggio verso ${destinazioneNome}. Riprova.`, "errore");
            }
          } else {
            // Stato cambiato con successo
            notifyMessage(`Ti sei spostato a ${destinazioneNome}`, "narrativo");
          }
        } catch (error) {
          console.error("Errore nel recuperare lo stato finale:", error);
        }
      }, 3000); // Aumentato a 3 secondi
    } catch (err) {
      console.error('Errore nel selezionare la destinazione:', err);
      const destinazioneNome = typeof destinazione === 'string' ? destinazione : destinazione.nome;
      notifyMessage(`Errore nel viaggiare verso ${destinazioneNome}: ${err.message}`, 'errore');
    }
  };

  return (
    <MappaContainer>
      <MappaPanel>
        <Title>Selezione Destinazione</Title>
        <Subtitle>La tua avventura sta per iniziare. Scegli dove vuoi andare:</Subtitle>
        
        {loading ? (
          <LoadingText>Caricamento destinazioni...</LoadingText>
        ) : (
          <>
            {error && <ErrorText>{error}</ErrorText>}
            
            <DestinazioneList>
              {destinazioni.map((dest, index) => (
                <DestinazioneButton 
                  key={index} 
                  onClick={() => handleSelectDestination(dest)}
                >
                  <DestinationIcon>{getIcon(dest.id)}</DestinationIcon>
                  {dest.nome}
                  {dest.descrizione && <span style={{ fontSize: '12px', display: 'block', marginTop: '4px', color: '#AAA' }}>{dest.descrizione}</span>}
                </DestinazioneButton>
              ))}
              
              {destinazioni.length === 0 && (
                <div style={{ textAlign: 'center', padding: '20px', color: '#FF6666' }}>
                  Nessuna destinazione disponibile.
                </div>
              )}
            </DestinazioneList>
            
            <div style={{ marginTop: '15px', display: 'flex', justifyContent: 'space-between' }}>
              <CloseButton onClick={onClose} style={{ width: '48%' }}>Torna Indietro</CloseButton>
              <CloseButton onClick={loadDestinazioni} style={{ width: '48%', backgroundColor: '#555' }}>Ricarica</CloseButton>
            </div>
          </>
        )}
      </MappaPanel>
    </MappaContainer>
  );
};

export default SceltaMappa; 
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useGameState } from './context/GameStateContext';
import { muoviGiocatore, getClassi } from './services/api';

const App = () => {
  const { 
    state, 
    executeCommand, 
    startGame, 
    refreshGameState, 
    addMessage 
  } = useGameState();
  
  const [playerName, setPlayerName] = useState('');
  const [playerClass, setPlayerClass] = useState('guerriero');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSceltaMappa, setShowSceltaMappa] = useState(false);
  const [classiDisponibili, setClassiDisponibili] = useState({});
  const [loadingClassi, setLoadingClassi] = useState(false);

  // Estrai i dati dallo stato globale
  const { 
    giocatore, 
    stato_nome, 
    messaggi, 
    loading, 
    error,
    sessione_attiva 
  } = state;

  // Carica le classi disponibili all'avvio
  useEffect(() => {
    async function loadClassi() {
      try {
        setLoadingClassi(true);
        const response = await getClassi();
        if (response && Object.keys(response).length > 0) {
          setClassiDisponibili(response);
          // Imposta la prima classe come default se non è già impostata
          if (!playerClass && Object.keys(response).length > 0) {
            setPlayerClass(Object.keys(response)[0]);
          }
        }
      } catch (err) {
        console.error("Errore nel caricamento delle classi:", err);
      } finally {
        setLoadingClassi(false);
      }
    }
    
    loadClassi();
  }, []);

  // ... rest of the code ...
}; 
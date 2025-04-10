import { useState, useEffect, useCallback } from 'react';
import { getStatoGioco, getMappa, getNotifiche } from '../services/api';

export const useGameState = () => {
  const [gameState, setGameState] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(Date.now());

  const refreshState = useCallback(async (force = false) => {
    const sessionId = localStorage.getItem('sessionId');
    if (!sessionId) {
      setLoading(false);
      return;
    }

    // Evita refresh troppo frequenti (minimo 500ms tra un refresh e l'altro)
    // a meno che non sia forzato
    const now = Date.now();
    if (!force && now - lastRefresh < 500) {
      return;
    }
    setLastRefresh(now);

    try {
      setLoading(true);
      const [statoData, mappaData, notificheData] = await Promise.all([
        getStatoGioco().catch(err => {
          console.error('Errore nel recuperare lo stato del gioco:', err);
          throw new Error('Impossibile recuperare lo stato del gioco');
        }),
        getMappa().catch(err => {
          console.error('Errore nel recuperare la mappa:', err);
          return null; // La mappa potrebbe non essere disponibile in alcuni contesti
        }),
        getNotifiche().catch(err => {
          console.error('Errore nel recuperare le notifiche:', err);
          return { notifiche: [] }; // Restituisci un array vuoto in caso di errore
        })
      ]);
      
      setGameState(statoData);
      
      if (mappaData) {
        setMapData(mappaData);
      }
      
      if (notificheData && notificheData.notifiche) {
        setNotifications(notificheData.notifiche);
      }
      
      setError(null);
    } catch (err) {
      console.error('Errore nel refresh dello stato:', err);
      setError('Errore nel caricamento dello stato: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [lastRefresh]);

  useEffect(() => {
    // Carica lo stato iniziale
    refreshState(true);
    
    // Imposta un intervallo per aggiornare lo stato del gioco periodicamente
    const refreshInterval = setInterval(() => {
      refreshState();
    }, 5000); // Aggiorna ogni 5 secondi
    
    // Imposta un intervallo per controllare nuove notifiche
    const notificationsInterval = setInterval(() => {
      const sessionId = localStorage.getItem('sessionId');
      if (sessionId) {
        getNotifiche().then(data => {
          if (data && data.notifiche) {
            setNotifications(data.notifiche);
          }
        }).catch(err => {
          console.error('Errore nel recuperare le notifiche:', err);
        });
      }
    }, 10000); // Controlla ogni 10 secondi
    
    return () => {
      clearInterval(refreshInterval);
      clearInterval(notificationsInterval);
    };
  }, [refreshState]);

  return {
    gameState,
    mapData,
    notifications,
    loading,
    error,
    refreshState: () => refreshState(true) // Esporta una versione forzata di refreshState
  };
};

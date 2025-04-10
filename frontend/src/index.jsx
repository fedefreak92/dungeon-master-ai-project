import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles.css';
import { GameStateProvider } from './context/GameStateContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <GameStateProvider>
        <App />
      </GameStateProvider>
    </BrowserRouter>
  </React.StrictMode>
);

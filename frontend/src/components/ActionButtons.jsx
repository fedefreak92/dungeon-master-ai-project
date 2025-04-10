import React from 'react';
import styled from 'styled-components';

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 120px;
  background-color: #222;
  border-right: 1px solid #444;
  padding: 10px 0;
`;

const ActionButton = styled.button`
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  padding: 20px 0;
  margin: 10px;
  cursor: pointer;
  font-family: monospace;
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background-color: #444;
  }
  
  &:active {
    background-color: #555;
  }
`;

const TimerSection = styled.div`
  margin-top: auto;
  padding: 10px;
  border-top: 1px solid #444;
`;

const TimerLabel = styled.div`
  color: #aaa;
  font-size: 12px;
  text-align: center;
  margin-bottom: 5px;
`;

const TimerControls = styled.div`
  display: flex;
  justify-content: space-around;
`;

const TimerButton = styled.button`
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
  
  &:hover {
    background-color: #444;
  }
`;

const ActionButtons = ({ onAction, currentState }) => {
  return (
    <ButtonContainer>
      {/* Pulsanti principali come nell'immagine */}
      <ActionButton onClick={() => onAction('pg')}>
        PG
      </ActionButton>
      
      <ActionButton onClick={() => onAction('attacco')}>
        ATTACCO
      </ActionButton>
      
      <ActionButton onClick={() => onAction('tiro_dadi')}>
        TIRO DADI
      </ActionButton>
      
      {/* Sezione Timer/Gestione Tempo in fondo come nell'immagine */}
      <TimerSection>
        <TimerLabel>Gestione Tempo</TimerLabel>
        <TimerControls>
          <TimerButton onClick={() => onAction('riposa')}>Aspetta</TimerButton>
        </TimerControls>
        <TimerControls style={{ marginTop: '5px' }}>
          <TimerButton onClick={() => onAction('riposa_ore')}>Riposa (8 ore)</TimerButton>
        </TimerControls>
        <TimerControls style={{ marginTop: '5px' }}>
          <TimerButton onClick={() => onAction('medita')}>Medita (4 ore)</TimerButton>
        </TimerControls>
        <TimerControls style={{ marginTop: '5px' }}>
          <TimerButton onClick={() => onAction('vedi_orario')}>Vedi Orario</TimerButton>
        </TimerControls>
      </TimerSection>
    </ButtonContainer>
  );
};

export default ActionButtons;

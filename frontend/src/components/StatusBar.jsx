import React from 'react';
import styled from 'styled-components';

const StatusBarContainer = styled.div`
  display: flex;
  flex-direction: column;
  background-color: #222;
  padding: 5px 10px;
  border-bottom: 1px solid #444;
  font-size: 12px;
  color: #ccc;
`;

const StatusRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 2px 0;
`;

const InfoSection = styled.div`
  display: flex;
  flex-direction: column;
`;

const TimeInfo = styled.div`
  color: #FFFF00;
  margin-top: 2px;
  text-align: center;
`;

const PlayerInfo = styled.div`
  margin-top: 2px;
  color: #AAFFFF;
`;

const StatusItem = styled.div`
  margin-right: 10px;
`;

const Label = styled.span`
  font-size: 12px;
  color: #aaa;
  margin-right: 5px;
`;

const Value = styled.span`
  font-size: 12px;
  color: #fff;
`;

const ProgressBarContainer = styled.div`
  width: 100px;
  height: 6px;
  background-color: #333;
  border-radius: 3px;
  overflow: hidden;
  margin-left: 5px;
  display: inline-block;
  vertical-align: middle;
`;

const ProgressBarFill = styled.div`
  height: 100%;
  background-color: ${props => props.color || '#e74c3c'};
  width: ${props => props.percentage}%;
`;

const NotificationBadge = styled.div`
  background-color: #e74c3c;
  color: white;
  font-size: 12px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 5px;
  cursor: pointer;
`;

const NotificationIcon = styled.div`
  cursor: pointer;
  color: #aaa;
  font-size: 16px;
  display: flex;
  align-items: center;
  
  &:hover {
    color: #fff;
  }
`;

const Spacer = styled.div`
  flex: 1;
`;

const StatusBar = ({ giocatore, stato }) => {
  if (!giocatore) return null;
  
  // Statistiche del giocatore
  const {
    nome = 'Sconosciuto',
    classe = 'Sconosciuto',
    hp = 0,
    max_hp = 0,
    statistiche = {},
    equipaggiamento = {}
  } = giocatore;
  
  // Calcola percentuale HP
  const hpPercentage = max_hp > 0 ? (hp / max_hp) * 100 : 0;
  
  // Estrai statistiche
  const { forza, destrezza, costituzione, intelligenza, saggezza, carisma } = statistiche;
  
  // Estrai informazioni sull'equipaggiamento
  const arma = equipaggiamento.arma || 'Nessuna';
  const armatura = equipaggiamento.armatura || 'Nessuna';
  
  // Dati temporali simulati (in un'implementazione reale verrebbero dal backend)
  const orario = {
    ora: '12:00',
    data: '1 Gennaio 1482',
    fase: 'mezzogiorno'
  };
  
  return (
    <StatusBarContainer>
      <StatusRow>
        <InfoSection>
          <TimeInfo>
            ⏱️ Ora attuale: {orario.ora}<br />
            📅 Data: {orario.data}<br />
            🌞 Fase del giorno: {orario.fase}
          </TimeInfo>
        </InfoSection>
        
        <InfoSection>
          <PlayerInfo>
            Giocatore: {nome} e' {classe}<br />
            Statistiche: forza {forza}, destrezza {destrezza}, costituzione {costituzione}, intelligenza {intelligenza}<br />
            Equipaggio: {arma}, {armatura}
          </PlayerInfo>
        </InfoSection>
      </StatusRow>
      
      <StatusRow>
        <StatusItem>
          <Label>HP:</Label>
          <Value>{hp}/{max_hp}</Value>
          <ProgressBarContainer>
            <ProgressBarFill percentage={hpPercentage} color="#e74c3c" />
          </ProgressBarContainer>
        </StatusItem>
        
        <StatusItem>
          <Value>Stato attuale: {stato || 'Esplorando'}</Value>
        </StatusItem>
      </StatusRow>
    </StatusBarContainer>
  );
};

export default StatusBar;

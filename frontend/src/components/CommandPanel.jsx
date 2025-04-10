import React from 'react';
import styled from 'styled-components';

const CommandsContainer = styled.div`
  background-color: #222;
  color: #fff;
  padding: 10px;
  border-left: 1px solid #444;
  width: 250px;
  height: 400px;
  overflow-y: auto;
`;

const CommandTitle = styled.h3`
  color: #FFFF00;
  margin-bottom: 15px;
  font-family: monospace;
  text-align: center;
  font-size: 18px;
`;

const CommandItem = styled.div`
  display: flex;
  margin-bottom: 5px;
  font-family: monospace;
`;

const CommandKey = styled.span`
  color: #FFFF00;
  width: 50px;
  margin-right: 10px;
  font-weight: ${props => props.highlight ? 'bold' : 'normal'};
`;

const CommandAction = styled.span`
  color: #FFFFFF;
`;

const CommandPanel = () => {
  const commands = [
    { key: 'Frecce', action: 'Movimento', highlight: true },
    { key: 'W', action: 'Nord', highlight: true },
    { key: 'A', action: 'Ovest', highlight: true },
    { key: 'S', action: 'Sud', highlight: true },
    { key: 'D', action: 'Est', highlight: true },
    { key: 'E', action: 'Interagisci' },
    { key: 'F', action: 'Combatti' },
    { key: 'I', action: 'Inventario' },
    { key: 'L', action: 'Mostrarecord logici' },
    { key: 'S', action: 'Mostrarecord statistici' },
    { key: 'SPAZIO', action: 'Azioni principali' },
    { key: 'M', action: 'Mappa' },
    { key: '+', action: 'Zoom in' },
    { key: '-', action: 'Zoom out' },
    { key: 'ESC', action: 'Esci' }
  ];
  
  return (
    <CommandsContainer>
      <CommandTitle>COMANDI</CommandTitle>
      {commands.map(cmd => (
        <CommandItem key={cmd.key}>
          <CommandKey highlight={cmd.highlight}>{cmd.key}</CommandKey>
          <CommandAction>{cmd.action}</CommandAction>
        </CommandItem>
      ))}
    </CommandsContainer>
  );
};

export default CommandPanel;

import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

const MessagesContainer = styled.div`
  height: 100%;
  overflow-y: auto;
  font-family: monospace;
  color: #ddd;
  line-height: 1.4;
`;

const DialogMessage = styled.div`
  margin-bottom: 5px;
  ${props => props.tipo === 'sistema' && 'color: #AAFFFF;'}
  ${props => props.tipo === 'errore' && 'color: #FF6666;'}
  ${props => props.tipo === 'comando' && 'color: #AAFFAA;'}
  ${props => props.tipo === 'narrativo' && 'color: #FFFFFF;'}
`;

const InputContainer = styled.div`
  display: flex;
  margin-top: 10px;
  background-color: transparent;
`;

const Input = styled.input`
  flex: 1;
  background-color: #333;
  color: #fff;
  border: 1px solid #444;
  padding: 5px 10px;
  font-family: monospace;
  font-size: 14px;
`;

const Button = styled.button`
  background-color: #444;
  color: #fff;
  border: 1px solid #555;
  padding: 5px 10px;
  margin-left: 5px;
  cursor: pointer;
  font-family: monospace;
  font-size: 14px;
  
  &:hover {
    background-color: #555;
  }
`;

const LoadingIndicator = styled.div`
  color: #AAFFFF;
  margin-top: 5px;
  font-style: italic;
`;

const DialogBox = ({ messages = [], loading = false, onExecuteCommand }) => {
  const [command, setCommand] = useState('');
  const dialogRef = useRef(null);
  
  // Auto-scroll al messaggio più recente
  useEffect(() => {
    if (dialogRef.current) {
      dialogRef.current.scrollTop = dialogRef.current.scrollHeight;
    }
  }, [messages]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (command.trim()) {
      onExecuteCommand(command);
      setCommand('');
    }
  };
  
  // Formattazione speciale per i messaggi
  const formatMessage = (msg) => {
    if (typeof msg === 'string') {
      return msg;
    }
    
    let prefix = '';
    
    switch (msg.tipo) {
      case 'sistema':
        prefix = '[SISTEMA] ';
        break;
      case 'errore':
        prefix = '[ERRORE] ';
        break;
      case 'comando':
        // Il comando già include il prefisso ">" in input
        prefix = '';
        break;
      default:
        prefix = '';
    }
    
    return prefix + msg.testo;
  };
  
  // Funzione per eliminare i messaggi duplicati consecutivi
  const deduplicaMessaggi = (msgs) => {
    if (!msgs || msgs.length === 0) return [];
    
    // Messaggi per cui l'unicità è importante solo per contenuto e non per tipo
    const soloTestoPerDuplica = ['narrativo', 'sistema'];
    
    return msgs.reduce((acc, current, index, array) => {
      // Se è il primo messaggio, aggiungilo sempre
      if (index === 0) {
        acc.push(current);
        return acc;
      }
      
      // Ottieni il testo del messaggio corrente
      const currentText = typeof current === 'string' 
        ? current 
        : (current.testo || '');
      const currentType = typeof current === 'string' 
        ? 'narrativo' 
        : (current.tipo || 'narrativo');
        
      // Ottieni il messaggio precedente
      const previous = array[index - 1];
      const previousText = typeof previous === 'string' 
        ? previous 
        : (previous.testo || '');
      const previousType = typeof previous === 'string' 
        ? 'narrativo' 
        : (previous.tipo || 'narrativo');
      
      // Confronta i testi e i tipi dei messaggi
      const isDuplicatoTesto = currentText === previousText;
      
      // Se il contenuto è diverso, aggiungi sempre
      if (!isDuplicatoTesto) {
        acc.push(current);
        return acc;
      }
      
      // Se il testo è uguale, controlla se il tipo è importante per la deduplicazione
      if (soloTestoPerDuplica.includes(currentType) && soloTestoPerDuplica.includes(previousType)) {
        // Per questi tipi, consideriamo solo il testo per la deduplicazione (già verificato)
        return acc; // Non aggiungere, è un duplicato
      }
      
      // Se il tipo è diverso e non è tra quelli per cui conta solo il testo, aggiungi
      if (currentType !== previousType) {
        acc.push(current);
      }
      
      return acc;
    }, []);
  };
  
  // Deduplicare i messaggi
  const messaggiUnificate = deduplicaMessaggi(messages);
  
  return (
    <>
      <MessagesContainer ref={dialogRef}>
        {messaggiUnificate.map((msg, idx) => (
          <DialogMessage key={idx} tipo={typeof msg === 'string' ? 'narrativo' : msg.tipo}>
            {formatMessage(msg)}
          </DialogMessage>
        ))}
        {loading && <LoadingIndicator>Caricamento in corso...</LoadingIndicator>}
      </MessagesContainer>
      
      <form onSubmit={handleSubmit}>
        <InputContainer>
          <Input 
            type="text" 
            value={command} 
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Inserisci un comando..."
            autoFocus
          />
          <Button type="submit">Invia</Button>
        </InputContainer>
      </form>
    </>
  );
};

export default DialogBox;

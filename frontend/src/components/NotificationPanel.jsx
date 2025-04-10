import React from 'react';
import styled from 'styled-components';
import { leggiNotifica, leggiTutteLeNotifiche } from '../services/api';

const NotificationContainer = styled.div`
  background-color: #2a2a2a;
  border-left: 1px solid #444;
  width: 300px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  max-height: 100%;
  overflow-y: auto;
`;

const NotificationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #444;
`;

const NotificationTitle = styled.h3`
  margin: 0;
  color: #ddd;
`;

const ClearButton = styled.button`
  background-color: #333;
  color: #ddd;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 12px;
  border-radius: 3px;
  
  &:hover {
    background-color: #444;
  }
`;

const NotificationList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
`;

const NotificationItem = styled.div`
  background-color: ${props => props.letta ? '#222' : '#333'};
  border-left: 3px solid ${props => {
    switch(props.tipo) {
      case 'info': return '#3498db';
      case 'warning': return '#f39c12';
      case 'error': return '#e74c3c';
      case 'achievement': return '#2ecc71';
      case 'quest': return '#9b59b6';
      default: return '#7f8c8d';
    }
  }};
  padding: 8px;
  border-radius: 3px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #3a3a3a;
  }
`;

const NotificationMessage = styled.p`
  margin: 0;
  font-size: 14px;
  color: ${props => props.letta ? '#aaa' : '#fff'};
`;

const NotificationTimestamp = styled.small`
  display: block;
  font-size: 11px;
  color: #888;
  margin-top: 4px;
`;

const EmptyNotifications = styled.p`
  color: #888;
  text-align: center;
  margin: 20px 0;
  font-style: italic;
`;

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('it-IT', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit'
  });
};

const NotificationPanel = ({ notifications = [], onRefresh }) => {
  const handleClickNotification = async (notification) => {
    if (!notification.letta) {
      try {
        await leggiNotifica(notification.id);
        if (onRefresh) onRefresh();
      } catch (error) {
        console.error('Errore nel segnare la notifica come letta:', error);
      }
    }
  };
  
  const handleClearAll = async () => {
    try {
      await leggiTutteLeNotifiche();
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Errore nel segnare tutte le notifiche come lette:', error);
    }
  };
  
  return (
    <NotificationContainer>
      <NotificationHeader>
        <NotificationTitle>Notifiche</NotificationTitle>
        {notifications.length > 0 && (
          <ClearButton onClick={handleClearAll}>Segna tutte come lette</ClearButton>
        )}
      </NotificationHeader>
      
      <NotificationList>
        {notifications.length === 0 ? (
          <EmptyNotifications>Nessuna notifica</EmptyNotifications>
        ) : (
          notifications.map((notification) => (
            <NotificationItem 
              key={notification.id}
              tipo={notification.tipo}
              letta={notification.letta}
              onClick={() => handleClickNotification(notification)}
            >
              <NotificationMessage letta={notification.letta}>
                {notification.messaggio}
              </NotificationMessage>
              <NotificationTimestamp>
                {formatTimestamp(notification.timestamp)}
              </NotificationTimestamp>
            </NotificationItem>
          ))
        )}
      </NotificationList>
    </NotificationContainer>
  );
};

export default NotificationPanel; 
import React from 'react';
import { Stage, Container, Graphics, Text } from '@pixi/react';
import styled from 'styled-components';
import * as PIXI from 'pixi.js';

const GridContainer = styled.div`
  width: 600px;
  height: 400px;
  background-color: #222;
  border: 1px solid #444;
  margin: 10px;
`;

const Grid = ({ mapData, gameState }) => {
  // Dimensione della cella
  const CELL_SIZE = 32;
  
  // Se non ci sono dati della mappa, mostra una griglia vuota
  if (!mapData || !gameState) {
    return (
      <GridContainer>
        <Stage width={600} height={400}>
          <Container>
            <Graphics 
              draw={g => {
                g.beginFill(0x333333);
                g.drawRect(0, 0, 600, 400);
                g.endFill();
              }}
            />
          </Container>
        </Stage>
      </GridContainer>
    );
  }
  
  // Funzione per determinare il colore della cella
  const getCellColor = (x, y) => {
    // Posizione del giocatore
    if (gameState.x === x && gameState.y === y) {
      return 0xFFFF00; // Giallo per il giocatore
    }
    
    // Controlla se c'è un NPC
    const npgPos = `(${x}, ${y})`;
    if (mapData.npg && mapData.npg[npgPos]) {
      return 0xFF9900; // Arancione per gli NPC
    }
    
    // Controlla se c'è un oggetto
    const objPos = `(${x}, ${y})`;
    if (mapData.oggetti && mapData.oggetti[objPos]) {
      return 0x00FF00; // Verde per gli oggetti
    }
    
    // Controlla se c'è un muro
    if (mapData.griglia && mapData.griglia[y] && mapData.griglia[y][x] === 1) {
      return 0x666666; // Grigio scuro per i muri
    }
    
    // Controlla se c'è una porta
    const portaPos = `(${x}, ${y})`;
    if (mapData.porte && mapData.porte[portaPos]) {
      return 0xCCCCCC; // Grigio chiaro per le porte
    }
    
    // Cella vuota
    return 0x444444;
  };
  
  // Funzione per ottenere il simbolo della cella
  const getCellSymbol = (x, y) => {
    // Posizione del giocatore
    if (gameState.x === x && gameState.y === y) {
      return 'P';
    }
    
    // Controlla se c'è un NPC
    const npgPos = `(${x}, ${y})`;
    if (mapData.npg && mapData.npg[npgPos]) {
      const npg = mapData.npg[npgPos];
      return npg.token || 'N';
    }
    
    // Controlla se c'è un oggetto
    const objPos = `(${x}, ${y})`;
    if (mapData.oggetti && mapData.oggetti[objPos]) {
      const obj = mapData.oggetti[objPos];
      return obj.token || 'O';
    }
    
    // Controlla se c'è un muro
    if (mapData.griglia && mapData.griglia[y] && mapData.griglia[y][x] === 1) {
      return '#';
    }
    
    // Controlla se c'è una porta
    const portaPos = `(${x}, ${y})`;
    if (mapData.porte && mapData.porte[portaPos]) {
      return 'D';
    }
    
    // Cella vuota
    return '';
  };
  
  // Calcola le dimensioni della griglia
  const gridWidth = mapData.larghezza || 15;
  const gridHeight = mapData.altezza || 15;
  
  return (
    <GridContainer>
      <Stage width={600} height={400}>
        <Container>
          {/* Disegna la griglia di sfondo */}
          <Graphics
            draw={g => {
              g.beginFill(0x222222);
              g.drawRect(0, 0, gridWidth * CELL_SIZE, gridHeight * CELL_SIZE);
              g.endFill();
              
              // Disegna le linee della griglia
              g.lineStyle(1, 0x333333);
              for (let x = 0; x <= gridWidth; x++) {
                g.moveTo(x * CELL_SIZE, 0);
                g.lineTo(x * CELL_SIZE, gridHeight * CELL_SIZE);
              }
              for (let y = 0; y <= gridHeight; y++) {
                g.moveTo(0, y * CELL_SIZE);
                g.lineTo(gridWidth * CELL_SIZE, y * CELL_SIZE);
              }
            }}
          />
          
          {/* Disegna le celle colorate */}
          {Array.from({ length: gridHeight }).map((_, y) =>
            Array.from({ length: gridWidth }).map((_, x) => (
              <Graphics
                key={`cell-${x}-${y}`}
                draw={g => {
                  const color = getCellColor(x, y);
                  g.beginFill(color);
                  g.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                  g.endFill();
                }}
              />
            ))
          )}
          
          {/* Disegna i simboli nelle celle */}
          {Array.from({ length: gridHeight }).map((_, y) =>
            Array.from({ length: gridWidth }).map((_, x) => {
              const symbol = getCellSymbol(x, y);
              return symbol ? (
                <Text
                  key={`symbol-${x}-${y}`}
                  text={symbol}
                  x={x * CELL_SIZE + CELL_SIZE / 2}
                  y={y * CELL_SIZE + CELL_SIZE / 2}
                  anchor={0.5}
                  style={
                    new PIXI.TextStyle({
                      fontFamily: 'monospace',
                      fontSize: 16,
                      fill: 0xFFFFFF,
                      align: 'center',
                    })
                  }
                />
              ) : null;
            })
          )}
        </Container>
      </Stage>
    </GridContainer>
  );
};

export default Grid;

/**
 * Schema OpenAPI 3.0 per le API del gioco RPG
 * Questo file può essere utilizzato per generare documentazione delle API,
 * validare le richieste/risposte e facilitare il test automatizzato.
 */

const API_BASE_URL = '/api';

const apiSchema = {
  openapi: '3.0.0',
  info: {
    title: 'Gioco RPG API',
    description: 'API per il gioco di ruolo basato su server',
    version: '1.0.0',
    contact: {
      email: 'supporto@giocoprg.esempio.it'
    }
  },
  servers: [
    {
      url: API_BASE_URL,
      description: 'Server principale'
    }
  ],
  components: {
    schemas: {
      Errore: {
        type: 'object',
        properties: {
          errore: {
            type: 'string',
            description: 'Messaggio di errore'
          }
        }
      },
      Giocatore: {
        type: 'object',
        properties: {
          nome: { 
            type: 'string',
            description: 'Nome del personaggio'
          },
          classe: { 
            type: 'string',
            description: 'Classe del personaggio'
          },
          livello: { 
            type: 'integer',
            description: 'Livello attuale del personaggio' 
          },
          hp: { 
            type: 'integer',
            description: 'Punti vita attuali' 
          },
          max_hp: { 
            type: 'integer',
            description: 'Punti vita massimi' 
          },
          mana: { 
            type: 'integer',
            description: 'Mana attuale' 
          },
          max_mana: { 
            type: 'integer',
            description: 'Mana massimo' 
          },
          esperienza: { 
            type: 'integer',
            description: 'Punti esperienza attuali' 
          },
          prossimo_livello: { 
            type: 'integer',
            description: 'Punti esperienza necessari per il prossimo livello' 
          }
        }
      },
      Oggetto: {
        type: 'object',
        properties: {
          id: { 
            type: 'string',
            description: 'Identificativo univoco dell\'oggetto' 
          },
          nome: { 
            type: 'string',
            description: 'Nome dell\'oggetto' 
          },
          descrizione: { 
            type: 'string',
            description: 'Descrizione dell\'oggetto' 
          },
          tipo: { 
            type: 'string',
            description: 'Tipo di oggetto (arma, armatura, pozione, ecc.)' 
          },
          valore: { 
            type: 'integer',
            description: 'Valore in monete dell\'oggetto' 
          },
          peso: { 
            type: 'number',
            description: 'Peso dell\'oggetto' 
          },
          effetti: { 
            type: 'object',
            description: 'Effetti dell\'oggetto' 
          },
          utilizzabile: { 
            type: 'boolean',
            description: 'Indica se l\'oggetto è utilizzabile' 
          },
          equipaggiabile: { 
            type: 'boolean',
            description: 'Indica se l\'oggetto è equipaggiabile' 
          }
        }
      },
      NPC: {
        type: 'object',
        properties: {
          id: { 
            type: 'string',
            description: 'Identificativo univoco dell\'NPC' 
          },
          nome: { 
            type: 'string',
            description: 'Nome dell\'NPC' 
          },
          descrizione: { 
            type: 'string',
            description: 'Descrizione dell\'NPC' 
          },
          tipo: { 
            type: 'string',
            description: 'Tipo di NPC (mercante, nemico, neutrale, ecc.)' 
          },
          interagibile: { 
            type: 'boolean',
            description: 'Indica se è possibile interagire con l\'NPC' 
          }
        }
      },
      Notifica: {
        type: 'object',
        properties: {
          id: { 
            type: 'string',
            description: 'Identificativo univoco della notifica' 
          },
          tipo: { 
            type: 'string',
            description: 'Tipo di notifica (info, warning, achievement, quest, combat, ecc.)' 
          },
          messaggio: { 
            type: 'string',
            description: 'Messaggio della notifica' 
          },
          data: { 
            type: 'object',
            description: 'Dati aggiuntivi associati alla notifica' 
          },
          timestamp: { 
            type: 'number',
            description: 'Timestamp della notifica' 
          },
          letta: { 
            type: 'boolean',
            description: 'Indica se la notifica è stata letta' 
          }
        }
      },
      OutputComando: {
        type: 'object',
        properties: {
          testo: { 
            type: 'array',
            items: { type: 'string' },
            description: 'Messaggi testuali generati dal comando' 
          },
          evento: { 
            type: 'string',
            description: 'Tipo di evento generato dal comando' 
          },
          dati: { 
            type: 'object',
            description: 'Dati strutturati associati all\'output del comando' 
          }
        }
      }
    },
    responses: {
      Error400: {
        description: 'Richiesta non valida',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Errore'
            }
          }
        }
      },
      Error404: {
        description: 'Risorsa non trovata',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Errore'
            }
          }
        }
      },
      Error500: {
        description: 'Errore interno del server',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Errore'
            }
          }
        }
      }
    },
    parameters: {
      SessioneId: {
        name: 'id_sessione',
        in: 'query',
        description: 'Identificativo della sessione di gioco',
        required: true,
        schema: {
          type: 'string'
        }
      },
      NomeFile: {
        name: 'nome_file',
        in: 'query',
        description: 'Nome del file di salvataggio',
        required: true,
        schema: {
          type: 'string'
        }
      }
    }
  },
  paths: {
    '/inizia': {
      post: {
        summary: 'Crea una nuova partita',
        description: 'Inizializza una nuova sessione di gioco con un personaggio',
        tags: ['Sessione'],
        requestBody: {
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['nome'],
                properties: {
                  nome: { 
                    type: 'string',
                    description: 'Nome del personaggio'
                  },
                  classe: { 
                    type: 'string',
                    description: 'Classe del personaggio (default: guerriero)'
                  }
                }
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Sessione creata con successo',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    id_sessione: {
                      type: 'string',
                      description: 'Identificativo univoco della sessione di gioco'
                    },
                    messaggio: {
                      type: 'string',
                      description: 'Messaggio di conferma'
                    },
                    stato: {
                      type: 'object',
                      description: 'Stato iniziale del gioco'
                    },
                    stato_nome: {
                      type: 'string',
                      description: 'Nome dello stato corrente'
                    }
                  }
                }
              }
            }
          },
          '400': {
            $ref: '#/components/responses/Error400'
          },
          '500': {
            $ref: '#/components/responses/Error500'
          }
        }
      }
    },
    '/comando': {
      post: {
        summary: 'Invia un comando alla partita',
        description: 'Elabora un comando inviato dal client',
        tags: ['Sessione'],
        requestBody: {
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['id_sessione', 'comando'],
                properties: {
                  id_sessione: {
                    type: 'string',
                    description: 'Identificativo della sessione di gioco'
                  },
                  comando: {
                    type: 'string',
                    description: 'Comando da eseguire'
                  }
                }
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Comando elaborato con successo',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    output: {
                      type: 'array',
                      items: {
                        $ref: '#/components/schemas/OutputComando'
                      },
                      description: 'Output strutturato del comando'
                    },
                    stato: {
                      type: 'object',
                      description: 'Stato aggiornato del gioco'
                    },
                    stato_nome: {
                      type: 'string',
                      description: 'Nome dello stato corrente'
                    },
                    fine: {
                      type: 'boolean',
                      description: 'Indica se il gioco è terminato'
                    }
                  }
                }
              }
            }
          },
          '400': {
            $ref: '#/components/responses/Error400'
          },
          '404': {
            $ref: '#/components/responses/Error404'
          },
          '500': {
            $ref: '#/components/responses/Error500'
          }
        }
      }
    },
    '/stato': {
      get: {
        summary: 'Ottieni lo stato attuale della partita',
        description: 'Restituisce lo stato attuale della sessione di gioco',
        tags: ['Sessione'],
        parameters: [
          {
            $ref: '#/components/parameters/SessioneId'
          }
        ],
        responses: {
          '200': {
            description: 'Stato ottenuto con successo',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  description: 'Stato completo del gioco'
                  // La struttura è variabile in base allo stato del gioco
                }
              }
            }
          },
          '400': {
            $ref: '#/components/responses/Error400'
          },
          '404': {
            $ref: '#/components/responses/Error404'
          }
        }
      }
    },
    '/mappa': {
      get: {
        summary: 'Ottieni informazioni sulla mappa attuale',
        description: 'Restituisce informazioni sulla mappa e sulla posizione del giocatore',
        tags: ['Mappa'],
        parameters: [
          {
            $ref: '#/components/parameters/SessioneId'
          }
        ],
        responses: {
          '200': {
            description: 'Informazioni sulla mappa ottenute con successo',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    nome: {
                      type: 'string',
                      description: 'Nome della mappa'
                    },
                    descrizione: {
                      type: 'string',
                      description: 'Descrizione della mappa'
                    },
                    dimensioni: {
                      type: 'object',
                      properties: {
                        larghezza: {
                          type: 'integer',
                          description: 'Larghezza della mappa'
                        },
                        altezza: {
                          type: 'integer',
                          description: 'Altezza della mappa'
                        }
                      }
                    },
                    celle: {
                      type: 'array',
                      description: 'Struttura delle celle della mappa'
                      // La struttura dettagliata dipende dal gioco
                    },
                    posizione_giocatore: {
                      type: 'object',
                      properties: {
                        x: {
                          type: 'integer',
                          description: 'Coordinata X del giocatore'
                        },
                        y: {
                          type: 'integer',
                          description: 'Coordinata Y del giocatore'
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          '400': {
            $ref: '#/components/responses/Error400'
          },
          '404': {
            $ref: '#/components/responses/Error404'
          }
        }
      }
    },
    '/inventario': {
      get: {
        summary: 'Ottieni l\'inventario del giocatore',
        description: 'Restituisce l\'inventario e l\'equipaggiamento del giocatore',
        tags: ['Giocatore', 'Inventario'],
        parameters: [
          {
            $ref: '#/components/parameters/SessioneId'
          }
        ],
        responses: {
          '200': {
            description: 'Inventario ottenuto con successo',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    inventario: {
                      type: 'array',
                      items: {
                        $ref: '#/components/schemas/Oggetto'
                      },
                      description: 'Oggetti nell\'inventario'
                    },
                    equipaggiamento: {
                      type: 'object',
                      description: 'Oggetti equipaggiati nei vari slot'
                      // Il formato esatto dipende dal gioco
                    }
                  }
                }
              }
            }
          },
          '400': {
            $ref: '#/components/responses/Error400'
          },
          '404': {
            $ref: '#/components/responses/Error404'
          }
        }
      }
    }
    // Altri endpoints omessi per brevità
    // La documentazione completa seguirebbe lo stesso modello per tutti gli endpoint
  }
};

export default apiSchema; 
# Documentazione API Gioco RPG

Questa directory contiene i file di definizione e schema delle API utilizzate nel progetto Gioco RPG. Questi file servono a standardizzare l'utilizzo delle API e fornire una documentazione completa per il team di sviluppo.

## File Inclusi

- **`api-definitions.js`**: Definizioni di tutti gli endpoint API del gioco, inclusi percorsi, metodi, parametri e strutture di risposta. Questo file viene utilizzato direttamente dal client per effettuare chiamate API.

- **`api-schema.js`**: Schema OpenAPI 3.0 che fornisce una documentazione formale delle API. Può essere utilizzato per generare documentazione interattiva o per validare le richieste/risposte.

## Come Utilizzare

### Nel Client (Frontend)

Per utilizzare le definizioni API nel client, importa i componenti necessari:

```javascript
import { API_ENDPOINTS, buildUrl } from '../api/api-definitions';

// Esempio di utilizzo con axios o fetch
const fetchInventario = async (sessioneId) => {
  const url = buildUrl(API_ENDPOINTS.INVENTARIO.path);
  
  // Con axios
  const response = await axios.get(url, {
    params: { id_sessione: sessioneId }
  });
  
  // Oppure con fetch
  // const response = await fetch(`${url}?id_sessione=${sessioneId}`);
  // const data = await response.json();
  
  return response.data;
};
```

### Generare Documentazione

Per generare documentazione interattiva dallo schema OpenAPI:

1. Installa swagger-ui-express (se stai usando Express sul server):

```bash
npm install swagger-ui-express
```

2. Configura nel server:

```javascript
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const apiSchema = require('./frontend/src/api/api-schema').default;

const app = express();

// Configura la documentazione Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(apiSchema));
```

Poi accedi a `http://localhost:tuaporta/api-docs` per visualizzare la documentazione interattiva.

## Estensione e Manutenzione

### Aggiungere un Nuovo Endpoint

1. Aggiungi la definizione dell'endpoint in `api-definitions.js`:

```javascript
NUOVO_ENDPOINT: {
  path: '/nuovo-endpoint',
  method: 'POST', // o GET, PUT, DELETE
  description: 'Descrizione del nuovo endpoint',
  params: {
    parametro1: 'Descrizione del parametro 1',
    parametro2: 'Descrizione del parametro 2'
  },
  response: {
    campo1: 'Descrizione del campo di risposta 1',
    campo2: 'Descrizione del campo di risposta 2'
  }
}
```

2. Aggiungi la documentazione OpenAPI in `api-schema.js`.

3. Crea una funzione helper nel file `api.js` per utilizzare il nuovo endpoint.

## Convenzioni

- I nomi degli endpoint in `api-definitions.js` sono in maiuscolo con underscore come separatore.
- Le descrizioni dovrebbero essere chiare e complete.
- Ogni endpoint dovrebbe specificare accuratamente sia i parametri di input che i dati di risposta.

## Note Importanti

- **Sicurezza**: Gli endpoint che richiedono autenticazione devono specificarlo chiaramente nella documentazione.
- **Controllo Versione**: Prima di modificare un endpoint esistente, valuta se è necessario creare una nuova versione per mantenere la compatibilità con le implementazioni esistenti.
- **Test**: Quando aggiungi o modifichi un endpoint, assicurati di aggiornare i test per verificare il corretto funzionamento.

---

Per qualsiasi domanda o suggerimento riguardante le API, contatta il team di sviluppo. 
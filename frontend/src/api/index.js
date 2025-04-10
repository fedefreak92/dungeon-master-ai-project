/**
 * Entry point per i componenti API
 * Questo file esporta tutte le definizioni e gli strumenti relativi alle API
 * per semplificare l'importazione dai componenti React.
 */

import { API_ENDPOINTS, buildUrl } from './api-definitions';
import apiSchema from './api-schema';

// Interfaccia principale per l'uso delle API
const API = {
  endpoints: API_ENDPOINTS,
  buildUrl,
  schema: apiSchema
};

export { API_ENDPOINTS, buildUrl, apiSchema };
export default API; 
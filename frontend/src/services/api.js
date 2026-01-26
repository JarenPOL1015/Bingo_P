// =============================================================================
// API Service - Comunicación con FastAPI Backend
// =============================================================================

// TODO ESTE CÓDIGO FUE DESARROLLADO POR DARWIN PACHECO

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  // Configuración
  async getConfig() {
    const response = await fetch(`${API_BASE_URL}/config`);
    return response.json();
  },

  // Reset
  async resetGame() {
    const response = await fetch(`${API_BASE_URL}/reset`, {
      method: 'POST'
    });
    return response.json();
  },

  // Carga masiva con configuración de idiomas
  async cargarMasivo(file, nJugadores, configIdiomas, ruleType = 'minimo_uno', bancosIdiomas = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('config_idiomas', JSON.stringify(configIdiomas));
    formData.append('bancos_idiomas', JSON.stringify(bancosIdiomas));
    formData.append('rule_type', ruleType);
    
    const response = await fetch(`${API_BASE_URL}/cargar-masivo?n_jugadores=${nJugadores}`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      const error = new Error('Error de validación');
      error.response = { data };
      throw error;
    }
    
    return data;
  },

  // Agregar jugador manual
  async agregarJugador(jugador) {
    const response = await fetch(`${API_BASE_URL}/agregar-jugador`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jugador)
    });
    return response.json();
  },

  // Generar cartón aleatorio
  async generarCartonAleatorio(idioma) {
    const response = await fetch(`${API_BASE_URL}/generar-carton-aleatorio/${idioma}`, {
      method: 'POST'
    });
    return response.json();
  },

  // Iniciar juego
  async iniciarJuego() {
    const response = await fetch(`${API_BASE_URL}/iniciar-juego`, {
      method: 'POST'
    });
    return response.json();
  },

  // Cantar palabra
  async cantarPalabra(palabra) {
    const response = await fetch(`${API_BASE_URL}/cantar-palabra`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ palabra })
    });
    const data = await response.json();
    if (!response.ok) {
      const error = new Error('Error al cantar palabra');
      error.response = { data };
      throw error;
    }
    return data;
  },

  // Siguiente idioma
  async siguienteIdioma() {
    const response = await fetch(`${API_BASE_URL}/siguiente-idioma`, {
      method: 'POST'
    });
    return response.json();
  },

  // Estado del juego
  async getEstado() {
    const response = await fetch(`${API_BASE_URL}/estado`);
    return response.json();
  },

  // Jugadores
  async getJugadores() {
    const response = await fetch(`${API_BASE_URL}/jugadores`);
    return response.json();
  },

  async getJugador(nombre) {
    const response = await fetch(`${API_BASE_URL}/jugador/${nombre}`);
    return response.json();
  }
};
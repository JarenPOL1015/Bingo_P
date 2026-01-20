import React, { useState } from 'react';
import { api } from '../services/api';
import './GameSetup.css';

const GameSetup = ({ onGameReady }) => {
  // Estados básicos
  const [nJugadores, setNJugadores] = useState(5);
  const [archivo, setArchivo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState(null);
  const [ruleType, setRuleType] = useState('minimo_uno');

  // Configuración de idiomas (editable por el usuario)
  const [idiomas, setIdiomas] = useState([
    { codigo: 'SP', nombre: 'Español', maxPalabras: 24 },
    { codigo: 'EN', nombre: 'Inglés', maxPalabras: 14 },
    { codigo: 'PT', nombre: 'Portugués', maxPalabras: 20 },
    { codigo: 'DT', nombre: 'Dutch', maxPalabras: 10 },
  ]);

  const [mostrarConfig, setMostrarConfig] = useState(false);

  // Agregar nuevo idioma
  const agregarIdioma = () => {
    setIdiomas([...idiomas, { codigo: '', nombre: '', maxPalabras: 0 }]);
  };

  // Actualizar idioma existente
  const actualizarIdioma = (index, campo, valor) => {
    const nuevosIdiomas = [...idiomas];
    if (campo === 'maxPalabras') {
      const num = parseInt(valor);
      nuevosIdiomas[index][campo] = isNaN(num) || num < 0 ? 0 : num;
    } else if (campo === 'codigo') {
      nuevosIdiomas[index][campo] = valor.toUpperCase();
    } else {
      // Para 'nombre', mantener como está (sin convertir a mayúsculas)
      nuevosIdiomas[index][campo] = valor;
    }
    setIdiomas(nuevosIdiomas);
  };

  // Eliminar idioma
  const eliminarIdioma = (index) => {
    setIdiomas(idiomas.filter((_, i) => i !== index));
  };

  const handleCargaMasiva = async () => {
    if (!archivo) {
      setMensaje('⚠️ Por favor seleccione un archivo');
      return;
    }

    // Validar número de jugadores
    if (nJugadores < 2) {
      setMensaje('⚠️ Debe haber mínimo 2 jugadores');
      return;
    }

    // Validar configuración de idiomas - filtrar solo los completos
    const idiomasValidos = idiomas.filter(i => 
      i.codigo && 
      i.codigo.trim() !== '' && 
      i.nombre && 
      i.nombre.trim() !== '' && 
      i.maxPalabras > 0
    );
    
    if (idiomasValidos.length === 0) {
      setMensaje('⚠️ Debe configurar al menos un idioma completo');
      return;
    }

    setLoading(true);
    setMensaje('📤 Subiendo archivo...');
    setError(null);
    
    try {
      // Enviar archivo CON configuración de idiomas
      const resultado = await api.cargarMasivo(archivo, nJugadores, idiomasValidos, ruleType);
      
      setMensaje(`✅ ${resultado.message}`);
      
      setTimeout(() => {
        onGameReady(resultado.estado);
      }, 1500);
      
    } catch (err) {
      console.error('Error:', err);
      
      let mensajeError = '❌ Error al cargar el archivo';
      let errorDetalle = null;
      
      if (err.response && err.response.data) {
        const data = err.response.data;
        if (data.detail) {
          if (typeof data.detail === 'string') {
            mensajeError = `❌ ${data.detail}`;
          } else if (data.detail.error) {
            mensajeError = `❌ ${data.detail.error}`;
            errorDetalle = data.detail.linea;
          }
        }
      }
      
      setMensaje(mensajeError);
      setError(errorDetalle);
      setLoading(false);
    }
  };

  return (
    <div className="game-setup">
      {/* Header */}
      <div className="header">
        <h1>🎲 Bingo - Configuración</h1>
        <p className="subtitle">
          Sistema con Divide y Conquista (Búsqueda Binaria O(log n))
        </p>
      </div>

      {/* Configuración de Idiomas */}
      <div className="config-idiomas">
        <div className="config-header">
          <h3>⚙️ Configuración de Idiomas</h3>
          <button 
            className="btn-toggle"
            onClick={() => setMostrarConfig(!mostrarConfig)}
            type="button"
          >
            {mostrarConfig ? '▼ Ocultar' : '▶ Mostrar'}
          </button>
        </div>

        {mostrarConfig && (
          <div className="idiomas-list">
            {idiomas.map((idioma, idx) => (
              <div key={idx} className="idioma-row">
                <input
                  type="text"
                  placeholder="Código (ej: SP)"
                  value={idioma.codigo}
                  onChange={(e) => actualizarIdioma(idx, 'codigo', e.target.value)}
                  maxLength="2"
                  disabled={loading}
                />
                <input
                  type="text"
                  placeholder="Nombre (ej: Español)"
                  value={idioma.nombre}
                  onChange={(e) => actualizarIdioma(idx, 'nombre', e.target.value)}
                  disabled={loading}
                />
                <input
                  type="number"
                  placeholder="Max palabras"
                  value={idioma.maxPalabras || ''}
                  onChange={(e) => actualizarIdioma(idx, 'maxPalabras', e.target.value)}
                  min="1"
                  disabled={loading}
                />
                <button
                  className="btn-eliminar"
                  onClick={() => eliminarIdioma(idx)}
                  disabled={loading || idiomas.length <= 1}
                  type="button"
                >
                  🗑️
                </button>
              </div>
            ))}
            <button 
              className="btn-agregar"
              onClick={agregarIdioma}
              disabled={loading}
              type="button"
            >
              ➕ Agregar Idioma
            </button>
          </div>
        )}
      </div>

      {/* Formulario de carga */}
      <div className="form-container">
        <h2>📁 Carga Masiva de Cartones</h2>
        
        <div className="form-group">
          <label>👥 Número de Jugadores:</label>
          <input 
            type="number" 
            min="2"
            max="100"
            value={nJugadores}
            onChange={(e) => {
              const val = parseInt(e.target.value);
              if (val >= 2) setNJugadores(val);
            }}
            disabled={loading}
          />
          <small>Mínimo 2 jugadores - Los cartones se repartirán equitativamente</small>
        </div>

        <div className="form-group">
          <label>📄 Archivo de Cartones (.txt):</label>
          <input 
            type="file" 
            accept=".txt" 
            onChange={(e) => setArchivo(e.target.files[0])}
            disabled={loading}
          />
          {archivo && (
            <div className="archivo-info">
              ✓ Archivo seleccionado: <strong>{archivo.name}</strong>
            </div>
          )}
        </div>

        <div className="form-group">
          <label>🧩 Regla de reparto:</label>
          <select
            value={ruleType}
            onChange={(e) => setRuleType(e.target.value)}
            disabled={loading}
          >
            <option value="minimo_uno">Mínimo un cartón por jugador</option>
            <option value="uno_por_idioma">Un cartón de cada idioma por jugador</option>
          </select>
          <small>Elige cómo se reparten los cartones tras la carga.</small>
        </div>

        <button 
          className="btn-primary" 
          onClick={handleCargaMasiva}
          disabled={loading}
        >
          {loading ? '⏳ Cargando...' : '📥 Cargar y Repartir Cartones'}
        </button>
      </div>

      {/* Mensajes */}
      {mensaje && (
        <div className={`mensaje ${mensaje.includes('❌') ? 'error' : 'success'}`}>
          {mensaje}
        </div>
      )}

      {/* Error detallado */}
      {error && (
        <div className="error-detallado">
          <h4>❌ Error en el archivo:</h4>
          <pre>{error}</pre>
        </div>
      )}

      {/* Info */}
      <div className="info-box">
        <h3>ℹ️ ¿Cómo funciona?</h3>
        <ol>
          <li>Configura los idiomas y cantidad máxima de palabras</li>
          <li>Selecciona un archivo .txt con cartones</li>
          <li>Define cuántos jugadores participarán</li>
          <li>El sistema valida formato y cantidad de palabras</li>
          <li>Usa <strong>búsqueda binaria O(log n)</strong> para marcar palabras</li>
        </ol>
        
        <h3>📝 Formato del archivo:</h3>
        <pre>
SP000001 CASA PERRO GATO SOL LUNA ...
EN000002 HOUSE DOG CAT SUN MOON ...
        </pre>
        <small>• ID: 8 caracteres (2 letras + 6 números)</small>
      </div>
    </div>
  );
};

export default GameSetup;
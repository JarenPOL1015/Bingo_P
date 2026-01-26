import React, { useState } from 'react';
import { api } from '../services/api';
import IdiomasModal from './IdiomasModal';
import './GameSetup.css';

/*
  TODO ESTE CÓDIGO FUE DESARROLLADO POR DARWIN PACHECO
*/

// Banco de palabras predefinidas
const BANCO_PREDEFINIDO = {
  'SP': ['CASA', 'PERRO', 'GATO', 'SOL', 'LUNA', 'PLAYA', 'MAR', 'TIEMPO', 'VIDA', 'MANZANA', 
         'MESA', 'SILLA', 'ARBOL', 'COCHE', 'LIBRO', 'COMPUTADORA', 'TECLADO', 'RATON', 
         'PANTALLA', 'INTERNET', 'CODIGO', 'PYTHON', 'JAVA', 'DATOS'],
  'EN': ['HOUSE', 'DOG', 'CAT', 'SUN', 'MOON', 'BEACH', 'SEA', 'TIME', 'LIFE', 'APPLE', 
         'TABLE', 'CHAIR', 'TREE', 'CAR', 'BOOK', 'COMPUTER', 'KEYBOARD', 'MOUSE', 
         'SCREEN', 'INTERNET', 'CODE', 'PYTHON', 'JAVA', 'DATA'],
  'PT': ['CASA', 'CACHORRO', 'GATO', 'SOL', 'LUA', 'PRAIA', 'MAR', 'TEMPO', 'VIDA', 'MACA', 
         'MESA', 'CADEIRA', 'ARVORE', 'CARRO', 'LIVRO', 'COMPUTADOR', 'TECLADO', 'MOUSE', 
         'TELA', 'INTERNET', 'CODIGO', 'PYTHON', 'JAVA', 'DADOS'],
  'DT': ['HUIS', 'HOND', 'KAT', 'ZON', 'MAAN', 'STRAND', 'ZEE', 'TIJD', 'LEVEN', 'APPEL', 
         'TAFEL', 'STOEL', 'BOOM', 'AUTO', 'BOEK', 'COMPUTER', 'TOETSENBORD', 'MUIS', 
         'SCHERM', 'INTERNET', 'CODE', 'PYTHON', 'JAVA', 'DATA']
};

const GameSetup = ({ onGameReady }) => {
  // Estados básicos
  const [nJugadores, setNJugadores] = useState(5);
  const [archivo, setArchivo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState(null);
  const [ruleType, setRuleType] = useState('minimo_uno');

  // Configuración de idiomas con banco de palabras
  const [idiomas, setIdiomas] = useState([
    { codigo: 'SP', nombre: 'Español', palabras: BANCO_PREDEFINIDO['SP'], cantidadEnCarton: 24 },
    { codigo: 'EN', nombre: 'Inglés', palabras: BANCO_PREDEFINIDO['EN'], cantidadEnCarton: 14 },
    { codigo: 'PT', nombre: 'Portugués', palabras: BANCO_PREDEFINIDO['PT'], cantidadEnCarton: 20 },
    { codigo: 'DT', nombre: 'Dutch', palabras: BANCO_PREDEFINIDO['DT'], cantidadEnCarton: 10 },
  ]);

  const [mostrarModalIdiomas, setMostrarModalIdiomas] = useState(false);

  // Actualizar cantidad de palabras en cartón
  const actualizarCantidadCarton = (codigo, cantidad) => {
    const nuevosIdiomas = idiomas.map(idioma => {
      if (idioma.codigo === codigo) {
        return { ...idioma, cantidadEnCarton: Math.max(0, parseInt(cantidad) || 0) };
      }
      return idioma;
    });
    setIdiomas(nuevosIdiomas);
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

    // Validar configuración de idiomas
    const idiomasValidos = idiomas.filter(i => 
      i.codigo && 
      i.codigo.trim() !== '' && 
      i.nombre && 
      i.nombre.trim() !== '' && 
      i.palabras && 
      i.palabras.length > 0
    );
    
    if (idiomasValidos.length === 0) {
      setMensaje('⚠️ Debe configurar al menos un idioma con palabras');
      return;
    }

    setLoading(true);
    setMensaje('📤 Subiendo archivo...');
    setError(null);
    
    try {
      // Convertir al formato esperado por el backend
      const idiomasConfig = idiomasValidos.map(idioma => ({
        codigo: idioma.codigo,
        nombre: idioma.nombre,
        maxPalabras: idioma.cantidadEnCarton
      }));

      // Bancos declarados (incluye idiomas personalizados)
      const bancosIdiomas = idiomasValidos.reduce((acc, idioma) => {
        acc[idioma.codigo] = idioma.palabras || [];
        return acc;
      }, {});

      // Enviar archivo CON configuración de idiomas
      const resultado = await api.cargarMasivo(archivo, nJugadores, idiomasConfig, ruleType, bancosIdiomas);
      
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

      {/* Configuración de Idiomas - Vista Simple */}
      <div className="config-idiomas-simple">
        <div className="config-header-simple">
          <h3>📚 Idiomas Configurados</h3>
          <button 
            className="btn-configurar"
            onClick={() => setMostrarModalIdiomas(true)}
            type="button"
            disabled={loading}
          >
            ⚙️ Configurar Bancos de Palabras
          </button>
        </div>

        {/* Tarjetas de idiomas mostrando máximo de palabras */}
        <div className="idiomas-summary">
          {idiomas.map((idioma) => (
            <div key={idioma.codigo} className="idioma-summary-card">
              <div className="idioma-summary-code">{idioma.codigo}</div>
              <div className="idioma-summary-info">
                <h4>{idioma.nombre}</h4>
                <div className="cantidad-input-wrapper">
                  <input
                    type="number"
                    min="0"
                    value={idioma.cantidadEnCarton || 0}
                    onChange={(e) => actualizarCantidadCarton(idioma.codigo, e.target.value)}
                    disabled={loading}
                    className="input-cantidad-carton"
                  />
                  <span>palabras/cartón</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de configuración de idiomas */}
      {mostrarModalIdiomas && (
        <IdiomasModal
          idiomas={idiomas}
          setIdiomas={setIdiomas}
          onClose={() => setMostrarModalIdiomas(false)}
          loading={loading}
        />
      )}

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
            lang="es"
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
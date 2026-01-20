import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './GameBoard.css';

/**
 * GameBoard - Tablero principal del juego
 * Visualiza cartones y gestiona el flujo del juego
 */
const GameBoard = ({ estadoInicial }) => {
  const [estado, setEstado] = useState(estadoInicial);
  const [palabraInput, setPalabraInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [ganador, setGanador] = useState(null);
  const [finSinGanador, setFinSinGanador] = useState(false);
  const [modalError, setModalError] = useState(null);

  useEffect(() => {
    if (estadoInicial) {
      setEstado(estadoInicial);
    }
  }, [estadoInicial]);

  const actualizarEstado = async () => {
    try {
      const nuevoEstado = await api.getEstado();
      setEstado(nuevoEstado);
    } catch (error) {
      console.error('Error al actualizar estado:', error);
    }
  };

  const handleCantarPalabra = async (e) => {
    e.preventDefault();
    
    if (!palabraInput.trim()) {
      setMensaje('Ingrese una palabra');
      return;
    }

    setLoading(true);
    try {
      const resultado = await api.cantarPalabra(palabraInput.toUpperCase());
      
      if (resultado.hay_ganador) {
        setGanador(resultado.ganadores);
        setMensaje(`🎉 ¡BINGO! ${resultado.ganadores[0].jugador} ganó con el cartón ${resultado.ganadores[0].carton_id}`);
      } else {
        setMensaje(`✅ "${resultado.palabra}" cantada - Sin ganadores`);
      }

      await actualizarEstado();
      setPalabraInput('');

      // Avanzar de inmediato a la siguiente ronda si no hay ganador y no terminó
      if (!resultado.hay_ganador && !resultado.juego_terminado) {
        try {
          await handleSiguienteIdioma();
        } catch (_) {
          /* ignore */
        }
      }
    } catch (error) {
      const detail = error?.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : (detail?.error || '❌ Error al cantar palabra');
      if (msg.toLowerCase().includes('no pertenece al idioma')) {
        setModalError(msg);
      } else {
        setMensaje(msg);
      }
    }
    setLoading(false);
  };

  const handleSiguienteIdioma = async () => {
    setLoading(true);
    try {
      const resultado = await api.siguienteIdioma();
      
      if (resultado.success) {
        // No mostramos alerta flotante en cambio de idioma
        await actualizarEstado();
      } else {
        setMensaje(resultado.message);
      }
    } catch (error) {
      setMensaje('❌ Error al cambiar idioma');
    }
    setLoading(false);
  };

  const handleReiniciar = async () => {
    if (window.confirm('¿Desea reiniciar el juego?')) {
      await api.resetGame();
      window.location.reload();
    }
  };

  const handleFinalizar = async () => {
    if (window.confirm('¿Finalizar el juego sin ganador?')) {
      // Cerrar partida mostrando modal pero con mensaje de que no hubo ganador
      setMensaje('⏹️ No ganó nadie el bingo');
      setFinSinGanador(true);
      setGanador([{ jugador: 'Nadie', carton_id: '—' }]);
      setEstado((prev) => prev ? { ...prev, juego_activo: false } : prev);
    }
  };

  if (!estado || !estado.idioma_actual) {
    return (
      <div className="loading-screen">
        <div className="loading-card">
          <div className="loading-spinner" aria-label="Cargando" />
          <h2>Cargando juego...</h2>
          <p>Preparando cartones y ordenando idiomas.</p>
          <div className="loading-progress">
            <span className="dot active" />
            <span className="dot" />
            <span className="dot" />
          </div>
        </div>
      </div>
    );
  }

  const idiomaActual = estado.idioma_actual;

  return (
    <div className="game-board">
      {/* Header */}
      <div className="game-header">
        <h1>🎲 Bingo en Progreso</h1>
        <div className="header-actions">
          <button onClick={handleFinalizar} className="btn-finalizar">⏹️ Finalizar</button>
          <button onClick={handleReiniciar} className="btn-reset">🔄 Reiniciar</button>
        </div>
      </div>

      {/* Panel de control */}
      <div className="control-panel">
        <div className="idioma-info">
          <h2>Idioma Actual: {idiomaActual.nombre}</h2>
          <div className="idiomas-orden">
            {estado.orden_idiomas.map((lang, idx) => (
              <span 
                key={lang} 
                className={`idioma-badge ${idx === idiomaActual.indice ? 'active' : ''} ${idx < idiomaActual.indice ? 'completed' : ''}`}
              >
                {lang}
              </span>
            ))}
          </div>
        </div>

        <div className="ronda-info">Idioma de la ronda: <span className="badge-idioma">{idiomaActual.codigo} - {idiomaActual.nombre}</span></div>

        <form onSubmit={handleCantarPalabra} className="cantar-form">
          <input 
            type="text" 
            value={palabraInput}
            onChange={(e) => setPalabraInput(e.target.value)}
            placeholder="Ingrese palabra..."
            disabled={loading || ganador}
          />
          <button type="submit" disabled={loading || ganador}>
            {loading ? '...' : '📢 Cantar'}
          </button>
        </form>

        {/* Palabras cantadas */}
        <div className="palabras-cantadas">
          <strong>Palabras cantadas:</strong>
          <div className="palabras-list">
            {(estado.palabras_cantadas || []).map((p, idx) => {
              const esObjeto = p && typeof p === 'object';
              const codigo = esObjeto ? p.idioma : (String(p).split(':')[0] || '');
              const texto = esObjeto ? p.palabra : (String(p).includes(':') ? String(p).split(':').slice(1).join(':') : String(p));
              return (
                <span key={idx} className="palabra-tag">
                  {codigo && <span className="palabra-codigo">{codigo}</span>} {texto}
                </span>
              );
            })}
          </div>
        </div>
      </div>

      {/* Vista de cartones ocultada para el operador */}

      {/* Modal de ganador */}
      {ganador && (
        <div className="modal-overlay" onClick={() => { setGanador(null); setFinSinGanador(false); }}>
          <div className={`modal-ganador ${finSinGanador ? 'loss' : 'win'}`} onClick={(e) => e.stopPropagation()}>
            <h2>{finSinGanador ? '⏹️ Partida finalizada' : '🎉 ¡BINGO! 🎉'}</h2>
            {ganador.map((g, idx) => (
              <div key={idx} className="ganador-info">
                <h3>{g.jugador}</h3>
                <p>Cartón: {g.carton_id}</p>
              </div>
            ))}
            <button onClick={handleReiniciar} className="btn-primary">
              Nuevo Juego
            </button>
          </div>
        </div>
      )}

      {modalError && (
        <div className="modal-overlay" onClick={() => setModalError(null)}>
          <div className="modal-alert" onClick={(e) => e.stopPropagation()}>
            <h3>Palabra inválida</h3>
            <p>{modalError}</p>
            <button className="btn-primary" onClick={() => setModalError(null)}>Entendido</button>
          </div>
        </div>
      )}

      {/* Mensajes */}
      {mensaje && (
        <div className={`mensaje-flotante ${mensaje.includes('❌') ? 'error' : 'success'}`}>
          {mensaje}
        </div>
      )}
    </div>
  );
};

export default GameBoard;

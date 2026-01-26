import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './GameBoard.css';

/*
  TODO ESTE CÓDIGO FUE DESARROLLADO POR DARWIN PACHECO
*/

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
  const [mostrarBancoPalabras, setMostrarBancoPalabras] = useState(false);
  const [mostrarTodosCartones, setMostrarTodosCartones] = useState(false);
  const [cartonSeleccionado, setCartonSeleccionado] = useState(null);

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
      if (msg.toLowerCase().includes('no pertenece al idioma') || 
          msg.toLowerCase().includes('no existe en ningún cartón') ||
          msg.toLowerCase().includes('pertenece al idioma')) {
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

  // Obtener todos los cartones ordenados por aciertos (mayor a menor)
  const obtenerCartonesOrdenados = () => {
    if (!estado || !estado.jugadores) return [];
    
    const todosCartones = [];
    estado.jugadores.forEach(jugador => {
      (jugador.cartones || []).forEach(carton => {
        todosCartones.push({
          ...carton,
          jugador: jugador.nombre
        });
      });
    });
    
    return todosCartones.sort((a, b) => b.aciertos - a.aciertos);
  };

  const cartonesOrdenados = obtenerCartonesOrdenados();
  const cincoTopCartones = cartonesOrdenados.slice(0, 5);

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
          <button 
            type="button"
            className="btn-banco-palabras"
            onClick={() => setMostrarBancoPalabras(true)}
            disabled={loading || ganador}
          >
            📚 Ver banco
          </button>
        </form>

        {/* Palabras cantadas */}
        <div className="palabras-cantadas">
          <strong>Palabras cantadas:</strong>
          <div className="palabras-por-idioma">
            {(() => {
              // Crear mapa de códigos a nombres desde idiomas_orden (misma fuente que idioma_actual)
              const nombresIdiomas = {};
              if (estado.idiomas_orden) {
                estado.idiomas_orden.forEach(idioma => {
                  if (typeof idioma === 'object') {
                    nombresIdiomas[idioma.codigo] = idioma.nombre;
                  }
                });
              }

              // Agrupar palabras por idioma
              const palabrasPorIdioma = {};
              (estado.palabras_cantadas || []).forEach(p => {
                const esObjeto = p && typeof p === 'object';
                const codigo = esObjeto ? p.idioma : (String(p).split(':')[0] || '');
                const texto = esObjeto ? p.palabra : (String(p).includes(':') ? String(p).split(':').slice(1).join(':') : String(p));
                
                if (!palabrasPorIdioma[codigo]) {
                  palabrasPorIdioma[codigo] = [];
                }
                palabrasPorIdioma[codigo].push(texto);
              });

              // Renderizar por idioma
              return Object.entries(palabrasPorIdioma).map(([idioma, palabras]) => {
                return (
                  <div key={idioma} className="idioma-grupo">
                    <div className="idioma-grupo-titulo">
                      {idioma.toUpperCase()}:
                    </div>
                    <div className="palabras-list">
                      {palabras.map((palabra, idx) => (
                        <span key={idx} className="palabra-tag">
                          {palabra}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              });
            })()}
          </div>
        </div>
      </div>

      {/* Sección de Cartones */}
      <div className="cartones-section">
        <div className="cartones-header">
          <h3>📦 Cartones con Mayor Progreso</h3>
        </div>
        
        <div className="cartones-grid">
          {cincoTopCartones.map((carton, idx) => (
            <div 
              key={`${carton.id}-${idx}`} 
              className="carton-card"
              onClick={() => setCartonSeleccionado(carton)}
            >
              <div className="carton-header">
                <h4>{carton.id}</h4>
                <span className="carton-jugador">{carton.jugador}</span>
              </div>
              <div className="carton-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${(carton.aciertos / carton.total_palabras) * 100}%` }}
                  />
                </div>
                <span className="progress-text">{carton.aciertos}/{carton.total_palabras}</span>
              </div>
              <div className="carton-status">
                {carton.es_ganador ? (
                  <span className="badge-ganador">🏆 ¡GANADOR!</span>
                ) : (
                  <span className="badge-progreso">{((carton.aciertos / carton.total_palabras) * 100).toFixed(0)}%</span>
                )}
              </div>
              <div className="carton-hint">Click para ver palabras</div>
            </div>
          ))}
        </div>

        {cartonesOrdenados.length > 5 && (
          <button 
            className="btn-ver-todos-cartones"
            onClick={() => setMostrarTodosCartones(true)}
          >
            👁️ Ver todos los cartones ({cartonesOrdenados.length})
          </button>
        )}
      </div>

      {/* Vista de cartones ocultada para el operador */}
      {/* Modal de detalles del cartón */}
      {cartonSeleccionado && (
        <div className="modal-overlay" onClick={() => setCartonSeleccionado(null)}>
          <div className="modal-carton-detalle" onClick={(e) => e.stopPropagation()}>
            <div className="modal-carton-header">
              <div className="carton-detalle-info">
                <h2>{cartonSeleccionado.id}</h2>
                <p className="carton-jugador-detalle">Jugador: {cartonSeleccionado.jugador}</p>
              </div>
              <button 
                className="btn-cerrar-modal" 
                onClick={() => setCartonSeleccionado(null)}
              >
                ✕
              </button>
            </div>

            <div className="carton-stats">
              <div className="stat-item">
                <span className="stat-label">Palabras Acertadas</span>
                <span className="stat-value">{cartonSeleccionado.aciertos}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Palabras</span>
                <span className="stat-value">{cartonSeleccionado.total_palabras}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Porcentaje</span>
                <span className="stat-value">{((cartonSeleccionado.aciertos / cartonSeleccionado.total_palabras) * 100).toFixed(1)}%</span>
              </div>
              {cartonSeleccionado.es_ganador && (
                <div className="stat-item ganador-item">
                  <span className="stat-label">Estado</span>
                  <span className="stat-value">🏆 GANADOR</span>
                </div>
              )}
            </div>

            <div className="carton-progress-detalle">
              <div className="progress-bar-detalle">
                <div 
                  className="progress-fill-detalle" 
                  style={{ width: `${(cartonSeleccionado.aciertos / cartonSeleccionado.total_palabras) * 100}%` }}
                />
              </div>
            </div>

            <div className="carton-palabras-container">
              <h3>Palabras del Cartón</h3>
              <div className="carton-palabras-grid">
                {cartonSeleccionado.palabras.map((palabra, idx) => {
                  const esMarcada = cartonSeleccionado.palabras_marcadas.includes(palabra);
                  return (
                    <div 
                      key={`${palabra}-${idx}`} 
                      className={`palabra-cell ${esMarcada ? 'marcada' : 'no-marcada'}`}
                      title={esMarcada ? '✓ Cantada' : 'No cantada aún'}
                    >
                      <span className="palabra-texto">{palabra}</span>
                      {esMarcada && <span className="palabra-check">✓</span>}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="modal-footer-carton">
              <button 
                className="btn-cerrar"
                onClick={() => setCartonSeleccionado(null)}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Modal de Todos los Cartones */}
      {mostrarTodosCartones && (
        <div className="modal-overlay" onClick={() => setMostrarTodosCartones(false)}>
          <div className="modal-todos-cartones" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-cartones">
              <h2>📦 Todos los Cartones</h2>
              <button 
                className="btn-cerrar-modal" 
                onClick={() => setMostrarTodosCartones(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="cartones-list-completa">
              {cartonesOrdenados.map((carton, idx) => (
                <div 
                  key={`${carton.id}-${idx}`} 
                  className="carton-row"
                  onClick={() => {
                    setCartonSeleccionado(carton);
                    setMostrarTodosCartones(false);
                  }}
                >
                  <span className="carton-rank">#{idx + 1}</span>
                  <span className="carton-id">{carton.id}</span>
                  <span className="carton-jugador-nombre">{carton.jugador}</span>
                  <div className="carton-progress-inline">
                    <div className="progress-bar-small">
                      <div 
                        className="progress-fill-small" 
                        style={{ width: `${(carton.aciertos / carton.total_palabras) * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="carton-aciertos">
                    {carton.aciertos}/{carton.total_palabras}
                  </span>
                  <span className="carton-porcentaje">
                    {((carton.aciertos / carton.total_palabras) * 100).toFixed(0)}%
                  </span>
                  {carton.es_ganador && <span className="badge-ganador-small">🏆</span>}
                </div>
              ))}
            </div>
            
            <div className="modal-footer-cartones">
              <button 
                className="btn-cerrar"
                onClick={() => setMostrarTodosCartones(false)}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

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

      {/* Modal de banco de palabras */}
      {mostrarBancoPalabras && estado && (
        <div className="modal-overlay" onClick={() => setMostrarBancoPalabras(false)}>
          <div className="modal-banco-palabras" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-banco">
              <h2>📚 Banco de Palabras - {idiomaActual?.nombre || 'Idioma'}</h2>
              <button 
                className="btn-cerrar-modal" 
                onClick={() => setMostrarBancoPalabras(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="palabras-grid">
              {(() => {
                const palabras = estado?.banco_palabras?.[idiomaActual?.codigo] || [];

                return palabras.length > 0 ? (
                  palabras.map((palabra) => (
                    <div 
                      key={palabra} 
                      className={`palabra-badge ${estado.palabras_cantadas?.some(p => (p?.palabra || p) === palabra && (p?.idioma || idiomaActual?.codigo) === idiomaActual?.codigo) ? 'cantada' : ''}`}
                    >
                      {palabra}
                    </div>
                  ))
                ) : (
                  <p className="sin-palabras">No hay palabras configuradas para este idioma</p>
                );
              })()}
            </div>
            
            <div className="modal-footer-banco">
              <p className="total-palabras">Total: {(estado?.banco_palabras?.[idiomaActual?.codigo] || []).length} palabras</p>
              <button 
                className="btn-cerrar"
                onClick={() => setMostrarBancoPalabras(false)}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameBoard;

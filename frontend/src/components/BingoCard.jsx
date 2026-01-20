import React from 'react';
import './BingoCard.css';

/**
 * Componente BingoCard - Visualiza un cartón de bingo
 * Mantiene la integridad de los datos procesados por el algoritmo DAC
 */
const BingoCard = ({ carton, isActive }) => {
  const { id, idioma, palabras, palabras_marcadas, aciertos, total_palabras, es_ganador } = carton;

  // Calcular progreso
  const progreso = total_palabras > 0 ? (aciertos / total_palabras * 100).toFixed(0) : 0;

  // Determinar el color del idioma
  const idiomaColor = {
    'SP': '#ff6b6b',
    'EN': '#4dabf7',
    'PT': '#51cf66',
    'DT': '#ffa94d'
  };

  return (
    <div className={`bingo-card ${es_ganador ? 'ganador' : ''} ${isActive ? 'active' : 'inactive'}`}>
      {/* Header */}
      <div className="card-header" style={{ backgroundColor: idiomaColor[idioma] }}>
        <h3>{id}</h3>
        <span className="idioma-badge">{idioma}</span>
      </div>

      {/* Progreso */}
      <div className="card-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progreso}%`, backgroundColor: idiomaColor[idioma] }}
          ></div>
        </div>
        <span className="progress-text">{aciertos} / {total_palabras}</span>
      </div>

      {/* Grid de palabras */}
      <div className="palabras-grid">
        {palabras.map((palabra, idx) => {
          const marcada = palabras_marcadas.includes(palabra);
          return (
            <div 
              key={idx} 
              className={`palabra-cell ${marcada ? 'marcada' : ''}`}
              style={marcada ? { backgroundColor: idiomaColor[idioma] } : {}}
            >
              {palabra}
              {marcada && <div className="check-mark">✓</div>}
            </div>
          );
        })}
      </div>

      {/* Footer con estado de ganador */}
      {es_ganador && (
        <div className="ganador-banner">
          🎉 ¡BINGO! 🎉
        </div>
      )}
    </div>
  );
};

export default BingoCard;

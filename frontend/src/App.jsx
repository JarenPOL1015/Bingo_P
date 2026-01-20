import React, { useState } from 'react';
import GameSetup from './pages/GameSetup';
import GameBoard from './pages/GameBoard';
import './App.css';

/**
 * App Principal
 * Gestiona el flujo entre Setup y Juego
 */
function App() {
  const [juegoIniciado, setJuegoIniciado] = useState(false);
  const [estadoJuego, setEstadoJuego] = useState(null);

  const handleGameReady = (estado) => {
    setEstadoJuego(estado);
    setJuegoIniciado(true);
  };

  return (
    <div className="App">
      {!juegoIniciado ? (
        <GameSetup onGameReady={handleGameReady} />
      ) : (
        <GameBoard estadoInicial={estadoJuego} />
      )}
    </div>
  );
}

export default App;

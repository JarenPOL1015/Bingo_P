import React, { useState } from 'react';
import './IdiomasModal.css';

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

const IdiomasModal = ({ idiomas, setIdiomas, onClose, loading }) => {
  const [nuevaPalabra, setNuevaPalabra] = useState('');
  const [idiomaEnEdicion, setIdiomaEnEdicion] = useState(null);
  const [nombreNuevoIdioma, setNombreNuevoIdioma] = useState('');
  const [codigoNuevoIdioma, setCodigoNuevoIdioma] = useState('');
  const [archivoCargaIdioma, setArchivoCargaIdioma] = useState(null);

  // Agregar nueva palabra al banco
  const agregarPalabra = (codigo) => {
    if (!nuevaPalabra.trim()) return;
    const palabra = nuevaPalabra.toUpperCase().trim();
    
    const nuevosIdiomas = idiomas.map(idioma => {
      if (idioma.codigo === codigo && !idioma.palabras.includes(palabra)) {
        return { ...idioma, palabras: [...idioma.palabras, palabra] };
      }
      return idioma;
    });
    
    setIdiomas(nuevosIdiomas);
    setNuevaPalabra('');
  };

  // Eliminar palabra del banco
  const eliminarPalabra = (codigo, palabra) => {
    const nuevosIdiomas = idiomas.map(idioma => {
      if (idioma.codigo === codigo) {
        return { ...idioma, palabras: idioma.palabras.filter(p => p !== palabra) };
      }
      return idioma;
    });
    setIdiomas(nuevosIdiomas);
  };

  // Agregar nuevo idioma personalizado
  const agregarIdioma = () => {
    if (!codigoNuevoIdioma.trim() || !nombreNuevoIdioma.trim()) {
      alert('Por favor completa código y nombre');
      return;
    }

    const codigo = codigoNuevoIdioma.toUpperCase().trim();
    
    // Verificar que no exista
    if (idiomas.some(i => i.codigo === codigo)) {
      alert('Este código de idioma ya existe');
      return;
    }

    setIdiomas([...idiomas, { 
      codigo, 
      nombre: nombreNuevoIdioma.trim(), 
      palabras: [],
      cantidadEnCarton: 0
    }]);

    setCodigoNuevoIdioma('');
    setNombreNuevoIdioma('');
  };

  // Eliminar idioma
  const eliminarIdioma = (codigo) => {
    setIdiomas(idiomas.filter(i => i.codigo !== codigo));
  };

  // Actualizar cantidad de palabras en cartón
  const actualizarCantidad = (codigo, cantidad) => {
    const nuevosIdiomas = idiomas.map(idioma => {
      if (idioma.codigo === codigo) {
        return { ...idioma, cantidadEnCarton: Math.max(0, Math.min(24, cantidad)) };
      }
      return idioma;
    });
    setIdiomas(nuevosIdiomas);
  };

  // Cargar palabras desde archivo
  const cargarPalabrasDesdeArchivo = (codigo) => {
    if (!archivoCargaIdioma) {
      alert('Por favor selecciona un archivo');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const contenido = e.target.result;
        // Dividir por saltos de línea y limpiar
        const palabras = contenido
          .split('\n')
          .map(p => p.trim().toUpperCase())
          .filter(p => p.length > 0); // Eliminar líneas vacías

        if (palabras.length === 0) {
          alert('El archivo no contiene palabras válidas');
          return;
        }

        const nuevosIdiomas = idiomas.map(idioma => {
          if (idioma.codigo === codigo) {
            // Agregar palabras nuevas (evitar duplicados)
            const palabrasActuales = new Set(idioma.palabras);
            const palabrasNuevas = palabras.filter(p => !palabrasActuales.has(p));
            return { ...idioma, palabras: [...idioma.palabras, ...palabrasNuevas] };
          }
          return idioma;
        });

        setIdiomas(nuevosIdiomas);
        setArchivoCargaIdioma(null);
        alert(`Se agregaron ${palabras.filter(p => !idiomas.find(i => i.codigo === codigo).palabras.includes(p)).length} palabras al banco`);
      } catch (error) {
        alert('Error al procesar el archivo: ' + error.message);
      }
    };
    reader.readAsText(archivoCargaIdioma);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {/* Header */}
        <div className="modal-header">
          <h2>⚙️ Configurar Idiomas y Banco de Palabras</h2>
          <button className="btn-cerrar" onClick={onClose} type="button">✕</button>
        </div>

        {/* Contenido scrollable */}
        <div className="modal-body">
          {/* Idiomas existentes */}
          <div className="idiomas-section">
            <h3>Idiomas Configurados</h3>
            <div className="idiomas-cards">
              {idiomas.map((idioma) => (
                <div key={idioma.codigo} className="idioma-card">
                  {/* Header de idioma */}
                  <div className="idioma-card-header">
                    <div className="idioma-info">
                      <h4>{idioma.codigo}</h4>
                      <p>{idioma.nombre}</p>
                    </div>
                    <div className="cantidad-carton">
                      <label>Palabras/Cartón:</label>
                      <input
                        type="number"
                        min="0"
                        max="24"
                        value={idioma.cantidadEnCarton || 0}
                        onChange={(e) => actualizarCantidad(idioma.codigo, parseInt(e.target.value) || 0)}
                        disabled={loading}
                        className="input-cantidad"
                      />
                    </div>
                    <span className="palabra-count">{idioma.palabras.length} disponibles</span>
                    <button
                      className="btn-eliminar-idioma"
                      onClick={() => eliminarIdioma(idioma.codigo)}
                      disabled={loading}
                      type="button"
                      title="Eliminar idioma"
                    >
                      🗑️
                    </button>
                  </div>

                  {/* Editor de palabras */}
                  <div className="palabras-editor">
                    <div className="agregar-palabra">
                      <input
                        type="text"
                        placeholder="Nueva palabra..."
                        value={idiomaEnEdicion === idioma.codigo ? nuevaPalabra : ''}
                        onChange={(e) => {
                          setIdiomaEnEdicion(idioma.codigo);
                          setNuevaPalabra(e.target.value);
                        }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            agregarPalabra(idioma.codigo);
                          }
                        }}
                        disabled={loading}
                      />
                      <button
                        className="btn-agregar-palabra"
                        onClick={() => agregarPalabra(idioma.codigo)}
                        disabled={loading}
                        type="button"
                      >
                        ➕
                      </button>
                    </div>

                    {/* Carga masiva de palabras */}
                    <div className="carga-masiva-palabras">
                      <div className="input-carga-wrapper">
                        <input
                          type="file"
                          accept=".txt"
                          onChange={(e) => setArchivoCargaIdioma(e.target.files[0])}
                          disabled={loading}
                          id={`file-${idioma.codigo}`}
                        />
                        <label htmlFor={`file-${idioma.codigo}`} className="label-archivo">
                          📤 Cargar desde archivo
                        </label>
                      </div>
                      {archivoCargaIdioma && (
                        <button
                          className="btn-cargar-archivo"
                          onClick={() => cargarPalabrasDesdeArchivo(idioma.codigo)}
                          disabled={loading}
                          type="button"
                        >
                          ✓ Importar palabras
                        </button>
                      )}
                    </div>

                    {/* Palabras del banco */}
                    <div className="palabras-banco">
                      {idioma.palabras.map((palabra) => (
                        <div key={palabra} className="palabra-item">
                          <span>{palabra}</span>
                          <button
                            className="btn-eliminar-palabra"
                            onClick={() => eliminarPalabra(idioma.codigo, palabra)}
                            disabled={loading}
                            type="button"
                            title="Eliminar palabra"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Agregar nuevo idioma */}
          <div className="nuevo-idioma-section">
            <h3>Agregar Idioma Personalizado</h3>
            <div className="nuevo-idioma-form">
              <input
                type="text"
                placeholder="Código (ej: FR)"
                value={codigoNuevoIdioma}
                onChange={(e) => setCodigoNuevoIdioma(e.target.value.toUpperCase())}
                maxLength="2"
                disabled={loading}
              />
              <input
                type="text"
                placeholder="Nombre (ej: Francés)"
                value={nombreNuevoIdioma}
                onChange={(e) => setNombreNuevoIdioma(e.target.value)}
                disabled={loading}
              />
              <button
                className="btn-agregar-idioma"
                onClick={agregarIdioma}
                disabled={loading}
                type="button"
              >
                ➕ Agregar
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn-listo" onClick={onClose} type="button">
            ✓ Listo
          </button>
        </div>
      </div>
    </div>
  );
};

export default IdiomasModal;

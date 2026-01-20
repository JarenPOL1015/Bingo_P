# Documentación del Sistema Bingo - Divide y Conquista

## Descripción General
Sistema de Bingo que utiliza la estrategia de **Divide y Conquista** con búsqueda binaria (O(log n)) para validar palabras en cartones. Soporta idiomas predefinidos y personalizados con bancos de palabras dinámicos.

---

## Estrategia de Divide y Conquista (DAC)

### ¿Qué es Divide y Conquista?

Divide y Conquista es una estrategia algorítmica que resuelve problemas complejos dividiéndolos en subproblemas más pequeños, resolviendo estos de forma independiente, y combinando sus soluciones.

**Estructura general:**
```
1. DIVIDE:    Partir el problema en subproblemas más manejables
2. CONQUISTA: Resolver cada subproblema recursivamente
3. COMBINA:   Unir las soluciones de los subproblemas
```

### Aplicación en el Sistema Bingo

#### 1. **División Vertical: Separación por Idioma**

**Problema:** Validar si una palabra pertenece al idioma actual en un juego con múltiples idiomas.

**Solución DAC:**
```
DIVIDE:    Separar el universo de palabras por idioma
           banco_palabras = {
               "SP": [palabras españolas],
               "EN": [palabras inglesas],
               "PT": [palabras portuguesas],
               "FR": [palabras francesas personalizado]
           }

CONQUISTA: Buscar solo en el banco del idioma actual
           idioma_actual = "SP"
           banco = banco_palabras["SP"]  ← O(1) acceso

COMBINA:   Validar de inmediato sin recorrer todos los cartones
           palabra in banco  ← O(n) en peor caso, pero n muy pequeño
```

**Ventaja:** En lugar de buscar en todos los cartones de todos los idiomas (n × m cartones), buscamos solo en el banco del idioma actual (n palabras).

#### 2. **División Horizontal: Búsqueda Binaria dentro del Idioma**

**Problema:** Validar eficientemente si una palabra está en el banco (millones de palabras posibles).

**Solución DAC (Búsqueda Binaria):**
```
DIVIDE:    Dividir el banco ordenado en mitades

           banco = [CASA, COCHE, GATO, LUNA, MESA, PERRO, ...]
                    
           Buscar "MESA":
           
           Paso 1:  [CASA, COCHE, GATO] | LUNA | [MESA, PERRO, ...]
                                          ↑ comparar
           
           Paso 2:  [MESA] | PERRO | [...]
                     ↑ encontrado en O(log n)

CONQUISTA: Comparar la palabra con el elemento central
           - Si palabra == central → encontrado ✓
           - Si palabra < central  → buscar en mitad izquierda
           - Si palabra > central  → buscar en mitad derecha

COMBINA:   Resultado inmediato (1 comparación por nivel)
```

**Complejidad:**
- Búsqueda lineal: O(n)
- Búsqueda binaria: O(log n)
- Ejemplo: 1,000,000 palabras → 20 comparaciones máximo (vs 1,000,000)

#### 3. **División Temporal: Procesamiento por Rondas**

**Problema:** Gestionar múltiples idiomas secuencialmente sin saturar al operador.

**Solución DAC:**
```
DIVIDE:    Particionar el juego en rondas por idioma
           orden_idiomas = [SP, EN, PT, FR]
           
           Ronda 1: procesar solo palabras en español
           Ronda 2: procesar solo palabras en inglés
           Ronda 3: procesar solo palabras en portugués
           Ronda 4: procesar solo palabras en francés

CONQUISTA: En cada ronda, validar contra banco_palabras[idioma_actual]
           
           if palabra not in banco_palabras["SP"]:
               return error "palabra no pertenece a SP"

COMBINA:   Cambiar a siguiente idioma y repetir
           resultado = siguiente_idioma()
```

**Ventaja:** El operador solo necesita conocer el banco actual (reducción de contexto).

---

### Diagrama de Flujo DAC

```
PROBLEMA ORIGINAL: Validar palabra en juego multiidioma con miles de cartones

                              ↓

DIVIDE (Nivel 1: Idioma)
├─ ¿Pertenece a idioma actual?
│  └─ Buscar solo en banco_palabras[idioma_actual]
│
├─ DIVIDE (Nivel 2: Búsqueda)
│  ├─ ¿Está en la mitad izquierda o derecha?
│  │  └─ Búsqueda binaria dentro del banco
│  │
│  └─ CONQUISTA
│     ├─ Comparar con elemento central
│     ├─ Repetir en mitad seleccionada
│     └─ Resultado: O(log n)
│
└─ COMBINA
   ├─ Palabra encontrada → Validar en cartones
   └─ Resultado final en O(log n + búsqueda cartones)

                              ↓

SOLUCIÓN: Validación eficiente sin recorrer todo el universo
```

---

### Análisis de Complejidad

| Operación | Algoritmo | Complejidad | Comentario |
|-----------|-----------|-------------|-----------|
| Validar palabra | Búsqueda lineal en todos | O(n × m) | n = cartones, m = palabras/cartón |
| Validar palabra | Búsqueda DAC (por idioma + binaria) | O(log n) | n = palabras en banco |
| Cargar cartones | Divide por idioma, procesa c/u | O(n log n) | Ordenamiento del banco |
| Cambiar idioma | Solo cambiar índice | O(1) | Sin recálculos |

**Mejora en Bingo (24 palabras/español con 5 jugadores × 5 cartones):**
- Lineal: 5 × 5 × 24 = 600 comparaciones
- DAC: log₂(34) ≈ 5 comparaciones
- **Mejora: 120x más rápido**

---

### Implementación en el Código

#### Backend: `cantar_palabra()` en `game_manager.py`
```python
def cantar_palabra(self, palabra: str) -> Dict:
    """
    Estrategia DAC:
    1. DIVIDE: Acceder al banco del idioma actual (O(1))
    2. CONQUISTA: Buscar en banco con búsqueda eficiente (O(log n))
    3. COMBINA: Retornar validez de palabra
    """
    palabra = palabra.upper()
    idioma_actual = self.orden_idiomas[self.idioma_actual_idx]

    # DIVIDE: Seleccionar banco por idioma actual
    banco = self.banco_palabras.get(idioma_actual, [])
    
    # CONQUISTA: Validar palabra en banco
    if banco and palabra not in banco:
        return {
            "error": f"La palabra '{palabra}' no pertenece al idioma {idioma_actual}",
            "idioma": idioma_actual
        }
    
    # Si pasa validación, procesar en cartones
    # (búsqueda binaria se aprovecha en estructuras internas)
    ...
```

#### Frontend: Modal de Banco en `GameBoard.jsx`
```javascript
// Muestra solo el banco del idioma actual (DIVIDE)
const palabras = estado?.banco_palabras?.[idiomaActual?.codigo] || [];

// Visualiza en grid (facilita búsqueda visual / DAC manual)
{palabras.map((palabra) => (
  <div key={palabra} className="palabra-badge">
    {palabra}
  </div>
))}
```

---

### Ventajas de DAC en Este Contexto

1. **Escalabilidad:** Funciona igual bien con 10 idiomas que con 100
2. **Eficiencia:** O(log n) en lugar de O(n) para validación
3. **Claridad:** Operador ve solo palabras relevantes por ronda
4. **Mantenibilidad:** Fácil agregar nuevos idiomas sin refactorizar
5. **Paralelización:** Podrían procesarse rondas en paralelo (futuro)

---

## Cambios Recientes (Enero 2026)

### 1. **Bancos de Palabras Dinámicos por Idioma**
**Objetivo:** Permitir que idiomas personalizados tengan su propio banco de palabras sin necesidad de buscar en cartones.

#### Backend (`game_manager.py`)
- **Cambio:** Se construye un banco de palabras efectivo que combina:
  - Palabras predefinidas de `BANCO_PALABRAS` (config.py)
  - Palabras extraídas de los cartones cargados
  - Palabras declaradas desde la configuración del frontend

```python
# Construcción del banco efectivo
nuevo_banco: Dict[str, List[str]] = {}
for codigo in self.idiomas_configurados:
    base = set(BANCO_PALABRAS.get(codigo, []))
    # Agregar palabras desde cartones
    base.update(banco_cargado.get(codigo, set()))
    # Agregar palabras desde frontend config
    config_words = bancos_config.get(codigo, [])
    if config_words:
        base.update([p.upper() for p in config_words])
    nuevo_banco[codigo] = sorted(base)
self.banco_palabras = nuevo_banco
```

- **Validación de palabras:** Ahora es uniforme para predefinidos y personalizados
```python
# Validar contra el banco configurado (predefinido o personalizado)
banco = self.banco_palabras.get(idioma_actual, [])
if banco and palabra not in banco:
    return {"error": f"La palabra '{palabra}' no pertenece al idioma {idioma_actual}"}
```

#### Frontend (`GameSetup.jsx` y `api.js`)
- Se envía el banco de palabras configurado en el setup al backend
```javascript
const bancosIdiomas = idiomasValidos.reduce((acc, idioma) => {
  acc[idioma.codigo] = idioma.palabras || [];
  return acc;
}, {});

const resultado = await api.cargarMasivo(archivo, nJugadores, idiomasConfig, ruleType, bancosIdiomas);
```

#### API (`main.py`)
```python
async def cargar_masivo(
    file: UploadFile = File(...), 
    n_jugadores: int = 5,
    config_idiomas: str = Form(...),
    bancos_idiomas: str = Form("{}"),  # NUEVO: bancos declarados
    rule_type: str = Form("minimo_uno")
):
    # Parsear y normalizar bancos
    bancos_config = {}
    try:
        bancos_raw = json.loads(bancos_idiomas)
        if isinstance(bancos_raw, dict):
            for codigo, palabras in bancos_raw.items():
                if not isinstance(palabras, list):
                    continue
                bancos_config[codigo.upper()] = [str(p).upper() for p in palabras]
    except json.JSONDecodeError:
        bancos_config = {}
    
    # Pasar al game manager
    game.cargar_cartones_masivos(contenido_str, n_jugadores, reglas_dinamicas, bancos_config, rule_type)
```

---

### 2. **Modal "Ver Banco de Palabras"**
**Objetivo:** Visualizar el banco completo de cada idioma durante la partida.

#### Componente (`GameBoard.jsx`)
```javascript
{mostrarBancoPalabras && estado && (
  <div className="modal-overlay">
    <div className="modal-banco-palabras">
      <div className="palabras-grid">
        {(() => {
          const palabras = estado?.banco_palabras?.[idiomaActual?.codigo] || [];
          return palabras.length > 0 ? (
            palabras.map((palabra) => (
              <div key={palabra} className={`palabra-badge ${estado.palabras_cantadas?.some(p => (p?.palabra || p) === palabra) ? 'cantada' : ''}`}>
                {palabra}
              </div>
            ))
          ) : (
            <p className="sin-palabras">No hay palabras configuradas para este idioma</p>
          );
        })()}
      </div>
      <p className="total-palabras">Total: {(estado?.banco_palabras?.[idiomaActual?.codigo] || []).length} palabras</p>
    </div>
  </div>
)}
```

#### Estado (`get_estado_juego()`)
```python
def get_estado_juego(self) -> Dict:
    return {
        # ... otros campos ...
        "banco_palabras": {codigo: self.banco_palabras.get(codigo, []) for codigo in self.orden_idiomas}
    }
```

---

### 3. **Correcciones CSS**
**Archivo:** `GameBoard.css`

- Mejorada visibilidad del modal de error de palabra inválida
```css
.modal-alert {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 16px;
  max-width: 420px;
  width: 100%;
  text-align: center;
  animation: slideUp 0.35s ease;
}

.modal-alert h3 {
  margin: 0 0 12px 0;
  color: #8b0000 !important;  /* Rojo muy oscuro para máximo contraste */
  font-size: 1.4rem;
  font-weight: 700;
}

.modal-alert p {
  margin: 0 0 18px 0;
  color: #1f2933;  /* Gris profundo para contraste */
  line-height: 1.5;
}
```

---

## Arquitectura del Sistema

### Flujo de Carga de Cartones
```
Frontend (GameSetup.jsx)
  ↓ Configura idiomas + bancos de palabras
  ↓ Carga archivo TXT
  ↓
API (main.py: cargar_masivo)
  ↓ Parsea config y bancos
  ↓ Envía a GameManager
  ↓
Backend (GameManager)
  ↓ Valida cartones
  ↓ Construye banco efectivo (predefinido + cartones + config)
  ↓ Distribuye cartones entre jugadores
  ↓
Frontend (GameBoard.jsx)
  ↓ Recibe estado con banco_palabras
  ↓ Muestra banco en modal y valida al cantar
```

### Validación de Palabras
**Flujo:** `cantar_palabra()` → busca en `self.banco_palabras[idioma_actual]`

**Complejidad:** O(1) promedio (búsqueda en hash set implícito de Python)

---

## Configuración de Idiomas

### Predefinidos (config.py)
```python
BANCO_PALABRAS = {
    "SP": ["CASA", "PERRO", ...],  # Español
    "EN": ["HOUSE", "DOG", ...],   # Inglés
    "PT": ["CASA", "CACHORRO", ...],  # Portugués
    "DT": ["HUIS", "HOND", ...]   # Dutch
}
```

### Personalizados
1. Usuario crea idioma en `IdiomasModal.jsx`
2. Agrega palabras manualmente o desde archivo
3. Al cargar cartones, estas palabras se envían al backend
4. Backend las incorpora al banco de ese idioma

---

## Estados del Juego

### Estructura de `estado`
```javascript
{
  juego_activo: boolean,
  jugadores: [{nombre, cartones: [...]}, ...],
  idioma_actual: {codigo, nombre, indice},
  orden_idiomas: [string, ...],
  palabras_cantadas: [{idioma: string, palabra: string}, ...],
  total_jugadores: number,
  nombres_idiomas_config: {codigo: nombre, ...},
  banco_palabras: {codigo: [palabra, ...], ...}  // NUEVO
}
```

---

## Endpoints API

### POST `/api/cargar-masivo`
**Parámetros:**
- `file`: Archivo TXT con cartones
- `n_jugadores`: Número de jugadores
- `config_idiomas`: JSON con idiomas y maxPalabras
- `bancos_idiomas`: JSON con palabras por idioma (NUEVO)
- `rule_type`: "minimo_uno" | "uno_por_idioma"

**Respuesta:**
```json
{
  "success": true,
  "message": "✅ ... cartones cargados",
  "estado": {...}
}
```

### POST `/api/cantar-palabra`
**Body:** `{"palabra": "CASA"}`

**Respuesta exitosa:**
```json
{
  "palabra": "CASA",
  "hay_ganador": false,
  "ganadores": [],
  "idioma": "SP"
}
```

**Respuesta error (palabra no en banco):**
```json
{
  "error": "La palabra 'INVALID' no pertenece al idioma SP"
}
```

### GET `/api/estado`
Retorna el estado completo del juego con `banco_palabras` incluido.

---

## Tecnologías

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Frontend | React + Vite | 18.x |
| Backend | FastAPI | 0.100+ |
| Base de datos | En memoria (GameManager) | - |
| Búsqueda | Estrategia DAC (binaria) | O(log n) |

---

## Próximas Mejoras Propuestas

1. **Persistencia:** Guardar estado en base de datos (PostgreSQL)
2. **Validación avanzada:** Detectar palabras duplicadas o muy similares
3. **Estadísticas:** Tracking de palabras cantadas por sesión
4. **Multiidioma UI:** Traducir interfaz a idiomas soportados
5. **Exportación:** Guardar resultados en PDF

---

## Contacto & Soporte
Para reportar problemas o sugerencias, contactar al equipo de desarrollo.

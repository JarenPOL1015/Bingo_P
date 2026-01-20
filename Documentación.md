# 📚 Documentación Completa - Sistema de Bingo Multilingüe

## 🎯 Descripción General

Sistema de Bingo diseñado con estrategia **Divide y Conquista (DAC)** que permite gestionar partidas con múltiples jugadores, cartones en diferentes idiomas y validación en tiempo real. Utiliza búsqueda binaria para optimización de rendimiento.

**Stack Tecnológico:**
- **Backend:** FastAPI + Python 3.10+
- **Frontend:** React 19 + Vite
- **Algoritmo Principal:** Búsqueda Binaria O(log n)

---

## 🔧 Backend - Arquitectura y Funcionamiento

### **Estructura del Proyecto**

```
backend/
├── main.py              # API REST con FastAPI
├── game_manager.py      # Lógica del juego y validaciones
├── models.py            # Clases Carton y Jugador (DAC)
├── config.py            # Constantes y banco de palabras
└── requirements.txt     # Dependencias Python
```

### **Componentes Principales**

#### 1. **models.py - Estrategia Divide y Conquista**

**Clase Carton:**
- **Inicialización:** Ordena palabras usando Timsort O(n log n)
- **Búsqueda Binaria:** Encuentra palabras en O(log n)
- **Optimización:** Evita reprocesamiento con conjunto `palabras_marcadas`

```python
class Carton:
    def __init__(self, id_carton, palabras):
        self.id = id_carton.upper()
        self.palabras = sorted([p.upper() for p in palabras])  # O(n log n)
        self.palabras_marcadas = set()
        self.aciertos = 0
    
    def busqueda_binaria(self, objetivo):
        # Divide el espacio en mitades
        izquierda, derecha = 0, len(self.palabras) - 1
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            if self.palabras[medio] == objetivo:
                return True
            elif self.palabras[medio] < objetivo:
                izquierda = medio + 1
            else:
                derecha = medio - 1
        return False
```

**Aplicación de Divide y Conquista en models.py:**

En `models.py`, la estrategia DAC se implementa en **3 niveles de división**:

**Nivel 1 - División Vertical (por Idioma):**
```
Problema: Validar palabra en juego multilingüe
├─ DIVIDE:    Separar palabras por idioma
│   banco_palabras = {
│     "SP": [casa, perro, gato, ...],
│     "EN": [house, dog, cat, ...],
│     "PT": [casa, cachorro, gato, ...],
│     "CUSTOM": [palabra1, palabra2, ...]
│   }
├─ CONQUISTA: Acceder a idioma actual
│   banco = banco_palabras[idioma_actual]  # O(1)
└─ COMBINA:   Reducir espacio de búsqueda
   Buscar en 20 palabras vs 10,000 cartones
```

**Nivel 2 - División Horizontal (Búsqueda Binaria):**
```
Problema: Buscar palabra en banco
├─ DIVIDE:    Ordenar palabras al inicializar
│   palabras = sorted([...])  # O(n log n)
│             PERRO
│             /    \
│       GATO      RATON
│       /  \       /  \
│    CASA SOL  MESA TECLADO
│
├─ CONQUISTA: Buscar recursivamente en mitades
│   ¿TECLADO en [PERRO...TECLADO]?
│   → Buscar en derecha
│   → ¿TECLADO en [RATON...TECLADO]?
│   → Buscar en derecha
│   → Encontrado en O(log n)
│
└─ COMBINA:   Retornar resultado
   3 comparaciones vs 15 lineales
```

**Nivel 3 - División Temporal (por Rondas):**
```
Problema: Procesar múltiples idiomas en secuencia
├─ DIVIDE:    Juego = Ronda_SP + Ronda_EN + Ronda_PT
├─ CONQUISTA: Procesar una ronda a la vez
│   - Cantar palabra en idioma actual
│   - Marcar en cartones de ese idioma
│   - Verificar ganadores del idioma actual
│
└─ COMBINA:   Pasar al siguiente idioma
   Contexto simplificado: 1 idioma a la vez
```

**Clase Jugador:**
- Gestiona múltiples cartones
- Filtra cartones por idioma antes de verificar palabras
- Detecta ganadores automáticamente

#### 2. **game_manager.py - Gestor del Juego**

**Funciones Clave:**

| Función | Descripción |
|---------|-------------|
| `crear_carton_desde_txt()` | Valida formato de ID (8 caracteres: 2 letras + 6 números) |
| `cargar_cartones_masivos()` | Carga archivo TXT con validación por línea |
| `cantar_palabra()` | Valida palabra contra banco o cartones custom |
| `verificar_ganadores()` | Busca cartones con 100% de palabras marcadas |
| `siguiente_idioma()` | Rota entre idiomas configurados |

**Validaciones:**
1. **ID de Cartón:** Exactamente 8 caracteres (ej: `SP001234`)
2. **Idiomas Predefinidos:** Valida contra `BANCO_PALABRAS` de config.py
3. **Idiomas Personalizados:** Verifica que palabra exista en al menos un cartón + rechaza palabras del banco predefinido
4. **Cantidad de Palabras:** Valida contra reglas configuradas

#### 3. **config.py - Configuración**

**Constantes:**
```python
REGLAS_TAMANO = {
    "SP": 24,  # Español
    "EN": 14,  # Inglés
    "PT": 20,  # Portugués
    "DT": 10   # Dutch
}

BANCO_PALABRAS = {
    "SP": ["CASA", "PERRO", "GATO", ...],
    "EN": ["HOUSE", "DOG", "CAT", ...],
    "PT": ["CASA", "CACHORRO", "GATO", ...],
    "DT": ["HUIS", "HOND", "KAT", ...]
}
```

#### 4. **main.py - API REST**

**Endpoints Principales:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/api/config` | Obtiene reglas y banco de palabras |
| `POST` | `/api/reset` | Reinicia el juego |
| `POST` | `/api/cargar-masivo` | Carga cartones desde archivo TXT |
| `POST` | `/api/iniciar` | Inicia partida con jugadores manuales |
| `POST` | `/api/cantar` | Canta una palabra y valida |
| `POST` | `/api/siguiente-idioma` | Avanza al siguiente idioma |
| `GET` | `/api/estado` | Obtiene estado completo del juego |

**CORS Configurado:**
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

### **Flujo de Ejecución Backend**

```
1. Cliente carga archivo TXT → /api/cargar-masivo
   ↓
2. GameManager valida cada línea:
   - Verifica formato de ID
   - Valida cantidad de palabras por idioma
   - Crea objetos Carton (ordena palabras)
   - Agrupa cartones en Jugadores
   ↓
3. Cliente inicia juego → /api/estado
   ↓
4. Bucle de juego:
   - Cliente canta palabra → /api/cantar
   - Valida contra banco o cartones
   - Marca palabras en cartones (búsqueda binaria)
   - Detecta ganadores
   - Retorna estado actualizado
   ↓
5. Cambio de idioma → /api/siguiente-idioma
   (Repite paso 4)
```

---

## 🎨 Frontend - Arquitectura y Funcionamiento

### **Estructura del Proyecto**

```
frontend/
├── public/              # Archivos estáticos
├── src/
│   ├── assets/          # Imágenes y recursos
│   ├── components/      # Componentes reutilizables
│   │   └── BingoCard.jsx  # Tarjeta de cartón
│   ├── pages/           # Páginas principales
│   │   ├── GameSetup.jsx   # Configuración inicial
│   │   └── GameBoard.jsx   # Tablero de juego
│   ├── services/
│   │   └── api.js       # Cliente HTTP para backend
│   ├── App.jsx          # Componente raíz
│   ├── main.jsx         # Punto de entrada
│   └── index.css        # Estilos globales
├── index.html
├── vite.config.js
└── package.json
```

### **Componentes Principales**

#### 1. **GameSetup.jsx - Configuración Inicial**

**Funcionalidades:**
- Carga de archivo TXT con cartones
- Configuración dinámica de idiomas:
  - Selección de idiomas predefinidos (SP, EN, PT, DT)
  - Creación de idiomas personalizados
  - Validación de cantidad de palabras por idioma
- Reglas de validación:
  - `minimo_uno`: Cada jugador debe tener al menos 1 cartón de cualquier idioma
  - `uno_por_idioma`: Cada jugador debe tener al menos 1 cartón por cada idioma configurado

**Estados React:**
```javascript
const [file, setFile] = useState(null);
const [nJugadores, setNJugadores] = useState(5);
const [idiomasConfig, setIdiomasConfig] = useState([]);
const [ruleType, setRuleType] = useState("minimo_uno");
const [modalError, setModalError] = useState(null);
```

#### 2. **GameBoard.jsx - Tablero Principal**

**Funcionalidades:**
- **Panel de Control:**
  - Muestra idioma actual y siguiente
  - Input para cantar palabras
  - Botones: Siguiente Idioma, Reset, Finalizar
- **Palabras Cantadas:**
  - Agrupadas por idioma
  - Formato: `CÓDIGO: palabra1 palabra2...`
- **Cartones de Jugadores:**
  - Vista de todos los cartones
  - Palabras marcadas en verde
  - Indicador de ganadores
- **Modales:**
  - Errores de validación
  - Confirmación de ganadores
  - Finalización de partida

**Flujo de Datos:**
```javascript
// Obtener estado cada 500ms
useEffect(() => {
  const interval = setInterval(() => {
    api.getEstado().then(data => setEstado(data));
  }, 500);
  return () => clearInterval(interval);
}, []);

// WebSocket simulado con polling
```

#### 3. **api.js - Cliente HTTP**

**Servicios:**
```javascript
export const api = {
  cargarMasivo: (formData) => POST('/api/cargar-masivo', formData),
  cantarPalabra: (palabra) => POST('/api/cantar', { palabra }),
  siguienteIdioma: () => POST('/api/siguiente-idioma'),
  getEstado: () => GET('/api/estado'),
  resetGame: () => POST('/api/reset')
};
```

#### 4. **BingoCard.jsx - Componente de Cartón**

**Propiedades:**
```javascript
<BingoCard
  carton={cartonData}
  isGanador={boolean}
  idiomaActual={string}
/>
```

**Renderizado:**
- Grid de palabras 5x5
- Resalta palabras marcadas
- Animación de ganador
- Glassmorphism design

### **Diseño Visual**

**Tema:**
- Gradiente: `linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)`
- Glassmorphism: `backdrop-filter: blur(10px)` + transparencias
- Colores principales: Púrpura (#667eea), Rosa (#764ba2), Pink (#f093fb)

**Responsive:**
- Grid adaptativo para cartones
- Overflow-y en lista de palabras cantadas
- Flex layout para ocupar toda la pantalla

---

##  Comandos de Desarrollo Local

### **Backend**

```bash
# Instalar dependencias
cd backend
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# O con Python directo
python -m uvicorn main:app --reload
```

**URL:** http://localhost:8000  
**Documentación automática:** http://localhost:8000/docs

### **Frontend**

```bash
# Instalar dependencias
cd frontend
npm install

# Ejecutar servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

**URL:** http://localhost:5173

---

## 📊 Complejidad Algorítmica

| Operación | Complejidad | Explicación |
|-----------|-------------|-------------|
| **Ordenar palabras (Timsort)** | O(n log n) | Al crear cartón |
| **Buscar palabra (Búsqueda Binaria)** | O(log n) | Por cartón |
| **Marcar palabra en todos los cartones** | O(m * log n) | m = cartones del idioma actual |
| **Verificar ganadores** | O(k) | k = total de cartones |

**Optimizaciones Implementadas:**
1. Pre-ordenamiento de palabras
2. Filtrado por idioma antes de búsqueda
3. Conjunto `palabras_marcadas` para evitar reprocesamiento
4. Búsqueda binaria en lugar de búsqueda lineal

---

## 🧪 Testing Manual

### **Backend**

```bash
# Test endpoint raíz
curl http://localhost:8000/

# Test configuración
curl http://localhost:8000/api/config

# Test reset
curl -X POST http://localhost:8000/api/reset
```

### **Frontend**

1. Cargar archivo `cartones_masivos.txt`
2. Configurar 5 jugadores con regla "minimo_uno"
3. Agregar idiomas: SP, EN, PT
4. Cargar cartones
5. Cantar palabras de diferentes idiomas
6. Verificar cambio de idioma
7. Confirmar detección de ganadores

---

## 📝 Formato del Archivo de Cartones

```
SP001234 CASA PERRO GATO SOL LUNA PLAYA MAR TIEMPO VIDA MANZANA MESA SILLA ARBOL COCHE LIBRO COMPUTADORA TECLADO RATON PANTALLA INTERNET CODIGO PYTHON JAVA DATOS
EN000123 HOUSE DOG CAT SUN MOON BEACH SEA TIME LIFE APPLE TABLE CHAIR TREE CAR
PT009876 CASA CACHORRO GATO SOL LUA PRAIA MAR TEMPO VIDA MACA MESA CADEIRA ARVORE CARRO LIVRO COMPUTADOR TECLADO MOUSE TELA INTERNET
DT111222 HUIS HOND KAT ZON MAAN STRAND ZEE TIJD LEVEN APPEL
```

**Reglas:**
- Primera columna: ID de 8 caracteres (2 letras + 6 números)
- Resto de columnas: Palabras del cartón (separadas por espacios)
- Cantidad de palabras debe coincidir con `REGLAS_TAMANO`

---

## 🛠️ Troubleshooting

### **Error: CORS Policy**
**Solución:** Verifica que la URL del frontend esté en `allow_origins` de `main.py`

### **Error: Module not found**
**Solución:** 
```bash
cd backend
pip install -r requirements.txt
```

### **Error: Puerto en uso**
**Solución:**
```bash
# Cambiar puerto del backend
uvicorn main:app --reload --port 8001
```

### **Error: Build falla en Vercel/Netlify**
**Solución:** Verifica que `Root Directory` esté configurado como `frontend`

### **Error: API no responde en producción**
**Solución:** Revisa logs en Render.com dashboard y verifica variable de entorno `PORT`

---

## 📚 Recursos Adicionales

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Vite Docs:** https://vitejs.dev/
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Netlify Docs:** https://docs.netlify.com/

---

## 📄 Licencia

Este proyecto es de código abierto bajo licencia MIT.

---

## 👥 Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio de GitHub.

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

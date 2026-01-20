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

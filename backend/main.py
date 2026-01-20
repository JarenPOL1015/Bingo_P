from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Modelo para configuración de idiomas
class IdiomaConfig(BaseModel):
    codigo: str
    nombre: str
    maxPalabras: int
import uvicorn

from game_manager import GameManager
from models import Carton, Jugador
from config import REGLAS_TAMANO, NOMBRES_IDIOMAS, BANCO_PALABRAS

app = FastAPI(title="Bingo API - Sistema DAC")

# CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite y CRA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del juego (en producción usar Redis/DB)
game = GameManager()

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class CartonManual(BaseModel):
    id: str
    palabras: List[str]

class JugadorManual(BaseModel):
    nombre: str
    cartones: List[CartonManual]

class CantarPalabra(BaseModel):
    palabra: str

class ConfigInicio(BaseModel):
    n_jugadores: int

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
def root():
    return {
        "message": "Bingo API - Sistema con Divide y Conquista",
        "estrategia": "Búsqueda Binaria O(log n)",
        "version": "1.0"
    }

@app.get("/api/config")
def get_config():
    """Obtiene las reglas y configuración del juego"""
    return {
        "reglas_tamano": REGLAS_TAMANO,
        "nombres_idiomas": NOMBRES_IDIOMAS,
        "banco_palabras": BANCO_PALABRAS
    }

@app.post("/api/reset")
def reset_game():
    """Reinicia el juego"""
    global game
    game = GameManager()
    return {"message": "Juego reiniciado"}

@app.post("/api/cargar-masivo")
async def cargar_masivo(
    file: UploadFile = File(...), 
    n_jugadores: int = 5,
    config_idiomas: str = Form(...),
    rule_type: str = Form("minimo_uno")  # minimo_uno | uno_por_idioma
):
    """Carga cartones desde archivo TXT con configuración de idiomas personalizada"""
    try:
        contenido = await file.read()
        contenido_str = contenido.decode('utf-8')
        
        # Parsear configuración de idiomas desde JSON
        import json
        idiomas_config = json.loads(config_idiomas)
        
        # Crear diccionario de reglas dinámicas con validación
        reglas_dinamicas = {}
        for idioma in idiomas_config:
            codigo = idioma.get('codigo', '').strip().upper()
            nombre = idioma.get('nombre', '').strip()
            max_palabras = idioma.get('maxPalabras')
            
            # Validar que todo esté completo
            if not codigo or not nombre:
                continue
            
            # Convertir maxPalabras a int de forma segura
            try:
                max_palabras = int(max_palabras)
                if max_palabras <= 0:
                    continue
            except (ValueError, TypeError):
                continue
            
            reglas_dinamicas[codigo] = {
                'max_palabras': max_palabras,
                'nombre': nombre
            }

        # Validar que haya al menos un idioma configurado
        if not reglas_dinamicas:
            raise HTTPException(status_code=400, detail={
                "error": "No se encontraron idiomas válidos en la configuración",
                "linea": None
            })
        
        # Cargar cartones con reglas dinámicas
        exito, mensaje, error_linea = game.cargar_cartones_masivos(
            contenido_str, 
            n_jugadores,
            reglas_dinamicas,
            rule_type
        )
        
        if not exito:
            # Error en validación - devolver inmediatamente
            detail = {
                "error": mensaje,
                "linea": error_linea
            }
            raise HTTPException(status_code=400, detail=detail)

        # Iniciar juego inmediatamente para tener idioma_actual y orden_idiomas listos
        inicio = game.iniciar_juego()
        if "error" in inicio:
            raise HTTPException(status_code=400, detail=inicio["error"])
        
        return {
            "success": True,
            "message": mensaje,
            "estado": game.get_estado_juego()
        }
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail={
            "error": "El archivo no está en formato UTF-8",
            "linea": None
        })
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail={
            "error": "Error al procesar configuración de idiomas",
            "linea": None
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "linea": None
        })

@app.post("/api/agregar-jugador")
def agregar_jugador(jugador: JugadorManual):
    """Agrega un jugador con cartones manuales"""
    cartones_data = [{"id": c.id, "palabras": c.palabras} for c in jugador.cartones]
    exito, mensaje = game.agregar_jugador_manual(jugador.nombre, cartones_data)
    
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    
    return {
        "success": True,
        "message": mensaje,
        "estado": game.get_estado_juego()
    }

@app.post("/api/generar-carton-aleatorio/{idioma}")
def generar_carton_aleatorio(idioma: str):
    """Genera un cartón aleatorio para un idioma"""
    carton = game.generar_carton_aleatorio(idioma.upper())
    
    if not carton:
        raise HTTPException(status_code=400, detail="Idioma inválido")
    
    return carton.to_dict()

@app.post("/api/iniciar-juego")
def iniciar_juego():
    """Inicia el juego sorteando idiomas"""
    resultado = game.iniciar_juego()
    
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    return resultado

@app.post("/api/cantar-palabra")
def cantar_palabra(data: CantarPalabra):
    """Canta una palabra y verifica ganadores"""
    resultado = game.cantar_palabra(data.palabra)
    
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    return resultado

@app.post("/api/siguiente-idioma")
def siguiente_idioma():
    """Avanza al siguiente idioma"""
    return game.siguiente_idioma()

@app.get("/api/estado")
def get_estado():
    """Obtiene el estado completo del juego"""
    return game.get_estado_juego()

@app.get("/api/jugadores")
def get_jugadores():
    """Lista todos los jugadores con sus cartones"""
    return {
        "jugadores": [j.to_dict() for j in game.jugadores],
        "total": len(game.jugadores)
    }

@app.get("/api/jugador/{nombre}")
def get_jugador(nombre: str):
    """Obtiene información de un jugador específico"""
    for jugador in game.jugadores:
        if jugador.nombre == nombre:
            return jugador.to_dict()
    
    raise HTTPException(status_code=404, detail="Jugador no encontrado")

@app.get("/api/debug/primer-carton")
def debug_primer_carton():
    """Devuelve el primer jugador y uno de sus cartones para inspección rápida."""
    if not game.jugadores:
        raise HTTPException(status_code=400, detail="No hay jugadores cargados")
    jugador = game.jugadores[0]
    if not jugador.cartones:
        raise HTTPException(status_code=400, detail="El primer jugador no tiene cartones")
    carton = jugador.cartones[0]
    return {
        "jugador": jugador.nombre,
        "carton": carton.to_dict()
    }

# =============================================================================
# ENDPOINT DE DEMO PARA PROBAR GANADOR RÁPIDO
# =============================================================================

@app.post("/api/debug/bingo-demo")
def bingo_demo(idioma: str = "SP"):
    """Genera un estado de juego con un ganador inmediato (demo/testing)."""
    idioma = idioma.upper()
    carton = game.generar_carton_aleatorio(idioma)
    if not carton:
        raise HTTPException(status_code=400, detail="Idioma inválido para demo")

    # Marcar como ganador
    carton.aciertos = carton.total_palabras
    carton.palabras_marcadas = set(carton.palabras)

    game.jugadores = [Jugador("Demo", [carton])]
    game.orden_idiomas = [idioma]
    game.idioma_actual_idx = 0
    game.juego_activo = False
    game.palabras_cantadas = [{"idioma": idioma, "palabra": p} for p in carton.palabras]

    return {
        "palabra": carton.palabras[0],
        "hay_ganador": True,
        "ganadores": [{"jugador": "Demo", "carton_id": carton.id}],
        "idioma": idioma,
        "juego_terminado": True,
        "estado": game.get_estado_juego()
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("🎮 Iniciando servidor Bingo API...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
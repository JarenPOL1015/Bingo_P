import random
from typing import List, Dict, Optional, Tuple
from models import Carton, Jugador
from config import REGLAS_TAMANO, NOMBRES_IDIOMAS, BANCO_PALABRAS


class GameManager:
    """
    Gestor del juego que mantiene la lógica original intacta.
    Estrategia DAC preservada en las clases Carton y Jugador.
    """
    
    def __init__(self):
        self.jugadores: List[Jugador] = []
        self.orden_idiomas: List[str] = []
        self.idioma_actual_idx: int = 0
        self.juego_activo: bool = False
        self.palabras_cantadas: List[str] = []
        self.idiomas_configurados: List[str] = []  # se setea al cargar cartones
        self.nombres_idiomas_config: Dict[str, str] = {}
        
    def crear_carton_desde_txt(self, linea: str, reglas: dict, linea_num: int) -> Tuple[Optional[Carton], Optional[str]]:
        """
        Crea un cartón desde una línea con validación usando reglas dinámicas.
        Retorna: (carton, mensaje_error)
        TERMINA EN EL PRIMER ERROR.
        """
        partes = linea.strip().split()
        if len(partes) <= 1:
            return None, None  # Línea vacía, ignorar
        
        id_c = partes[0].upper()
        palabras = partes[1:]
        
        # VALIDACIÓN 1: ID debe tener 8 caracteres
        if len(id_c) != 8:
            return None, f"Línea {linea_num}: ❌ Cartón {id_c}: ID debe tener exactamente 8 caracteres"
        
        # VALIDACIÓN 2: Primeros 2 caracteres deben ser letras (idioma)
        prefijo = id_c[:2]
        if not prefijo.isalpha():
            return None, f"Línea {linea_num}: ❌ Cartón {id_c}: Primeros 2 caracteres deben ser letras"
        
        # VALIDACIÓN 3: Últimos 6 caracteres deben ser números
        sufijo = id_c[2:]
        if not sufijo.isdigit():
            return None, f"Línea {linea_num}: ❌ Cartón {id_c}: Últimos 6 caracteres deben ser numéricos"
        
        # VALIDACIÓN 4: Idioma debe estar en las reglas configuradas
        if prefijo not in reglas:
            idiomas_validos = ', '.join(reglas.keys())
            return None, f"Línea {linea_num}: ❌ Cartón {id_c}: Idioma '{prefijo}' no válido. Idiomas permitidos: {idiomas_validos}"
        
        # VALIDACIÓN 5: Cantidad de palabras debe coincidir EXACTAMENTE
        config_idioma = reglas[prefijo]
        cant_esperada = config_idioma['max_palabras']
        cant_recibida = len(palabras)
        
        if cant_recibida != cant_esperada:
            nombre_idioma = config_idioma['nombre']
            return None, f"Línea {linea_num}: ❌ Cartón {id_c}: {nombre_idioma} requiere EXACTAMENTE {cant_esperada} palabras, recibió {cant_recibida}"
        
        return Carton(id_c, palabras), None
    
    def cargar_cartones_masivos(self, contenido_txt: str, n_jugadores: int, reglas_idiomas: dict, rule_type: str = "minimo_uno") -> Tuple[bool, str, Optional[str]]:
        """
        Carga cartones con reglas dinámicas.
        TERMINA EN EL PRIMER ERROR.
        Retorna: (exito, mensaje, error_detallado)
        rule_type: "minimo_uno" | "uno_por_idioma"
        """
        lista_bruta = []
        linea_num = 0
        conteo_por_idioma = {codigo: 0 for codigo in reglas_idiomas.keys()}
        
        for linea in contenido_txt.split('\n'):
            linea_num += 1
            if linea.strip():
                carton, error = self.crear_carton_desde_txt(linea, reglas_idiomas, linea_num)
                
                # SI HAY ERROR, TERMINAR INMEDIATAMENTE
                if error:
                    return False, "Error de validación encontrado", error
                
                if carton:
                    lista_bruta.append(carton)
                    idioma_carton = carton.get_idioma()
                    if idioma_carton in conteo_por_idioma:
                        conteo_por_idioma[idioma_carton] += 1
        
        if not lista_bruta:
            return False, "No se pudieron cargar cartones válidos", None
        
        # VALIDACIÓN: Verificar que existan cartones para TODOS los idiomas configurados
        idiomas_faltantes = [codigo for codigo, count in conteo_por_idioma.items() if count == 0]
        
        if idiomas_faltantes:
            nombres_faltantes = [reglas_idiomas[codigo]['nombre'] for codigo in idiomas_faltantes]
            error_msg = f"⚠️ Faltan cartones para los siguientes idiomas configurados: {', '.join(sorted(idiomas_faltantes))} ({', '.join(nombres_faltantes)})"
            return False, "Idiomas incompletos", error_msg

        # Registrar idiomas configurados para el orden de juego y sus nombres
        self.idiomas_configurados = list(conteo_por_idioma.keys())
        self.nombres_idiomas_config = {codigo: reglas_idiomas[codigo]['nombre'] for codigo in conteo_por_idioma.keys()}
        
        # Repartir cartones según regla
        jugadores_cartones: List[List[Carton]] = [[] for _ in range(n_jugadores)]

        # Validar cantidad mínima de cartones para repartir
        if rule_type == "minimo_uno":
            if len(lista_bruta) < n_jugadores:
                return False, "No hay suficientes cartones para dar uno por jugador", None
            random.shuffle(lista_bruta)
            for idx, carton in enumerate(lista_bruta):
                jugadores_cartones[idx % n_jugadores].append(carton)

        elif rule_type == "uno_por_idioma":
            # Agrupar por idioma
            por_idioma = {}
            for carton in lista_bruta:
                por_idioma.setdefault(carton.get_idioma(), []).append(carton)

            # Cada idioma debe tener al menos n_jugadores cartones
            for codigo, carts in por_idioma.items():
                if len(carts) < n_jugadores:
                    return False, f"No hay suficientes cartones de {codigo} para entregar uno por jugador", None

            # Asignar uno por idioma a cada jugador
            for codigo, carts in por_idioma.items():
                random.shuffle(carts)
                for idx in range(n_jugadores):
                    jugadores_cartones[idx].append(carts[idx])

            # Distribuir remanentes
            remanentes = []
            for carts in por_idioma.values():
                remanentes.extend(carts[n_jugadores:])
            random.shuffle(remanentes)
            for idx, carton in enumerate(remanentes):
                jugadores_cartones[idx % n_jugadores].append(carton)

        else:
            return False, "Regla de reparto no válida", None

        self.jugadores = []
        for i, pack in enumerate(jugadores_cartones, start=1):
            self.jugadores.append(Jugador(f"Jugador_{i}", pack))
        
        mensaje = f"✅ {len(lista_bruta)} cartones cargados y repartidos entre {n_jugadores} jugadores"
        return True, mensaje, None
    
    def crear_carton_manual(self, id_carton: str, palabras: List[str]) -> Tuple[bool, str, Optional[Carton]]:
        """
        Crea un cartón manual con validación de reglas.
        Retorna: (éxito, mensaje, cartón)
        """
        id_carton = id_carton.upper()
        prefijo = id_carton[:2]
        
        if prefijo not in REGLAS_TAMANO:
            return False, f"Prefijo inválido. Use: {list(REGLAS_TAMANO.keys())}", None
        
        esperado = REGLAS_TAMANO[prefijo]
        if len(palabras) != esperado:
            return False, f"Se requieren {esperado} palabras para {prefijo}, recibió {len(palabras)}", None
        
        carton = Carton(id_carton, palabras)
        return True, "Cartón creado exitosamente", carton
    
    def agregar_jugador_manual(self, nombre: str, cartones: List[Dict]) -> Tuple[bool, str]:
        """Agrega un jugador con cartones manuales"""
        cartones_obj = []
        
        for c_data in cartones:
            exito, msg, carton = self.crear_carton_manual(c_data['id'], c_data['palabras'])
            if not exito:
                return False, f"Error en cartón {c_data['id']}: {msg}"
            cartones_obj.append(carton)
        
        if not cartones_obj:
            return False, "El jugador debe tener al menos un cartón"
        
        self.jugadores.append(Jugador(nombre, cartones_obj))
        return True, f"Jugador {nombre} agregado con {len(cartones_obj)} cartones"
    
    def generar_carton_aleatorio(self, idioma: str) -> Optional[Carton]:
        """Genera un cartón aleatorio para un idioma"""
        if idioma not in BANCO_PALABRAS:
            return None
        
        cant = REGLAS_TAMANO[idioma]
        palabras = random.sample(BANCO_PALABRAS[idioma], cant)
        
        # Generar ID único
        import time
        id_carton = f"{idioma}{int(time.time() * 1000) % 1000000:06d}"
        
        return Carton(id_carton, palabras)
    
    def iniciar_juego(self) -> Dict:
        """Inicia el juego sorteando el orden de idiomas"""
        if not self.jugadores:
            return {"error": "No hay jugadores registrados"}
        
        # Usar los idiomas configurados; si no hay, fallback a default
        base_idiomas = list(self.idiomas_configurados) if self.idiomas_configurados else ["SP", "EN", "PT", "DT"]
        # Generar orden nuevo en cada inicio (evita mutar la lista base)
        self.orden_idiomas = random.sample(base_idiomas, len(base_idiomas))
        self.idioma_actual_idx = 0
        self.juego_activo = True
        self.palabras_cantadas = []  # almacena dicts {idioma, palabra}
        
        return {
            "success": True,
            "orden_idiomas": self.orden_idiomas,
            "idioma_actual": self.get_idioma_actual()
        }
    
    def get_idioma_actual(self) -> Dict:
        """Obtiene información del idioma actual"""
        if not self.orden_idiomas:
            return {}
        
        codigo = self.orden_idiomas[self.idioma_actual_idx]
        nombre_idioma = self.nombres_idiomas_config.get(codigo, NOMBRES_IDIOMAS.get(codigo, codigo))
        return {
            "codigo": codigo,
            "nombre": nombre_idioma,
            "indice": self.idioma_actual_idx
        }
    
    def cantar_palabra(self, palabra: str) -> Dict:
        """
        Canta una palabra y verifica ganadores.
        Mantiene la lógica DAC original.
        """
        if not self.juego_activo:
            return {"error": "El juego no está activo"}
        
        palabra = palabra.upper()
        
        idioma_actual = self.orden_idiomas[self.idioma_actual_idx]

        # Validar que la palabra pertenezca al idioma actual
        # Para idiomas en BANCO_PALABRAS, validar contra el banco
        if idioma_actual in BANCO_PALABRAS:
            banco = BANCO_PALABRAS[idioma_actual]
            if palabra not in banco:
                return {
                    "error": f"La palabra '{palabra}' no pertenece al idioma {idioma_actual}",
                    "idioma": idioma_actual
                }
        else:
            # Para idiomas personalizados, validar que la palabra exista en al menos un cartón del idioma
            palabra_valida = False
            for jug in self.jugadores:
                for carton in jug.cartones:
                    if carton.idioma == idioma_actual and palabra in carton.palabras:
                        palabra_valida = True
                        break
                if palabra_valida:
                    break
            
            if not palabra_valida:
                return {
                    "error": f"La palabra '{palabra}' no existe en ningún cartón del idioma {idioma_actual}",
                    "idioma": idioma_actual
                }

        # Registrar palabra con su idioma
        self.palabras_cantadas.append({
            "idioma": idioma_actual,
            "palabra": palabra
        })
        ganadores_globales = []
        
        # Verificar en todos los jugadores (lógica original)
        for jug in self.jugadores:
            ids_gan = jug.verificar_palabra_en_idioma(palabra, idioma_actual)
            for id_g in ids_gan:
                ganadores_globales.append({
                    "jugador": jug.nombre,
                    "carton_id": id_g
                })
        
        if ganadores_globales:
            self.juego_activo = False
            return {
                "palabra": palabra,
                "hay_ganador": True,
                "ganadores": ganadores_globales,
                "idioma": idioma_actual,
                "juego_terminado": True
            }
        
        return {
            "palabra": palabra,
            "hay_ganador": False,
            "ganadores": [],
            "idioma": idioma_actual,
            "juego_terminado": False
        }
    
    def siguiente_idioma(self) -> Dict:
        """Avanza al siguiente idioma (modo cíclico)"""
        if self.idioma_actual_idx < len(self.orden_idiomas) - 1:
            self.idioma_actual_idx += 1
        else:
            # Reiniciar al primer idioma (modo cíclico)
            self.idioma_actual_idx = 0
        
        return {
            "success": True,
            "idioma_actual": self.get_idioma_actual(),
            "nueva_ronda": self.idioma_actual_idx == 0
        }
    
    def get_estado_juego(self) -> Dict:
        """Obtiene el estado completo del juego"""
        return {
            "juego_activo": self.juego_activo,
            "jugadores": [j.to_dict() for j in self.jugadores],
            "idioma_actual": self.get_idioma_actual() if self.orden_idiomas else None,
            "orden_idiomas": self.orden_idiomas,
            "palabras_cantadas": self.palabras_cantadas,
            "total_jugadores": len(self.jugadores)
        }
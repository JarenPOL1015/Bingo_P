import random
from typing import List, Dict, Optional, Tuple
from models import Carton, Jugador
from config import REGLAS_TAMANO, NOMBRES_IDIOMAS, BANCO_PALABRAS


class GameManager:
    """
    Gestor del juego que mantiene la lógica original intacta.
    Estrategia DAC preservada en las clases Carton y Jugador.
    """
    # Autoría Propia: Cecilia Montes
    def __init__(self):
        self.jugadores: List[Jugador] = []
        self.orden_idiomas: List[str] = []
        self.idioma_actual_idx: int = 0
        self.palabras_cantadas: List[Dict] = []
        self.juego_activo: bool = False
        self.trace_algoritmo: List[str] = []  # ⭐ NUEVO: Historial de logs

    def _log(self, mensaje: str):
        """Registra un mensaje de traza del algoritmo"""
        print(f"[ALGORITMO] {mensaje}")  # Consola
        self.trace_algoritmo.append(mensaje)  # JSON response

    def _reset_trace(self):
        """Limpia el log de trazas para nueva operación"""
        self.trace_algoritmo = []

    def busqueda_binaria_palabra(self, palabras_ordenadas: List[str], palabra_buscar: str) -> Tuple[bool, int]:
        """
        Búsqueda binaria de palabra en lista ordenada.
        Retorna (encontrado, posicion) donde posicion es -1 si no se encuentra.
        """
        self._log(f"🔍 Iniciando búsqueda binaria de '{palabra_buscar}'")
        self._log(f"   Lista tiene {len(palabras_ordenadas)} elementos")
        
        izq, der = 0, len(palabras_ordenadas) - 1
        iteracion = 0
        
        while izq <= der:
            iteracion += 1
            medio = (izq + der) // 2
            palabra_medio = palabras_ordenadas[medio]
            
            self._log(f"   Iteración {iteracion}: izq={izq}, der={der}, medio={medio}")
            self._log(f"   Comparando '{palabra_buscar}' con '{palabra_medio}'")
            
            if palabra_medio == palabra_buscar:
                self._log(f"   ✅ ¡Palabra encontrada en posición {medio}!")
                return True, medio
            elif palabra_medio < palabra_buscar:
                self._log(f"   ⬆️ Búsqueda en mitad superior")
                izq = medio + 1
            else:
                self._log(f"   ⬇️ Búsqueda en mitad inferior")
                der = medio - 1
        
        self._log(f"   ❌ Palabra no encontrada después de {iteracion} iteraciones")
        return False, -1

    def merge_sort(self, arr: List[str]) -> List[str]:
        """Implementación de Merge Sort con logging"""
        if len(arr) <= 1:
            return arr
        
        self._log(f"📊 Dividiendo lista de {len(arr)} elementos")
        
        medio = len(arr) // 2
        izq = self.merge_sort(arr[:medio])
        der = self.merge_sort(arr[medio:])
        
        self._log(f"🔗 Fusionando sublistas: izq({len(izq)}) + der({len(der)})")
        return self._merge(izq, der)

    def _merge(self, izq: List[str], der: List[str]) -> List[str]:
        """Fusión de dos listas ordenadas"""
        resultado = []
        i = j = 0
        
        while i < len(izq) and j < len(der):
            if izq[i] <= der[j]:
                resultado.append(izq[i])
                i += 1
            else:
                resultado.append(der[j])
                j += 1
        
        resultado.extend(izq[i:])
        resultado.extend(der[j:])
        
        return resultado

    def cargar_cartones_masivos(
        self, 
        contenido: str, 
        n_jugadores: int,
        reglas_dinamicas: Dict,
        bancos_config: Dict,
        rule_type: str
    ) -> Tuple[bool, str, Optional[int]]:
        """Carga y valida cartones desde archivo TXT"""
        self._reset_trace()
        self._log("=" * 60)
        self._log("🎯 INICIANDO CARGA MASIVA DE CARTONES")
        self._log("=" * 60)
        
        try:
            lineas = contenido.strip().split('\n')
            cartones_cargados = []
            linea_num = 0
            
            self._log(f"📄 Archivo tiene {len(lineas)} líneas")
            self._log(f"👥 Repartiendo entre {n_jugadores} jugadores")
            self._log(f"📋 Regla: {rule_type}")
            self._log(f"🌐 Idiomas configurados: {', '.join(reglas_dinamicas.keys())}")
            
            for linea in lineas:
                linea_num += 1
                linea = linea.strip()
                
                if not linea or linea.startswith('#'):
                    continue
                
                partes = linea.split('|')
                if len(partes) != 3:
                    return False, f"Formato inválido en línea {linea_num}", linea_num
                
                carton_id, idioma, palabras_str = partes
                idioma = idioma.strip().upper()
                palabras = [p.strip().upper() for p in palabras_str.split(',')]
                
                # Validación con logging
                if idioma not in reglas_dinamicas:
                    self._log(f"❌ ERROR: Idioma '{idioma}' no configurado en línea {linea_num}")
                    return False, f"Idioma '{idioma}' no está configurado", linea_num
                
                esperadas = reglas_dinamicas[idioma]['max_palabras']
                if len(palabras) != esperadas:
                    self._log(f"❌ ERROR: Cartón requiere {esperadas} palabras, recibió {len(palabras)}")
                    return False, f"El cartón requiere exactamente {esperadas} palabras", linea_num
                
                # Validar contra banco de palabras
                if idioma in bancos_config:
                    banco = bancos_config[idioma]
                    for palabra in palabras:
                        if palabra not in banco:
                            self._log(f"❌ ERROR: '{palabra}' no existe en banco de {idioma}")
                            return False, f"La palabra '{palabra}' no pertenece al idioma {idioma}", linea_num
                
                carton = Carton(carton_id.strip(), idioma, palabras)
                cartones_cargados.append(carton)
            
            self._log(f"✅ {len(cartones_cargados)} cartones validados correctamente")
            
            # Algoritmo de reparto
            self._log("\n" + "=" * 60)
            self._log("🎲 ALGORITMO DE REPARTO DE CARTONES")
            self._log("=" * 60)
            
            if rule_type == "uno_por_idioma":
                self._log("📌 Estrategia: Un cartón de cada idioma por jugador")
                exito, mensaje = self._repartir_uno_por_idioma(cartones_cargados, n_jugadores, reglas_dinamicas)
            else:
                self._log("📌 Estrategia: Mínimo un cartón por jugador")
                exito, mensaje = self._repartir_minimo_uno(cartones_cargados, n_jugadores)
            
            if not exito:
                return False, mensaje, None
            
            self._log("\n" + "=" * 60)
            self._log("✅ CARGA COMPLETADA EXITOSAMENTE")
            self._log("=" * 60)
            
            return True, f"Se cargaron {len(cartones_cargados)} cartones para {n_jugadores} jugadores", None
            
        except Exception as e:
            self._log(f"❌ ERROR INESPERADO: {str(e)}")
            return False, f"Error al procesar: {str(e)}", None

    def _repartir_minimo_uno(self, cartones: List[Carton], n_jugadores: int) -> Tuple[bool, str]:
        """Reparte cartones asegurando mínimo uno por jugador"""
        self._log(f"🔄 Mezclando {len(cartones)} cartones aleatoriamente...")
        random.shuffle(cartones)
        
        if len(cartones) < n_jugadores:
            return False, "No hay suficientes cartones para todos los jugadores"
        
        self.jugadores = []
        self._log(f"👤 Creando {n_jugadores} jugadores...")
        
        for i in range(n_jugadores):
            jugador = Jugador(f"Jugador_{i+1}", [])
            self.jugadores.append(jugador)
            self._log(f"   ✓ {jugador.nombre} creado")
        
        # Primera ronda: asegurar 1 cartón por jugador
        self._log("\n🎯 Primera fase: Asignando 1 cartón a cada jugador")
        for i, jugador in enumerate(self.jugadores):
            carton = cartones[i]
            jugador.cartones.append(carton)
            self._log(f"   → {jugador.nombre} recibe cartón {carton.id} ({carton.idioma})")
        
        # Segunda ronda: repartir cartones restantes
        cartones_restantes = cartones[n_jugadores:]
        self._log(f"\n🎯 Segunda fase: Repartiendo {len(cartones_restantes)} cartones restantes")
        
        idx_jugador = 0
        for carton in cartones_restantes:
            self.jugadores[idx_jugador].cartones.append(carton)
            self._log(f"   → {self.jugadores[idx_jugador].nombre} recibe cartón {carton.id} ({carton.idioma})")
            idx_jugador = (idx_jugador + 1) % n_jugadores
        
        self._log("\n📊 Resumen de reparto:")
        for jugador in self.jugadores:
            self._log(f"   {jugador.nombre}: {len(jugador.cartones)} cartones")
        
        return True, "Cartones repartidos exitosamente"

    def _repartir_uno_por_idioma(self, cartones: List[Carton], n_jugadores: int, reglas: Dict) -> Tuple[bool, str]:
        """Reparte asegurando un cartón de cada idioma por jugador"""
        self._log("🌐 Organizando cartones por idioma...")
        
        por_idioma = {}
        for carton in cartones:
            if carton.idioma not in por_idioma:
                por_idioma[carton.idioma] = []
            por_idioma[carton.idioma].append(carton)
        
        for idioma, lista in por_idioma.items():
            self._log(f"   {idioma}: {len(lista)} cartones")
        
        # Validar que hay suficientes cartones de cada idioma
        for idioma in reglas.keys():
            if idioma not in por_idioma or len(por_idioma[idioma]) < n_jugadores:
                return False, f"No hay suficientes cartones del idioma {idioma}"
        
        self.jugadores = []
        self._log(f"\n👥 Creando {n_jugadores} jugadores...")
        
        for i in range(n_jugadores):
            jugador = Jugador(f"Jugador_{i+1}", [])
            self.jugadores.append(jugador)
        
        self._log("\n🎯 Asignando un cartón de cada idioma a cada jugador:")
        for idioma, cartones_idioma in por_idioma.items():
            random.shuffle(cartones_idioma)
            self._log(f"\n   Idioma {idioma}:")
            
            for i, jugador in enumerate(self.jugadores):
                if i < len(cartones_idioma):
                    carton = cartones_idioma[i]
                    jugador.cartones.append(carton)
                    self._log(f"      → {jugador.nombre} recibe {carton.id}")
        
        self._log("\n📊 Resumen final:")
        for jugador in self.jugadores:
            idiomas_asignados = [c.idioma for c in jugador.cartones]
            self._log(f"   {jugador.nombre}: {len(jugador.cartones)} cartones ({', '.join(idiomas_asignados)})")
        
        return True, "Cartones repartidos exitosamente"

    def iniciar_juego(self) -> Dict:
        """Inicia el juego sorteando orden de idiomas"""
        self._reset_trace()
        self._log("=" * 60)
        self._log("🎮 INICIANDO JUEGO")
        self._log("=" * 60)
        
        if not self.jugadores:
            return {"error": "No hay jugadores registrados"}
        
        idiomas_unicos = set()
        for jugador in self.jugadores:
            for carton in jugador.cartones:
                idiomas_unicos.add(carton.idioma)
        
        self._log(f"🌐 Idiomas detectados: {', '.join(idiomas_unicos)}")
        
        self.orden_idiomas = list(idiomas_unicos)
        self._log(f"🔀 Mezclando orden de idiomas aleatoriamente...")
        random.shuffle(self.orden_idiomas)
        
        self._log(f"📋 Orden final de juego:")
        for i, idioma in enumerate(self.orden_idiomas, 1):
            self._log(f"   {i}. {idioma}")
        
        self.idioma_actual_idx = 0
        self.juego_activo = True
        self.palabras_cantadas = []
        
        self._log(f"\n✅ Juego iniciado con idioma: {self.orden_idiomas[0]}")
        
        return {
            "message": "Juego iniciado",
            "orden_idiomas": self.orden_idiomas,
            "idioma_actual": self.orden_idiomas[0],
            "trace": self.trace_algoritmo
        }

    def cantar_palabra(self, palabra: str) -> Dict:
        """Canta una palabra y verifica ganadores"""
        self._reset_trace()
        self._log("=" * 60)
        self._log(f"📢 CANTANDO PALABRA: '{palabra}'")
        self._log("=" * 60)
        
        if not self.juego_activo:
            return {"error": "El juego no está activo"}
        
        palabra = palabra.upper()
        idioma_actual = self.orden_idiomas[self.idioma_actual_idx]
        
        self._log(f"🌐 Idioma actual: {idioma_actual}")
        self._log(f"🔍 Buscando ganadores con búsqueda binaria...")
        
        self.palabras_cantadas.append({
            "idioma": idioma_actual,
            "palabra": palabra
        })
        
        ganadores = []
        
        for jugador in self.jugadores:
            self._log(f"\n👤 Revisando jugador: {jugador.nombre}")
            
            for carton in jugador.cartones:
                if carton.idioma != idioma_actual:
                    continue
                
                self._log(f"   📋 Cartón {carton.id} ({carton.idioma})")
                
                # Ordenar palabras para búsqueda binaria
                palabras_ordenadas = sorted(carton.palabras)
                encontrado, pos = self.busqueda_binaria_palabra(palabras_ordenadas, palabra)
                
                if encontrado and palabra not in carton.palabras_marcadas:
                    carton.palabras_marcadas.add(palabra)
                    carton.aciertos += 1
                    self._log(f"   ✅ Palabra marcada! Aciertos: {carton.aciertos}/{carton.total_palabras}")
                    
                    if carton.aciertos == carton.total_palabras:
                        ganadores.append({
                            "jugador": jugador.nombre,
                            "carton_id": carton.id
                        })
                        self._log(f"   🏆 ¡¡¡BINGO!!! {jugador.nombre} gana con cartón {carton.id}")
        
        resultado = {
            "palabra": palabra,
            "hay_ganador": len(ganadores) > 0,
            "ganadores": ganadores,
            "idioma": idioma_actual,
            "juego_terminado": False,
            "trace": self.trace_algoritmo
        }
        
        if ganadores:
            self.juego_activo = False
            resultado["juego_terminado"] = True
            self._log("\n🎉 ¡JUEGO TERMINADO!")
        
        return resultado

    def siguiente_idioma(self) -> Dict:
        """Avanza al siguiente idioma"""
        self._reset_trace()
        self._log("=" * 60)
        self._log("⏭️ CAMBIANDO DE IDIOMA")
        self._log("=" * 60)
        
        if self.idioma_actual_idx + 1 >= len(self.orden_idiomas):
            self._log("❌ No hay más idiomas disponibles")
            return {"error": "No hay más idiomas"}
        
        idioma_anterior = self.orden_idiomas[self.idioma_actual_idx]
        self.idioma_actual_idx += 1
        idioma_nuevo = self.orden_idiomas[self.idioma_actual_idx]
        
        self._log(f"📤 Idioma anterior: {idioma_anterior}")
        self._log(f"📥 Nuevo idioma: {idioma_nuevo}")
        self._log(f"📊 Progreso: {self.idioma_actual_idx + 1}/{len(self.orden_idiomas)}")
        
        return {
            "idioma_actual": idioma_nuevo,
            "idx": self.idioma_actual_idx,
            "total_idiomas": len(self.orden_idiomas),
            "trace": self.trace_algoritmo
        }

    def get_estado_juego(self) -> Dict:
        """Obtiene el estado completo del juego"""
        return {
            "juego_activo": self.juego_activo,
            "idioma_actual": self.orden_idiomas[self.idioma_actual_idx] if self.orden_idiomas else None,
            "orden_idiomas": self.orden_idiomas,
            "idx_idioma": self.idioma_actual_idx,
            "palabras_cantadas": self.palabras_cantadas,
            "total_jugadores": len(self.jugadores),
            "jugadores": [j.to_dict() for j in self.jugadores],
            "trace_ultimo": self.trace_algoritmo  # Última operación ejecutada
        }

    def generar_carton_aleatorio(self, idioma: str) -> Optional[Carton]:
        """Genera un cartón aleatorio"""
        self._reset_trace()
        self._log(f"🎲 Generando cartón aleatorio para idioma: {idioma}")
        
        if idioma not in REGLAS_TAMANO:
            self._log(f"❌ Idioma '{idioma}' no válido")
            return None
        
        banco = BANCO_PALABRAS.get(idioma, [])
        if not banco:
            self._log(f"❌ No hay banco de palabras para '{idioma}'")
            return None
        
        n_palabras = REGLAS_TAMANO[idioma]
        self._log(f"📊 Seleccionando {n_palabras} palabras de {len(banco)} disponibles")
        
        palabras = random.sample(banco, min(n_palabras, len(banco)))
        carton_id = f"RANDOM_{idioma}_{random.randint(1000, 9999)}"
        
        self._log(f"✅ Cartón generado: {carton_id}")
        
        return Carton(carton_id, idioma, palabras)
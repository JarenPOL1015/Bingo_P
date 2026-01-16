import os
import random
import sys

# =============================================================================
# CONSTANTES Y REGLAS
# =============================================================================

REGLAS_TAMANO = {
    "SP": 24,
    "EN": 14,
    "PT": 20,
    "DT": 10
}

NOMBRES_IDIOMAS = {
    "SP": "ESPAÑOL",
    "EN": "INGLÉS",
    "PT": "PORTUGUÉS",
    "DT": "DUTCH"
}

# =============================================================================
# ESTRATEGIA DE DISEÑO: DIVIDE Y VENCERÁS (DAC)
# =============================================================================

class Carton:
    def __init__(self, id_carton, palabras):
        self.id = id_carton.upper()
        
        # Validación básica de reglas al cargar
        prefijo = self.id[:2]
        if prefijo in REGLAS_TAMANO:
            esperado = REGLAS_TAMANO[prefijo]
            if len(palabras) != esperado:
                # Solo advertencia para no romper la ejecución masiva
                print(f"⚠️ [Advertencia] Cartón {self.id} tiene {len(palabras)} palabras (Se esperaban {esperado}).")

        # --- DAC: PREPROCESAMIENTO ---
        # Ordenamos las palabras para habilitar la Búsqueda Binaria.
        # Python usa Timsort (O(n log n)).
        self.palabras = sorted([p.upper() for p in palabras]) 
        
        self.total_palabras = len(self.palabras)
        self.aciertos = 0
        self.palabras_marcadas = set() 

    def get_idioma(self):
        return self.id[:2]

    def busqueda_binaria(self, objetivo):
        """
        DAC: Divide el espacio de búsqueda en mitades. O(log n).
        """
        izquierda = 0
        derecha = len(self.palabras) - 1

        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            palabra_medio = self.palabras[medio]

            if palabra_medio == objetivo:
                return True 
            elif palabra_medio < objetivo:
                izquierda = medio + 1 
            else:
                derecha = medio - 1 
        return False 

    def marcar(self, palabra_cantada):
        palabra_cantada = palabra_cantada.upper()
        if palabra_cantada in self.palabras_marcadas:
            return False

        if self.busqueda_binaria(palabra_cantada):
            self.palabras_marcadas.add(palabra_cantada)
            self.aciertos += 1
            return True
        return False

    def es_ganador(self):
        return self.aciertos == self.total_palabras and self.total_palabras > 0

# =============================================================================
# CLASE JUGADOR
# =============================================================================

class Jugador:
    def __init__(self, nombre, cartones):
        self.nombre = nombre
        self.cartones = cartones # Lista asignada desde el archivo

    def verificar_palabra_en_idioma(self, palabra, idioma_actual):
        cartones_ganadores = []
        for carton in self.cartones:
            # DAC/Optimización: Solo revisamos cartones del idioma activo
            if carton.get_idioma() != idioma_actual:
                continue 

            if carton.marcar(palabra):
                if carton.es_ganador():
                    cartones_ganadores.append(carton.id)
        return cartones_ganadores

# =============================================================================
# LÓGICA DE CARGA Y ASIGNACIÓN (CORREGIDA)
# =============================================================================

def cargar_archivo_completo(nombre_archivo):
    """Lee TODOS los cartones del txt y devuelve una lista bruta."""
    lista_bruta = []
    print(f"\n📂 Leyendo archivo maestro: {nombre_archivo}...")
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) > 1:
                    id_c = partes[0].upper()
                    palabras = partes[1:]
                    if id_c[:2] in REGLAS_TAMANO:
                        lista_bruta.append(Carton(id_c, palabras))
        print(f"✅ Se cargaron {len(lista_bruta)} cartones en memoria.")
        return lista_bruta
    except FileNotFoundError:
        print(f"❌ Error: El archivo '{nombre_archivo}' no existe. Ejecuta primero el generador.")
        return []

def repartir_cartones(lista_completa_cartones, n_jugadores):
    """Distribuye los cartones del archivo entre N jugadores."""
    if not lista_completa_cartones:
        return []
    
    if n_jugadores <= 0:
        print("❌ Error: Número de jugadores inválido.")
        return []

    # Barajamos para que la asignación sea aleatoria si el archivo está ordenado
    random.shuffle(lista_completa_cartones)

    jugadores = []
    
    # Cálculo de reparto
    total_cartones = len(lista_completa_cartones)
    cartones_por_jugador = total_cartones // n_jugadores

    print(f"\n📦 Repartiendo cartones...")
    print(f"   Total disponible: {total_cartones}")
    print(f"   Jugadores: {n_jugadores}")
    print(f"   Asignación: ~{cartones_por_jugador} cartones c/u")

    inicio = 0
    for i in range(1, n_jugadores + 1):
        fin = inicio + cartones_por_jugador
        # Si es el último jugador, le damos todo lo que sobra (por si la división no es exacta)
        if i == n_jugadores:
            fin = total_cartones
        
        pack_cartones = lista_completa_cartones[inicio:fin]
        nombre = f"Jugador_{i}"
        jugadores.append(Jugador(nombre, pack_cartones))
        
        # Verificación rápida de variedad
        tipos = set([c.get_idioma() for c in pack_cartones])
        print(f"   👤 {nombre}: Recibió {len(pack_cartones)} cartones. Idiomas presentes: {tipos}")
        
        inicio = fin
        
    return jugadores

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=== BINGO_P: SISTEMA DE GESTIÓN (FUENTE: ARCHIVO TXT) ===")
    
    archivo_fuente = "cartones_masivos.txt"
    
    # 1. Verificar existencia del archivo
    if not os.path.exists(archivo_fuente):
        print(f"⚠️  NO SE ENCONTRÓ '{archivo_fuente}'.")
        print("Por favor, ejecuta el script generador de archivo primero.")
        return

    # 2. Carga completa en memoria
    banco_cartones = cargar_archivo_completo(archivo_fuente)
    if not banco_cartones: return

    # 3. Definición de Jugadores
    try:
        n = int(input("\nIngrese cantidad de jugadores para la partida: "))
        lista_jugadores = repartir_cartones(banco_cartones, n)
    except ValueError:
        print("Debe ingresar un número entero.")
        return

    # 4. Sorteo de Rondas
    orden_idiomas = ["SP", "EN", "PT", "DT"]
    random.shuffle(orden_idiomas)
    
    print("\n" + "="*60)
    print(f"🎲 ORDEN DE IDIOMAS SORTEADO: {' -> '.join(orden_idiomas)}")
    print("="*60)
    
    # 5. Bucle del Juego
    juego_terminado = False
    
    for idioma_actual in orden_idiomas:
        if juego_terminado: break
        
        nombre_idioma = NOMBRES_IDIOMAS[idioma_actual]
        print(f"\n>>> RONDA DE: {nombre_idioma} ({idioma_actual}) <<<")
        print(f"ℹ️  Solo juegan cartones que inician con '{idioma_actual}'")
        print("Escriba 'SIGUIENTE' para forzar cambio de idioma.")

        while True:
            palabra = input(f"[{idioma_actual}] Palabra cantada: ").strip().upper()
            
            if palabra == "SIGUIENTE":
                print(f"--- Fin de ronda {nombre_idioma} ---")
                break
            if palabra == "": continue

            ganadores_globales = []

            # Verificar en todos los jugadores
            for jug in lista_jugadores:
                ids_gan = jug.verificar_palabra_en_idioma(palabra, idioma_actual)
                for id_g in ids_gan:
                    ganadores_globales.append((jug.nombre, id_g))
            
            if ganadores_globales:
                print("\n" + "🎉"*25)
                print(f"¡BINGO! JUEGO TERMINADO EN LA RONDA DE {nombre_idioma}")
                print("🎉"*25)
                for nombre, id_c in ganadores_globales:
                    print(f"🏆 {nombre} completó el cartón {id_c}")
                
                juego_terminado = True
                break 
            else:
                 print(f">> '{palabra}': Sin ganadores totales aún.")

    if not juego_terminado:
        print("\nSe agotaron los idiomas y nadie ganó.")

if __name__ == "__main__":
    main()
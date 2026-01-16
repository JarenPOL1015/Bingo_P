import os
import sys

# =============================================================================
# ESTRATEGIA DE DISEÑO: DIVIDE Y VENCERÁS (DIVIDE AND CONQUER)
# Implementación: Ordenamiento (MergeSort/Timsort) + Búsqueda Binaria
# =============================================================================

class Carton:
    def __init__(self, id_carton, palabras):
        self.id = id_carton
        # PASO 1 (PREPROCESAMIENTO):
        # Para aplicar Búsqueda Binaria, los datos DEBEN estar ordenados.
        # Python usa Timsort (basado en MergeSort), que es eficiente O(n log n).
        self.palabras = sorted([p.upper() for p in palabras]) 
        
        self.total_palabras = len(self.palabras)
        self.aciertos = 0
        self.palabras_marcadas = set() # Para evitar contar la misma palabra dos veces

    def busqueda_binaria(self, objetivo):
        """
        Implementación pura de la estrategia DIVIDE Y VENCERÁS.
        Divide el espacio de búsqueda en mitades recursiva o iterativamente.
        Complejidad: O(log n)
        """
        izquierda = 0
        derecha = len(self.palabras) - 1

        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            palabra_medio = self.palabras[medio]

            if palabra_medio == objetivo:
                return True # ¡Encontrado!
            elif palabra_medio < objetivo:
                izquierda = medio + 1 # Descartar mitad inferior (Divide)
            else:
                derecha = medio - 1 # Descartar mitad superior (Divide)
        
        return False # No encontrado

    def marcar(self, palabra_cantada):
        palabra_cantada = palabra_cantada.upper()
        
        # Verificamos si ya la marcamos antes para no procesar doble
        if palabra_cantada in self.palabras_marcadas:
            return False

        # Aplicamos la estrategia de búsqueda
        encontrada = self.busqueda_binaria(palabra_cantada)

        if encontrada:
            self.palabras_marcadas.add(palabra_cantada)
            self.aciertos += 1
            return True
        return False

    def es_ganador(self):
        return self.aciertos == self.total_palabras

    def __str__(self):
        return f"[{self.id}] Aciertos: {self.aciertos}/{self.total_palabras}"

# =============================================================================
# GESTIÓN DEL JUEGO
# =============================================================================

def cargar_desde_archivo(nombre_archivo):
    cartones = []
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) > 1:
                    id_carton = partes[0]
                    palabras = partes[1:]
                    cartones.append(Carton(id_carton, palabras))
        print(f"✅ Se cargaron {len(cartones)} cartones exitosamente.")
        return cartones
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{nombre_archivo}'.")
        return []

def ingreso_manual():
    cartones = []
    print("\n--- Ingreso Manual (Escribe 'FIN' en el ID para terminar) ---")
    while True:
        id_input = input("Ingrese ID del cartón (8 caracteres): ").strip()
        if id_input.upper() == 'FIN':
            break
        palabras_input = input("Ingrese las palabras separadas por espacio: ").strip()
        palabras = palabras_input.split()
        if len(palabras) > 0:
            cartones.append(Carton(id_input, palabras))
            print("Cartón guardado.")
        else:
            print("El cartón debe tener al menos una palabra.")
    return cartones

def generar_archivo_prueba():
    """Genera un archivo dummy para probar la carga masiva rápidamente"""
    contenido = """ES000001 SOL PLAYA ARENA MAR
ES000002 LUNA ESTRELLA CIELO NOCHE
EN000003 SUN BEACH SAND SEA
PT000004 SOL PRAIA AREIA MAR
ES000005 COMPUTADORA ALGORITMO PYTHON BINGO
"""
    with open("cartones_prueba.txt", "w", encoding='utf-8') as f:
        f.write(contenido)
    print("ℹ️ Archivo 'cartones_prueba.txt' generado para pruebas.")

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=== BINGO_P: SISTEMA DE GESTIÓN DE BINGO DE PALABRAS ===")
    
    # Paso 0: Generar archivo de prueba si no existe (Ayuda para el usuario)
    if not os.path.exists("cartones_prueba.txt"):
        generar_archivo_prueba()

    cartones_en_juego = []

    # Paso 1: Configuración
    while True:
        print("\nSeleccione modo de carga:")
        print("1. Carga Masiva (desde 'cartones_prueba.txt')")
        print("2. Ingreso Manual")
        opcion = input("Opción: ")

        if opcion == "1":
            cartones_en_juego = cargar_desde_archivo("cartones_prueba.txt")
            if cartones_en_juego: break
        elif opcion == "2":
            cartones_en_juego = ingreso_manual()
            if cartones_en_juego: break
        else:
            print("Opción no válida.")

    if not cartones_en_juego:
        print("No hay cartones para jugar. Saliendo.")
        return

    # Paso 2: Bucle del Juego
    print("\n=== ¡COMIENZA EL JUEGO! ===")
    ronda = 0
    juego_activo = True

    while juego_activo:
        ronda += 1
        print(f"\n--- RONDA {ronda} ---")
        palabra_cantada = input("Ingrese la palabra cantada por el locutor (o 'SALIR'): ").strip()

        if palabra_cantada.upper() == 'SALIR':
            break

        ganadores_ronda = []

        # Procesar todos los cartones
        for carton in cartones_en_juego:
            # Aquí es donde la MAGIA de la eficiencia ocurre
            carton.marcar(palabra_cantada)
            
            if carton.es_ganador():
                ganadores_ronda.append(carton.id)

        # Salida del sistema según enunciado
        if ganadores_ronda:
            print("\n🎉 ¡BINGO! TENEMOS GANADORES 🎉")
            for ganador_id in ganadores_ronda:
                print(f"🏆 El cartón ganador es: {ganador_id}")
            
            continuar = input("\n¿Desea continuar jugando por otros premios? (S/N): ")
            if continuar.upper() != 'S':
                juego_activo = False
                # Removemos a los ganadores si siguen jugando? 
                # El enunciado no especifica, asumimos que termina el juego principal.
        else:
            print(">> No hubo cartones ganadores en esta ronda.")

if __name__ == "__main__":
    main()
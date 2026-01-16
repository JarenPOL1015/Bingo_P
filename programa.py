import os
import sys
import random  # Necesario para la aleatoriedad de los idiomas

# =============================================================================
# ESTRATEGIA DE DISEÑO: DIVIDE Y VENCERÁS (DIVIDE AND CONQUER)
# =============================================================================

class Carton:
    def __init__(self, id_carton, palabras):
        self.id = id_carton
        # PREPROCESAMIENTO (DAC): Ordenar para poder usar Búsqueda Binaria
        self.palabras = sorted([p.upper() for p in palabras]) 
        self.total_palabras = len(self.palabras)
        self.aciertos = 0
        self.palabras_marcadas = set() 

    def busqueda_binaria(self, objetivo):
        """Busca la palabra usando Divide y Vencerás (O(log n))"""
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
        return self.aciertos == self.total_palabras

    def __str__(self):
        return f"[{self.id}] Faltan: {self.total_palabras - self.aciertos}"

# =============================================================================
# GESTIÓN DE ARCHIVOS Y JUEGO
# =============================================================================

def generar_archivo_prueba():
    """Genera cartones dummy para probar rápidamente"""
    contenido = """ES000001 SOL PLAYA ARENA MAR
ES000002 LUNA ESTRELLA CIELO NOCHE
EN000003 SUN BEACH SAND SEA
PT000004 SOL PRAIA AREIA MAR
NL000005 ZON STRAND ZAND ZEE
"""
    with open("cartones_prueba.txt", "w", encoding='utf-8') as f:
        f.write(contenido)
    print("ℹ️ Archivo 'cartones_prueba.txt' generado.")

def cargar_desde_archivo(nombre_archivo):
    cartones = []
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) > 1:
                    cartones.append(Carton(partes[0], partes[1:]))
        print(f"✅ Se cargaron {len(cartones)} cartones.")
        return cartones
    except FileNotFoundError:
        print(f"❌ Error: Archivo '{nombre_archivo}' no encontrado.")
        return []

def ingreso_manual():
    cartones = []
    print("\n--- Ingreso Manual (Escribe 'FIN' en ID para terminar) ---")
    while True:
        id_input = input("ID Cartón: ").strip()
        if id_input.upper() == 'FIN': break
        palabras = input("Palabras: ").strip().split()
        if words: cartones.append(Carton(id_input, palabras))
    return cartones

# =============================================================================
# LÓGICA PRINCIPAL (MAIN)
# =============================================================================

def main():
    print("=== BINGO_P: GESTIÓN DE BINGO (Estrategia: DAC) ===")
    
    if not os.path.exists("cartones_prueba.txt"):
        generar_archivo_prueba()

    # 1. CARGA DE CARTONES
    cartones_en_juego = []
    opcion = input("\n1. Carga Masiva\n2. Manual\nOpción: ")
    if opcion == "1":
        cartones_en_juego = cargar_desde_archivo("cartones_prueba.txt")
    else:
        cartones_en_juego = ingreso_manual()

    if not cartones_en_juego: return

    # 2. DEFINICIÓN DE ORDEN DE IDIOMAS (CORRECCIÓN 1)
    idiomas = ["Español", "Inglés", "Portugués", "Dutch"]
    random.shuffle(idiomas) # Aleatoriedad requerida
    
    print("\n" + "="*50)
    print("🎲 ORDEN DE IDIOMAS PARA ESTA PARTIDA 🎲")
    print(f"La secuencia aleatoria es: {' -> '.join(idiomas)}")
    print("="*50)
    print("(Nota: Tú eres el locutor, ingresa palabras siguiendo este orden si lo deseas)")

    # 3. BUCLE DE JUEGO
    ronda = 0
    juego_activo = True

    while juego_activo and cartones_en_juego:
        ronda += 1
        print(f"\n--- RONDA {ronda} ---")
        print(f"Cartones activos: {len(cartones_en_juego)}")
        palabra = input("Ingrese palabra cantada (o 'SALIR'): ").strip()

        if palabra.upper() == 'SALIR': break

        # Lista temporal para guardar los que ganan en ESTA ronda
        ganadores_esta_ronda = [] 

        # Verificación
        for carton in cartones_en_juego:
            carton.marcar(palabra)
            if carton.es_ganador():
                ganadores_esta_ronda.append(carton)

        # Reporte y Eliminación (CORRECCIÓN 2)
        if ganadores_esta_ronda:
            print(f"\n🎉 ¡BINGO! SE HAN COMPLETADO {len(ganadores_esta_ronda)} CARTÓN(ES) 🎉")
            for ganador in ganadores_esta_ronda:
                print(f"🏆 GANADOR: {ganador.id}")
                # ELIMINAR EL CARTÓN DEL JUEGO
                cartones_en_juego.remove(ganador) 
            
            if not cartones_en_juego:
                print("\n🛑 ¡Se han acabado todos los cartones! Fin del juego.")
                juego_activo = False
            else:
                cont = input("\n¿Continuar jugando por los cartones restantes? (S/N): ")
                if cont.upper() != 'S': juego_activo = False
        else:
            print(">> Nadie ha completado su cartón todavía.")

if __name__ == "__main__":
    main()
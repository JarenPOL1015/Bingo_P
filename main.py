import os
import random
import sys

# =============================================================================
# CONSTANTES Y REGLAS DE NEGOCIO
# =============================================================================

REGLAS_TAMANO = {
    "SP": 24,  # Español
    "EN": 14,  # Inglés
    "PT": 20,  # Portugués
    "DT": 10   # Dutch
}

NOMBRES_IDIOMAS = {
    "SP": "ESPAÑOL",
    "EN": "INGLÉS",
    "PT": "PORTUGUÉS",
    "DT": "DUTCH"
}

# =============================================================================
# CLASE CARTON (ESTRATEGIA: DIVIDE Y VENCERÁS)
# =============================================================================

class Carton:
    def __init__(self, id_carton, palabras):
        self.id = id_carton.upper()
        
        # --- VALIDACIÓN DE REGLAS (Fundamental para ingreso manual) ---
        prefijo = self.id[:2]
        if prefijo in REGLAS_TAMANO:
            esperado = REGLAS_TAMANO[prefijo]
            if len(palabras) != esperado:
                # En modo manual esto se controla antes, pero validamos por seguridad
                print(f"⚠️ [Data Error] Cartón {self.id} tiene {len(palabras)} palabras. Se requieren {esperado}.")

        # --- DAC: PREPROCESAMIENTO ---
        # Ordenamos las palabras para habilitar la Búsqueda Binaria.
        # Python usa Timsort (MergeSort optimizado) -> O(n log n).
        self.palabras = sorted([p.upper() for p in palabras]) 
        
        self.total_palabras = len(self.palabras)
        self.aciertos = 0
        self.palabras_marcadas = set() 

    def get_idioma(self):
        return self.id[:2]

    def busqueda_binaria(self, objetivo):
        """
        DAC: Divide el espacio de búsqueda en mitades. Complejidad: O(log n).
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
        
        # Evitar re-procesamiento si ya se marcó
        if palabra_cantada in self.palabras_marcadas:
            return False

        # Aplicamos la Búsqueda Binaria
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
        self.cartones = cartones 

    def verificar_palabra_en_idioma(self, palabra, idioma_actual):
        cartones_ganadores = []
        for carton in self.cartones:
            # OPTIMIZACIÓN: Ignorar cartones de otros idiomas
            if carton.get_idioma() != idioma_actual:
                continue 

            if carton.marcar(palabra):
                if carton.es_ganador():
                    cartones_ganadores.append(carton.id)
        return cartones_ganadores

# =============================================================================
# LÓGICA DE CARGA (MASIVA Y MANUAL)
# =============================================================================

def cargar_masiva_desde_txt(nombre_archivo, n_jugadores):
    """Lee el archivo TXT y reparte cartones a N jugadores."""
    lista_bruta = []
    print(f"\n📂 Leyendo archivo maestro: {nombre_archivo}...")
    
    if not os.path.exists(nombre_archivo):
        print(f"❌ Error: No se encuentra '{nombre_archivo}'.")
        return []

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
        
        # Repartir
        if not lista_bruta: return []
        random.shuffle(lista_bruta)
        
        cartones_por_jugador = len(lista_bruta) // n_jugadores
        jugadores = []
        inicio = 0
        
        print(f"📦 Repartiendo ~{cartones_por_jugador} cartones por jugador...")
        
        for i in range(1, n_jugadores + 1):
            fin = inicio + cartones_por_jugador
            if i == n_jugadores: fin = len(lista_bruta) # El último se lleva el resto
            
            pack = lista_bruta[inicio:fin]
            jugadores.append(Jugador(f"Jugador_{i}", pack))
            inicio = fin
            
        return jugadores

    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return []

def cargar_manual_interactiva(n_jugadores):
    """
    Permite al usuario escribir los cartones por teclado, validando reglas.
    """
    jugadores = []
    print("\n✍️  --- INGRESO MANUAL DE CARTONES ---")
    print("Reglas de palabras por idioma:")
    for k, v in REGLAS_TAMANO.items():
        print(f"  - {k} ({NOMBRES_IDIOMAS[k]}): {v} palabras")

    for i in range(1, n_jugadores + 1):
        nombre = f"Jugador_{i}"
        cartones_jugador = []
        print(f"\n👤 Configurando: {nombre}")
        
        while True:
            print(f"\n> Nuevo Cartón para {nombre} (o escriba 'FIN' para pasar al siguiente jugador)")
            id_input = input("  Ingrese ID (ej. SP001, EN005): ").strip().upper()
            
            if id_input == 'FIN':
                if not cartones_jugador:
                    print("  ⚠️ El jugador debe tener al menos un cartón.")
                    continue
                break
            
            # 1. Validar Prefijo
            prefijo = id_input[:2]
            if prefijo not in REGLAS_TAMANO:
                print(f"  ❌ Error: ID debe empezar con {list(REGLAS_TAMANO.keys())}")
                continue
            
            cant_necesaria = REGLAS_TAMANO[prefijo]
            
            # 2. Ingresar Palabras
            print(f"  Ingrese las {cant_necesaria} palabras separadas por espacio:")
            entrada_palabras = input("  Palabras: ").strip()
            lista_palabras = entrada_palabras.split()
            
            # 3. Validar Cantidad
            if len(lista_palabras) != cant_necesaria:
                print(f"  ❌ Error: Ingresó {len(lista_palabras)} palabras, pero se requieren {cant_necesaria} para {prefijo}.")
                print("  Inténtelo de nuevo.")
            else:
                nuevo_carton = Carton(id_input, lista_palabras)
                cartones_jugador.append(nuevo_carton)
                print(f"  ✅ Cartón {id_input} guardado correctamente.")
        
        jugadores.append(Jugador(nombre, cartones_jugador))
    
    return jugadores

# =============================================================================
# MAIN (LÓGICA PRINCIPAL)
# =============================================================================

def main():
    print("=== BINGO_P: SISTEMA DE GESTIÓN (Multimodalidad) ===")
    
    lista_jugadores = []
    
    # 1. MENÚ DE MODALIDAD
    while True:
        print("\nSeleccione la modalidad de entrada:")
        print("1. Carga Masiva (Archivo .TXT)")
        print("2. Ingreso Manual (Teclado)")
        opcion = input("Opción: ").strip()
        
        if opcion in ["1", "2"]:
            try:
                n = int(input("Ingrese la cantidad de jugadores: "))
                if n < 1: raise ValueError
                
                if opcion == "1":
                    archivo = "cartones_masivos.txt" # O preguntar input()
                    # Si el archivo no existe, avisar
                    if not os.path.exists(archivo):
                        archivo = input("Nombre del archivo .txt (ej. mis_cartones.txt): ")
                    
                    lista_jugadores = cargar_masiva_desde_txt(archivo, n)
                else:
                    lista_jugadores = cargar_manual_interactiva(n)
                
                if lista_jugadores: break
            except ValueError:
                print("❌ Por favor ingrese un número válido de jugadores.")
        else:
            print("Opción no válida.")

    # 2. SORTEO DE RONDAS
    orden_idiomas = ["SP", "EN", "PT", "DT"]
    random.shuffle(orden_idiomas)
    
    print("\n" + "="*60)
    print(f"🎲 ORDEN DE IDIOMAS SORTEADO: {' -> '.join(orden_idiomas)}")
    print("="*60)
    
    # 3. BUCLE DE JUEGO
    juego_terminado = False
    
    for idioma_actual in orden_idiomas:
        if juego_terminado: break
        
        nombre_idioma = NOMBRES_IDIOMAS[idioma_actual]
        print(f"\n>>> INICIO RONDA: {nombre_idioma} ({idioma_actual}) <<<")
        print(f"ℹ️  Solo juegan cartones que inician con '{idioma_actual}'")
        print("Escriba 'SIGUIENTE' para cambiar de idioma si se acaban las palabras.")

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
                 print(f">> '{palabra}': No hubo ganadores.")

    if not juego_terminado:
        print("\n🚫 Se agotaron los idiomas y nadie ganó la partida.")

if __name__ == "__main__":
    main()
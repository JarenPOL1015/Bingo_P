import random

# CONFIGURACIÓN DE REGLAS
REGLAS = {"SP": 24, "EN": 14, "PT": 20, "DT": 10}
BANCO = {
    "SP": ["CASA", "PERRO", "GATO", "SOL", "LUNA", "PLAYA", "MAR", "TIEMPO", "VIDA", "MANZANA", "MESA", "SILLA", "ARBOL", "COCHE", "LIBRO", "COMPUTADORA", "TECLADO", "RATON", "PANTALLA", "INTERNET", "CODIGO", "PYTHON", "JAVA", "DATOS", "ALGORITMO", "BINGO", "GANADOR", "SUERTE", "AMIGO", "FAMILIA", "FIESTA", "MUSICA", "NOCHE", "DIA"],
    "EN": ["HOUSE", "DOG", "CAT", "SUN", "MOON", "BEACH", "SEA", "TIME", "LIFE", "APPLE", "TABLE", "CHAIR", "TREE", "CAR", "BOOK", "COMPUTER", "KEYBOARD", "MOUSE", "SCREEN", "INTERNET", "CODE", "PYTHON", "JAVA", "DATA", "ALGORITHM", "BINGO", "WINNER", "LUCK", "FRIEND", "FAMILY", "PARTY", "MUSIC", "NIGHT", "DAY"],
    "PT": ["CASA", "CACHORRO", "GATO", "SOL", "LUA", "PRAIA", "MAR", "TEMPO", "VIDA", "MACA", "MESA", "CADEIRA", "ARVORE", "CARRO", "LIVRO", "COMPUTADOR", "TECLADO", "MOUSE", "TELA", "INTERNET", "CODIGO", "PYTHON", "JAVA", "DADOS", "ALGORITMO", "BINGO", "VENCEDOR", "SORTE", "AMIGO", "FAMILIA", "FESTA", "MUSICA", "NOITE", "DIA"],
    "DT": ["HUIS", "HOND", "KAT", "ZON", "MAAN", "STRAND", "ZEE", "TIJD", "LEVEN", "APPEL", "TAFEL", "STOEL", "BOOM", "AUTO", "BOEK", "COMPUTER", "TOETSENBORD", "MUIS", "SCHERM", "INTERNET", "CODE", "PYTHON", "JAVA", "DATA", "ALGORITME", "BINGO", "WINNAAR", "GELUK", "VRIEND", "FAMILIE", "FEEST", "MUZIEK", "NACHT", "DAG"]
}

def generar_archivo_txt():
    print("Generando 'cartones_masivos.txt'...")
    with open("cartones_masivos.txt", "w", encoding="utf-8") as f:
        # Generamos 1000 cartones (Suficiente para 5 jugadores de 200 c/u)
        tipos = ["SP", "EN", "PT", "DT"]
        cantidad_cartones = 1000000
        for i in range(1, cantidad_cartones + 1):
            # Aseguramos variedad cíclica (SP, EN, PT, DT, SP...)
            tipo = tipos[(i-1) % 4]
            cant = REGLAS[tipo]
            
            # Selección aleatoria sin repetidos
            palabras = random.sample(BANCO[tipo], cant)
            
            # Formato ID: SP0001, EN0002...
            id_carton = f"{tipo}{str(i).zfill(6)}"
            linea = f"{id_carton} {' '.join(palabras)}\n"
            f.write(linea)
            
    print(f"✅ Archivo creado exitosamente con {cantidad_cartones} cartones.")

if __name__ == "__main__":
    generar_archivo_txt()
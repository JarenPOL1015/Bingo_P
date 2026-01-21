# =============================================================================
# MODELOS DEL SISTEMA - ESTRATEGIA DAC PRESERVADA
# =============================================================================

class Carton:
    """
    Clase Carton con estrategia Divide y Conquista.
    - Búsqueda Binaria O(log n)
    """
    def __init__(self, id_carton, palabras):
        self.id = id_carton.upper()
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

    def to_dict(self):
        """Serialización para API"""
        return {
            "id": self.id,
            "idioma": self.get_idioma(),
            "palabras": self.palabras,
            "palabras_marcadas": list(self.palabras_marcadas),
            "aciertos": self.aciertos,
            "total_palabras": self.total_palabras,
            "es_ganador": self.es_ganador()
        }


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

    def to_dict(self):
        """Serialización para API"""
        return {
            "nombre": self.nombre,
            "cartones": [c.to_dict() for c in self.cartones],
            "total_cartones": len(self.cartones)
        }

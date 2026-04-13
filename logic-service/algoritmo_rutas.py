import math

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia real en metros entre dos coordenadas GPS 
    usando la fórmula de Haversine.
    """
    R = 6371000  # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return distancia

def calcular_mejor_ruta(origen, contenedores):
    """
    Aplica el algoritmo del Problema del Viajante (TSP) usando la 
    heurística del Vecino Más Cercano.
    """
    nodos_pendientes = contenedores.copy()
    ruta_ordenada = []
    nodo_actual = origen
    distancia_total = 0.0

    while len(nodos_pendientes) > 0:
        mas_cercano_idx = 0
        distancia_minima = float('inf')

        # Buscar el contenedor más cercano al punto actual
        for i, contenedor in enumerate(nodos_pendientes):
            d = calcular_distancia(
                nodo_actual['lat'], nodo_actual['lng'],
                contenedor['lat'], contenedor['lng']
            )
            if d < distancia_minima:
                distancia_minima = d
                mas_cercano_idx = i

        # Moverse al contenedor más cercano
        siguiente_parada = nodos_pendientes.pop(mas_cercano_idx)
        ruta_ordenada.append(siguiente_parada)
        distancia_total += distancia_minima
        nodo_actual = siguiente_parada

    return ruta_ordenada, distancia_total
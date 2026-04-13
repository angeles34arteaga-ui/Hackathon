from flask import Flask, request, jsonify
from flask_cors import CORS
from algoritmo_rutas import calcular_mejor_ruta

app = Flask(__name__)
# Habilitamos CORS para que tu frontend (HTML) pueda conectarse sin bloqueos de seguridad
CORS(app) 

@app.route('/api/optimizar-ruta', methods=['POST'])
def optimizar_ruta():
    try:
        datos = request.json
        origen = datos.get('origen')
        contenedores = datos.get('contenedores')

        if not origen or not contenedores:
            return jsonify({"error": "Faltan datos de origen o contenedores"}), 400
        
        # Llamada a tu algoritmo de IA
        ruta_ordenada, distancia_total = calcular_mejor_ruta(origen, contenedores)
        
        # Devolvemos la respuesta al navegador en formato JSON
        return jsonify({
            "ruta_ordenada": ruta_ordenada,
            "distancia_total_km": round(distancia_total / 1000, 2) # Convertimos metros a km
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # El servidor correrá en http://localhost:5000
    app.run(debug=True, port=5000)
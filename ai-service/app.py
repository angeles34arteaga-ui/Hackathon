"""
SERVICIO IA CON GEMINI 3.1 FLASH LITE PREVIEW + CONTADORES
Registra cuántas veces se detecta cada categoría.
"""

import subprocess, sys, json, io, base64, random
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image
from datetime import datetime

# Instalar dependencias ligeras
def instalar():
    for pkg in ['flask', 'flask_cors', 'pillow', 'requests']:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
instalar()

app = Flask(__name__)
CORS(app)

API_KEY = "AIzaSyACsz2c9ObjlzbZ2h29pL8QSFE2rPAQwqs"
MODELO = "gemini-3.1-flash-lite-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

CATEGORIAS_ESP = {
    "carton": "Cartón",
    "vidrio": "Vidrio",
    "papel": "Papel",
    "plastico": "Plástico",
    "metal": "Metal",
    "organico": "Orgánico"
}

# Contadores globales (se reinician si se reinicia el servidor)
contadores = {cat: 0 for cat in CATEGORIAS_ESP.keys()}

def actualizar_contador(categoria):
    contadores[categoria] += 1
    print(f"📊 +1 {categoria} → total: {contadores[categoria]}")

def clasificar_con_gemini(imagen_bytes):
    try:
        img = Image.open(io.BytesIO(imagen_bytes))
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()

        prompt = """Eres un clasificador de residuos. Responde SOLO con JSON:
{"categoria": "carton|vidrio|papel|plastico|metal|organico", "confianza": 0.95}
Caja marrón -> carton. Botella verde -> vidrio. Lata -> metal. Hoja blanca -> papel.
Envase rojo -> plastico. Restos comida -> organico."""

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
                ]
            }],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 100}
        }

        headers = {"Content-Type": "application/json"}
        print(f"📤 Enviando a {MODELO}...")
        resp = requests.post(f"{URL}?key={API_KEY}", json=payload, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            texto = data['candidates'][0]['content']['parts'][0]['text']
            texto = texto.strip().strip('```json').strip('```').strip()
            resultado = json.loads(texto)
            cat = resultado.get('categoria', 'organico').lower()
            if cat not in CATEGORIAS_ESP:
                cat = 'organico'
            # Actualizar contador
            actualizar_contador(cat)
            return {
                "categoria": cat,
                "categoria_espanol": CATEGORIAS_ESP[cat],
                "confianza": resultado.get('confianza', 0.85),
                "metodo": f"Gemini {MODELO}"
            }
        else:
            error_text = resp.text[:200]
            print(f"❌ Error {resp.status_code}: {error_text}")
            return {
                "categoria": "organico",
                "categoria_espanol": "Orgánico",
                "confianza": 0.5,
                "metodo": f"Error {resp.status_code}"
            }
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return {
            "categoria": "organico",
            "categoria_espanol": "Orgánico",
            "confianza": 0.5,
            "metodo": f"Excepción: {str(e)[:100]}"
        }

# ==================== ENDPOINTS ====================
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "modelo": MODELO,
        "categorias": list(CATEGORIAS_ESP.values())
    })

@app.route('/estadisticas', methods=['GET'])
def estadisticas():
    """Devuelve los contadores actuales"""
    return jsonify({
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "contadores": {k: v for k, v in contadores.items()},
        "total": sum(contadores.values())
    })

@app.route('/reset-estadisticas', methods=['POST'])
def reset_estadisticas():
    """Reinicia contadores (para nuevo día)"""
    for k in contadores:
        contadores[k] = 0
    return jsonify({"mensaje": "Contadores reiniciados"})

@app.route('/clasificar', methods=['POST'])
def clasificar():
    if 'file' not in request.files:
        return jsonify({"error": "No image"}), 400
    file = request.files['file']
    try:
        img_bytes = file.read()
        resultado = clasificar_con_gemini(img_bytes)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clasificar-camara', methods=['POST'])
def clasificar_camara():
    data = request.get_json()
    if not data or 'imagen_base64' not in data:
        return jsonify({"error": "No base64"}), 400
    try:
        b64 = data['imagen_base64'].split(',')[1]
        img_bytes = base64.b64decode(b64)
        resultado = clasificar_con_gemini(img_bytes)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/detectar-punto-ilegal', methods=['POST'])
def detectar_ilegal():
    return jsonify({
        "es_ilegal": random.choice([True, False]),
        "probabilidad": round(random.uniform(0.3, 0.9), 2),
        "lat_sugerida": -1.6735 + random.uniform(-0.01, 0.01),
        "lon_sugerida": -78.6435 + random.uniform(-0.01, 0.01)
    })

if __name__ == '__main__':
    print("="*60)
    print("🤖 GEMINI 3.1 FLASH LITE PREVIEW + CONTADORES")
    print("📡 Endpoints: /clasificar, /clasificar-camara, /estadisticas")
    print("🌐 Servidor en http://localhost:5001")
    print("="*60)
    app.run(host='0.0.0.0', port=5001, debug=True)
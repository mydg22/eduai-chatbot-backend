# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Habilitar CORS para permitir solicitudes desde tu dominio de Moodle
# En un entorno de producción, reemplaza "*" con el dominio específico de tu Moodle
CORS(app)

# Tu clave de API de Gemini. Es MEJOR obtenerla de una variable de entorno
# por seguridad, pero para la demostración la ponemos directamente.
# ¡NUNCA expongas esto en un repositorio público!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#¡Así debe quedar para GitHub!
# La parte ", "TU_CLAVE_DE_API_DE_GEMINI_AQUI"" es solo para pruebas locales si no configuras la variable de entorno localmente.
# Para GitHub, es mejor que solo espere la variable de entorno.

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@app.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_prompt = data.get('userPrompt')

    if not user_prompt:
        return jsonify({"error": "Missing userPrompt"}), 400

    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}]
    }
    params = {
        "key": GEMINI_API_KEY
    }

    try:
        # Realiza la solicitud a la API de Gemini
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params=params)
        response.raise_for_status() # Lanza una excepción para códigos de estado de error (4xx o 5xx)
        gemini_response = response.json()

        # Extrae el texto generado
        if gemini_response and 'candidates' in gemini_response and len(gemini_response['candidates']) > 0:
            generated_text = gemini_response['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"generatedPrompt": generated_text})
        else:
            return jsonify({"error": "No se pudo obtener una respuesta válida de Gemini."}), 500

    except requests.exceptions.RequestException as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return jsonify({"error": f"Error al conectar con la API de Gemini: {e}"}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500

if __name__ == '__main__':
    # Para ejecutar localmente:
    # 1. Instala Flask y Flask-CORS: pip install Flask Flask-CORS requests
    # 2. Reemplaza "TU_CLAVE_DE_API_DE_GEMINI_AQUI" con tu clave real.
    # 3. Ejecuta: python app.py
    # Se ejecutará en http://127.0.0.1:5000/
    app.run(debug=True, port=5000)

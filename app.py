import os
import requests
import traceback
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator, MyMemoryTranslator

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Verificación inicial del token en los logs
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("⚠️ ADVERTENCIA: No se encontró HF_TOKEN en el entorno.")
else:
    print("✅ TOKEN CARGADO CORRECTAMENTE (primeros 10 caracteres):", str(HF_TOKEN)[:10] + "...")

app = Flask(__name__)
CORS(app)

# Historial de conversación en memoria
conversation_history = []

# Modelo y URL de la API de Hugging Face
HF_MODEL = "facebook/blenderbot-400M-distill"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def traducir(texto, origen, destino):
    """Intenta traducir con GoogleTranslator; si falla, usa MyMemoryTranslator de respaldo."""
    if not texto or not str(texto).strip():
        return texto
    try:
        return GoogleTranslator(source=origen, target=destino).translate(texto)
    except Exception as e:
        print(f"⚠️ Error en GoogleTranslator ({origen}->{destino}): {e}. Usando MyMemoryTranslator.")
        try:
            return MyMemoryTranslator(source=origen, target=destino).translate(texto)
        except Exception as e2:
            print(f"❌ Error en MyMemoryTranslator: {e2}. Devolviendo texto original.")
            return texto


@app.route('/', methods=['GET'])
def home():
    """Ruta principal que sirve la interfaz web."""
    return render_template('index.html')


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    """Endpoint de procesamiento del chat."""
    if request.method == 'GET':
        return jsonify({"message": "Endpoint /chatbot activo. Envía una petición POST con el mensaje."}), 200

    global conversation_history

    # Extracción segura de la carga JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Solicitud sin datos JSON válidos"}), 400

    user_message = data.get('prompt', '').strip() or data.get('message', '').strip()
    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        # 1. Traducir el mensaje entrante del usuario de español a inglés
        user_message_en = traducir(user_message, 'es', 'en')

        # 2. Mantener únicamente los últimos 6 mensajes en memoria
        conversation_history = conversation_history[-6:]

        # 3. Construir el prompt concatenando el historial
        history = "\n".join(conversation_history)
        full_prompt = f"{history}\nUser: {user_message_en}\nBot:" if history else f"User: {user_message_en}\nBot:"

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 60,
                "repetition_penalty": 1.3,
                "temperature": 0.6
            }
        }

        # 4. Manejo seguro de los headers para evitar que un token nulo rompa el servidor (evita error 500)
        token_actual = os.environ.get("HF_TOKEN")
        headers = {}
        if token_actual and str(token_actual).strip():
            headers["Authorization"] = f"Bearer {str(token_actual).strip()}"

        print(f"\n📤 Enviando a Hugging Face: {full_prompt[:100]}...")
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=15)

        # 5. Procesar la respuesta devuelta por la API
        if response.status_code == 200:
            result = response.json()
            print("📥 Respuesta de Hugging Face:", result)

            if isinstance(result, list) and len(result) > 0:
                bot_response_en = result[0].get('generated_text', '')
            elif isinstance(result, dict) and 'generated_text' in result:
                bot_response_en = result['generated_text']
            elif isinstance(result, dict) and 'error' in result:
                bot_response_en = f"Error devuelto por la API: {result['error']}"
            else:
                bot_response_en = ""

            # Limpiar la repetición del prompt si la API lo devuelve en el cuerpo
            if bot_response_en.startswith(full_prompt):
                bot_response_en = bot_response_en[len(full_prompt):].strip()
            elif "Bot:" in bot_response_en:
                bot_response_en = bot_response_en.split("Bot:", 1)[-1].strip()

            if not bot_response_en:
                bot_response_en = "Lo siento, no pude generar una respuesta."

            # Guardar la interacción actual en el historial
            conversation_history.append(f"User: {user_message_en}")
            conversation_history.append(f"Bot: {bot_response_en}")

        elif response.status_code == 503:
            bot_response_en = "El modelo se está cargando en Hugging Face. Por favor, espera unos segundos y reintenta."
        else:
            error_msg = response.text[:200] if response.text else "Sin detalles"
            bot_response_en = f"Error en Hugging Face API (código {response.status_code}): {error_msg}"

        # 6. Traducir la respuesta devuelta de inglés a español
        bot_response_es = traducir(bot_response_en, 'en', 'es')

        return jsonify({
            "response": bot_response_es,
            "reply": bot_response_es
        }), 200

    except Exception as e:
        error_detalle = traceback.format_exc()
        print("\n" + "="*50 + "\n❌ ERROR EN CHATBOT:\n" + error_detalle + "="*50 + "\n")
        return jsonify({
            "error": str(e),
            "response": "Ocurrió un error interno al procesar el mensaje."
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
      

from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import re
load_dotenv()
app = Flask(__name__)
CORS(app)
client = OpenAI(
    api_key= os.getenv("API_KEY")
)
system_message = [
    {"role": "system", "content": "Sé un asistente virtual con experiencia en la salud mental. Formatea tus respuestas usando HTML simple (como <b> para negritas, <ul> y <li> para listas, <p> para párrafos) para que sean más legibles y estructuradas. Asegúrate de que las listas estén bien definidas y que el texto sea claro. Responde SOLO con la información relevante a la consulta actual. No envuelvas respuestas simples en <p> a menos que sea necesario."}
]

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'error': 'El mensaje no ha sido recibido'}), 400
        messages = system_message + [{"role": "user", "content": user_message}]
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        response = completion.choices[0].message.content
        response = re.sub(r'¡Hola!.?\n', '', response, flags=re.IGNORECASE)
        response = response.strip()
        if not response.startswith('<'):
            lines = response.split('\n')
            in_list = False
            formatted_response = ''
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if ':' in line and not in_list:
                    formatted_response += '<ul>'
                    in_list = True
                    title, desc = line.split(':', 1)
                    formatted_response += f'<li><b>{title.strip()}:</b> {desc.strip()}</li>'
                elif in_list and line:
                    if ':' in line:
                        title, desc = line.split(':', 1)
                        formatted_response += f'<li><b>{title.strip()}:</b> {desc.strip()}</li>'
                    else:
                        formatted_response += f'<li>{line}</li>'
                else:
                    if in_list:
                        formatted_response += '</ul>'
                        in_list = False
                    formatted_response += f'{line}<br>'
            if in_list:
                formatted_response += '</ul>'
            response = formatted_response

        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot import predict_intents, get_response

app = Flask(__name__, static_folder='frontend')  # <-- this tells Flask where your frontend files are
CORS(app)

# -------- THIS ROUTE IS MISSING --------
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('frontend', filename)
# ---------------------------------------

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    user_msg = data['message']
    intents = predict_intents(user_msg)
    reply = get_response(intents)
    return jsonify({'response': reply})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
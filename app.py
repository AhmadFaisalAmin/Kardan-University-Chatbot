from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot import predict_intents, get_response   # reuse your chatbot logic

app = Flask(__name__, static_folder='frontend')    # serve frontend files from the 'frontend' folder
CORS(app)   # allow cross-origin requests (for development)

# -----------------------------
# Serve frontend files
# -----------------------------
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('frontend', filename)

# -----------------------------
# Chat API endpoint
# -----------------------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_msg = data['message']
    intents = predict_intents(user_msg)
    reply = get_response(intents)
    return jsonify({'response': reply})

# -----------------------------
# Run the server
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
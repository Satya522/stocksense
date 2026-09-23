"""
StockSense - AI Query REST API Server
======================================
Exposes the NLP Stock Query Engine as a REST API endpoint.
This allows any frontend (web, mobile, chatbot) to send questions
and receive answers.

Usage:
  cd python
  venv\\Scripts\\activate
  python src/ai_query_api.py

API:
  POST http://localhost:5000/api/ask
  Body: { "question": "What is my lowest stock item?" }
"""

import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Import our NLP engine
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ai_stock_query import StockQueryEngine

# Initialize engine
query_engine = StockQueryEngine()


class AIQueryHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for the AI query API."""

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        """Handle POST /api/ask"""
        if self.path == '/api/ask':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(body)
                question = data.get('question', '')

                if not question:
                    self._send_json(400, {"error": "Question is required"})
                    return

                answer = query_engine.ask(question)
                self._send_json(200, {"question": question, "answer": answer})

            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_GET(self):
        """Serve the chat UI on GET /"""
        if self.path == '/' or self.path == '/index.html':
            self._serve_chat_ui()
        elif self.path == '/api/health':
            self._send_json(200, {"status": "ok", "service": "StockSense AI"})
        else:
            self._send_json(404, {"error": "Not found"})

    def _serve_chat_ui(self):
        """Serve the embedded chat HTML page."""
        html = get_chat_html()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, format, *args):
        print(f"[API] {args[0]}")


def get_chat_html():
    """Returns the embedded chat UI HTML."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockSense AI - Chat</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e0e0e0;
        }
        .chat-container {
            width: 90%;
            max-width: 700px;
            height: 85vh;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }
        .chat-header {
            padding: 20px 24px;
            background: rgba(255,255,255,0.08);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }
        .chat-header h1 {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .chat-header p { font-size: 12px; color: #888; margin-top: 4px; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #3a7bd5, #00d2ff);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.ai {
            align-self: flex-start;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.1);
            border-bottom-left-radius: 4px;
            white-space: pre-wrap;
            font-family: 'Inter', monospace;
            font-size: 13px;
        }
        .message.ai .label {
            font-size: 10px;
            color: #00d2ff;
            font-weight: 600;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .input-area {
            padding: 16px 20px;
            background: rgba(255,255,255,0.05);
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px;
            background: rgba(255,255,255,0.08);
            color: white;
            font-size: 14px;
            font-family: 'Inter', sans-serif;
            outline: none;
            transition: border 0.2s;
        }
        .input-area input:focus { border-color: #00d2ff; }
        .input-area input::placeholder { color: #666; }
        .input-area button {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #3a7bd5, #00d2ff);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
            font-family: 'Inter', sans-serif;
        }
        .input-area button:hover { transform: scale(1.02); }
        .input-area button:active { transform: scale(0.98); }
        .input-area button:disabled { opacity: 0.5; cursor: not-allowed; }
        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 0 20px 12px;
        }
        .suggestion {
            padding: 6px 12px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            font-size: 12px;
            color: #aaa;
            cursor: pointer;
            transition: all 0.2s;
        }
        .suggestion:hover {
            background: rgba(0,210,255,0.15);
            border-color: #00d2ff;
            color: #00d2ff;
        }
        .typing { color: #888; font-style: italic; font-size: 13px; padding: 8px 16px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>StockSense AI</h1>
            <p>Ask anything about your warehouse stock in plain English or Hindi</p>
        </div>
        <div class="messages" id="messages">
            <div class="message ai">
                <div class="label">StockSense AI</div>
                Namaste! Main tumhara stock assistant hoon. Mujhse kuch bhi poocho apne warehouse ke baare mein. Neeche kuch suggestions hain:
            </div>
        </div>
        <div class="suggestions" id="suggestions">
            <span class="suggestion" onclick="askSuggestion(this)">Lowest stock items</span>
            <span class="suggestion" onclick="askSuggestion(this)">Total stock value</span>
            <span class="suggestion" onclick="askSuggestion(this)">Items needing reorder</span>
            <span class="suggestion" onclick="askSuggestion(this)">Warehouse summary</span>
            <span class="suggestion" onclick="askSuggestion(this)">Out of stock items</span>
            <span class="suggestion" onclick="askSuggestion(this)">Recent movements</span>
        </div>
        <div class="input-area">
            <input type="text" id="questionInput" placeholder="Apna sawal poocho..." onkeypress="if(event.key==='Enter') sendQuestion()">
            <button id="sendBtn" onclick="sendQuestion()">Ask</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('questionInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(text, type) {
            const msg = document.createElement('div');
            msg.className = 'message ' + type;
            if (type === 'ai') {
                msg.innerHTML = '<div class="label">StockSense AI</div>' + escapeHtml(text);
            } else {
                msg.textContent = text;
            }
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function askSuggestion(el) {
            input.value = el.textContent;
            sendQuestion();
        }

        async function sendQuestion() {
            const question = input.value.trim();
            if (!question) return;

            addMessage(question, 'user');
            input.value = '';
            sendBtn.disabled = true;

            const typing = document.createElement('div');
            typing.className = 'typing';
            typing.textContent = 'Thinking...';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                const data = await res.json();
                typing.remove();
                addMessage(data.answer || data.error || 'No response', 'ai');
            } catch (err) {
                typing.remove();
                addMessage('Error connecting to server: ' + err.message, 'ai');
            }

            sendBtn.disabled = false;
            input.focus();
        }

        input.focus();
    </script>
</body>
</html>'''


# --- Start Server ---
if __name__ == "__main__":
    PORT = 5000
    print("=" * 60)
    print("  StockSense AI Query API Server")
    print("=" * 60)
    print(f"  Chat UI:  http://localhost:{PORT}")
    print(f"  API:      http://localhost:{PORT}/api/ask")
    print(f"  Health:   http://localhost:{PORT}/api/health")
    print("=" * 60)

    server = HTTPServer(('0.0.0.0', PORT), AIQueryHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()

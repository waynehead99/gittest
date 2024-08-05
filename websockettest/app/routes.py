from flask import render_template, jsonify
from app import app
import threading
import websocket
import json

# Store the state of the Home Assistant entities
entities = {}

# WebSocket connection details
HA_URL = "ws://10.0.254.147:8123/api/websocket"
HA_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiYWI5YzljYjllMmE0OWNhOWJhYmEzOTIyY2MzMDBlMyIsImlhdCI6MTcyMjczMzIzMSwiZXhwIjoyMDM4MDkzMjMxfQ.7l-TvRyOEbAQLdSsQnMlyL_WfuSoye4LKFp25oy0aR4"

def on_message(ws, message):
    global entities
    data = json.loads(message)
    if data.get('type') == 'event' and data['event']['event_type'] == 'state_changed':
        entity_id = data['event']['data']['entity_id']
        new_state = data['event']['data']['new_state']
        entities[entity_id] = new_state

def on_open(ws):
    auth_message = json.dumps({"type": "auth", "access_token": HA_ACCESS_TOKEN})
    ws.send(auth_message)

    # Subscribe to state changes
    subscribe_message = json.dumps({"id": 1, "type": "subscribe_events", "event_type": "state_changed"})
    ws.send(subscribe_message)

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws):
    print("WebSocket connection closed")

# Function to start the WebSocket connection
def start_ws():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(HA_URL, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()

# Start the WebSocket connection in a separate thread
ws_thread = threading.Thread(target=start_ws)
ws_thread.start()

@app.route('/')
def index():
    return render_template('index.html', entities=entities)

@app.route('/api/entities', methods=['GET'])
def get_entities():
    return jsonify(entities)

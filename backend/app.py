# Import eventlet and patch the standard library before anything else
import eventlet
eventlet.monkey_patch()

# Now import Flask and other modules
from flask import Flask
from flask_socketio import SocketIO, emit
import redis
import os

# Flask and Socket.IO setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # You should change this for production
socketio = SocketIO(app, cors_allowed_origins="*")

# Redis setup
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"),  # Redis hostname (set in Docker Compose)
    port=6379,
    decode_responses=True
)

# Subscribe to Redis draw channel
pubsub = redis_client.pubsub()
pubsub.subscribe("draw_channel")

@app.route("/")
def index():
    return "Backend Running"

@socketio.on("draw_event")
def handle_draw_event(data):
    print(f"Received draw event: {data}")  # Debug log
    redis_client.publish("draw_channel", str(data))  # Publish event to Redis
    emit("draw_event", data, broadcast=True)  # Broadcast to all clients

def listen_to_redis():
    """Listen to Redis and broadcast events to all clients."""
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received from Redis: {message['data']}")  # Debug log
            socketio.emit("draw_event", message["data"], broadcast=True)

if __name__ == "__main__":
    socketio.start_background_task(listen_to_redis)  # Run Redis listener in the background
    socketio.run(app, host="0.0.0.0", port=5000)  # Backend always runs on port 5000 internally

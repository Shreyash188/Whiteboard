import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO, emit
import redis
import os

# Flask and Socket.IO setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Redis setup
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")  # Use the REDIS_URL environment variable
redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)

# Subscribe to Redis draw channel
pubsub = redis_client.pubsub()
pubsub.subscribe("draw_channel")

# Store the whiteboard state in Redis
@app.route("/")
def index():
    return "Backend Running"

@socketio.on("connect")
def handle_new_connection():
    """Send the saved state to a newly connected user."""
    print("New client connected")
    try:
        saved_state = redis_client.lrange("whiteboard_state", 0, -1)
        for event in saved_state:
            emit("draw_event", eval(event))  # Send saved events to the new client
    except Exception as e:
        print(f"Error fetching saved state from Redis: {e}")

@socketio.on("draw_event")
def handle_draw_event(data):
    """Handle drawing events and broadcast them."""
    print(f"User {data['user']} drew at x:{data['x']} y:{data['y']}")
    try:
        redis_client.rpush("whiteboard_state", str(data))  # Save state to Redis
        redis_client.publish("draw_channel", str(data))  # Publish event to Redis
        emit("draw_event", data, broadcast=True)  # Broadcast to all clients
    except Exception as e:
        print(f"Error handling draw event: {e}")

def listen_to_redis():
    """Listen to Redis and broadcast updates to clients."""
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                socketio.emit("draw_event", eval(message["data"]), broadcast=True)
            except Exception as e:
                print(f"Error broadcasting Redis message: {e}")

if __name__ == "__main__":
    socketio.start_background_task(listen_to_redis)
    socketio.run(app, host="0.0.0.0", port=5000)

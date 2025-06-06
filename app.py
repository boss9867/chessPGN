from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
socketio = SocketIO(app, cors_allowed_origins="*")

# Store game states in memory (for demo, not persistent)
games = {}

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f"User joined room: {room}")
    # Send current game state to user if exists
    if room in games:
        emit('game_state', games[room], room=request.sid)
    else:
        games[room] = {'fen': 'start'}  # default start position

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    print(f"User left room: {room}")

@socketio.on('move')
def on_move(data):
    """
    data = {
      'room': 'room_id',
      'fen': 'new FEN string after move',
      'move': 'e2e4'  # optional, algebraic notation or uci move
    }
    """
    room = data['room']
    fen = data['fen']
    games[room] = {'fen': fen}
    # Broadcast new game state to all in room except sender
    emit('game_state', {'fen': fen}, room=room, include_self=False)
    print(f"Move in room {room}: {data['move']}")

if __name__ == '__main__':
    # Use eventlet or gevent for SocketIO production. For dev:
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from AI_MAZE import generate_dnd_maze,play
app = Flask(__name__)
socketio = SocketIO(app)

# Store information about lobbies and player positions
lobbies = {}
player_positions = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    player_id = request.sid
    emit('player_id', {'player_id': player_id})

@socketio.on('join_lobby')
def handle_join_lobby(data):
    player_id = data['player_id']
    lobby_id = data['lobby_id']

    # Join the room corresponding to the lobby
    join_room(lobby_id)

    # Add the player to the lobby
    lobbies.setdefault(lobby_id, []).append(player_id)

    # Initialize player position
    player_positions.setdefault(lobby_id, {}).setdefault(player_id, {'x': 0, 'y': 0})

    # Broadcast the updated player list and initial game scenario to all clients in the lobby
    emit('lobby_players', {'players': lobbies[lobby_id]}, room=lobby_id)
    emit('game_command', {'player_id': 'system', 'command': get_description_for_position(lobby_id)}, room=lobby_id)

@socketio.on('leave_lobby')
def handle_leave_lobby(data):
    player_id = data['player_id']
    lobby_id = data['lobby_id']

    # Leave the room corresponding to the lobby
    leave_room(lobby_id)

    # Remove the player from the lobby and player positions
    lobbies.get(lobby_id, []).remove(player_id)
    player_positions.get(lobby_id, {}).pop(player_id, None)

    # Broadcast the updated player list to all clients in the lobby
    emit('lobby_players', {'players': lobbies.get(lobby_id, [])}, room=lobby_id)


@socketio.on('chat_message')
def handle_chat_message(data):
    player_id = data['player_id']
    lobby_id = data['lobby_id']
    message = data['message']

    # Validate the message
    if lobby_id in lobbies.get(lobby_id, []) and player_id in lobbies[lobby_id]:
        emit('chat_message', {'player_id': player_id, 'message': message}, room=lobby_id)


@socketio.on('command')
def handle_command(data):
    player_id = data['player_id']
    lobby_id = data['lobby_id']
    command = data['command']

    if command.lower() == '/generate_maze':
        # Generate D&D maze using OpenAI API
        maze_scenario = generate_dnd_maze()

        # Reset player positions
        player_positions[lobby_id] = {player_id: {'x': 0, 'y': 0} for player_id in lobbies.get(lobby_id, [])}

        # Broadcast the generated maze scenario and initial player positions to all clients in the lobby
        emit('game_command', {'player_id': 'system', 'command': 'D&D Maze: ' + maze_scenario}, room=lobby_id)
        emit('game_command', {'player_id': 'system', 'command': get_description_for_position(lobby_id)}, room=lobby_id)
    else:
        # Handle other commands using the play function
        scenario_result = play(command)

        # Broadcast the resulting scenario to all clients in the lobby
        emit('game_command', {'player_id': 'system', 'command': 'D&D Scenario: ' + scenario_result}, room=lobby_id)

        # Emit the result back to the client who sent the command
        emit('play_command_result', {'player_id': player_id, 'result': scenario_result})
        print(f"Sent play_command_result to {player_id}: {scenario_result}")


def update_player_position(command, lobby_id, player_id):
    # Update player position based on movement commands
    x, y = player_positions[lobby_id][player_id]['x'], player_positions[lobby_id][player_id]['y']
    if command == 'w':
        y -= 1
    elif command == 'a':
        x -= 1
    elif command == 's':
        y += 1
    elif command == 'd':
        x += 1

    # Update player position in the dictionary
    player_positions[lobby_id][player_id]['x'], player_positions[lobby_id][player_id]['y'] = x, y
def get_description_for_position(lobby_id):
    # Example: Get description based on player positions
    player_positions_str = ', '.join([f'{player_id}: ({pos["x"]}, {pos["y"]})' for player_id, pos in player_positions[lobby_id].items()])
    return f'Player positions: {player_positions_str}'


if __name__ == '__main__':
    socketio.run(app, debug=True)
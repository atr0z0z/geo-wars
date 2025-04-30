from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import random
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

rooms = {}

with open('questions.json', encoding='utf-8') as f:
    QUESTIONS = json.load(f)
print(f"Загружено вопросов: {len(QUESTIONS)}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all_questions')
def all_q():
    return jsonify(QUESTIONS)


@app.route('/question')
def get_question():
    question = random.choice(QUESTIONS)
    return jsonify(question)

@socketio.on('create_room')
def handle_create(data):
    room_id = str(uuid.uuid4())[:6].upper()
    username = data['username']
    color = data['color']

    rooms[room_id] = {
        'players': [{ 'name': username, 'color': color, 'sid': request.sid }],
        'map': {},  # например: {'CA': {'owner': 'Alice', 'color': '#ff0000'}}
        'turn_index': 0
    }

    join_room(room_id)
    emit('room_created', {'room_id': room_id, 'players': rooms[room_id]['players']}, room=request.sid)


@socketio.on('join_room')
def handle_join(data):
    room_id = data['room_id']
    username = data['username']
    color = data['color']

    if room_id in rooms:
        rooms[room_id]['players'].append({ 'name': username, 'color': color, 'sid': request.sid })
        join_room(room_id)
        emit('player_joined', { 'players': rooms[room_id]['players'] }, room=room_id)
    else:
        emit('error', {'message': 'Комната не найдена'})


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)


from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import json
import random
import uuid
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Загрузка вопросов
with open('questions.json', encoding='utf-8') as f:
    QUESTIONS = json.load(f)
print(f"Загружено вопросов: {len(QUESTIONS)}")

# Комнаты: room_id -> {players, map, turn_index, attack}
rooms = {}

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
        'map': {},
        'turn_index': 0,
        'attack': None
    }

    join_room(room_id)

    # Назначить стартовый штат
    start_states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado"]
    rooms[room_id]['map'][start_states[0]] = {
        'owner': username,
        'color': color
    }

    # 💥 Вот эта строка обязательна:
    emit('room_created', {
        'room_id': room_id,
        'players': rooms[room_id]['players'],
        'map': rooms[room_id]['map']
    }, room=request.sid)


    # Назначить стартовый штат
    start_states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado"]
    rooms[room_id]['map'][start_states[0]] = {
        'owner': username,
        'color': color
    }

    emit('room_created', {'room_id': room_id, 'players': rooms[room_id]['players']}, room=request.sid)

@socketio.on('join_room')
def handle_join(data):
    room_id = data['room_id']
    username = data['username']
    color = data['color']

    if room_id not in rooms:
        emit('error', {'message': 'Комната не найдена'})
        return

    room = rooms[room_id]
    room['players'].append({ 'name': username, 'color': color, 'sid': request.sid })
    join_room(room_id)

    # Назначить стартовый штат
    start_states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado"]
    if len(room['players']) < len(start_states):
        state = start_states[len(room['players']) - 1]
        room['map'][state] = {
            'owner': username,
            'color': color
        }

    emit('player_joined', { 'players': room['players'], 'map': room['map'], 'turn': room['players'][room['turn_index']]['name'] }, room=room_id)

@socketio.on('start_attack')
def handle_attack(data):
    room_id = data['room_id']
    state = data['state']
    sid = request.sid

    room = rooms.get(room_id)
    if not room:
        emit('error', {'msg': 'Комната не найдена'})
        return

    current_player = room['players'][room['turn_index']]
    if current_player['sid'] != sid:
        emit('error', {'msg': 'Сейчас не ваш ход'})
        return

    if state in room['map'] and room['map'][state]['owner'] == current_player['name']:
        emit('error', {'msg': 'Вы уже владеете этим штатом'})
        return

    question = random.choice(QUESTIONS)
    room['attack'] = {
        'state': state,
        'question': question,
        'answers': {}
    }

    emit('attack_started', {
        'state': state,
        'question': question['question'],
        'options': question['options']
    }, room=room_id)

@socketio.on('answer')
def handle_answer(data):
    room_id = data['room_id']
    answer = data['answer']
    sid = request.sid

    room = rooms.get(room_id)
    if not room or not room['attack']:
        return

    q = room['attack']['question']
    correct = q['answer'].lower().strip() == answer.lower().strip()

    if sid not in room['attack']['answers']:
        room['attack']['answers'][sid] = 0

    if correct:
        room['attack']['answers'][sid] += 1

    if len(room['attack']['answers']) >= len(room['players']):
        finish_attack(room_id)

def finish_attack(room_id):
    room = rooms[room_id]
    attack = room['attack']
    state = attack['state']
    answers = attack['answers']

    if not answers:
        winner_sid = None
    else:
        sorted_scores = sorted(answers.items(), key=lambda x: x[1], reverse=True)
        top = sorted_scores[0][1]
        top_players = [sid for sid, score in sorted_scores if score == top]
        winner_sid = top_players[0] if len(top_players) == 1 else None

    if winner_sid:
        for p in room['players']:
            if p['sid'] == winner_sid:
                room['map'][state] = { 'owner': p['name'], 'color': p['color'] }
                break

    room['turn_index'] = (room['turn_index'] + 1) % len(room['players'])
    room['attack'] = None

    emit('game_state', {
        'map': room['map'],
        'turn': room['players'][room['turn_index']]['name']
    }, room=room_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
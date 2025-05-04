from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import random
import uuid
import os

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
        'map': {},  # пример: {'CA': {'owner': 'Alice', 'color': '#ff0000'}}
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

players = {}
game_state = {
    "players": {},
    "currentTurn": None,
    "claimedStates": {}
}
ongoing_attack = None

available_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFA500", "#800080"]
available_states = [  # Пример: первые несколько штатов
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado"
]

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    print(f"Игрок подключился: {sid}")

    if not available_colors or not available_states:
        emit("player_data", {"error": "Нет мест для новых игроков"})
        return

    color = available_colors.pop(0)
    state = available_states.pop(0)

    players[sid] = {
        "color": color,
        "startState": state,
        "score": 0
    }

    game_state["players"][sid] = {
        "color": color,
        "startState": state
    }
    game_state["claimedStates"][state] = sid

    if game_state["currentTurn"] is None:
        game_state["currentTurn"] = sid

    emit("player_data", {"playerId": sid, "color": color})
    send_game_state()

@socketio.on('start_attack')
def handle_attack(data):
    global ongoing_attack
    sid = request.sid
    state = data["state"]

    if game_state["currentTurn"] != sid:
        emit("error", {"msg": "Сейчас не ваш ход"})
        return

    if state in game_state["claimedStates"] and game_state["claimedStates"][state] == sid:
        emit("error", {"msg": "Вы уже владеете этим штатом"})
        return

    question = random.choice(QUESTIONS)
    ongoing_attack = {
        "state": state,
        "question": question,
        "answers": {}
    }

    socketio.emit("attack_started", {
        "state": state,
        "question": question["question"],
        "options": question["options"]
    })

@socketio.on('answer')
def handle_answer(data):
    global ongoing_attack
    sid = request.sid
    answer = data["answer"]

    if not ongoing_attack:
        return

    q = ongoing_attack["question"]
    correct = q["answer"].lower().strip() == answer.lower().strip()

    if sid not in ongoing_attack["answers"]:
        ongoing_attack["answers"][sid] = 0

    if correct:
        ongoing_attack["answers"][sid] += 1

    # Все игроки ответили — завершить раунд
    if len(ongoing_attack["answers"]) >= len(players):
        finish_attack()

def finish_attack():
    global ongoing_attack

    state = ongoing_attack["state"]
    answers = ongoing_attack["answers"]

    if not answers:
        winner_sid = None
    else:
        sorted_scores = sorted(answers.items(), key=lambda x: x[1], reverse=True)
        top = sorted_scores[0][1]
        top_players = [sid for sid, score in sorted_scores if score == top]

        if len(top_players) == 1:
            winner_sid = top_players[0]
        else:
            winner_sid = None  # ничья

    if winner_sid:
        game_state["claimedStates"][state] = winner_sid
        print(f"Штат {state} захвачен игроком {winner_sid}")
    else:
        print(f"Ничья за штат {state}")

    # передаём ход следующему игроку
    turn_order = list(players.keys())
    if game_state["currentTurn"] in turn_order:
        idx = turn_order.index(game_state["currentTurn"])
        idx = (idx + 1) % len(turn_order)
        game_state["currentTurn"] = turn_order[idx]

    ongoing_attack = None
    send_game_state()


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"Игрок отключился: {sid}")

    if sid in players:
        available_colors.insert(0, players[sid]["color"])
        available_states.insert(0, players[sid]["startState"])
        del players[sid]
        del game_state["players"][sid]

        # Освобождаем захваченные штаты
        to_remove = [s for s, owner in game_state["claimedStates"].items() if owner == sid]
        for s in to_remove:
            del game_state["claimedStates"][s]

        if game_state["currentTurn"] == sid:
            if players:
                game_state["currentTurn"] = next(iter(players.keys()))
            else:
                game_state["currentTurn"] = None

        send_game_state()

def send_game_state():
    socketio.emit("game_state", game_state)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)



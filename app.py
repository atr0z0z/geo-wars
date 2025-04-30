from flask import Flask, render_template, request, jsonify
import json
import random

app = Flask(__name__)

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

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

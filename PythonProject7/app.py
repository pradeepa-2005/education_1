from flask import Flask, render_template, request, jsonify
from translator1 import translate_text
from app1 import get_recommendations
from pyngrok import ngrok
import json
import joblib
import sqlite3

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    try:
        translated = translate_text(data['text'], data['src'], data['dest'])
        return jsonify({'translated': translated})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/recommendations', methods=['GET'])
def recommend():
    try:
        data = get_recommendations()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_quiz', methods=['GET'])
def get_quiz():
    with open('quiz_questions.json', 'r') as f:
        questions = json.load(f)
    return jsonify(questions)

@app.route('/submit_activity', methods=['POST'])
def submit_activity():
    data = request.json
    conn = sqlite3.connect('education.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            activity_type TEXT,
            topic TEXT,
            score REAL,
            time_spent INTEGER,
            attempts INTEGER,
            correct_attempts INTEGER,
            difficulty TEXT,
            date TEXT
        )
    ''')

    cursor.execute('''
        INSERT INTO student_activity 
        (student_id, activity_type, topic, score, time_spent, attempts, correct_attempts, difficulty, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['student_id'], data['activity_type'], data['topic'], data['score'],
         data['time_spent'], data['attempts'], data['correct_attempts'], data['difficulty'], data['date'])
    )

    conn.commit()
    conn.close()
    return {'status': 'success'}

@app.route('/predict_gap', methods=['POST'])
def predict_gap():
    data = request.json
    try:
        model = joblib.load('learning_gap_model.pkl')
        encoder = joblib.load('difficulty_encoder.pkl')

        difficulty_encoded = encoder.transform([data['difficulty']])[0]

        features = [[
            data['score'],
            data['time_spent'],
            data['attempts'],
            data['correct_attempts'],
            difficulty_encoded
        ]]

        prediction = model.predict(features)[0]

        topic = data['topic'].strip().lower()

        interventions = {
            'fractions': "📘 Review fractions with this [video lesson](https://www.khanacademy.org/math/arithmetic/fraction-arithmetic)",
            'algebra': "🧠 Practice Algebra basics here: [Algebra I Practice](https://www.khanacademy.org/math/algebra)",
            'geometry': "📐 Try this: [Geometry Basics](https://www.khanacademy.org/math/geometry)"
        }

        intervention = interventions.get(topic, "📚 Please review this topic with your teacher or tutor.") \
            if prediction == 1 else "✅ No gap detected. Keep going!"

        return jsonify({
            'learning_gap': bool(prediction),
            'intervention': intervention
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = 5000
    public_url = ngrok.connect(port)
    print(f"🚀 Public URL: {public_url}")
    app.run(port=port)

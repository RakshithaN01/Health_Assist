from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import librosa
import numpy as np
import os
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
app.secret_key = '12345'

# Upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid credentials. Try again."
    return render_template('login.html')

@app.route('/clinic_news')
def clinic_news():
    return render_template('clinic_news.html')

@app.route('/cardiac-care')
def cardiac_care():
    return render_template('heart.html')

def analyze_heartbeat(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        bpm = int(tempo[0]) if len(tempo) > 0 else 0

        if 60 <= bpm <= 80:
            category = "Excellent"
            color = "green"
        elif 81 <= bpm <= 100:
            category = "Good"
            color = "orange"
        else:
            category = "Average"
            color = "red"

        return bpm, category, color
    except Exception as e:
        traceback.print_exc()
        raise

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['audio']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        bpm, category, color = analyze_heartbeat(filepath)
        os.remove(filepath)

        # Get user input from the form
        name = request.form.get('name', '')
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        symptoms = request.form.get('symptoms', '')

        report = {
            'bpm': bpm,
            'category': category,
            'color': color,
            'summary': get_summary(category),
            'rhythm': 'Regular',
            'notes': 'No abnormalities detected.',
            'recommendations': [
                "Maintain a healthy diet and regular exercise.",
                "Avoid stress and get regular checkups.",
                "If symptoms worsen, seek medical attention immediately."
            ],
            'name': name,
            'age': age,
            'gender': gender,
            'symptoms': symptoms
        }

        return jsonify(report)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Failed to analyze audio'}),500

@app.route('/report')
def report():
    report_data = request.args.to_dict()
    report_data['recommendations'] = [
        "Maintain a healthy diet and regular exercise.",
        "Avoid stress and get regular checkups.",
        "If symptoms worsen, seek medical attention immediately."
    ]
    return render_template('report.html', report=report_data)

def get_summary(category):
    if category == "Excellent":
        return "Your heart rate is within a healthy range. Keep up the good work!"
    elif category == "Good":
        return "Your heart rate is a bit high, but still okay. Consider regular monitoring."
    else:
        return "Your heart rate is outside the normal range. Please consult a doctor."


if __name__ == '__main__':
    app.run(debug=True)


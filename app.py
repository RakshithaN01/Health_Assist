from flask import Flask,jsonify, render_template, request, redirect, url_for,session
import librosa
import numpy as np
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key='12345'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form data here
        username = request.form['username']
        password = request.form['password']
        # Example check (You can connect to DB here)
        if username == 'admin' and password == 'admin123':
            session['user']=username
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

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def analyze_heartbeat(file_path):
    # Load audio file
    y, sr = librosa.load(file_path, sr=None)
    
    # Extract onset envelope and compute tempo
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)

    bpm = int(tempo[0]) if len(tempo) > 0 else 0  # Safe check

    # Classify heart rate
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

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        bpm, category, color = analyze_heartbeat(filepath)
        os.remove(filepath)  # Clean up
        return jsonify({
            'bpm': bpm,
            'category': category,
            'color': color
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Failed to analyze audio'}), 500


if __name__ == '__main__':
    app.run(debug=True)
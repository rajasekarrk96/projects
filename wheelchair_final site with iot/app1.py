from flask import Flask, Response, render_template,jsonify
import cv2
import requests
import numpy as np
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone
import os
from functools import wraps
from ultralytics import YOLO
import time

app = Flask(__name__)

mode1 = "0"

# Load YOLOv8n model once
model = YOLO("yolov8n.pt")


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
global user_id
user_id=None
ESP32_IP = "http://192.168.99.43"
ESPCAM = "http://192.168.99.103"
ESP_iot = "http://192.168.99.166/buzz"

# Separate function to control the buzzer and light on the ESP8266
def trigger_buzzer(buzz_state):
    try:
        # Send the request to ESP with buzzs=0 or 1
        response = requests.post(f"{ESP_iot}?buzzs={buzz_state}", timeout=3)
        if response.status_code == 200:
            print(f"Buzzer and light set to: {buzz_state}")
        else:
            print(f"Failed to trigger buzzer. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error contacting ESP: {e}")

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'doctor', 'patient', 'caretaker'
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    patients = db.relationship('Patient', backref='user', lazy=True)
    caretakers = db.relationship('Caretaker', backref='user', lazy=True)
    doctor = db.relationship('Doctor', backref='user', uselist=False, lazy=True)
    created_users = db.relationship('User', backref=db.backref('creator', remote_side=[id]), lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialty = db.Column(db.String(100), nullable=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretaker.id'), nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Caretaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patients = db.relationship('Patient', backref='caretaker', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IoTData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    spo2 = db.Column(db.Float, nullable=True)
    heart_rate = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    patient = db.relationship('Patient', backref='iot_data', lazy=True)


# Create database tables
with app.app_context():
    db.create_all()

# Decorators for role-based access control
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'doctor':
            flash('You need to be a doctor to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global user_id
        if 'user_id' not in session or session.get('role') != 'patient':
            user_id=session.get('user_id')
            flash('You need to be a patient to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def caretaker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'caretaker':
            flash('You need to be a caretaker to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/caretaker/key')
@login_required
@caretaker_required
def key():
    return render_template('caretaker/key.html')

@app.route('/img')
def img():
    return render_template("images.html",img1=ESPCAM)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and (user.password == password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif role == 'patient':
        return redirect(url_for('patient_dashboard'))
    elif role == 'caretaker':
        return redirect(url_for('caretaker_dashboard'))
    return redirect(url_for('index'))

@app.route('/doctor/dashboard')
@login_required
@doctor_required
def doctor_dashboard():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()

    patients = Patient.query.filter_by(doctor_id=doctor.id).all()
    
    # Fetch the latest IoT data for each patient
    for patient in patients:
        patient.last_iot_data = (
            IoTData.query.filter_by(patient_id=patient.id)
            .order_by(IoTData.timestamp.desc())  # Get the latest data
            .first()
        )

    caretakers = Caretaker.query.filter_by(doctor_id=doctor.id).all()
    pending_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='pending').all()

    return render_template(
        'doctor/dashboard.html', 
        doctor=doctor, 
        patients=patients, 
        caretakers=caretakers, 
        pending_appointments=pending_appointments,
        User=User, 
        Caretaker=Caretaker, 
        Patient=Patient
    )

@app.route('/patient/dashboard')
@login_required
@patient_required
def patient_dashboard():
    global user_id
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('home'))
    # Fetch doctor details
    doctor = Doctor.query.get(patient.doctor_id)
    doctor_user = User.query.get(doctor.user_id) if doctor else None
    # Fetch caretaker details
    caretaker_user = User.query.get(patient.caretaker_id) if patient.caretaker_id else None
    # Fetch appointments
    appointments = Appointment.query.filter(
    Appointment.patient_id == patient.id, 
    Appointment.status != "cancelled"
    ).all()
    return render_template(
        'patient/dashboard.html',
        patient=patient,
        appointments=appointments,
        doctor_user=doctor_user,  # Pass doctor user object
        caretaker_user=caretaker_user,User=User,
        Doctor=Doctor,  # Pass Doctor model
        Caretaker=Caretaker,Appointment=Appointment)

@app.route('/caretaker/dashboard')
@login_required
@caretaker_required
def caretaker_dashboard():
    user_id = session.get('user_id')
    print(user_id)
    # Get all patients assigned to the caretaker
    patients = Patient.query.filter_by(caretaker_id=user_id).all()
    print(patients)
    now = datetime.utcnow()
    appointment_data = []
    loc=[]
    for patient in patients:
        latest_data = IoTData.query.filter_by(patient_id=patient.id).order_by(IoTData.timestamp.desc()).first()
        if latest_data:
            lat = latest_data.latitude
            lon = latest_data.longitude
        else:
            lat = None
            lon = None
        appointments = Appointment.query.filter(Appointment.patient_id == patient.id,Appointment.status != "cancelled").all()
        for appointment in appointments:
            appointment_time = appointment.date_time
            if appointment_time.tzinfo is not None:
                appointment_time = appointment_time.replace(tzinfo=None)
            if appointment_time.date() == now.date():
                status = "Today"
            elif appointment_time > now:
                status = "Upcoming"
            else:
                status = "Past"
            appointment_data.append({
                "patient_name": User.query.get(patient.user_id).username,
                "date_time": appointment_time.strftime('%d %b %Y, %H:%M'),
                "status": status
            })
        loc.append({
                "patient_name": User.query.get(patient.user_id).username,
                "lat":lat,
                "lon":lon
            })

    return render_template(
        'caretaker/dashboard.html', 
        patients=patients, 
        appointment_data=appointment_data,User=User,
        Doctor=Doctor,
        Caretaker=Caretaker,Appointment=Appointment,
        locss=loc
    )

@app.route('/doctor/create_accounts', methods=['GET', 'POST'])
@login_required
@doctor_required
def create_accounts():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create_patient_caretaker':
            patient_username = request.form.get('patient_username')
            patient_email = request.form.get('patient_email')
            patient_password = request.form.get('patient_password')
            caretaker_username = request.form.get('caretaker_username')
            caretaker_email = request.form.get('caretaker_email')
            caretaker_password = request.form.get('caretaker_password')
            medical_history = request.form.get('medical_history')
            user_id = session.get('user_id')
            doctor = Doctor.query.filter_by(user_id=user_id).first()
            patient_user = User(
                username=patient_username,
                email=patient_email,
                password=patient_password,
                role='patient',
                created_by=user_id
            )
            db.session.add(patient_user)
            db.session.flush()
            caretaker_user = User(
                username=caretaker_username,
                email=caretaker_email,
                password=caretaker_password,
                role='caretaker',
                created_by=user_id
            )
            db.session.add(caretaker_user)
            db.session.flush()
            caretaker = Caretaker(
                user_id=caretaker_user.id,
                doctor_id=doctor.id
            )
            db.session.add(caretaker)
            db.session.flush()
            patient = Patient(
                user_id=patient_user.id,
                doctor_id=doctor.id,
                caretaker_id=caretaker_user.id,
                medical_history=medical_history
            )
            db.session.add(patient)
            db.session.commit()
            flash('Patient and Caretaker accounts created successfully!', 'success')
            return redirect(url_for('doctor_dashboard'))
    return render_template('doctor/create_accounts.html')

@app.route('/patient/book_appointment', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        date_str = request.form.get('appointment_date')
        time_str = request.form.get('appointment_time')
        date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=patient.doctor_id,
            date_time=date_time,
            status='pending'
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment request submitted successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
    return render_template('patient/book_appointment.html',User=User,Caretaker=Caretaker,Patient=Patient,Appointment=Appointment)

@app.route('/doctor/manage_appointments')
@login_required
@doctor_required
def manage_appointments():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for('home'))
    # Fetch pending and accepted appointments
    pending_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status="pending").all()
    accepted_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status="accepted").all()
    # Fetch patient and caretaker details before rendering template
    appointment_data = []
    for appointment in pending_appointments + accepted_appointments:
        patient = Patient.query.get(appointment.patient_id)
        patient_user = User.query.get(patient.user_id) if patient else None
        # Fetch caretaker directly from User table using caretaker_id from Patient table
        caretaker_user = User.query.get(patient.caretaker_id) if patient and patient.caretaker_id else None
        appointment_data.append({
            "appointment": appointment,
            "patient": patient_user,
            "caretaker": caretaker_user
        })
    return render_template(
        'doctor/manage_appointments.html',
        appointment_data=appointment_data,
        pending_appointments=pending_appointments,
        accepted_appointments=accepted_appointments,User=User,Caretaker=Caretaker,Patient=Patient,Appointment=Appointment
    )

@app.route('/doctor/appointment/<int:appointment_id>/<action>')
@login_required
@doctor_required
def handle_appointment(appointment_id, action):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if action == 'accept':
        appointment.status = 'accepted'
        flash('Appointment accepted.', 'success')
    elif action == 'reject':
        appointment.status = 'cancelled'
        flash('Appointment cancelled.', 'info')
    
    db.session.commit()
    return redirect(url_for('manage_appointments'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        specialty = request.form.get('specialty')  # Only for doctors

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please use a different one.', 'error')
            return redirect(url_for('signup'))
        
        # Create a new doctor user
        new_user = User(username=username, email=email, password=password, role='doctor')
        db.session.add(new_user)
        db.session.flush()  # Get new_user.id before committing

        # Create doctor profile
        new_doctor = Doctor(user_id=new_user.id, specialty=specialty)
        db.session.add(new_doctor)
        
        # Commit to the database
        db.session.commit()

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/update', methods=['POST'])
def save_iot_data():
    global user_id   
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Extracting data safely from the payload
        spo2 = data.get("spo2")
        heart_rate = data.get("heart_rate")
        latitude = data.get("gps_lat")  # Ensure the key matches with the Arduino payload
        longitude = data.get("gps_long")  # Ensure the key matches with the Arduino payload
        
        # Validation: Ensure required fields are present
        if spo2 is None or heart_rate is None:
            return jsonify({"error": "Missing required fields: spo2 or heart_rate"}), 400
        
        # Save data to the database
        new_entry = IoTData(
            patient_id=patient.id,
            spo2=spo2,
            heart_rate=heart_rate,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({"message": "IoT data saved successfully"}), 201
    except Exception as e:
        db.session.rollback()  # Rollback in case of failure
        print(f"Error saving IoT data: {e}")  # Log error for debugging
        return jsonify({"error": "Internal Server Error"}), 500

    
@app.route('/patient/iot_data')
@login_required
@patient_required
def patient_iot_data():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('patient_dashboard'))
    iot_data = IoTData.query.filter_by(patient_id=patient.id).order_by(IoTData.timestamp.desc()).all()
    
    return render_template('patient/iot_data.html', iot_data=iot_data)

# Control movement
@app.route('/move/<direction>', methods=['GET'])
def move(direction):
    if direction in ["forward", "backward", "left", "right", "stop"]:
        url = f"{ESP32_IP}/move_{direction}"
        response = requests.get(url,timeout=3)
        return jsonify({"message": f"Moved {direction}", "response": response.text})
    return jsonify({"error": "Invalid direction"}), 400

def move(direction):
    if direction in ["forward", "backward", "left", "right", "stop"]:
        try:
            requests.get(f"{ESP32_IP}/move_{direction}", timeout=1)
        except Exception as e:
            print(f"Failed to move {direction}: {e}")

def predict_yolo(frame):
    results = model.predict(frame, imgsz=640, conf=0.5)
    names = results[0].names
    classes = results[0].boxes.cls.cpu().numpy()
    
    detected_labels = [names[int(cls)] for cls in classes]
    print("Detected:", detected_labels)

    if "person" in detected_labels:
        return "person"
    elif len(detected_labels) > 0:
        return "object"
    else:
        return "none"

def process_frames_from_esp32():
    global mode1
    print("Started YOLO processing loop...")
    while mode1 == "2":
        try:
            response = requests.get(f"{ESPCAM}/cam-hi.jpg", timeout=2)
            if response.status_code != 200 :
                print("Invalid image data")
                continue

            img_array = np.frombuffer(response.content, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is None:
                print("Failed to decode image")
                continue

            result = predict_yolo(frame)

            if result == "person":
                trigger_buzzer(1)
                move("stop")
            elif result == "object":
                trigger_buzzer(1)
                move("backward")
            else:
                trigger_buzzer(0)
                move("forward")
            time.sleep(3)
        except Exception as e:
            print("Frame error:", e)

# Set Master Control Mode
@app.route('/set_mode', methods=['GET'])
def set_mode():
    global mode1
    mode = request.args.get("mode")
    
    if mode == "2":
        mode1 = "2"
        url = f"{ESP32_IP}/set_mode?mode=1"  # Inform ESP32 it's in camera processing mode
        try:
            requests.get(url)
            print("summa")
        except Exception as e:
            print("Error notifying ESP32:", e)

        # Start camera processing loop
        threading.Thread(target=process_frames_from_esp32).start()
        return jsonify({"message": "Camera YOLO mode started"})

    if mode in ["0", "1"]:
        mode1 = mode
        url = f"{ESP32_IP}/set_mode?mode={mode}"
        try:
            response = requests.get(url)
            return jsonify({"message": f"Mode set to {mode}", "response": response.text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid mode"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
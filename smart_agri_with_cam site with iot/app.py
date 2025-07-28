# Import required libraries
import time
import io
import base64
import threading
import sqlite3
import requests
import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response, jsonify, stream_with_context
from ultralytics import YOLO
from scipy.interpolate import griddata

# Configure matplotlib to use non-interactive backend
matplotlib.use('Agg')

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Store last detected label for tracking
last_detected_label = None

# List of animal classes YOLO should respond to
ANIMAL_CLASSES = ["bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"]

# URLs for ESP32 devices (camera and server)
ESP32_CAM_URL = "http://192.168.10.45/cam-mid.jpg"
ESP32_SERVER_URL = "http://192.168.10.55"

# Initialize Flask application
app = Flask(__name__)

import time
from twilio.rest import Client

# Twilio credentials and phone numbers
ACCOUNT_SID = ""
AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""
TO_PHONE_NUMBER = ""

# Initialize Twilio Client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Dictionary to store last sent time for each category
last_sent_times = {}

# Time limit in seconds (3 minutes)
TIME_LIMIT = 3 * 60

# Function to send SMS with time limit check
def send_sms(body, category):
    current_time = time.time()

    # Check if category was sent recently
    last_sent = last_sent_times.get(category, 0)
    if current_time - last_sent >= TIME_LIMIT:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        last_sent_times[category] = current_time
        print(f"Message sent for '{category}'! SID: {message.sid}")
    else:
        wait_time = int(TIME_LIMIT - (current_time - last_sent))
        print(f"Wait {wait_time} seconds before sending another '{category}' message.")



# Database configuration
DB_NAME = 'sensor_data.db'

# Function to create database table if not exists
def create_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            soil_moisture INTEGER,
                            water_level INTEGER,
                            temperature REAL)''')

# Function to save sensor data to the database
def save_data(soil_moisture, water_level, temperature):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO sensor_data (soil_moisture, water_level, temperature) VALUES (?, ?, ?)",
                     (soil_moisture, water_level, temperature))

# Function to fetch all sensor data from the database
def fetch_all_data():
    """Fetch sensor data from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT soil_moisture, water_level, temperature FROM sensor_data").fetchall()

# Function to activate scarecrow using ESP32
def activate_scarecrow():
    """Trigger scarecrow system via ESP32."""
    url = f"{ESP32_SERVER_URL}/video_feed"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("✅ Scarecrow activated!")
        else:
            print(f"⚠ Failed to activate scarecrow. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("🚨 Error:", e)

# Function to detect objects in a given image using YOLO
def detect_objects(image):
    """Run YOLO model and return detected animals with confidence."""
    results = model(image)
    detections = results[0].boxes.data  # Extract bounding box data
    CLASS_LABELS = model.names

    detected_animals = []

    if len(detections) > 0:
        for detection in detections:
            conf = float(detection[4]) * 100  # Convert to percentage
            label_index = int(detection[5])

            if 0 <= label_index < len(CLASS_LABELS):
                label = CLASS_LABELS[label_index]
                if label in ANIMAL_CLASSES:  # Filter only animals
                    detected_animals.append((label, conf))
                    send_sms(f"⚠️ Animal detected {label}", "animal")

    return detected_animals if detected_animals else [("Not Available", 0)]

# Initial pump status
previous_pump_status = None

def check_pump_status_and_notify(sensor_data):
    global previous_pump_status

    # Determine current status
    current_status = "Pump ON" if sensor_data['water_level'] > 2000 else "Pump OFF"

    # Send SMS only on transition from OFF → ON
    if previous_pump_status == "Pump OFF" and current_status == "Pump ON":
        send_sms("💧 Pump just turned ON due to high water level!", "pump")

    # Update previous status
    previous_pump_status = current_status

    return current_status


# Video streaming function with YOLO detection
def generate_frames():
    """Fetch video frames from ESP32-CAM, detect objects, and stream processed frames."""
    global last_detected_label
    while True:
        try:
            response = requests.get(ESP32_CAM_URL, timeout=5)
            if response.status_code == 200:
                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                # Run YOLO detection
                detected_animals = detect_objects(frame)

                if detected_animals and detected_animals[0][1] > 30:
                    label, confidence = detected_animals[0]
                    print(f"🦁 Detected: {label} ({confidence:.1f}%)")
                    if label:
                        activate_scarecrow()
                        send_sms(f"⚠ Alert: {label} detected with {confidence:.1f}% confidence!, location:11.9139419,79.8003295")

                    # Display label on the frame
                    cv2.putText(frame, f"{label} ({confidence:.1f}%)", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)

                # Yield frame as byte stream for video streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                print("⚠ Failed to retrieve frame from ESP32-CAM")

        except Exception as e:
            print("🚨 Error fetching frame:", e)
            continue

# Generate 3D plot of sensor data
def plot_3d_graph():
    """Generate a 3D plot based on available data."""
    data = fetch_all_data()
    if not data or len(data) < 3:
        print("Error: Insufficient data for plotting.")
        return None

    soil_moisture, water_level, temperature = zip(*data)
    x = np.array(soil_moisture)
    y = np.array(water_level)
    z = np.array(temperature)

    unique_points = np.unique(np.column_stack((x, y)), axis=0)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    if len(unique_points) < 3:
        ax.scatter(x, y, z, c='r', marker='o')
    else:
        grid_x, grid_y = np.meshgrid(
            np.linspace(min(x), max(x), 50),
            np.linspace(min(y), max(y), 50)
        )
        try:
            grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
            ax.plot_wireframe(grid_x, grid_y, grid_z, color='black')
        except Exception as e:
            print("Griddata interpolation failed:", e)
            ax.scatter(x, y, z, c='r', marker='o')
    ax.set_xlabel('Soil Moisture (%)')
    ax.set_ylabel('Water Level (%)')
    ax.set_zlabel('Temperature (°C)')
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png', dpi=300)
    img_bytes.seek(0)
    plt.close(fig)
    return base64.b64encode(img_bytes.getvalue()).decode('utf-8')

@app.route('/')
def home():
    img_data = plot_3d_graph()
    return render_template('home1.html', img_data=img_data) if img_data else "No data available."

@app.route('/video_feed')
def video_feed():
    return Response(stream_with_context(generate_frames()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sensor_status')
def sensor_status():
    """Serve real-time sensor data for the dashboard."""
    try:
        response = requests.get(f"{ESP32_SERVER_URL}/sensor_data")
        if response.status_code == 200:
            sensor_data = response.json()
            irrigation_status = "Pump ON" if sensor_data['soil_moisture'] < 2000 else "Pump OFF"
            pump_status = "Pump ON" if sensor_data['water_level'] > 2000 else "Pump OFF"
            check_pump_status_and_notify(pump_status)
            save_data(sensor_data['soil_moisture'], sensor_data['water_level'], sensor_data['temperature'])
            return jsonify({
                "soil_moisture": ((4095 - sensor_data['soil_moisture']) / 4095) * 100,
                "water_level": (sensor_data['water_level']/ 2448) * 100,
                "temperature": sensor_data['temperature'],
                "irrigation_status": irrigation_status,
                "pump": pump_status
            })
        return jsonify({"error": "Failed to retrieve data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    create_database()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
from flask import Flask, Response, render_template
import cv2
import requests
import numpy as np
from ultralytics import YOLO
import threading
import requests
import time

app = Flask(__name__, template_folder="templates")  # Set template folder

# Load YOLO model
model = YOLO("yolov8n.pt")

# ESP32-CAM image URLs (Update with correct IP addresses)
LEFT_CAM_URL = "http://192.168.52.91/cam-mid.jpg"
RIGHT_CAM_URL = "http://192.168.52.174/cam-mid.jpg"

ESP_IP="http://192.168.52.17"

# Vehicle labels YOLO can detect
VEHICLE_LABELS = ["car", "motorcycle", "bus", "truck"]

# Detection flags
left_detected = False
right_detected = False
lock = threading.Lock()

def send_signal(signal):
    url = f"{ESP_IP}/SIGNAL?data={signal}"
    try:
        response = requests.get(url, timeout=5)  # 5 seconds timeout
        if response.status_code == 200:
            print(f"✅ Signal {signal} Sent Successfully!")
            print("Response:", response.text)
        else:
            print(f"⚠️ Failed to Send Signal {signal}. HTTP Code:", response.status_code)
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error Sending Signal {signal}: {e}")

def process_frame(frame, side):
    """Runs YOLO inference on the frame and updates detection flags."""
    global left_detected, right_detected

    # Run YOLOv8 inference
    results = model.predict(frame, conf=0.5, verbose=False)
    detected_vehicle = False

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0].item())]
            if label in VEHICLE_LABELS:
                detected_vehicle = True
                with lock:
                    if side == "left" and not left_detected:
                        left_detected = True
                        right_detected = False
                        print(f"🚗 Vehicle ({label}) detected on LEFT! Alert RIGHT direction.")
                        send_signal(1)
                        time.sleep(5)

                    elif side == "right" and not right_detected:
                        right_detected = True
                        left_detected = False
                        print(f"🚗 Vehicle ({label}) detected on RIGHT! Alert LEFT direction.")
                        send_signal(2)
                        time.sleep(5)
    
    # Reset flags if no vehicle is detected
    if not detected_vehicle:
        send_signal(0)
        with lock:
            if side == "left":
                left_detected = False
            elif side == "right":
                right_detected = False
            else:
                left_detected=False
                right_detected=False

    return frame


def generate_frames(cam_url, side):
    """Fetches frames from ESP32-CAM, processes them, and streams via Flask."""
    while True:
        try:
            # Request frame from ESP32-CAM
            response = requests.get(cam_url, timeout=2)
            if response.status_code == 200:
                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                # Process frame with YOLO
                frame = process_frame(frame, side)

                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error fetching from {side} camera: {e}")
            continue


@app.route('/')
def index():
    """Serve the HTML file as the homepage."""
    return render_template("index.html")


@app.route('/left_feed')
def left_feed():
    return Response(generate_frames(LEFT_CAM_URL, "left"), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/right_feed')
def right_feed():
    return Response(generate_frames(RIGHT_CAM_URL, "right"), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
ESP32_IP = "http://192.168.75.96"  # Replace with your ESP32's IP
last_angle = -1

@app.route('/')
def index():
    return render_template('portfolio_solar.html')

@app.route('/original')
def original():
    return render_template('index1.html')

@app.route('/track_sun', methods=['POST'])
def track_sun():
    global last_angle
    data = request.json
    azimuth = data['azimuth']
    elevation = data['elevation']
    timestamp = data.get('timestamp')

    print(f"Azimuth: {azimuth}, Elevation: {elevation}, Time: {timestamp}")

    if elevation <= 0 or not (75 <= azimuth <= 105):
        if last_angle != 0:
            print("☁️ Not optimal — resetting to 0")
            last_angle = 0
            try:
                requests.get(f"{ESP32_IP}/set_servo?servo1=0", timeout=5)
            except:
                print("ESP32 not reachable")
        return jsonify({'status': 'Reset to 0'})

    norm = (azimuth - 75) / 30
    angle = int(norm * 180)

    if abs(angle - last_angle) < 5:
        print("🔄 No significant change")
        return jsonify({'status': 'No significant change'})

    last_angle = angle
    print(f"📡 Sending angle: {angle}")
    try:
        requests.get(f"{ESP32_IP}/set_servo?servo1={angle}", timeout=2)
    except:
        print("ESP32 not reachable")

    return jsonify({'status': 'Angle sent', 'angle': angle})

def send_signal_to_iot(signal):
    print(f"Sending signal to IoT device: {signal}")
    try:
        requests.get(f"{ESP32_IP}/set_relay?relay={signal}", timeout=5)
    except:
        print("ESP Not Reachable")

@app.route('/manual/<direction>', methods=['POST'])
def manual_control(direction):
    if direction.lower() == 'up':
        send_signal_to_iot(1)
        return jsonify({"status": "success", "signal": 1, "message": "Moved UP"})
    elif direction.lower() == 'down':
        send_signal_to_iot(0)
        return jsonify({"status": "success", "signal": 0, "message": "Moved DOWN"})
    else:
        return jsonify({"status": "error", "message": "Invalid direction"}), 400

@app.route('/clean', methods=['POST'])
def clean():
    try:
        requests.get(f"{ESP32_IP}/clean", timeout=5)
    except:
        print("ESP Not reachable")
    return jsonify({'status': 'Cleaning triggered'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

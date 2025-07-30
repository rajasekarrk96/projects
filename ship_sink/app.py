import json
import requests
from flask import Flask, request, jsonify, render_template
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Fast2SMS authorization key
fast2sms_api_key = "9cRIxJ7UJxjpRulbgYXhDer9OnzaXR8pb37AsSVlq59EWegtimpMPPJXc5d7"

# Shared variable for sensor data
sensor_data = {
    'temperature': 24.5,
    'pressure': 1013.2,
    'latitude': 19.0760,
    'longitude': 72.8777,
    'water_pressure': 101.3,
    'last_updated': time.time()
}

# Demo mode flag
demo_mode = True


# Route to serve the dashboard HTML page
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('index.html')


# Route to receive sensor data from Arduino
@app.route('/data', methods=['POST'])
def receive_data():
    global sensor_data, demo_mode
    if request.method == 'POST':
        # Get the JSON data from the POST request
        data = request.get_json()

        if data:
            try:
                # Separate and print each value
                sensor_data = {
                    'temperature': data.get('temperature'),
                    'pressure': data.get('pressure'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'water_pressure': data.get('Water_pressure'),
                    'last_updated': time.time(),
                    'demo_mode': False
                }
                
                # Disable demo mode when real data is received
                demo_mode = False

                print(f"Received Real Data: {sensor_data}")
                return "Data received!", 200
            except Exception as e:
                return f"Error processing data: {str(e)}", 500
        else:
            return "No data received", 400


# New route to serve sensor data as JSON for the HTML page
@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    global sensor_data
    
    # If in demo mode and no recent real data, generate realistic demo data
    if demo_mode and (not sensor_data.get('last_updated') or time.time() - sensor_data.get('last_updated', 0) > 30):
        import random
        
        # Generate realistic maritime sensor data
        sensor_data = {
            'temperature': round(random.uniform(20.0, 35.0), 1),
            'pressure': round(random.uniform(1000.0, 1025.0), 1),
            'latitude': round(random.uniform(18.5, 19.5), 6),
            'longitude': round(random.uniform(72.0, 73.0), 6),
            'water_pressure': round(random.uniform(95.0, 110.0), 1),
            'last_updated': time.time(),
            'demo_mode': True
        }
    
    return jsonify(sensor_data)


# Function to periodically send SMS with sensor data
def run_periodic_task(interval_minutes):
    while True:
        time.sleep(interval_minutes * 60)  # Convert minutes to seconds

        if sensor_data:
            message = (f"Sensor Data:\n"
                       f"Temperature: {sensor_data['temperature']} °C\n"
                       f"Pressure: {sensor_data['pressure']} mb\n"
                       f"https://www.google.com/maps/place/{sensor_data['latitude']},{sensor_data['longitude']}\n"
                       f"Water Pressure: {sensor_data['water_pressure']} mPa")

            send_sms(fast2sms_api_key, message, ["6383706926"])  # Replace with your numbers


# Function to send SMS using Fast2SMS
def send_sms(api_key, message, numbers):
    url = "https://www.fast2sms.com/dev/bulkV2"

    # Convert the numbers list into a comma-separated string
    number_string = ",".join(numbers)

    # Setup the query parameters
    query_params = {
        "authorization": api_key,
        "route": "q",
        "message": message,
        "numbers": number_string,
        "flash": "0"
    }

    headers = {
        "cache-control": "no-cache"
    }

    # Send the GET request
    response = requests.get(url, params=query_params, headers=headers)

    # Print the response from Fast2SMS
    if response.status_code == 200:
        print(f"SMS sent successfully: {response.json()}")
    else:
        print(f"Failed to send SMS: {response.status_code}, {response.text}")


# Start the periodic task in a background thread
if __name__ == '__main__':
    interval_minutes = 10  # Set the interval in minutes (you can change this)

    # Start a background thread for periodic task
    thread = threading.Thread(target=run_periodic_task, args=(interval_minutes,))
    thread.daemon = True  # Daemon thread will shut down with the main program
    thread.start()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0',port=5000)
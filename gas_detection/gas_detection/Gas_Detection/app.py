from flask import Flask, render_template, jsonify
import requests
from twilio.rest import Client

app = Flask(__name__)

# Global variable to track last gas detection state
last = False

ESP32_IP = "http://192.168.184.95/"  # Your ESP32 IP

def send_sms(message_body):
    # Replace with your Twilio credentials
    account_sid = ''
    auth_token = ''
    from_number = ''
    to_number = ''

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )

    print(f"SMS sent: SID {message.sid}")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def get_data():
    global last  # this is required to modify the global variable
    try:
        response = requests.get(ESP32_IP, timeout=5)
        data = response.json()

        if data['gas_detected'] and last != data['gas_detected']:
            send_sms("Alert: Gas Detected ⚠️")
        
        last = data['gas_detected']  # always update the last status

    except Exception as e:
        print(f"Error: {e}")
        data = {
            "gas_detected": False,
            "humidity": 0,
            "temperature": 0,
            "gas_value": 0
        }

    return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

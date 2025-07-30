# SafeGuard Pro - Industrial Gas Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![ESP32](https://img.shields.io/badge/ESP32-Compatible-red.svg)](https://www.espressif.com/en/products/socs/esp32)

## 🛡️ Overview

SafeGuard Pro is a comprehensive IoT-based gas detection and monitoring system designed for industrial environments. The system combines real-time sensor data collection, web-based monitoring, and automated safety protocols to ensure workplace safety.

## 🌟 Features

### Hardware Components
- **ESP32 Microcontroller** - Main processing unit with WiFi connectivity
- **MQ135 Gas Sensor** - Detects CO2, NH3, NOx, alcohol, and smoke
- **DHT11 Sensor** - Temperature and humidity monitoring
- **LED Indicators** - Visual status feedback (Green: Safe, Red: Danger)
- **Relay Control** - Automated safety shutoff mechanism

### Software Features
- **Real-time Monitoring** - Live data updates every 2 seconds
- **Web Dashboard** - Professional, responsive interface
- **SMS Alerts** - Twilio integration for emergency notifications
- **Data Visualization** - Interactive charts and status indicators
- **Safety Protocols** - Automated relay control for hazard mitigation
- **Mobile Responsive** - Optimized for all device sizes

## 🏗️ System Architecture

```
┌─────────────────┐    WiFi     ┌─────────────────┐    HTTP     ┌─────────────────┐
│                 │ ◄────────── │                 │ ◄────────── │                 │
│   ESP32 + MQ135 │             │  Flask Web App  │             │  Web Dashboard  │
│   + DHT11       │ ────────────► │                 │ ────────────► │                 │
│                 │    JSON      │                 │    HTML     │                 │
└─────────────────┘             └─────────────────┘             └─────────────────┘
                                          │
                                          │ SMS API
                                          ▼
                                ┌─────────────────┐
                                │                 │
                                │  Twilio SMS     │
                                │  Service        │
                                │                 │
                                └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Arduino IDE
- ESP32 development board
- MQ135 gas sensor
- DHT11 temperature/humidity sensor

### Hardware Setup
1. Connect MQ135 sensor to GPIO34 (analog input)
2. Connect DHT11 sensor to GPIO4
3. Connect LEDs to GPIO15 (Green) and GPIO17 (Red)
4. Connect relay to GPIO5
5. Power the ESP32 via USB or external supply

### Software Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gas_detection
   ```

2. **Install Python dependencies**
   ```bash
   cd Gas_Detection
   pip install -r requirements.txt
   ```

3. **Configure ESP32**
   - Open `gas_detection.ino` in Arduino IDE
   - Update WiFi credentials in the code
   - Upload to ESP32 board

4. **Configure Flask App**
   - Update ESP32 IP address in `app.py`
   - Configure Twilio credentials (use environment variables)
   - Set recipient phone number

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   - Open browser and navigate to `http://localhost:5000`
   - Monitor real-time gas levels and environmental data

## 📊 Dashboard Features

### Main Status Display
- **Environment Status** - Large, prominent safety indicator
- **Real-time Alerts** - Emergency banner for critical situations
- **System Health** - Connection status and uptime tracking

### Metrics Grid
- **Temperature Monitoring** - Real-time temperature readings
- **Humidity Tracking** - Environmental humidity levels
- **Gas Level Detection** - PPM readings with safety thresholds

### System Information
- **Device Status** - Online/offline indicator
- **Sensor Details** - Hardware specifications
- **Safety Thresholds** - Configurable alert levels
- **Alert Systems** - SMS and visual notification status

## 🔧 Configuration

### Gas Detection Threshold
```cpp
// In gas_detection.ino
int gas_threshold = 800; // Adjust based on your environment
```

### SMS Configuration
```python
# In app.py - Use environment variables in production
account_sid = 'your_twilio_account_sid'
auth_token = 'your_twilio_auth_token'
from_number = 'your_twilio_phone_number'
to_number = 'recipient_phone_number'
```

## 🛠️ Technical Specifications

| Component | Specification |
|-----------|---------------|
| Microcontroller | ESP32 (240MHz dual-core) |
| Gas Sensor | MQ135 (CO2, NH3, NOx detection) |
| Temperature Sensor | DHT11 (±2°C accuracy) |
| Humidity Sensor | DHT11 (±5% RH accuracy) |
| Communication | WiFi 802.11 b/g/n |
| Power Supply | 5V DC via USB or external |
| Operating Range | -10°C to +50°C |

## 📱 Mobile Support

The dashboard is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🔒 Security Considerations

- Use environment variables for sensitive credentials
- Implement HTTPS in production environments
- Consider VPN access for remote monitoring
- Regular security updates for all components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Developed as a comprehensive IoT solution demonstrating:
- Embedded systems programming
- Web application development
- Real-time data processing
- Industrial safety protocols
- Modern UI/UX design

## 🆘 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

---

**SafeGuard Pro** - Protecting lives through intelligent monitoring technology.

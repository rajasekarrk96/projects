# 🚢 MarineSafe Pro - Maritime Safety Monitoring System

A professional IoT-based maritime safety monitoring system with real-time sensor data collection, emergency alerts, and modern web dashboard.

## 🌟 Features

- **Real-time Monitoring**: Live sensor data from temperature, pressure, GPS, and water pressure sensors
- **Emergency Alerts**: Automatic SMS notifications with GPS coordinates when thresholds are exceeded
- **Professional Dashboard**: Modern, responsive web interface with real-time data visualization
- **Demo Mode**: Realistic data simulation for demonstration purposes
- **Error Handling**: Graceful fallback mechanisms and connection status monitoring
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices

## 🏗️ Architecture

```
Arduino Sensors → ESP8266 WiFi → Flask API → Web Dashboard
                                     ↓
                              SMS Alert System
```

## 🛠️ Technology Stack

- **Backend**: Python Flask, Fast2SMS API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Hardware**: ESP8266, DHT11, BMP180, GPS Module, Analog Pressure Sensor
- **Libraries**: TinyGPS++, SFE_BMP180, DHT, ESP8266WiFi

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install flask requests
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access Dashboard**:
   Open your browser to `http://localhost:5000`

## 📊 API Endpoints

- `GET /` - Serves the main dashboard
- `POST /data` - Receives sensor data from Arduino
- `GET /sensor_data` - Returns current sensor readings as JSON

## 🔧 Configuration

### Arduino Setup
Update the server URL in `ship_sink.ino`:
```cpp
const char* serverURL = "http://your-server-ip:5000/data";
```

### SMS Configuration
Update your Fast2SMS API key in `app.py`:
```python
fast2sms_api_key = "your-api-key-here"
```

## 📱 Demo Mode

The system automatically enters demo mode when no live Arduino data is available, generating realistic maritime sensor data for demonstration purposes.

## 🎯 Use Cases

- **Maritime Safety**: Early warning system for ship emergencies
- **Fleet Management**: Real-time monitoring of vessel conditions
- **Research**: Environmental data collection for maritime studies
- **Training**: Educational tool for maritime safety protocols

## 🔒 Safety Features

- **Threshold Monitoring**: Automatic alerts when sensor values exceed safe limits
- **GPS Tracking**: Real-time location monitoring with Google Maps integration
- **Emergency Response**: Immediate SMS notifications to emergency contacts
- **Data Logging**: Continuous monitoring and data storage

## 📈 Future Enhancements

- Database integration for historical data analysis
- Multi-vessel monitoring dashboard
- Advanced analytics and predictive maintenance
- Integration with maritime authorities
- Mobile application for remote monitoring

## 👨‍💻 Developer

Built with modern web technologies and IoT best practices to demonstrate full-stack development skills and real-world problem-solving capabilities.

---

**Note**: This system is designed for educational and demonstration purposes. For production maritime use, additional safety certifications and redundancies would be required.

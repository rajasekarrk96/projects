// Include necessary libraries
#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <ESP32Servo.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// WiFi Credentials
#define WIFI_SSID "project1234"       // WiFi SSID
#define WIFI_PASSWORD "project1234"   // WiFi Password

// DHT Sensor Configuration
#define DHTPIN 4                      // DHT sensor pin
#define DHTTYPE DHT11                 // DHT sensor type
DHT dht(DHTPIN, DHTTYPE);            // Initialize DHT sensor

// Sensor Pins
#define SOIL_MOISTURE_PIN 34          // Analog pin for soil moisture sensor
#define WATER_LEVEL_PIN 32            // Analog pin for water level sensor
#define MOTOR_RELAY 26                // Relay pin for motor
#define SERVO_PIN 25                  // Servo motor control pin
#define LED_PIN 14                    // LED pin for alert indication
#define BUZZER_PIN 33                 // Buzzer pin for alert indication

// GPS Configuration Pins
#define RXD2 16                       // GPS module RX pin
#define TXD2 17                       // GPS module TX pin
TinyGPSPlus gps;                     // GPS library instance
HardwareSerial gpsSerial(2);         // Use Serial2 for GPS

// Web Server Initialization
WebServer server(80);                // Web server runs on port 80
Servo servoMotor;                    // Servo motor object

// Connect to WiFi function
void connectToWiFi() {
  Serial.print("Connecting to WiFi");

  WiFi.mode(WIFI_STA);               // Set WiFi to station mode
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);  // Begin WiFi connection

  int maxAttempts = 30;              // Max attempts to connect (~15s)
  int attempt = 0;

  // Try connecting to WiFi
  while (WiFi.status() != WL_CONNECTED && attempt < maxAttempts) {
    delay(500);
    Serial.print(".");
    attempt++;
  }

  // If connected, print IP address
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("📡 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Failed to connect to WiFi.");
    // Optional: ESP.restart();
  }
}

// Handle GET request for sensor data
void sendSensorData() {
  int rawSoilMoisture = analogRead(SOIL_MOISTURE_PIN);  // Read raw soil moisture value
  int adjustedMoisture = 4095 - rawSoilMoisture;         // Convert to proper scale
  int waterLevel = analogRead(WATER_LEVEL_PIN);          // Read water level
  float temp = dht.readTemperature();                    // Read temperature

  // Print sensor readings to Serial Monitor
  Serial.println("---- Sensor Data ----");
  Serial.println("Raw Soil Moisture: " + String(rawSoilMoisture));
  Serial.println("Adjusted Soil Moisture: " + String(adjustedMoisture));
  Serial.println("Water Level: " + String(waterLevel));
  Serial.println("Temperature: " + String(temp) + "°C");
  Serial.println("----------------------");

  // Create JSON data string
  String data = "{\"soil_moisture\":" + String(adjustedMoisture) + 
                ",\"water_level\":" + String(waterLevel) + 
                ",\"temperature\":" + String(temp) + "}";
  server.send(200, "application/json", data);  // Send data to client
}

// Handle POST request to trigger animal alert
void animalAlertHandler() {
  Serial.println("🐾 Animal alert triggered!");
  servoMotor.write(0);                          // Move servo to 0°
  digitalWrite(LED_PIN, HIGH);                  // Turn on LED
  digitalWrite(BUZZER_PIN, HIGH);               // Turn on Buzzer
  Serial.println("🚨 Servo at 0°, LED ON, Buzzer ON");

  // Servo sweep motion for scare
  for (int i = 0; i < 5; i++) {
    servoMotor.write(180);
    delay(1000);
    servoMotor.write(90);
    delay(1000);
    servoMotor.write(0);
    delay(1000);
  }

  delay(5000);                                   // Wait before resetting
  servoMotor.write(180);                         // Reset servo
  digitalWrite(LED_PIN, LOW);                    // Turn off LED
  digitalWrite(BUZZER_PIN, LOW);                 // Turn off Buzzer
  Serial.println("✅ Animal alert handled");
  server.send(200, "text/plain", "Animal alert handled");  // Send response
}

// Function to control water pump based on soil moisture
void controlWateringSystem() {
  int rawMoisture = analogRead(SOIL_MOISTURE_PIN);   // Read raw value
  int adjustedMoisture = 4095 - rawMoisture;         // Adjust value

  Serial.println("💧 Checking watering system...");
  Serial.print("Raw Soil Moisture: "); Serial.println(rawMoisture);
  Serial.print("Adjusted Soil Moisture: "); Serial.println(adjustedMoisture);

  // Determine moisture level and control motor
  if (adjustedMoisture <= 2000) {                    // Soil is dry
    digitalWrite(MOTOR_RELAY, LOW);                  // Turn pump ON (Active LOW)
    Serial.println("🔴 Soil is DRY! Pump is ON (Relay LOW)");
  } else {                                           // Soil is wet
    digitalWrite(MOTOR_RELAY, HIGH);                 // Turn pump OFF
    Serial.println("🟢 Soil is WET! Pump is OFF (Relay HIGH)");
  }

  // Log current relay state
  int relayState = digitalRead(MOTOR_RELAY);
  Serial.print("📢 Relay State: "); Serial.println(relayState == LOW ? "ON" : "OFF");
}

// Setup function runs once at startup
void setup() {
  Serial.begin(115200);                  // Start Serial Monitor
  dht.begin();                           // Initialize DHT sensor

  // Motor relay setup and test
  pinMode(MOTOR_RELAY, OUTPUT);
  digitalWrite(MOTOR_RELAY, HIGH);       // Initially OFF
  delay(2000);
  digitalWrite(MOTOR_RELAY, LOW);        // Test ON
  delay(2000);

  // Output pins setup
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Initialize and attach servo motor
  servoMotor.setPeriodHertz(50);         // Set servo frequency to 50Hz
  servoMotor.attach(SERVO_PIN, 500, 2500);  // Attach servo pin
  Serial.println("🚀 Servo on GPIO 25 initialized");

  // Initialize GPS module on Serial2
  gpsSerial.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("📡 GPS Module Initialized");

  // Connect to WiFi
  connectToWiFi();

  // Define server routes
  server.on("/sensor_data", HTTP_GET, sendSensorData);      // Sensor data endpoint
  server.on("/video_feed", HTTP_POST, animalAlertHandler);  // Animal alert trigger endpoint

  // Start the web server
  server.begin();
  Serial.println("🌐 Web server started");
}

// Loop function runs repeatedly
void loop() {
  // Read and process GPS data
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Handle web server requests
  server.handleClient();

  // Check and control water pump system
  controlWateringSystem();

  // Wait before next cycle
  delay(5000);
}

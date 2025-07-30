#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <SFE_BMP180.h>
#include <Wire.h>
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define ALTITUDE 10.0   // Enter your country's altitude in meters
#define DHTPIN D0       // Pin connected to the DHT11 data pin
#define DHTTYPE DHT11   // DHT 11 sensor type

#define PRESSURE_PIN A0 // Analog pin connected to the output of the analog pressure sensor
SFE_BMP180 bmp;
DHT dht(DHTPIN, DHTTYPE);
static const int RXPin = 4, TXPin = 5;
static const uint32_t GPSBaud = 9600;

// WiFi credentials
const char* ssid = "project12345";       // Your WiFi SSID
const char* password = "project12345"; // Your WiFi password
const char* serverURL = "http://192.168.1.146:5000";  // Python server URL

// The TinyGPS++ object
TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

double T_bmp;           // Temperature from BMP180 sensor
double P, S, A;

const double dfp = 1013.25; // Default sea-level pressure value
const double TEMP_THRESHOLD = 35.0;  // Temperature threshold for warning (in Celsius)
const double PRESSURE_THRESHOLD = 1100;  // Pressure threshold for warning (in Pascals)

// Variables for sinking time calculation
unsigned long lastPressureCheckTime = 0;
double lastPressure = 0.0;
double sinkingRate = 0.0;  // Pressure change per second
double criticalPressure = 2000.0;  // Pressure level indicating the ship has fully sunk (arbitrary value)
double timeToSink = 0.0;  // Time remaining before ship sinks (in hours)

// Function to initialize sensors
void initializeSensors() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);  // Connect to WiFi

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi.");
}

void sendWarningToServer(float temperature, float pressure, double latitude, double longitude, double timeToSink) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;  // Create a WiFiClient object
    HTTPClient http;

    // Prepare the warning message
    String warningMessage = "{\"temperature\": " + String(temperature) +
                            ", \"pressure\": " + String(pressure) +
                            ", \"latitude\": " + String(latitude, 6) +
                            ", \"longitude\": " + String(longitude, 6) +
                            ", \"time_to_sink\": " + String(timeToSink, 2) + " hours}";

    http.begin(client, serverURL);  // Use the new API: pass the WiFiClient and the URL
    http.addHeader("Content-Type", "application/json");  // Set content type to JSON

    int httpResponseCode = http.POST(warningMessage);  // Send HTTP POST request

    if (httpResponseCode > 0) {
      String response = http.getString();  // Get the response
      Serial.println("Response from server: " + response);
    } else {
      Serial.print("Error in sending POST request: ");
      Serial.println(httpResponseCode);
    }

    http.end();  // End the HTTP connection
  } else {
    Serial.println("WiFi Disconnected");
  }
}

// Function to calculate time remaining before sinking based on pressure increase rate
void calculateTimeToSink(double currentPressure) {
  unsigned long currentTime = millis();
  
  if (lastPressureCheckTime > 0) {
    // Calculate time difference in seconds
    double timeDiff = (currentTime - lastPressureCheckTime) / 1000.0;

    // Calculate sinking rate (pressure increase per second)
    sinkingRate = (currentPressure - lastPressure) / timeDiff;

    // Calculate time remaining before pressure reaches critical level (in hours)
    if (sinkingRate > 0) {
      timeToSink = (criticalPressure - currentPressure) / sinkingRate / 3600.0;
    } else {
      timeToSink = -1;  // Sinking rate is negative or zero (invalid case)
    }
  }

  // Update last pressure and time
  lastPressure = currentPressure;
  lastPressureCheckTime = currentTime;
}

// Function to read temperature from DHT11 sensor
float readDHT11Temperature() {
  float T = dht.readTemperature();  // Read temperature in Celsius
  if (isnan(T)) {
    Serial.println("Failed to read from DHT11 sensor!");
    return -1;                      // Return -1 to indicate failure
  }
  return T;
}

// Function to calculate pressure and altitude from BMP180 using the provided temperature
void calculateBMP180Pressure(float temperature) {
  if (bmp.startPressure(3)) {  // Start pressure measurement with oversampling = 3
    delay(100);                // Allow time for pressure measurement
    if (bmp.getPressure(P, T_bmp)) {  // Use T_bmp for pressure calculation
      // Calculate sea-level pressure
      S = bmp.sealevel(P, ALTITUDE);

      // Calculate altitude
      A = bmp.altitude(P, S);
      return;
    }
  }

  // Fallback values in case the BMP180 sensor fails
  P = dfp;
  S = bmp.sealevel(P, ALTITUDE);
  A = bmp.altitude(P, S);
}

// Function to print the sensor data to the serial monitor
void printSensorData(float temperature) {
  Serial.print("Provided altitude: ");
  Serial.print(ALTITUDE, 0);
  Serial.print(" meters, ");
  Serial.print(ALTITUDE * 3.28084, 0);  // Convert to feet
  Serial.println(" feet");

  Serial.print("Temperature from DHT11: ");
  Serial.print(temperature, 2);
  Serial.println(" °C");

  Serial.print("Absolute pressure: ");
  Serial.print(P, 2);
  Serial.println(" mb");

  Serial.print("Relative (sea-level) pressure: ");
  Serial.print(S);
  Serial.println(" mb");

  Serial.print("Computed altitude: ");
  Serial.print(A, 0);
  Serial.print(" meters, ");
  Serial.print(A * 3.28084, 0);  // Convert to feet
  Serial.println(" feet");

  Serial.println(); // Add an empty line for readability
}

void setup() {
  Serial.begin(9600);
  ss.begin(GPSBaud);
  initializeSensors();  // Initialize BMP180 and DHT11 sensors
}

void loop() {
  // Process GPS data
  double latitude = 0.0;
  double longitude = 0.0;

  while (ss.available() > 0) {
    gps.encode(ss.read());
    if (gps.location.isUpdated()) {
      latitude = gps.location.lat();
      longitude = gps.location.lng();
      Serial.print("Latitude= ");
      Serial.print(latitude, 6);
      Serial.print(" Longitude= ");
      Serial.println(longitude, 6);
    }
  }

  // Read temperature from DHT11 sensor
  float temperature = readDHT11Temperature();
  if (temperature != -1) {  // Proceed only if temperature is valid
    T_bmp = temperature;    // Use DHT11 temperature for BMP180 calculations
    calculateBMP180Pressure(T_bmp);  // Calculate pressure and altitude
    printSensorData(temperature);    // Print the sensor data to the serial monitor
  }

  // Analog pressure sensor reading
  int sensorValue = analogRead(PRESSURE_PIN);  // Read analog value
  float voltage = sensorValue * (5.0 / 1023.0);  // Convert analog value to voltage
  float pressure = (voltage / 5.0) * 1200;  // Convert voltage to pressure (assuming 1.2 kPa max for 5V)

  Serial.print("Analog Sensor Value: ");
  Serial.print(sensorValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 2);
  Serial.print(" V | Pressure: ");
  Serial.print(pressure, 2);
  Serial.println(" Pa");  // Print pressure in Pascals

  // Calculate time to sink
  calculateTimeToSink(pressure);

  if (timeToSink > 0) {
    Serial.print("Estimated time remaining before ship sinks: ");
    Serial.print(timeToSink, 2);
    Serial.println(" hours");
  } else {
    Serial.println("Sinking rate too low or invalid.");
  }

  // Check if pressure or temperature exceeds threshold and send warning
  if (temperature > TEMP_THRESHOLD || pressure > PRESSURE_THRESHOLD) {
    Serial.println("Warning: Temperature or pressure exceeded threshold!");
    sendWarningToServer(temperature, pressure, latitude, longitude, timeToSink);
  }

  delay(3000);  // Wait 3 seconds before next measurement
}

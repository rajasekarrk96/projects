#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>  // Correct header for ESP8266

// Dummy sensor data
float orgLat = 37.7749;
float orgLong = -122.4194;
float orgHeartRate = 75.0;
float orgSpO2 = 98.0;

// WiFi credentials
const char* ssid = "project12345";
const char* password = "project12345";

// Pins for buzzer and light
const int BUZZER_PIN = D5;  // Use actual GPIO pin numbers (e.g., D5 = GPIO14)
const int LIGHT_PIN  = D6;  // D6 = GPIO12

// Web server on port 80
ESP8266WebServer server(80);

// Handle /buzz?buzzs=0 or 1
void handleBuzzControl() {
  if (server.hasArg("buzzs")) {
    int buzzState = server.arg("buzzs").toInt();
    digitalWrite(BUZZER_PIN, buzzState ? HIGH : LOW);
    digitalWrite(LIGHT_PIN, buzzState ? HIGH : LOW);

    String response = "{\"status\": \"ok\", \"buzzs\": " + String(buzzState) + "}";
    server.send(200, "application/json", response);
  } else {
    server.send(400, "application/json", "{\"error\": \"Missing buzzs param\"}");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LIGHT_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LIGHT_PIN, LOW);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.println(WiFi.localIP());

  server.on("/buzz", handleBuzzControl);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  // Sensor POST to Flask
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    String serverUrl = "http://192.168.99.61:5000/update";

    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{ \"gps_lat\": " + String("11.8275079") +
                      ", \"gps_long\": " + String("79.7827223") +
                      ", \"heart_rate\": " + String(orgHeartRate) +
                      ", \"spo2\": " + String(orgSpO2) + " }";

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response from server: " + response);
    } else {
      Serial.println("Error in HTTP request");
    }
    http.end();
  }

  orgHeartRate = 60 + random(0, 40);
  orgSpO2 = 95 + random(0, 5);

  // Handle HTTP requests
  server.handleClient();

  delay(1000);
}

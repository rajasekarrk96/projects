#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>

// Wi-Fi Credentials
const char* ssid = "project1234";
const char* password = "project1234";

// Pin Definitions
#define MQ135_PIN 34       // MQ135 connected to GPIO34 (Analog)
#define GREEN_LED 15       // Green LED: No Gas Detected
#define RED_LED 17         // Red LED: Gas Detected
#define RELAY_PIN 5        // Relay control pin
#define DHTPIN 4           // DHT11 data pin
#define DHTTYPE DHT11

// Threshold for detecting gas (you may need to calibrate this)
int gas_threshold = 800;

// DHT Sensor
DHT dht(DHTPIN, DHTTYPE);

// Web server on port 80
WebServer server(80);

void handleRoot() {
  int mq135_value = analogRead(MQ135_PIN);
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  bool gas_detected = mq135_value > gas_threshold;

  String json = "{";
  json += "\"gas_detected\":";
  json += gas_detected ? "true" : "false";
  json += ",\"humidity\":";
  json += isnan(humidity) ? "0" : String(humidity, 1);
  json += ",\"temperature\":";
  json += isnan(temperature) ? "0" : String(temperature, 1);
  json += ",\"gas_value\":";
  json += mq135_value;
  json += "}";

  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(RELAY_PIN, HIGH);

  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");
  int maxAttempts = 30;
  int attempt = 0;

  while (WiFi.status() != WL_CONNECTED && attempt < maxAttempts) {
    delay(500);
    Serial.print(".");
    attempt++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi.");
    delay(3000);
    // Optional: Restart on failure
    // ESP.restart();
  }

  // Set up web server route
  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  int mq135_value = analogRead(MQ135_PIN);
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  Serial.println(mq135_value);
  if (mq135_value > gas_threshold) {
    // Gas detected
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RELAY_PIN, LOW); // Relay ON (e.g., to disable engine)
    Serial.println("Status: Gas Detected - Relay ON");
  } else {
    // No gas
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RELAY_PIN, HIGH); // Relay OFF (normal condition)
    Serial.println("Status: No Gas - Relay OFF");
  }

  server.handleClient();
  delay(2000); // 2 seconds delay
}
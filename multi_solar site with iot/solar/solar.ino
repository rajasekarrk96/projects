#include <WiFi.h>
#include <Wire.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// === Wi-Fi Credentials ===
const char* ssid = "project1234";
const char* password = "project1234";

// === Servo Pins ===
#define SERVO1_PIN 12
#define SERVO2_PIN 13
#define SERVO3_PIN 14
#define WIPER_PIN  27
#define WATER_SERVO_PIN 15  // New servo for water detection

// === Sensor Pins ===
#define WATER_SENSOR_PIN 33
#define TILT_SENSOR_PIN  32

// === L298N Motor Driver Pins ===
#define IN1 25  
#define IN2 26

// === Servo Objects ===
Servo panel1;
Servo panel2;
Servo panel3;
Servo wiper;
Servo waterServo;

WebServer server(80);

// === State tracking ===
bool wasTiltLow = false;

void setup() {
  Serial.begin(115200);

  // Attach servos
  panel1.attach(SERVO1_PIN);
  panel2.attach(SERVO2_PIN);
  panel3.attach(SERVO3_PIN);
  wiper.attach(WIPER_PIN);
  waterServo.attach(WATER_SERVO_PIN);

  panel1.write(90);
  panel2.write(90);
  panel3.write(90);
  wiper.write(90);
  waterServo.write(0);

  // Pin modes
  pinMode(WATER_SENSOR_PIN, INPUT);
  pinMode(TILT_SENSOR_PIN, INPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  // WiFi connect
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED && attempt < 30) {
    delay(500);
    Serial.print(".");
    attempt++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("📶 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Failed to connect to WiFi.");
    delay(3000);
  }
  

  // Web routes
  server.on("/set_servo", []() {
    if (server.hasArg("servo1")) {
      int angle = constrain(server.arg("servo1").toInt(), 0, 180);
      int angle1 = 180 - angle;
      panel1.write(angle);
      panel2.write(angle);
      panel3.write(angle1);
      Serial.println("☀️ Panels adjusted to angle: " + String(angle));
      server.send(200, "text/plain", "Panels set to " + String(angle));
    } else {
      server.send(400, "text/plain", "Missing 'servo1' parameter.");
    }
  });

  server.on("/set_relay", []() {
    if (server.hasArg("relay")) {
      int relay = server.arg("relay").toInt();
      if (relay == 1) {
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        Serial.println("🔼 Moving UP");
      } else if (relay == 0) {
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, HIGH);
        Serial.println("🔽 Moving DOWN");
      } else {
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, LOW);
        Serial.println("⛔ Invalid signal - motor stopped");
      }
      delay(5000);
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
      Serial.println("⏹️ Motor stopped");
      server.send(200, "text/plain", "Motor action completed.");
    } else {
      server.send(400, "text/plain", "Missing 'relay' parameter.");
    }
  });

  server.on("/clean", []() {
    Serial.println("🧼 Cleaning activated!");
    for (int i = 0; i < 3; i++) {
      wiper.write(0);
      delay(400);
      wiper.write(180);
      delay(400);
    }
    wiper.write(90);
    server.send(200, "text/plain", "Cleaning completed.");
  });

  server.begin();
  Serial.println("🌐 Web server started.");
}

void loop() {
  server.handleClient();

  bool waterDetected = digitalRead(WATER_SENSOR_PIN) == LOW;
  bool tiltDetected = digitalRead(TILT_SENSOR_PIN) == LOW;

  if (waterDetected) {
    Serial.println("💧 Water detected — Activating water servo");
    waterServo.write(90);`
  }

  if (tiltDetected && !wasTiltLow) {
    Serial.println("⚠️ Tilt detected — Moving DOWN");
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    delay(5000);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    wasTiltLow = true;
  }

  if (!tiltDetected && wasTiltLow) {
    Serial.println("✅ Tilt cleared — Moving UP");
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    delay(5000);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    wasTiltLow = false;
  }

  delay(300);
}

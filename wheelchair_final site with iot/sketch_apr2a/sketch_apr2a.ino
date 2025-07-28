#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

#define IR_SENSOR1 D2
#define EN1 D3
#define EN2 D4
#define IN1 D5
#define IN2 D6
#define IN3 D7
#define IN4 D8
#define TRIG D0
#define ECHO D1
#define IR_SENSOR2 A0

ESP8266WebServer server(80);

// Blink detection
int blinkCounter1 = 0;
bool eyeClosed1 = false;
unsigned long blinkStartTime1 = 0;
unsigned long windowStartTime1 = 0;
bool windowActive1 = false;

int blinkCounter2 = 0;
bool eyeClosed2 = false;
unsigned long blinkStartTime2 = 0;
unsigned long windowStartTime2 = 0;
bool windowActive2 = false;

const int longBlinkThreshold = 1200;
const int blinkWindow = 1500;

int motorSpeed = 150;
String carStatus = "Stopped";
bool webControlActive = false;

const char* ssid = "project12345";
const char* password = "project12345";

// For limiting ultrasonic distance printing
int lastDistance = 0;
unsigned long lastDistancePrint = 0;

void setup() {
  Serial.begin(115200);
  pinMode(IR_SENSOR1, INPUT);
  pinMode(EN1, OUTPUT); pinMode(EN2, OUTPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT);
  stopMotors();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nConnected to WiFi. IP: " + WiFi.localIP().toString());

  server.on("/move_forward", []() { moveForward(); server.send(200, "text/plain", "Moving Forward"); });
  server.on("/move_backward", []() { moveBackward(); server.send(200, "text/plain", "Moving Backward"); });
  server.on("/move_left", []() { turnLeft(); server.send(200, "text/plain", "Turning Left"); });
  server.on("/move_right", []() { turnRight(); server.send(200, "text/plain", "Turning Right"); });
  server.on("/move_stop", []() { emergencyStop(); server.send(200, "text/plain", "Emergency Stop"); });
  server.on("/set_mode", handleSetMode);
  server.begin();
}

void loop() {
  server.handleClient();

  if (!webControlActive) {
    handleBlink(IR_SENSOR1, blinkCounter1, eyeClosed1, blinkStartTime1, windowStartTime1, windowActive1, true);
    handleBlinkAnalog(IR_SENSOR2, blinkCounter2, eyeClosed2, blinkStartTime2, windowStartTime2, windowActive2);
  }

  obstacleAvoidance(); // call obstacle detection continuously
}

void handleBlink(int pin, int &counter, bool &closed, unsigned long &start, unsigned long &windowStart, bool &windowActive, bool isFirstSensor) {
  int irValue = digitalRead(pin);
  unsigned long currentTime = millis();

  if (irValue == LOW && !closed) {
    closed = true;
    start = currentTime;
  }

  if (irValue == HIGH && closed) {
    closed = false;
    unsigned long blinkDuration = currentTime - start;

    if (!windowActive && blinkDuration >= 50 && blinkDuration < longBlinkThreshold) {
      windowStart = currentTime;
      counter = 1;
      windowActive = true;
      Serial.println("First blink detected (IR1).");
    } else if (windowActive && blinkDuration >= 50 && blinkDuration < longBlinkThreshold) {
      counter++;
    }
  }

  if (irValue == LOW && !windowActive && closed && (currentTime - start) >= longBlinkThreshold) {
    Serial.println("Long blink detected (IR1). Emergency stop!");
    emergencyStop();
    counter = 0; closed = false; windowActive = false;
    return;
  }

  if (windowActive && (currentTime - windowStart >= blinkWindow)) {
    Serial.print("Blinks counted (IR1): ");
    Serial.println(counter);
    if (isFirstSensor) controlCarForwardBackward(counter);
    counter = 0; windowActive = false;
  }
}

void handleBlinkAnalog(int pin, int &counter, bool &closed, unsigned long &start, unsigned long &windowStart, bool &windowActive) {
  int irValue = analogRead(pin);
  unsigned long currentTime = millis();

  if (irValue < 500 && !closed) {
    closed = true;
    start = currentTime;
  }

  if (irValue >= 500 && closed) {
    closed = false;
    unsigned long blinkDuration = currentTime - start;

    if (!windowActive && blinkDuration >= 50 && blinkDuration < longBlinkThreshold) {
      windowStart = currentTime;
      counter = 1;
      windowActive = true;
      Serial.println("First blink detected (IR2).");
    } else if (windowActive && blinkDuration >= 50 && blinkDuration < longBlinkThreshold) {
      counter++;
    }
  }

  if (irValue < 500 && !windowActive && closed && (currentTime - start) >= longBlinkThreshold) {
    Serial.println("Long blink detected (IR2). Emergency stop!");
    emergencyStop();
    counter = 0; closed = false; windowActive = false;
    return;
  }

  if (windowActive && (currentTime - windowStart >= blinkWindow)) {
    Serial.print("Blinks counted (IR2): ");
    Serial.println(counter);
    controlCarLeftRight(counter);
    counter = 0; windowActive = false;
  }
}

void controlCarForwardBackward(int count) {
  Serial.print("Blink Count IR1 (F/B): ");
  Serial.println(count);
  if (count == 1) moveForward();
  else if (count == 2) moveBackward();
  else emergencyStop();
}

void controlCarLeftRight(int count) {
  Serial.print("Blink Count IR2 (L/R): ");
  Serial.println(count);
  if (count == 1) turnLeft();
  else if (count == 2) turnRight();
  else emergencyStop();
}

void handleSetMode() {
  if (!server.hasArg("mode")) {
    server.send(400, "text/plain", "Missing Mode");
    return;
  }
  String mode = server.arg("mode");
  webControlActive = (mode == "1");
  server.send(200, "text/plain", "Mode Set");
}

void moveForward() {
  carStatus = "Moving Forward";
  analogWrite(EN1, 300); analogWrite(EN2, 300);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  Serial.println("Car Status: Forward");
}

void moveBackward() {
  carStatus = "Moving Backward";
  analogWrite(EN1, 300); analogWrite(EN2, 300);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  Serial.println("Car Status: Backward");
}

void turnLeft() {
  carStatus = "Turning Left";
  analogWrite(EN1, 300); analogWrite(EN2, 300);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  Serial.println("Car Status: Left");
}

void turnRight() {
  carStatus = "Turning Right";
  analogWrite(EN1, 300); analogWrite(EN2, 300);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  Serial.println("Car Status: Right");
}

void emergencyStop() {
  carStatus = "EMERGENCY STOP";
  stopMotors();
  Serial.println("EMERGENCY STOP ACTIVATED!");
}

void stopMotors() {
  analogWrite(EN1, 0); analogWrite(EN2, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

bool detectObstacle() {
  // Send a pulse to trigger the ultrasonic sensor
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2); // Short delay to ensure proper timing
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10); // 10us pulse to trigger
  digitalWrite(TRIG, LOW);

  // Measure the pulse duration on the ECHO pin
  long duration = pulseIn(ECHO, HIGH, 20000); // Timeout after 20ms

  // Debug print the duration
  // Serial.print("Duration: ");
  // Serial.println(duration);
  
  if (duration == 0) {
    // Serial.println("No Echo received!");
    return false; // If no echo, return false
  }
  
  // Calculate the distance in cm
  int distance = duration * 0.034 / 2;
  // Serial.print("Distance: ");
  // Serial.println(distance);

  // If the distance is too small or too large, consider it invalid
  if (distance <= 5 || distance > 200) {
    // Serial.println("Invalid distance, ignoring.");
    return false;
  }

  // Filter out rapid fluctuations in distance
  unsigned long currentTime = millis();
  if (abs(distance - lastDistance) >= 5 || (currentTime - lastDistancePrint) >= 1000) {
    lastDistance = distance;
    lastDistancePrint = currentTime;
  }

  // Return true if distance is less than 30cm (object detected)
  return (distance <= 30); 
}

unsigned long lastObstacleTime = 0;
bool avoidCooldown = false;

void obstacleAvoidance() {
  if (avoidCooldown && (millis() - lastObstacleTime < 4000)) {
    return;  // Skip obstacle detection for 4 seconds after avoidance
  }

  if (detectObstacle()) {
    Serial.println("Obstacle Detected: Auto-stopping");
    emergencyStop();
    // Start cooldown
    avoidCooldown = true;
    lastObstacleTime = millis();
  } else {
    avoidCooldown = false;
  }
}

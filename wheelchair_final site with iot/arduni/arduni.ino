#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

#define IR_SENSOR D2   // IR Sensor for Eye Blink Detection

#define EN1 D3   // Speed Control for Left Motor
#define EN2 D4   // Speed Control for Right Motor

#define IN1 D5   // Motor A
#define IN2 D6
#define IN3 D7   // Motor B
#define IN4 D8

#define TRIG D0  // Ultrasonic Trigger
#define ECHO D1  // Ultrasonic Echo

ESP8266WebServer server(80);

int blinkCount = 0;
unsigned long lastBlinkTime = 0;
const int blinkThreshold = 500;  // Time limit to count multiple blinks (ms)
const int longBlinkThreshold = 1000;  // Time for emergency stop (1 sec)
int motorSpeed = 150;  // Speed (0-255)
String carStatus = "Stopped";

bool webControlActive = false;  // False = blind-based control, True = web control

const char* ssid = "project1234";
const char* password = "project1234";

void setup() {
  Serial.begin(115200);
  pinMode(IR_SENSOR, INPUT);
  
  pinMode(EN1, OUTPUT);
  pinMode(EN2, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  stopMotors();
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi. IP: " + WiFi.localIP().toString());

  // Web Server Routes
  server.on("/", handleRoot);
  server.on("/move", handleMove);
  server.on("/set_mode", handleSetMode);

  server.begin();
}

void loop() {
  server.handleClient();  // Handle web requests
}

void handleRoot() {
  String html = "<html><head><title>Car Control</title></head><body>";
  html += "<h1>Car Control Panel</h1>";
  html += "<p>Status: " + carStatus + "</p>";
  html += "<button onclick=\"fetch('/move?direction=forward')\">Forward</button> ";
  html += "<button onclick=\"fetch('/move?direction=left')\">Left</button> ";
  html += "<button onclick=\"fetch('/move?direction=right')\">Right</button> ";
  html += "<button onclick=\"fetch('/move?direction=backward')\">Backward</button> ";
  html += "<button onclick=\"fetch('/move?direction=stop')\">Stop</button> ";
  html += "<button onclick=\"fetch('/set_mode?mode='+(mode=mode==='1'?'0':'1'))\">Toggle Mode</button> ";
  html += "<script>function fetch(url){ var xhttp=new XMLHttpRequest();xhttp.open('GET', url, true);xhttp.send();}</script>";
  html += "</body></html>";

  server.send(200, "text/html", html);
}

void handleMove() {
  if (!server.hasArg("direction")) {
    server.send(400, "text/plain", "Missing Direction");
    return;
  }
  String direction = server.arg("direction");

  if (direction == "forward") moveForward();
  else if (direction == "backward") moveBackward();
  else if (direction == "left") turnLeft();
  else if (direction == "right") turnRight();
  else if (direction == "stop") emergencyStop();
  else {
    server.send(400, "text/plain", "Invalid Direction");
    return;
  }

  server.send(200, "text/plain", "Command Executed");
}

void handleSetMode() {
  if (!server.hasArg("mode")) {
    server.send(400, "text/plain", "Missing Mode");
    return;
  }
  String mode = server.arg("mode");
  
  if (mode == "0") webControlActive = false;
  else if (mode == "1") webControlActive = true;
  else {
    server.send(400, "text/plain", "Invalid Mode");
    return;
  }

  server.send(200, "text/plain", "Mode Set");
}

void moveForward() {
  if (detectObstacle()) return;
  carStatus = "Moving Forward";
  analogWrite(EN1, motorSpeed);
  analogWrite(EN2, motorSpeed);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  carStatus = "Moving Backward";
  analogWrite(EN1, motorSpeed);
  analogWrite(EN2, motorSpeed);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  carStatus = "Turning Left";
  analogWrite(EN1, motorSpeed);
  analogWrite(EN2, motorSpeed);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  carStatus = "Turning Right";
  analogWrite(EN1, motorSpeed);
  analogWrite(EN2, motorSpeed);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void emergencyStop() {
  carStatus = "EMERGENCY STOP";
  stopMotors();
  Serial.println("EMERGENCY STOP ACTIVATED!");
}

void stopMotors() {
  analogWrite(EN1, 0);
  analogWrite(EN2, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

bool detectObstacle() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long duration = pulseIn(ECHO, HIGH);
  int distance = duration * 0.034 / 2;

  if (distance > 0 && distance <= 30) {
    Serial.println("Obstacle Detected! Stopping...");
    emergencyStop();
    return true;
  }
  return false;
}

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <base64.h>

// Traffic Lights 1
#define RED1 5
#define YELLOW1 4
#define GREEN1 15

// Traffic Lights 2
#define RED2 14
#define YELLOW2 12
#define GREEN2 13

// Sensors & Buzzer
#define TILT_SENSOR 16
#define BUZZER 2

// LCD I2C
#define LCD_SDA 22
#define LCD_SCL 23

// GPS
#define GPS_TX 17  // RX of ESP32
#define GPS_RX 18  // TX of ESP32

// WiFi & Server Config
const char* ssid = "project1234";
const char* password = "project1234";

// Twilio Config
const char* twilio_url = "https://api.twilio.com/2010-04-01/Accounts/<TWILIO_ACCOUNT>/Messages.json";
const char* twilio_sid = "<TWILIO_ACCOUNT>";
const char* twilio_token = "<TWILIO_AUTH_TOKEN>";
const char* recipient_number = "+91XXXXXXXXXX";
const char* twilio_number = "+1XXXXXXXXXX";

WebServer server(80);

LiquidCrystal_I2C lcd1(0x27, 16, 2);
LiquidCrystal_I2C lcd2(0x26, 16, 2);  // Second LCD (Change address if needed)

TinyGPSPlus gps;
HardwareSerial gpsSerial(1);

int data = 0;
bool tiltDetected = false;
unsigned long tiltStartTime = 0;

void setup() {
    Serial.begin(115200);
    gpsSerial.begin(9600, SERIAL_8N1, GPS_TX, GPS_RX);

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    // Define Web Server Route
    server.on("/SIGNAL", HTTP_GET, handleUpdate);
    server.begin();

    pinMode(RED1, OUTPUT);
    pinMode(YELLOW1, OUTPUT);
    pinMode(GREEN1, OUTPUT);
    pinMode(RED2, OUTPUT);
    pinMode(YELLOW2, OUTPUT);
    pinMode(GREEN2, OUTPUT);
    pinMode(TILT_SENSOR, INPUT);
    pinMode(BUZZER, OUTPUT);

    Wire.begin(LCD_SDA, LCD_SCL);
    lcd1.begin(16, 2);
    lcd2.begin(16, 2);
    lcd1.backlight();
    lcd2.backlight();
    updateLCD("Hairpin Safety", "System Ready");

    // Default to Yellow
    controlTraffic(0);
}

void loop() {
    server.handleClient();
    checkTiltSensor();

    if (data == 1) {
        controlTraffic(1);
    } else if (data == 2) {
        controlTraffic(2);
    } else {
        controlTraffic(0);
    }

    delay(500);
}

// ✅ Handle Incoming GET Requests
void handleUpdate() {
    if (server.hasArg("data")) {
        data = server.arg("data").toInt();
        Serial.println("Received Data: " + String(data));
        server.send(200, "text/plain", "Data Updated");
    } else {
        server.send(400, "text/plain", "Missing 'data' parameter");
    }
}

// ✅ Update LCDs
void updateLCD(String line1, String line2) {
    lcd1.clear();
    lcd1.setCursor(0, 0);
    lcd1.print(line1);
    lcd1.setCursor(0, 1);
    lcd1.print(line2);

    lcd2.clear();
    lcd2.setCursor(0, 0);
    lcd2.print(line1);
    lcd2.setCursor(0, 1);
    lcd2.print(line2);
}

// ✅ Control Traffic Lights
void controlTraffic(int side) {
    if (side == 1) {
        digitalWrite(RED1, LOW);
        digitalWrite(GREEN1, HIGH);
        digitalWrite(YELLOW1, LOW);
        digitalWrite(RED2, HIGH);
        digitalWrite(GREEN2, LOW);
        digitalWrite(YELLOW2, LOW);
        updateLCD("Lane 1: GO", "Lane 2: STOP");
    } else if (side == 2) {
        digitalWrite(RED1, HIGH);
        digitalWrite(GREEN1, LOW);
        digitalWrite(YELLOW1, LOW);
        digitalWrite(RED2, LOW);
        digitalWrite(GREEN2, HIGH);
        digitalWrite(YELLOW2, LOW);
        updateLCD("Lane 1: STOP", "Lane 2: GO");
    } else {
        digitalWrite(RED1, LOW);
        digitalWrite(GREEN1, LOW);
        digitalWrite(YELLOW1, HIGH);
        digitalWrite(RED2, LOW);
        digitalWrite(GREEN2, LOW);
        digitalWrite(YELLOW2, HIGH);
        updateLCD("No Vehicle", "Proceed with Caution");
    }
}

// ✅ Check Tilt Sensor & Trigger Alert
void checkTiltSensor() {
    int tiltState = digitalRead(TILT_SENSOR);
    if (tiltState == LOW) {  
        if (!tiltDetected) {
            tiltDetected = true;
            tiltStartTime = millis();
        } else if (millis() - tiltStartTime >= 3000) {  // If tilt persists for 3 sec
            Serial.println("TILT ALERT! Sending SMS...");
            updateLCD("Accident!", "Sending Alert...");
            digitalWrite(GREEN1, HIGH);
            digitalWrite(BUZZER, LOW);
            sendTwilioAlert();
        }
    } else {  
        tiltDetected = false;
        digitalWrite(GREEN1, LOW);
        digitalWrite(BUZZER, HIGH);
    }
}

// ✅ Send SMS via Twilio
void sendTwilioAlert() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String gpsLocation = getGPSLocation();
        String msgBody = "Accident detected! Location: " + gpsLocation;
        String postData = "To=" + String(recipient_number) + "&From=" + String(twilio_number) + "&Body=" + msgBody;

        String auth = String(twilio_sid) + ":" + String(twilio_token);
        String encodedAuth = base64::encode(auth);

        http.begin(twilio_url);
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");
        http.addHeader("Authorization", "Basic " + encodedAuth);

        int httpResponseCode = http.POST(postData);
        if (httpResponseCode == 201) {
            Serial.println("✅ SMS Sent Successfully!");
        } else {
            Serial.println("❌ Failed to Send SMS. Code: " + String(httpResponseCode));
        }
        http.end();
    }
}

// ✅ Get GPS Location
String getGPSLocation() {
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }
    if (gps.location.isValid()) {
        return "Lat: " + String(gps.location.lat(), 6) + ", Lng: " + String(gps.location.lng(), 6);
    } else {
        return "GPS Unavailable";
    }
}

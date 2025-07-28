#include "DHT.h"
#define DHTPIN 2          // what digital pin we're connected to
#define DHTTYPE DHT11     // DHT11

// Define the analog pin
const int mq135Pin = A0;  // Pin where the analog output is connected
const int mq7Pin = A4;  // Pin where the analog output is connected

#define SensorPin A1            //pH meter Analog output to Arduino Analog Input 0
#define Offset 0.00            //deviation compensate
#define LED 13
#define samplingInterval 20
#define printInterval 800
#define ArrayLenth  40    //times of collection

#define TdsSensorPin A2
#define VREF 5.0              // analog reference voltage(Volt) of the ADC
#define SCOUNT  30            // sum of sample point
int analogBuffer[SCOUNT];     // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0;
int copyIndex = 0;
float averageVoltage = 0;
float tdsValue = 0;
float temperature = 16;       // current temperature for compensation

unsigned long int avgValue;  //Store the average value of the sensor feedback
float b;
int buf[10],temp;
 
float humi;
float tempC;
DHT dht(DHTPIN, DHTTYPE);

String dict;

// Define thresholds for each sensor
//float pHThreshold = 7.0;        // Example: pH should be > 7.0
//float humiThreshold = 10.0;     // Example: Humidity should be > 50%
//float tempThreshold = 25.0;     // Example: Temperature should be > 25°C
//int mq135Threshold = 10;       // Example: MQ-135 sensor value should be > 300
//int mq7Threshold = 10;         // Example: MQ-7 sensor value should be > 200
//float tdsThreshold = 10;       // Example: TDS should be > 500 ppm
//int turbidityThreshold = 10;   // Example: Turbidity should be > 400

// median filtering algorithm
int getMedianNum(int bArray[], int iFilterLen) {
  int bTab[iFilterLen];
  for (byte i = 0; i < iFilterLen; i++)
    bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0) {
    bTemp = bTab[(iFilterLen - 1) / 2];
  }
  else {
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  }
  return bTemp;
}

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(TdsSensorPin, INPUT);
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  dht.begin();

}
void ph()
{
  for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
  { 
    buf[i]=analogRead(SensorPin);
    delay(10);
  }
  for(int i=0;i<9;i++)        //sort the analog from small to large
  {
    for(int j=i+1;j<10;j++)
    {
      if(buf[i]>buf[j])
      {
        temp=buf[i];
        buf[i]=buf[j];
        buf[j]=temp;
      }
    }
  }
  avgValue=0;
  for(int i=2;i<8;i++)                      //take the average value of 6 center sample
    avgValue+=buf[i];
  float phValue=(float)avgValue*5.0/1024/6; //convert the analog into millivolt
  phValue=3.5*phValue; 
    dict =  "{'phvalue:'" + String(phValue) + ",";
  
}
double avergearray(int* arr, int number) {
  int i;
  int max, min;
  double avg;
  long amount = 0;
  if (number <= 0) {
    Serial.println("Error number for the array to avraging!/n");
    return 0;
  }
  if (number < 5) { //less than 5, calculated directly statistics
    for (i = 0; i < number; i++) {
      amount += arr[i];
    }
    avg = amount / number;
    return avg;
  } else {
    if (arr[0] < arr[1]) {
      min = arr[0]; max = arr[1];
    }
    else {
      min = arr[1]; max = arr[0];
    }
    for (i = 2; i < number; i++) {
      if (arr[i] < min) {
        amount += min;      //arr<min
        min = arr[i];
      } else {
        if (arr[i] > max) {
          amount += max;  //arr>max
          max = arr[i];
        } else {
          amount += arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount / (number - 2);
  }//if
  return avg;
}
void dhtsen() {
//  delay(2000);
  float humi = dht.readHumidity();
  float tempC = dht.readTemperature();

  if (isnan(humi) || isnan(tempC) )
  {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  //  Serial.print("Humidity: "); Serial.print(humi); Serial.print(" %\t");
  //  Serial.print("Temperature: ");
  //  Serial.print(tempC); Serial.print(" *C ");
  //  Serial.print(tempF); Serial.println(" *F");
  dict = dict + "'humitity:'" + String(humi) + ",'tempC':" + String(tempC) + ",";
}
void mq135() {
  // Read the analog value from the MQ-135
  int sensorValue = analogRead(mq135Pin);

  // Print the value to the Serial Monitor
  //  Serial.print("MQ-135 Sensor Value: ");
  //  Serial.println(sensorValue);
  dict = dict + "'mq135':" + String(sensorValue) + ",";
}
void mq7() {
  // Read the analog value from the MQ-135
  int sensorValue = analogRead(mq7Pin);

  // Print the value to the Serial Monitor
  //  Serial.print("MQ-135 Sensor Value: ");
  //  Serial.println(sensorValue);
  dict = dict + "'mq7':" + String(sensorValue) + ",";
}
void tds() {
  static unsigned long printTimepoint = millis();
  if (millis() - printTimepoint > 1000U) { // Every 1000 ms (1 second)
    printTimepoint = millis();
    
    // Read the analog value directly from the TDS sensor
    int rawValue = analogRead(TdsSensorPin);
    
    // Convert to voltage
    float averageVoltage = rawValue * (float)VREF / 1024.0;

    // Temperature compensation formula
    float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0);
    // Temperature compensated voltage
    float compensationVoltage = averageVoltage / compensationCoefficient;

    // Convert voltage value to TDS value
    tdsValue = (133.42 * compensationVoltage * compensationVoltage * compensationVoltage 
                - 255.86 * compensationVoltage * compensationVoltage 
                + 857.39 * compensationVoltage) * 0.5;

//    // Print the TDS value
//    Serial.print("TDS Value:");
//    Serial.print(tdsValue, 0);
//    Serial.println(" ppm");
    
    // Append to the dict string for data transmission
    dict += "'tds':" + String(tdsValue) + ",";
  }
}

void turbitity() {
  // read the input on analog pin 0:
  int sensorValue = analogRead(A3);
  // print out the value you read:
  //  Serial.println(sensorValue);
  dict+="'turbidity':"+String(sensorValue)+"}";
//  delay(1);        // delay in between reads for stability
}
void loop(void) {
  ph();
  dhtsen();
  mq135();
  mq7();
  tds();
  turbitity();
// Check if all values exceed their thresholds
//  if (pHValue > pHThreshold &&
//      humi > humiThreshold &&
//      tempC > tempThreshold &&
//      analogRead(mq135Pin) > mq135Threshold &&
//      analogRead(mq7Pin) > mq7Threshold &&
//      tdsValue > tdsThreshold &&
//      analogRead(A3) > turbidityThreshold) {

    // If all conditions are met, send the data to Python
    Serial.println(dict);
//  }
  // Add a small delay before the next reading
  delay(1000);
}

const int sensorPin1 = A0;
const int sensorPin2 = A1;
const int sensorPin3 = A2;
const int numReadings = 10;
const float weightThreshold = 0.9; // Gewicht waarboven en onder, true/false statements gegeven worden

const int ledPin = 9;

bool previousState1 = false;
bool previousState2 = false;
bool previousState3 = false;

// instellingen bij opstarten
void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  analogWrite(ledPin, 255);
}

void loop() {
  checkAndSendSensorData(1, sensorPin1, previousState1);
  checkAndSendSensorData(2, sensorPin2, previousState2);
  checkAndSendSensorData(3, sensorPin3, previousState3);
  
  delay(100);  
}

void checkAndSendSensorData(int sensorId, int pin, bool &previousState) {
  int sensorValue = getAverageReading(pin);
  float forceN = rawValueToNewtons(sensorValue);
  float weightKg = newtonsToKilograms(forceN);

  bool currentState = (weightKg >= weightThreshold);

  //  LED strip afgestemd op sensor 1
  if (sensorId == 1) {
    if (currentState && !previousState) {
      fadeIn(ledPin, 1000);
    } else if (!currentState && previousState) {
      fadeOut(ledPin, 1000);
    }
  }

  // Veranderen van state en alleen printen bij een verandering
  if (currentState != previousState) {
    Serial.print("GATEWAY:2,SENSOR:");
    Serial.print(sensorId);
    Serial.print(",STATE:");
    Serial.print(currentState ? "1" : "0");
    Serial.print(",WEIGHT:");
    Serial.println(weightKg);
    previousState = currentState;
  }
}

int getAverageReading(int pin) {
  long sum = 0;
  for (int i = 0; i < numReadings; i++) {
    sum += analogRead(pin);
    delay(1);  
  }
  return sum / numReadings;
}

float rawValueToNewtons(int sensorValue) {
  float minForce = 0.3;  // Minimum force in Newtons
  float maxForce = 9.8;  // Maximum force in Newtons
  
  return map(sensorValue, 0, 1023, minForce * 100, maxForce * 100) / 100.0;
}

float newtonsToKilograms(float forceN) {
  return forceN / 9.8;
}

void fadeOut(int pin, int duration) {
  int steps = 256;
  int delayTime = duration / steps;
  for (int i = 255; i >= 0; i--) {
    analogWrite(pin, i);
    delay(delayTime);
  }
}

void fadeIn(int pin, int duration) {
  int steps = 256;
  int delayTime = duration / steps;
  for (int i = 0; i <= 255; i++) {
    analogWrite(pin, i);
    delay(delayTime);
  }
}

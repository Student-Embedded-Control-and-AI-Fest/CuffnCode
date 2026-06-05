#include <Arduino.h>

const int SENSOR_PIN = PA0;
const int PUMP_PIN = PB0;
const int VALVE_PIN = PB1;

const int TARGET_PRESSURE_MMHG = 160;
const float ADC_REF_VOLTAGE = 3.3;
const int ADC_RESOLUTION = 4095;

float currentPressure = 0.0;
float filteredSignal = 0.0;

float x[3] = {0, 0, 0};
float y[3] = {0, 0, 0};

float readPressure();
float applyNotchFilter(float input);
void startPump();
void stopPump();
void openValve();
void closeValve();

void setup() {
  Serial.begin(115200);
  
  analogReadResolution(12);
  
  pinMode(SENSOR_PIN, INPUT_ANALOG);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);

  stopPump();
  openValve();
  
  Serial.println("CuffnCode Initialized.");
  Serial.println("System Ready.");
}

void loop() {
  currentPressure = readPressure();
  
  filteredSignal = applyNotchFilter(currentPressure);

  Serial.print("RawPressure:");
  Serial.print(currentPressure);
  Serial.print(",");
  Serial.print("FilteredSignal:");
  Serial.println(filteredSignal);
  
  delay(2); 
}

float readPressure() {
  int rawADC = analogRead(SENSOR_PIN);
  
  float voltage = (rawADC / (float)ADC_RESOLUTION) * ADC_REF_VOLTAGE;
  
  float pressure_mmHg = voltage * 50.0;
  
  return pressure_mmHg;
}

float applyNotchFilter(float input) {
  x[2] = x[1];
  x[1] = x[0];
  x[0] = input;
  
  y[2] = y[1];
  y[1] = y[0];
  
  const float b0 = 0.9408, b1 = -1.5226, b2 = 0.9408;
  const float a1 = -1.5226, a2 = 0.8816;
  
  y[0] = b0*x[0] + b1*x[1] + b2*x[2] - a1*y[1] - a2*y[2];
  
  return y[0];
}

void startPump() {
  digitalWrite(PUMP_PIN, HIGH);
}

void stopPump() {
  digitalWrite(PUMP_PIN, LOW);
}

void openValve() {
  digitalWrite(VALVE_PIN, HIGH);
}

void closeValve() {
  digitalWrite(VALVE_PIN, LOW);
}

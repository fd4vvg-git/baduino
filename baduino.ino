// FD4WG

#include <Keyboard.h>

const int safetyPin = 3;

bool payloadExecuted = false;

void setup() {
pinMode(safetyPin, INPUT_PULLUP);
Keyboard.begin();

}

void runPayload() {
//This section is for the badusb payload.
  
}

void loop() {
int safetyState = digitalRead(safetyPin);

if (safetyState == LOW && payloadExecuted == false) {
  runPayload();
payloadExecuted = true;
}

if (safetyState == HIGH) {
  payloadExecuted=false;
}

}


// FD4WG

#include <Keyboard.h>

const int safetyPin = 2;

bool payloadExecuted = false;

void setup() {
pinMode(safetyPin, INPUT_PULLUP);
Keyboard.begin();

}

void runPayload() {
//This section is for the badusb payload.
  
}

void loop() {
int safteyState = digitalRead(safetyPin);

if (safteyState == LOW && payloadExecuted == false) {
  runPayload();
payloadExecuted = true;
}

if (safteyState == HIGH) {
  payloadExecuted=false;
}

}


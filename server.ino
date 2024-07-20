#include <HX711_ADC.h>
#include <EEPROM.h>

#define MAX_LOAD_CELLS 4  // Maximum number of load cells that can be configured

// HX711 pointers for each load cell
HX711_ADC* loadCells[MAX_LOAD_CELLS];
int numLoadCells = 0; // Number of currently configured load cells

// Pins arrays for each load cell
int doutPins[MAX_LOAD_CELLS];
int sckPins[MAX_LOAD_CELLS];

const int EEPROM_START_ADDRESS = 0;
float calibrationFactors[MAX_LOAD_CELLS];

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println("Starting...");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'z') {
      zeroLoadCells();
    } else if (command == 'c') {
      calibrate();
    } else if (command == 's') {
      streamReadings();
    } else if (command == 'n') {
      configureNewLoadCell();
    }
  }
}

void zeroLoadCells() {
  Serial.println("Zeroing load cells...");
  for (int i = 0; i < numLoadCells; i++) {
    Serial.print("Zeroing load cell ");
    Serial.println(i);
    loadCells[i]->tare();
  }
  Serial.println("Zeroing complete.");
}

void calibrate() {
  Serial.println("Starting calibration...");
  for (int i = 0; i < numLoadCells; i++) {
    Serial.print("Calibrating load cell ");
    Serial.println(i);
    Serial.println("Place a known mass on the load cell and enter its weight:");

    float known_mass = 0;
    while (known_mass == 0) {
      while (Serial.available() == 0) {
        delay(10);
      }
      known_mass = Serial.parseFloat();
      if (known_mass == 0) {
        Serial.println("You must place a mass > 0");
      }
    }
    Serial.print("You have placed mass: ");
    Serial.println(known_mass);
    
    Serial.println("refreshing dataset");
    loadCells[i]->refreshDataSet();
    Serial.println("getting new calibration");
    float newCalibrationValue = loadCells[i]->getNewCalibration(known_mass);
    Serial.println("done that");
    Serial.print("Calibration factor for load cell ");
    Serial.print(i);
    Serial.print(" set to: ");
    Serial.print(newCalibrationValue);
    Serial.print(", configured with known mass ");
    Serial.println(known_mass);
    calibrationFactors[i] = newCalibrationValue;
  }
}

void streamReadings() {
  Serial.println("Streaming readings. Send 'q' to stop.");
  while (true) {
    if (Serial.available() > 0) {
      char command = Serial.read();
      if (command == 'q') {
        Serial.println("Stopping stream.");
        break;
      }
    }

    for (int i = 0; i < numLoadCells; i++) {
      if (loadCells[i]->update()) {
        for (int j = 0; j < numLoadCells; j++) {
          float reading = loadCells[j]->getData();
          Serial.print(reading);
          if (j < numLoadCells - 1) {
            Serial.print(", ");
          }
        }
        Serial.println();
        break; // Break out of the loop once values have been printed
      }
    }
    delay(20); // Adjust the delay as needed
  }
}

void configureNewLoadCell() {
  Serial.println("Configuring new load cell");

  if (numLoadCells >= MAX_LOAD_CELLS) {
    Serial.println("Maximum number of load cells already configured.");
    return;
  }

  int doutPin = 0;
  int sckPin = 0;

  while (Serial.available() == 0) {
    delay(10);
  }
  doutPin = Serial.parseInt();
  Serial.print("You have selected DOUT pin: ");
  Serial.println(doutPin);

  while (Serial.available() == 0) {
    delay(10);
  }
  sckPin = Serial.parseInt();
  Serial.print("You have selected SCK pin: ");
  Serial.println(sckPin);

  if (doutPin >= 0 && sckPin >= 0) {
    doutPins[numLoadCells] = doutPin;
    sckPins[numLoadCells] = sckPin;
    loadCells[numLoadCells] = new HX711_ADC(doutPin, sckPin);
    loadCells[numLoadCells]->begin();
    loadCells[numLoadCells]->start(2000, true);
    loadCells[numLoadCells]->setReverseOutput();
    numLoadCells++;
    Serial.println("New load cell configured.");
  } else {
    Serial.println("Invalid pin configuration.");
  }
}
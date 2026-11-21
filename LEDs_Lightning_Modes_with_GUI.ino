/*========================================================================
                         LEDs Lighting Modes with GUI
==========================================================================
Description:
 An ESP32-based LED controller with Blink, Alternate, and Running modes, 
 controlled through a Python GUI or physical switches, with an I2C LCD 
 displaying the selected mode.

Programmer:
 Felicity M. De Asis
 Shanna Dale R. Dela Torre
 Rhile L. Galpo

Date:
 18 Nov 2026
==========================================================================*/
#include <Arduino.h>
#include <Wire.h>  // comms
#include <LiquidCrystal_I2C.h>  //function

// LED GPIO configuration
const uint8_t LED[] = {19, 18, 5, 17, 16, 4};
const uint8_t NUM_LEDS = sizeof(LED) / sizeof(LED[0]);

// Switch GPIO configuration
const uint8_t SW1 = 32;
const uint8_t SW2 = 33;

// LCD GPIO configuration
const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;

// LCD configuration
const uint8_t LCD_ADDR = 0x27;
const uint8_t LCD_COLS = 16;
const uint8_t LCD_ROWS = 2;

// Variables
int previousSwitchMode = -1;
uint8_t Smode = 0;

LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);

// Include LED modes
#include "modes.h"


// Display mode and source on LCD
void updateLCD(String ledStateStr, String sourceStr) {

  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("LED: " + ledStateStr);

  lcd.setCursor(0, 1);
  lcd.print("Src: " + sourceStr);

}


// Turn OFF all LEDs
void led_off() {

  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED[i], LOW);
  }

}


// Execute selected mode
void setLedState(int modeId, String src) {

  switch (modeId) {

    case 0:
      updateLCD("OFF", src);
      led_off();
      Serial.println("All LEDs OFF");
      break;

    case 1:
      updateLCD("Blink", src);
      Serial.println("Mode 1 selected - BLINK");
      led_blink();
      break;

    case 2:
      updateLCD("Alternate", src);
      Serial.println("Mode 2 selected - ALTERNATE");
      led_alt();
      break;

    case 3:
      updateLCD("Run", src);
      Serial.println("Mode 3 selected - RUNNING");
      led_run();
      break;

  }

}


// Read switch combination
int readSwitchMode() {

  bool sw1State = (digitalRead(SW1) == HIGH);
  bool sw2State = (digitalRead(SW2) == HIGH);

  if (sw1State && sw2State) {
    return 1;  // BLINK 11
  }

  else if (!sw1State && sw2State) {
    return 2;  // ALTERNATE 01
  }

  else if (sw1State && !sw2State) {
    return 3;  // RUN 10
  }

  else {
    return 0;  // OFF
  }

}


// Display available serial commands
void mode_msg() {

  Serial.println("\nSelect Mode:");
  Serial.println("1. Blink");
  Serial.println("2. Alternate");
  Serial.println("3. Running");

}


void setup() {

  // Start Serial Communication
  Serial.begin(9600);
  Serial.setTimeout(50);

  delay(100);

  // Initialize switches
  pinMode(SW1, INPUT);
  pinMode(SW2, INPUT);

  // Initialize LEDs
  for (int i = 0; i < NUM_LEDS; i++) {

    pinMode(LED[i], OUTPUT);
    digitalWrite(LED[i], LOW);

  }

  // Initialize I2C LCD
  Wire.begin(SDA_PIN, SCL_PIN);

  lcd.init();
  lcd.backlight();

  updateLCD("None", "System Ready");

  Serial.println("ESP32 LED Controller Ready");

  mode_msg();

}


void loop() {

  // Read physical switches
  int currentSwitchMode = readSwitchMode(); //store data

  // Only execute when switch combination changes
  if (currentSwitchMode != previousSwitchMode) {    //detects changes (ex swt combi)

    previousSwitchMode = currentSwitchMode;

    setLedState(currentSwitchMode, "Switch");

  }


  // Read commands from Python GUI or Serial Monitor
  if (Serial.available() > 0) {

    String inputStr = Serial.readStringUntil('\n'); //receive msg thru serial
    inputStr.trim();

    if (inputStr.length() > 0) {

      Smode = inputStr.toInt();

      if (Smode >= 1 && Smode <= 3) {

        Serial.printf("Mode %d selected through Serial\n", Smode);

        setLedState(Smode, "GUI");

        mode_msg();

      }

      else {

        Serial.println("Invalid mode number. Enter 1, 2, or 3.");

        mode_msg();

      }

    }

  }

}
// Number of repetitions
const uint8_t REPEAT = 3;


// MODE 1: BLINK
void led_blink() {

  for (int i = 0; i < REPEAT; i++) {

    // Turn ON all LEDs
    for (int j = 0; j < NUM_LEDS; j++) {
      digitalWrite(LED[j], HIGH);
    }

    delay(1000);

    // Turn OFF all LEDs
    for (int j = 0; j < NUM_LEDS; j++) {
      digitalWrite(LED[j], LOW);
    }

    delay(1000);

  }

}


// MODE 2: ALTERNATE
void led_alt() {

  for (int i = 0; i < REPEAT; i++) {

    // Turn ON first half
    for (int j = 0; j < NUM_LEDS / 2; j++) {
      digitalWrite(LED[j], HIGH);
    }

    delay(1000);

    // Turn OFF first half
    for (int j = 0; j < NUM_LEDS / 2; j++) {
      digitalWrite(LED[j], LOW);
    }

    delay(1000);


    // Turn ON second half
    for (int j = NUM_LEDS - 1; j >= NUM_LEDS / 2; j--) {
      digitalWrite(LED[j], HIGH);
    }

    delay(1000);

    // Turn OFF second half
    for (int j = NUM_LEDS - 1; j >= NUM_LEDS / 2; j--) {
      digitalWrite(LED[j], LOW);
    }

    delay(1000);

  }

}


// MODE 3: RUNNING LIGHTS
void led_run() {

  const uint8_t DELAY_TIME = 250;

  for (int i = 0; i < REPEAT; i++) {

    // Forward running
    for (int j = 0; j < NUM_LEDS; j++) {

      digitalWrite(LED[j], HIGH);
      delay(DELAY_TIME);
      digitalWrite(LED[j], LOW);

    }

    // Reverse running
    for (int j = NUM_LEDS - 1; j >= 0; j--) {

      digitalWrite(LED[j], HIGH);
      delay(DELAY_TIME);
      digitalWrite(LED[j], LOW);

    }

  }

}
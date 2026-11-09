const int ADC_PIN = 34;

const unsigned long INTERVAL_MS = 50;

unsigned long next_due = 0;

void setup() {
  Serial.begin(115200);

  analogReadResolution(12);
  analogSetPinAttenuation(ADC_PIN, ADC_11db);

  delay(300);

  Serial.println("timestamp_ms,adc_raw");

  next_due = millis();
}

void loop() {
  unsigned long now = millis();

  if ((long)(now - next_due) >= 0) {

    unsigned long timestamp_ms = millis();

    int adc_raw = analogRead(ADC_PIN);

    Serial.print(timestamp_ms);
    Serial.print(",");
    Serial.println(adc_raw);

    next_due += INTERVAL_MS;

    if ((long)(millis() - next_due) >= 0) {
      next_due = millis() + INTERVAL_MS;
    }
  }
}

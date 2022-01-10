void Serial_setup() {
  Serial.begin(115200);
  Serial.setTimeout(2000);

}

void Serial_loop() {
  bool new_data = 0;
  String incomingString = "";

  if (Serial.available() > 0) {
    // read the incoming byte:
    //String incomingSerial = Serial.readStringUntil('\n');
    DeserializationError err = deserializeJson(from_pc_doc, Serial);
    //DeserializationError err = deserializeJson(from_pc_doc, incomingSerial);
    String incomingSerial = "n/E";
    json_error(err, incomingSerial);
  }
}

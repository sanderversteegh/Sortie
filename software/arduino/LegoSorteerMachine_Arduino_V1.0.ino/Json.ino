void json_error(DeserializationError err, String incomingSerial) {
  if (!err == DeserializationError::Ok)
  {

    // Print error to the "debug" serial port
    Serial.print("#");
    Serial.print("deserializeJson returned: ");
    Serial.println(err.c_str());

    Serial.print("#");
    Serial.print("dat line: ");
    Serial.println(incomingSerial);
    


  }
  else
  {
    json_update = 1;
  }
}

void json_send(){
  if (old_to_pc_doc != to_pc_doc){ //Kijk of er veranderingen zijn in het JSON bestand.
    old_to_pc_doc = to_pc_doc;
    serializeJson(to_pc_doc, Serial);
    Serial.println();
  }
  
  
}

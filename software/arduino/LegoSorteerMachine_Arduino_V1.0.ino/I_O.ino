void IO_setup() {
  //--------------------Output pinSet--------------------
  pinMode(Dc_motor2, OUTPUT);
  pinMode(Dc_motor1, OUTPUT);
  pinMode(R_led, OUTPUT);
  pinMode(G_led, OUTPUT);
  pinMode(B_led, OUTPUT);
  pinMode(W_led, OUTPUT);
  pinMode(STEP_T, OUTPUT);
  pinMode(DIR_T, OUTPUT);

  //--------------------Input pinSet--------------------
  pinMode(D4, INPUT_PULLUP);
  pinMode(D3, INPUT_PULLUP);
  pinMode(D2, INPUT_PULLUP);
  pinMode(D1, INPUT_PULLUP);
  pinMode(Opto1, INPUT_PULLUP);
  pinMode(Opto2, INPUT_PULLUP);
}


void IO_read() {
  bool io_change = 0;

  bool D4_read = digitalRead(D4);
  bool D3_read = digitalRead(D3);
  bool D2_read = digitalRead(D2);
  bool D1_read = digitalRead(D1);
  bool Opto1_read = digitalRead(Opto1);
  bool Opto2_read = digitalRead(Opto2);
  bool Home_hall_read = digitalRead(Home_hall);

  to_pc_doc["Home_hall"] = Home_hall_read;

  if (D4_read == !D4_state) {
    io_change = 1;
    D4_state = D4_read;
    to_pc_doc["D4"] = D4_read;
  }
  if (D3_read == !D3_state) {
    io_change = 1;
    D3_state = D3_read;
    to_pc_doc["D3"] = D3_read;

  }
  if (D2_read == !D2_state) {
    io_change = 1;
    D2_state = D2_read;
    to_pc_doc["D2"] = D2_read;

  }
  if (D1_read == !D1_state) {
    io_change = 1;
    D1_state = D1_read;
    to_pc_doc["D1"] = D1_read;

  }
  if (Opto1_read == !Opto1_state) {
    io_change = 1;
    Opto1_state = D4_read;
    to_pc_doc["Opto1"] = Opto1_read;

  }
  if (Opto2_read == !Opto2_state) {
    io_change = 1;
    Opto2_state = Opto2_read;
    to_pc_doc["Opto2"] = Opto2_read;

  }

  if (io_change == 1) {
    io_change = 0;
    //json_send();
  }
}

void IO_write() {

  analogWrite(W_led, 255);
  //analogWrite(W_led, from_pc_doc["W_led"].as<int>());
  analogWrite(Dc_motor2, from_pc_doc["Dc_motor2"].as<int>());
  analogWrite(Dc_motor1, from_pc_doc["Dc_motor1"].as<int>());
  //stepper_C.setRPM(from_pc_doc["Carousel_speed"].as<int>());
  

}

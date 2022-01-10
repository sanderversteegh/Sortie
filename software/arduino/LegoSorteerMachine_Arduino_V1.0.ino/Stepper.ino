void Stepper_setup() {
  //--------------------stepper setup--------------------
  stepper_C.setSpeedProfile(stepper_C.LINEAR_SPEED, MOTOR_ACCEL_C, MOTOR_DECEL_C);
  stepper_C.begin(RPM_C);
  stepper_C.setRPM(RPM_C);

  digitalWrite(DIR_T, LOW);
  TCCR4B = TCCR4B & B11111000 | B00000010;  // for PWM frequency of 3921.16 Hz
}

void stepper_loop() {
  // motor control loop - send pulse and return how long to wait until next pulse
  unsigned wait_time_micros_C = stepper_C.nextAction();
}

void carousel_GoPos() {

  if (stepper_C.getCurrentState() == stepper_C.STOPPED && newMove == 1){
    to_pc_doc["Status_arduino"] = "Ready";
    newMove = 0;
  }

  if (stepper_C.getCurrentState() == stepper_C.STOPPED) {
    int bakkje = from_pc_doc["Carousel_bakkje"].as<int>();
    if (Carousel_position != bakkje) {
      to_pc_doc["Status_arduino"] = "Moving";
      newMove = 1;
      int newpos = bakPositions[bakkje] - Carousel_graden;
      stepper_C.startRotate(newpos);
      Carousel_graden = Carousel_graden + newpos;
    }
  }

}

void transportband() {
  String stringV = from_pc_doc["Conveyor_IO"].as<String>();
  int snelheid = (from_pc_doc["Conveyor_speed"].as<int>());

  if (snelheid != snelheid_T) {
  snelheid_T = snelheid;
    switch (snelheid) {
      case 1:
        TCCR4B = TCCR4B & B11111000 | B00000101;    // for PWM frequency of 30.64 Hz
        break;
      case 2:
        TCCR4B = TCCR4B & B11111000 | B00000100;   // for PWM frequency of 122.55 Hz
        break;
      case 3:
        TCCR4B = TCCR4B & B11111000 | B00000011;  // for PWM frequency of 490.20 Hz
        break;
      case 4:
        TCCR4B = TCCR4B & B11111000 | B00000010;  // for PWM frequency of 3921.16 Hz
        break;
      case 5:
        TCCR4B = TCCR4B & B11111000 | B00000001;   // for PWM frequency of 31372.55 Hz
        break;

      default:
        TCCR4B = TCCR4B & B11111000 | B00000010;  // for PWM frequency of 3921.16 Hz
        break;
    }
  }

  if (stringV == "1") {
    analogWrite(STEP_T, 127);
  }
  else
  {
    digitalWrite(STEP_T, LOW);
  }
}

void Carousel_homing_function() {
  to_pc_doc["Case"] = Carousel_homing;
  switch (Carousel_homing) {
    case 0: //Lees uit of er een homing command is
      if (from_pc_doc["Carousel_command"].as<String>() == "Home") { //Als het homing comand is ontvangen, zet de variable naar stap 1, zet de arduino status naar "homing" en start de carusel draaien
        Carousel_homing++;
        to_pc_doc["Status_arduino"] = "Homing";
        stepper_C.setRPM(2);
        if (digitalRead(Home_hall) == HIGH) {
          stepper_C.startRotate(10000);
        }
      }
      break;

    case 1: //Kijk of de homing sensor iets ziet.
      if (digitalRead(Home_hall) == LOW) {
        Carousel_homing++;
        stepper_C.startBrake();                     //Stop de motor;
        homingTimer.reset();
      }
      break;

    case 2:   //Waneer de motor is uitgedraaid, ga een stuk achteruit

      if (homingTimer.isReady()) {
        if (stepper_C.getCurrentState() == stepper_C.STOPPED) {
          Carousel_homing++;
          stepper_C.startRotate(-200);
        }
      }
      break;
    case 3: //Ga met een lage snelheid weer vooruit.
      if (digitalRead(Home_hall) == HIGH) {
        Carousel_homing++;
        stepper_C.startBrake();
        homingTimer.setInterval(500);
        homingTimer.reset();
      }
      break;
    case 4:
      if (homingTimer.isReady()) {
        Carousel_homing++;
        stepper_C.setRPM(1);
        stepper_C.startRotate(200);
      }
      break;
    case 5: //Rem de motor waneer de sensor weer gezien wordt.
      if (digitalRead(Home_hall) == LOW) {
        Carousel_homing++;
        stepper_C.stop();                           //Stop de motor;
      }
      break;
    case 6: //Draai naar de ofset van de carousel
      if (stepper_C.getCurrentState() == stepper_C.STOPPED) {
        Carousel_homing++;
        stepper_C.setRPM(RPM_C);
        stepper_C.startRotate(Carousel_ofset);
      }
      break;
    case 7:
      to_pc_doc["Status_arduino"] = "Ready";
      Carousel_position = 0;
      Carousel_homing = 0;
      Carousel_graden = 0;
      break;
  }
}

void move_stepper() {
  String motor_dir = from_pc_doc["Motor"].as<String>();
  if (motor_dir == "F") {
    stepper_C.startRotate(360 * 10);
  }
  if (motor_dir == "R") {
    stepper_C.startRotate(-360 * 10);
  }


}

//stepper_C.startRotate(360*10);                     // or in degrees
//stepper_T.startRotate(360*10);                     // or in degrees

/*
    Choosing stop() vs startBrake():
    constant speed mode, they are the same (stop immediately)
    linear (accelerated) mode with brake, the motor will go past the stopper a bit
*/
//stepper.stop();
// stepper.startBrake();

//--------------------Includes and librarys--------------------
#include <ArduinoJson.h>
#include <Arduino.h>
#include "BasicStepperDriver.h"
#include <SimpleTimer.h>
#include <RGBLed.h>

//--------------------Define stepper motor--------------------
// stepper carusel
#define MOTOR_STEPS_C 1600
#define DIR_C 14
#define STEP_C 15
// Target RPM
#define RPM_C 10
// Acceleration and deceleration values are always in FULL steps / s^2
#define MOTOR_ACCEL_C 250
#define MOTOR_DECEL_C 250
// 1=full step, 2=half step etc.
BasicStepperDriver stepper_C(MOTOR_STEPS_C, DIR_C, STEP_C);

//Stepper transportband
#define DIR_T 4
#define STEP_T 6
#define direction_T LOW
#define standardSnelheid 4
byte snelheid_T = 0;

//--------------------Output define--------------------
#define W_led 9
#define B_led 10
#define G_led 11
#define R_led 12
#define Dc_motor2 8
#define Dc_motor1 7

//--------------------Input define--------------------
#define D4 26
#define D3 27
#define D2 28
#define D1 29
#define Opto1 30
#define Opto2 31

#define Home_hall 32


//--------------------Global declaration--------------------
StaticJsonDocument<600> from_pc_doc;
StaticJsonDocument<600> to_pc_doc;
StaticJsonDocument<600> old_to_pc_doc;

int D4_state = 0;
int D3_state = 0;
int D2_state = 0;
int D1_state = 0;
int Opto1_state = 0;
int Opto2_state = 0;


byte Carousel_homing = 0;
int Carousel_position = 0;
int Carousel_position_queue = 0;
int Carousel_ofset = -33;
int Carousel_graden = 0;

int bakPositions[] = {32, 65, 98, 130, 163, 196, 229, 261, 294, 327, 360}; 

bool json_update = 1;

bool newMove = 0; 

//--------------------Timer Prepare-----------------
SimpleTimer homingTimer(1000);
SimpleTimer printTimer(2000);

//--------------------RGB setup--------------------
RGBLed led(R_led, G_led, B_led, RGBLed::COMMON_CATHODE);
String RGB_status = "";


//--------------------setup--------------------
void setup() {
  Serial_setup();
  IO_setup();
  Stepper_setup();

  from_pc_doc["Status_pc"] = "";
  from_pc_doc["RGB_led"] = "Rood_arduino";
  from_pc_doc["Dc_motor1"] = 0;
  from_pc_doc["Dc_motor2"] = 0;
  from_pc_doc["Conveyor_speed"] = standardSnelheid;
  from_pc_doc["Conveyor_IO"] = "0";
  from_pc_doc["Conveyor_direction"] = "";
  from_pc_doc["Carousel_speed"] = RPM_C;
  from_pc_doc["Carousel_bakkje"] = 0;
  from_pc_doc["Carousel_command"] = "";

  to_pc_doc["Status_arduino"] = "Ready";
  to_pc_doc["D4"] = false;
  to_pc_doc["D3"] = false;
  to_pc_doc["D2"] = false;
  to_pc_doc["D1"] = false;
  to_pc_doc["Opto1"] = false;
  to_pc_doc["Opto2"] = false;

  
  
  //Serial.println("START");

}
//--------------------loop--------------------
void loop() {
  stepper_loop();
  IO_read();
  Serial_loop();
  json_send();
  Carousel_homing_function();
  carousel_GoPos();

  if (json_update == 1){
    json_update = 0;
    IO_write();
    RGB_ledStrip();
    transportband();
  }

}

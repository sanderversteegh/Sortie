void RGB_ledStrip() {
  if (RGB_status != from_pc_doc["RGB_led"]) {
    RGB_status = from_pc_doc["RGB_led"].as<String>();
    
    String RGB_waarde = from_pc_doc["RGB_led"];
    if (RGB_waarde == "Rood") {
      // Fade in red color, with 5 steps during 100ms
      led.fadeIn(RGBLed::RED, 100, 100);
    }
    else if (RGB_waarde == "Rood_arduino") {
      led.flash(RGBLed::RED, 500); // Interval 100ms
    }
    else if (RGB_waarde == "Groen") {
      // Fade in red color, with 5 steps during 100ms
      led.fadeIn(RGBLed::GREEN, 100, 100);
    }
    else if (RGB_waarde == "Oranje") {
      led.fadeIn(255, 165, 0, 100, 100); // Fade in with 5 steps during 100ms
    }
    else {
      //Serial.println("RGB led error");
    }
  }
}

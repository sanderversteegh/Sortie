# import the necessary packages
from tkinter.constants import FALSE, TRUE
from imutils.video import VideoStream
import datetime
import argparse
import imutils
import time
import cv2
import threading
import pathlib
import os
import serial
import json

#widndows
#ser = serial.Serial('COM10', 115200, timeout=1)
#linux
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

ser.reset_output_buffer()
ser.reset_input_buffer()

time.sleep(1)


# construct the argument parser and parse the arguments
min_area = 500

# if the video argument is None, then we are reading from webcam
vs = VideoStream(src=0).start()
time.sleep(2.0)
# otherwise, we are reading from a video file
# initialize the first frame in the video stream
firstFrame = None
frame_o = None
blokje = False
callback = False
counter = 0

NewSerialdata = ""
dict_update = False
to_arduino_dict = {
    "Status_pc": 'Booting',
    "W_led": 255,
    "RGB_led": 'Rood',
    "Dc_motor1": 0,
    "Dc_motor2": 0,
    "Conveyor_speed": 12,
    "Conveyor_IO": "0",
    "Conveyor_direction": 'F',
    "Carousel_speed": 50,
    "Carousel_bakkje": 0,
    "Carousel_command": ''
}

old_arduino_dict = {
    "Status_pc": 'Booting',
    "W_led": 255,
    "RGB_led": 'Rood',
    "Dc_motor1": 0,
    "Dc_motor2": 0,
    "Conveyor_speed": 0,
    "Conveyor_IO": "0",
    "Conveyor_direction": 'F',
    "Carousel_speed": 0,
    "Carousel_bakkje": 0,
    "Carousel_command": ''
}

from_arduino_dict = {
    "Status_arduino": "",
    "D4": False,
    "D3": False,
    "D2": False,
    "D1": False,
    "Opto1": False,
    "Opto2": False
}


def update_dict(item, value):
    global to_arduino_dict
    global dict_update
    dict_update = True
    to_arduino_dict[item] = value


def send_json():
    global NewSerialdata
    global to_arduino_dict
    global old_arduino_dict


serial_Update = 0
first_boot = False



def SerialComLoop():
    global serial_Update
    global first_boot
    global dict_update
    global to_arduino_dict
    global old_arduino_dict
    global from_arduino_dict
    global serq

    # Check if incoming bytes are waiting to be read from the serial input
    # buffer.
    if (ser.inWaiting() > 0):
        serial_Update = 1
        # time.sleep(0.01)
        # read the bytes and convert from binary array to ASCII
        data_str = ser.readline().decode('ascii')
        #data_str = ser.readline(ser.inWaiting()).decode('ascii')
        # ('\n') automatically after every print()
        #print("incomming serial data:")
        print(data_str, end='')

    if serial_Update == 1:
        serial_Update = 0
        if (data_str[0] != "#"):
            try:
                from_arduino_dict = json.loads(data_str)
            except ValueError:
                print("Json error")
                #print (sys.exc_info())
        else:
            print("Debug data")
            print(data_str)

    if from_arduino_dict.get("Status_arduino") == "Ready" and first_boot == False:
        print("Arduino ready")
        first_boot = True
        update_dict("Conveyor_IO", "1")

    if first_boot:
        if from_arduino_dict.get("Status_arduino") == "Homing" and to_arduino_dict.get("Carousel_command") != "":
            print("Busy homing")
            update_dict("Carousel_command", "")

        if dict_update:
            dict_update = False
            data = json.dumps(to_arduino_dict)
            NewSerialdata = (data.encode('ascii'))   # send the pyte string 'H'
            print('New data to send:')
            print(NewSerialdata)
            ser.write(bytearray(NewSerialdata))
            NewSerialdata = ""


def callback_band():
    global callback
    global frame_o
    global counter
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PREFIX = 'detected'
    EXTENSION = 'jpg'
    file_name_format = "{:s}-{:d}-{:%Y%m%d_%H%M%S}.{:s}"
    date = datetime.datetime.now()
    not_detected_posture = 0
    file_name = file_name_format.format(
        PREFIX, not_detected_posture, date, EXTENSION)
    file_path = BASE_DIR + file_name
    update_dict("Conveyor_IO", "0")
    print("Stop band")
    time.sleep(1)
    if not cv2.imwrite(file_path, frame_o):
        raise Exception("Could not write image")
    else:
        print("File path = '%s'" % file_path)
        counter = counter + 1
        print("Counter: ")
        print(counter)
        cv2.putText(frame_o, "counter: {}".format(counter), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
        cv2.imshow("Image", frame_o)
    callback = True
    update_dict("Conveyor_IO", "1")
    print("band aan, weg met blokje")
    return


# loop over the frames of the video
while True:
    SerialComLoop()
    if first_boot:
        # grab the current frame and initialize the occupied/unoccupied
        # text
        frame_o = vs.read()

        text = "Geen blokje"
        # resize the frame, convert it to grayscale, and blur it
        #max frame size 720x1280
        #img[start_row:end_row, start_col:end_col]
        cropped_image = frame_o[0:720, 170:950]
        #cv2.imshow("cropped", cropped_image)

        #print(frame_o.shape[0])
        #print(frame_o.shape[1])
        

        frame = imutils.resize(cropped_image, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            continue

        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 60, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) == 0:
            if callback == True:
                print("callback off")
                blokje = False
                callback = False

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < min_area:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Blokje"
            if blokje == False:
                timer = threading.Timer(0.50, callback_band)
                timer.start()
                blokje = True

        # draw the text and timestamp on the frame
        cv2.putText(frame, "Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        # show the frame and record if the user presses a key
        
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frameDelta)
        cv2.imshow("Security Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break
        elif key == ord("p"):
            print("New frame")
            firstFrame = gray
        elif key == ord("f"):
            print("Force picture")
            timer = threading.Timer(0.50, callback_band)
            timer.start()
# cleanup the camera and close any open windows
update_dict("Conveyor_IO", "0")
SerialComLoop()
vs.stop()
cv2.destroyAllWindows()

import threading
import time
import cv2
import serial
import json
import var
import time
from serialcom import update_dict, serialFunc
import sched, time
import jetson.inference
import jetson.utils
import imutils

s = sched.scheduler(time.time, time.sleep)

def justBootFunc():
	print ("----------------execute just boot")
	justBoot_th = threading.currentThread()
	time.sleep(2)
	while getattr(justBoot_th, "run", True):	
		if var.from_arduino_dict.get("Status_arduino") == "Ready":
			print ("Arduino ready")
			var.currentMode = 2
			break
		time.sleep(0.1)
		

def resettingFunc():
	print ("----------------execute resset")
	resetting_th = threading.currentThread()
	step = 0
	while getattr(resetting_th, "run", True):
		if step ==  0:
			update_dict("Carousel_command", "Home")
			step += 1

		elif step == 1:
			if var.from_arduino_dict.get("Status_arduino") == "Homing":
				print("Busy homing")
				update_dict("Carousel_command", "")
				step += 1
		
		elif step == 2:
			if var.from_arduino_dict.get("Status_arduino") == "Ready":
				print("Homing done")
				step += 1
				
		elif step == 3:
			var.currentMode = 3
			break
		time.sleep(0.1)
		



def readyFunc():
	print ("----------------execute ready")

def errorFunc():
	print ("----------------execute error")

Vstate = 0

def turnOnVCallBack():
	global Vstate
	if Vstate == 0:
		Vstate = 1
		update_dict("Dc_motor1", var.DC_MOTOR1_SPEED)
		s.enter(3, 1, turnOnVCallBack)
	else:
		Vstate = 0
		update_dict("Dc_motor1", 0)
		s.enter(10, 1, turnOnVCallBack)


orgImg = None
callback = False

def callback_band():
	global callback
	print ("Zie blokje")
	callback = True
	update_dict("Conveyor_IO", "0")
	time.sleep(0.5)
	class_id, confidence = net.Classify(orgImg)
	print(class_id)
	update_dict("Conveyor_IO", "1")
	return


def runningFunc():
	global orgImg
	global callback
	global net
	firstFrame = None
	blokje = False
	print ("----------------execute running")
	running_th = threading.currentThread()
	#s.enter(2, 1, turnOnVCallBack)
		
	update_dict("Dc_motor2", var.DC_MOTOR2_SPEED)
	update_dict("Conveyor_IO", "1")
	argvString = ('--model=' + var.MODEL + '--labels=' + var.LABELS + '--input-blob=input_0' '--output-cvg=output_0')
	print(argvString)
	net = jetson.inference.imageNet(argv=['--netwerk=restnet18', '--model=models/lego51/lego51.onnx', '--labels=data/lego5/labels.txt', '--input_blob=input_0', '--output_blob=output_0'])
	font = jetson.utils.cudaFont()
	output = jetson.utils.videoOutput()
	#input = jetson.utils.videoSource('/dev/video0')

	while getattr(running_th, "run", True):
		s.run(blocking=False)
		text = "Geen blokje"
		orgImg = var.streamInput.Capture()
		# convert to BGR, since that's what OpenCV expects
		bgr_img = jetson.utils.cudaAllocMapped(width=orgImg.width,
							    height=orgImg.height,
							    format='bgr8')
		jetson.utils.cudaConvertColor(orgImg, bgr_img)
		jetson.utils.cudaDeviceSynchronize()
		cv_img = jetson.utils.cudaToNumpy(bgr_img)
		var.newestFrame = cv_img
		

		cropped_image = cv_img[0:720, 170:950]
		frame = imutils.resize(cropped_image, width=500)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)
		
		# if the first frame is None, initialize it
		if firstFrame is None:
			firstFrame = gray
			
		# compute the absolute difference between the current frame and first frame
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
				blokje = False
				callback = False


		# loop over the contours
		for c in cnts:
		    # if the contour is too small, ignore it
			if cv2.contourArea(c) < var.MIN_AREA:
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

		cv2.putText(frame, "Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

		cv2.imshow("Thresh", thresh)
		cv2.imshow("Frame Delta", frameDelta)
		cv2.imshow("Security Feed", frame)

		#class_id, confidence = net.Classify(orgImg)
		#class_desc = net.GetClassDesc(class_id)
		


		#net.PrintProfilerTimes()

		time.sleep(0.01)
	
	cv2.destroyAllWindows()
		

def traysFunc():
	print ("----------------execute trays")


def stopAll():
	update_dict("Dc_motor2", 0)
	update_dict("Dc_motor2", 0)
	update_dict("Conveyor_IO", "0")
	print("alles uit")


def modes(arg):
	availableModes = {
		1: justBootFunc,
		2: resettingFunc,
		3: readyFunc,
		4: errorFunc,
		5: runningFunc,
		6: traysFunc
	}

	return availableModes.get(arg)



def securityTh():
	securityTh_th = threading.currentThread()
	counter = 0
	while getattr(securityTh_th, "run", True):
		#print ("alive? ", counter)
		counter += 1
		time.sleep(0.1)



def main_program ():
	main_program_th = threading.currentThread()
	oldMode = None
	mode_th = threading.Thread()
	while getattr(main_program_th, "run", True):
		if oldMode != var.currentMode:
			oldMode = var.currentMode
			mode_th.run = False
			execute = modes(var.currentMode)
			mode_th = threading.Thread(target=execute)
			mode_th.start()
			print('mode change')
		serialFunc()
		time.sleep(0.001)

	mode_th.run = False


		


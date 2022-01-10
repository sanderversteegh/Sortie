import serial
import json
import var
import threading
import time
import sys

#widndows
#ser = serial.Serial('COM10', 115200, timeout=1)
#linux
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

def serialBoot():
	ser.setDTR(False)
	ser.reset_output_buffer()
	ser.reset_input_buffer()
	time.sleep(2)
	ser.setDTR(True)


NewSerialdata = ""
serial_Update = 0
dict_update = False
to_arduino_dict = {
    "Status_pc": 'Booting',
    "W_led" : 0,
    "RGB_led" : 'Rood',
    "Dc_motor1" : 0,
    "Dc_motor2" : 0,
    "Conveyor_speed"  : 4,
    "Conveyor_IO"  : "0",
    "Conveyor_direction"  : 'F',
    "Carousel_speed" : 50,
    "Carousel_bakkje": 0,
    "Carousel_command" : ''
} 



old_arduino_dict = {
    "Status_pc": 'Booting',
    "W_led" : 0,
    "RGB_led" : 'Rood',
    "Dc_motor1" : 0,
    "Dc_motor2" : 0,
    "Conveyor_speed"  : 0,
    "Conveyor_IO"  : "0",
    "Conveyor_direction"  : 'F',
    "Carousel_speed" : 0,
    "Carousel_bakkje": 0,
    "Carousel_command" : ''
} 

def update_dict(item, value):
    global to_arduino_dict
    global dict_update
    dict_update = True
    to_arduino_dict[item] = value


def serialTh():
	global serial_Update
	global dict_update
	global NewSerialdata
	serialTh_th = threading.currentThread()
	#widndows
	ser = serial.Serial('COM10', 115200, timeout=1)
	#linux
	#ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
	ser.setDTR(False)
	ser.reset_output_buffer()
	ser.reset_input_buffer()
	time.sleep(1)
	ser.setDTR(True)
	while getattr(serialTh_th, "run", True):	
		# Check if incoming bytes are waiting to be read from the serial input 
		# buffer.
		if (ser.inWaiting() > 0):
			serial_Update = 1
			#time.sleep(0.01)
			# read the bytes and convert from binary array to ASCII
			data_str = ser.readline().decode('ascii') 
			#data_str = ser.readline(ser.inWaiting()).decode('ascii') 
			# ('\n') automatically after every print()
			#print("incomming serial data:")
			print(data_str, end='')
			
		if serial_Update ==  1:
			serial_Update = 0
			if (data_str[0] != "#"):
				try:
					var.from_arduino_dict = json.loads(data_str) 
				except ValueError:
					print ("Json error")
					print (sys.exc_info())
			else:
				print("Arduino Debug data")
				print(data_str)

		if dict_update:
			dict_update = False
			data = json.dumps(to_arduino_dict)
			NewSerialdata = (data.encode('ascii'))   # send the pyte string 'H'
			print('New data to send:')
			print(NewSerialdata)
			ser.write(bytearray(NewSerialdata))
			NewSerialdata = ""
		time.sleep(0.05)

def serialFunc():
	global serial_Update
	global dict_update
	global NewSerialdata
	global ser	
	# Check if incoming bytes are waiting to be read from the serial input 
	# buffer.
	if (ser.inWaiting() > 0):
		serial_Update = 1
		#time.sleep(0.01)
		# read the bytes and convert from binary array to ASCII
		data_str = ser.readline().decode('ascii') 
		#data_str = ser.readline(ser.inWaiting()).decode('ascii') 
		# ('\n') automatically after every print()
		#print("incomming serial data:")
		print(data_str, end='')
		
	if serial_Update ==  1:
		serial_Update = 0
		if (data_str[0] != "#"):
			try:
				var.from_arduino_dict = json.loads(data_str) 
			except ValueError:
				print ("Json error")
				print (sys.exc_info())
		else:
			print("Arduino Debug data")
			print(data_str)

	if dict_update:
		dict_update = False
		data = json.dumps(to_arduino_dict)
		NewSerialdata = (data.encode('ascii'))   # send the pyte string 'H'
		print('New data to send:')
		print(NewSerialdata)
		ser.write(bytearray(NewSerialdata))
		NewSerialdata = ""
streamInput = None
newestFrame = None
currentMode =  1


DC_MOTOR1_SPEED = 240
DC_MOTOR2_SPEED = 220

MIN_AREA = 500

MODEL = 'models/lego44/lego44.onnx'
NETWORK = 'restnet18'
LABELS = 'data/lego4/labels.txt'



from_arduino_dict =  {
	"Status_arduino": "",
    "D4" : False,
    "D3" : False,
    "D2" : False,
    "D1" : False,
    "Opto1" : False,
    "Opto2" : False
}
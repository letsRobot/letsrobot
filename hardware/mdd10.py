# TODO pull out pin numbering and drivingSpeedActuallyUsed into
# conf file. Pull driving speed actually used code from motor hat into here.

import RPi.GPIO as GPIO
import schedule

maxSpeedEnabled = False
AN1 - None
AN2 = None
DIG1 = None
DIG2 = None
turnDelay = None
straightDelay = None

#Cytron MDD10 GPIO setup
def setup(robot_config):
    global AN1
    global AN2
    global DIG1
    global DIG2
    global turnDelay
    global straightDelay

    straightDelay = robot_config.getfloat('robot', 'straight_delay')
    turnDelay = robot_config.getfloat('robot', 'turn_delay')

    
#    pwm.setPWMFreq(60)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    AN2 = 13
    AN1 = 12
    DIG2 = 24
    DIG1 = 26
    GPIO.setup(AN2, GPIO.OUT)
    GPIO.setup(AN1, GPIO.OUT)
    GPIO.setup(DIG2, GPIO.OUT)
    GPIO.setup(DIG1, GPIO.OUT)
    time.sleep(1)
    p1 = GPIO.PWM(AN1, 100)
    p2 = GPIO.PWM(AN2, 100)


def SpeedNormal():
    maxSpeedEnabled = False
    print("normal speed")

#MDD10 speed and movement controls
def move(args):
    global maxSpeedEnabled
	                
	  command = args['command']
    if command == 'MAXSPEED':
        handleMaxSpeedCommand()
        maxSpeedEnabled = True
        print("max speed")
        schedule.single_task(120, SpeedNormal)        
        return
        
    if maxSpeedEnabled:
        print("AT MAX.....................")
        print(maxSpeedEnabled)
        moveMDD10(command, 100)
    else:
        print("NORMAL.................")
        print(maxSpeedEnabled)
        moveMDD10(command, int(float(drivingSpeedActuallyUsed) / 2.55))                


def moveMDD10(command, speedPercent):
    if command == 'F':
        GPIO.output(DIG1, GPIO.LOW)
        GPIO.output(DIG2, GPIO.LOW)
        p1.start(speedPercent)  # set speed for M1 
        p2.start(speedPercent)  # set speed for M2 
        time.sleep(straightDelay)
        p1.start(0)
        p2.start(0)
    if command == 'B':
        GPIO.output(DIG1, GPIO.HIGH)
        GPIO.output(DIG2, GPIO.HIGH)
        p1.start(speedPercent)
        p2.start(speedPercent)
        time.sleep(straightDelay)
        p1.start(0)
        p2.start(0)
    if command == 'L':
        GPIO.output(DIG1, GPIO.LOW)
        GPIO.output(DIG2, GPIO.HIGH)
        p1.start(speedPercent)
        p2.start(speedPercent)
        time.sleep(turnDelay)
        p1.start(0)
        p2.start(0)
    if command == 'R':
        GPIO.output(DIG1, GPIO.HIGH)
        GPIO.output(DIG2, GPIO.LOW)
        p1.start(speedPercent)
        p2.start(speedPercent)
        time.sleep(turnDelay)
        p1.start(0)
        p2.start(0)

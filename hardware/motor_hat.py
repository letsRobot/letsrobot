import RPi.GPIO as GPIO
import datetime
import os
import getpass
import random
import atexit
import networking
import tts.tts as tts
import json
import time
import logging
log = logging.getLogger('RemoTV.hardware.motor_hat')

try:
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
    motorsEnabled = True
except ImportError:
    log.critical("You need to install Adafruit_MotorHAT")
    log.critical("Please install Adafruit_MotorHAT for python and restart this script.")
    log.critical("To install: cd /usr/local/src && sudo git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git")
    log.critical("cd /usr/local/src/Adafruit-Motor-HAT-Python-Library && sudo python setup.py install")
    log.error("Motorhat running in test mode.")
    log.error("Ctrl-C to quit")
    motorsEnabled = False

# todo: specificity is not correct, this is specific to a bot with a claw, not all motor_hat based bots
#from Adafruit_PWM_Servo_Driver import PWM

mh = None
motorA = None
motorB = None
turningSpeedActuallyUsed = None
dayTimeDrivingSpeedActuallyUsed = None
nightTimeDrivingSpeedActuallyUsed = None
drivingSpeed = 0
chargeValue = 100

secondsToCharge = None
secondsToDischarge = None
chargeIONumber = None

forward = None
backward = None
left = None
right = None

straightDelay = None
turnDelay = None


servoMin = [150, 150, 130]  # Min pulse length out of 4096
servoMax = [600, 600, 270]  # Max pulse length out of 4096
armServo = [300, 300, 300]

def setSpeedBasedOnCharge(chargeValue):
    global dayTimeDrivingSpeedActuallyUsed
    global nightTimeDrivingSpeedActuallyUsed

    if chargeValue < 30:
        multiples = [0.2, 1.0]
        multiple = random.choice(multiples)
        dayTimeDrivingSpeedActuallyUsed = int(float(commandArgs.day_speed) * multiple)
        nightTimeDrivingSpeedActuallyUsed = int(float(commandArgs.night_speed) * multiple)
    else:
        dayTimeDrivingSpeedActuallyUsed = commandArgs.day_speed
        nightTimeDrivingSpeedActuallyUsed = commandArgs.night_speed

def updateChargeApproximation():

    global chargeValue
    
    username = getpass.getuser()
    path = "/home/pi/charge_state_%s.txt" % username

    # read charge value
    # assume it is zero if no file exists
    if os.path.isfile(path):
        file = open(path, 'r')
        try:
            chargeValue = float(file.read())
            log.error("error reading float from file", path)
        except:
            chargeValue = 0
        file.close()
    else:
        log.info("setting charge value to zero")
        chargeValue = 0

    chargePerSecond = 1.0 / secondsToCharge
    dischargePerSecond = 1.0 / secondsToDischarge
    
    if GPIO.input(chargeIONumber) == 1:
        chargeValue += 100.0 * chargePerSecond * chargeCheckInterval
    else:
        chargeValue -= 100.0 * dischargePerSecond * chargeCheckInterval

    if chargeValue > 100.0:
        chargeValue = 100.0
    if chargeValue < 0:
        chargeValue = 0.0
        
    # write new charge value
    file = open(path, 'w')
    file.write(str(chargeValue))
    file.close()        

    log.debug("charge value updated to", chargeValue)
    return chargeValue

# true if it's on the charger and it needs to be charging
def isCharging():
    log.info("is charging current value", chargeValue)

    # only tested for motor hat robot currently, so only runs with that type
    if commandArgs.type == "motor_hat":
        log.debug("RPi.GPIO is in sys.modules")
        if chargeValue < 99: # if it's not full charged already
            log.debug("charge value is low")
            return GPIO.input(chargeIONumber) == 1 # return whether it's connected to the dock

    return False
    
def sendChargeState():
    networking.sendChargeState(isCharging())

def sendChargeStateCallback(x):
    sendChargeState()

#schedule a task to report charge status to the server
def sendChargeState_task():
    if commandArgs.type == 'motor_hat':
        chargeValue = updateChargeApproximation()
        sendChargeState()
        if slow_for_low_battery:
            setSpeedBasedOnCharge(chargeValue)


#schedule tasks to tts out a message about battery percentage and need to charge
def reportBatteryStatus_task():
    if chargeValue < 30:
        tts.say("battery low, %d percent" % int(chargeValue))


def reportNeedToCharge():
    if not isCharging():
        if chargeValue <= 25:
            tts.say("need to charge")


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

def incrementArmServo(channel, amount):

    armServo[channel] += amount

    log.debug("arm servo positions:", armServo)

    if armServo[channel] > servoMax[channel]:
        armServo[channel] = servoMax[channel]
    if armServo[channel] < servoMin[channel]:
        armServo[channel] = servoMin[channel]
    pwm.setPWM(channel, 0, armServo[channel])

def runMotor(motorIndex, direction):
    motor = mh.getMotor(motorIndex+1)
    if direction == 1:
        motor.setSpeed(drivingSpeed)
        motor.run(Adafruit_MotorHAT.FORWARD)
    if direction == -1:
        motor.setSpeed(drivingSpeed)
        motor.run(Adafruit_MotorHAT.BACKWARD)
    if direction == 0.5:
        motor.setSpeed(128)
        motor.run(Adafruit_MotorHAT.FORWARD)
    if direction == -0.5:
        motor.setSpeed(128)
        motor.run(Adafruit_MotorHAT.BACKWARD)

def times(lst, number):
    return [x*number for x in lst]


def setup(robot_config):
    global mh
    global motorA
    global motorB
    global turningSpeedActuallyUsed
    global dayTimeDrivingSpeedActuallyUsed
    global nightTimeDrivingSpeedActuallyUsed
    global secondsToCharge
    global secondsToDischarge
    global chargeIONumber
    global forward
    global backward
    global left
    global right
    global straightDelay
    global turnDelay

    GPIO.setmode(GPIO.BCM)
    chargeIONumber = robot_config.getint('motor_hat', 'chargeIONumber')
    GPIO.setup(chargeIONumber, GPIO.IN)
    secondsToCharge = 60.0 * 60.0 * robot_config.getfloat('motor_hat', 'charge_hours')
    secondsToDischarge = 60.0 * 60.0 * robot_config.getfloat('motor_hat', 'discharge_hours')

    forward = json.loads(robot_config.get('motor_hat', 'forward'))
    backward = times(forward, -1)
    left = json.loads(robot_config.get('motor_hat', 'left'))
    right = times(left, -1)

    straightDelay = robot_config.getfloat('robot', 'straight_delay')
    turnDelay = robot_config.getfloat('robot', 'turn_delay')


    if motorsEnabled:
        # create a default object, no changes to I2C address or frequency
        mh = Adafruit_MotorHAT(addr=0x60)
        #mhArm = Adafruit_MotorHAT(addr=0x61)
        atexit.register(turnOffMotors)
        motorA = mh.getMotor(1)
        motorB = mh.getMotor(2)

    # Initialise the PWM device
#    pwm = PWM(0x42)
#    pwm.setPWMFreq(60)    # Set frequency to 60 Hz
    
    turningSpeedActuallyUsed = robot_config.getint('motor_hat', 'turning_speed')
    dayTimeDrivingSpeedActuallyUsed = robot_config.getint('motor_hat', 'day_speed')
    nightTimeDrivingSpeedActuallyUsed = robot_config.getint('motor_hat', 'night_speed')

    if robot_config.getboolean('motor_hat', 'slow_for_low_battery'):
        GPIO.add_event_detect(chargeIONumber, GPIO.BOTH)
        GPIO.add_event_callback(chargeIONumber, sendChargeStateCallback)
        chargeCheckInterval = int(robot_config.getint('motor_hat', 'chargeCheckInterval'))
    
        if (robot_config.get('tts', 'type') != 'none'):
            schedule.repeat_task(60, reportBatteryStatus_task)
            schedule.repeat_task(17, reportNeedToCharge)
            schedule.task(chargeCheckInterval, sendChargeState_task)
        


def move( args ):
    command = args['button']['command']

    global drivingSpeed
    
    now = datetime.datetime.now()
    now_time = now.time()
    # if it's late, make the robot slower
    if now_time >= datetime.time(21,30) or now_time <= datetime.time(9,30):
        #print("within the late time interval")
        drivingSpeedActuallyUsed = nightTimeDrivingSpeedActuallyUsed
    else:
        drivingSpeedActuallyUsed = dayTimeDrivingSpeedActuallyUsed
    
    motorA.setSpeed(drivingSpeed)
    motorB.setSpeed(drivingSpeed)
    if command == 'f':
        drivingSpeed = drivingSpeedActuallyUsed
        for motorIndex in range(4):
            runMotor(motorIndex, forward[motorIndex])
        time.sleep(straightDelay)
    if command == 'b':
        drivingSpeed = drivingSpeedActuallyUsed
        for motorIndex in range(4):
            runMotor(motorIndex, backward[motorIndex])
        time.sleep(straightDelay)
    if command == 'l':
        drivingSpeed = turningSpeedActuallyUsed
        for motorIndex in range(4):
            runMotor(motorIndex, left[motorIndex])
        time.sleep(turnDelay)
    if command == 'r':
        drivingSpeed = turningSpeedActuallyUsed
        for motorIndex in range(4):
            runMotor(motorIndex, right[motorIndex])
        time.sleep(turnDelay)
    if command == 'u':
        #mhArm.getMotor(1).setSpeed(127)
        #mhArm.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
        incrementArmServo(1, 10)
        time.sleep(0.05)
    if command == 'd':
        #mhArm.getMotor(1).setSpeed(127)
        #mhArm.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
        incrementArmServo(1, -10)
        time.sleep(0.05)
    if command == 'o':
        #mhArm.getMotor(2).setSpeed(127)
        #mhArm.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
        incrementArmServo(2, -10)
        time.sleep(0.05)
    if command == 'c':
        #mhArm.getMotor(2).setSpeed(127)
        #mhArm.getMotor(2).run(Adafruit_MotorHAT.FORWARD)
        incrementArmServo(2, 10)
        time.sleep(0.05)

    turnOffMotors()

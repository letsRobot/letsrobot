import RPi.GPIO as GPIO
import time

Motor1A = None
Motor1B = None
Motor1Enable = None
Motor2A = None
Motor2B = None
Motor2Enable = None
Motor3A = None
Motor3B = None
Motor3Enable = None
Motor4A = None
Motor4B = None
Motor4Enable = None
MotorDelay = None

def setup(robot_config):
    global Motor1A
    global Motor1B
    global Motor1Enable
    global Motor2A
    global Motor2B
    global Motor2Enable
    global Motor3A
    global Motor3B
    global Motor3Enable
    global Motor4A
    global Motor4B
    global Motor4Enable
    global MotorDelay

    Motor1A = robot_config/getint('motozero', 'Motor1A')
    Motor1B = robot_config/getint('motozero', 'Motor1B')
    Motor1Enable = robot_config/getint('motozero', 'Motor1Enable')
    Motor2A = robot_config/getint('motozero', 'Motor2A')
    Motor2B = robot_config/getint('motozero', 'Motor2B')
    Motor2Enable = robot_config/getint('motozero', 'Motor2Enable')
    Motor3A = robot_config/getint('motozero', 'Motor3A')
    Motor3B = robot_config/getint('motozero', 'Motor3B')
    Motor3Enable = robot_config/getint('motozero', 'Motor3Enable')
    Motor4A = robot_config/getint('motozero', 'Motor4A')
    Motor4B = robot_config/getint('motozero', 'Motor4B')
    Motor4Enable = robot_config/getint('motozero', 'Motor4Enable')
    MotorDelay = robot_config.getfloat('motozero', 'MotorDelay')

    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.setup(Motor1Enable,GPIO.OUT)

    GPIO.setup(Motor2A,GPIO.OUT)
    GPIO.setup(Motor2B,GPIO.OUT)
    GPIO.setup(Motor2Enable,GPIO.OUT) 

    GPIO.setup(Motor3A,GPIO.OUT)
    GPIO.setup(Motor3B,GPIO.OUT)
    GPIO.setup(Motor3Enable,GPIO.OUT)

    GPIO.setup(Motor4A,GPIO.OUT)
    GPIO.setup(Motor4B,GPIO.OUT)
    GPIO.setup(Motor4Enable,GPIO.OUT)
	

def move(args):
    direction = args['command']
    
    if direction == 'F':
        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor1Enable,GPIO.HIGH)

        GPIO.output(Motor2B, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor3A, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor4B, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(MotorDelay)

        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        GPIO.output(Motor3A, GPIO.LOW)
        GPIO.output(Motor4B, GPIO.LOW)
    if direction == 'B':
        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor3B, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor4A, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(MotorDelay)

        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor3B, GPIO.LOW)
        GPIO.output(Motor4A, GPIO.LOW)

    if direction =='L':
        GPIO.output(Motor3B, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2B, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor4B, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(MotorDelay)

        GPIO.output(Motor3B, GPIO.LOW)
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        GPIO.output(Motor4B, GPIO.LOW)

    if direction == 'R':
        GPIO.output(Motor3A, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor4A, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(MotorDelay)

        GPIO.output(Motor3A, GPIO.LOW)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor4A, GPIO.LOW)

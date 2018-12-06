import logging
log = logging.getLogger('LR.hardware.mc33926')

try:
    from dual_mc33926_rpi import motors, MAX_SPEED
except ImportError:
    logging.critical("You need to install dual-mc33926-motor-driver-rpi")
    logging.critical("Please install dual-mc33926-motor-driver-rpi for python and restart this script.")
    logging.critical("To install: cd /usr/local/src && sudo git clone https://github.com/pololu/dual-mc33926-motor-driver-rpi")
    logging.critical("cd /usr/local/src/dual-mc33926-motor-driver-rpi && sudo python setup.py install")
    logging.info("mc33926 running in test mode.")
    logging.info("Ctrl-C to quit")

drivingSpeed = 0

def setup(robot_config):
    global drivingSpeed
    drivingSpeed = robot_config.getint('mc33926', 'driving_speed')   

def move(args):
    command = args['command']
    
    drivingSpeed = -180
    if direction == 'F':
              motors.enable()
              motors.setSpeeds(-drivingSpeed, drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()
    if direction == 'B':
              motors.enable()
              motors.setSpeeds(drivingSpeed, -drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()
    if direction == 'L':
              motors.enable()
              motors.setSpeeds(drivingSpeed, drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()
    if direction == 'R':
              motors.enable()
              motors.setSpeeds(-drivingSpeed, -drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()

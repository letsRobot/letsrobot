import logging
log = logging.getLogger('RemoTV.hardware.pololu')

try:
    from pololu_drv8835_rpi import motors, MAX_SPEED
except ImportError:
    log.critical("You need to install drv8835-motor-driver-rpi")
    log.critical("Please install drv8835-motor-driver-rpi for python and restart this script.")
    log.critical("To install: cd /usr/local/src && sudo git clone https://github.com/pololu/drv8835-motor-driver-rpi")
    log.critical("cd /usr/local/src/drv8835-motor-driver-rpi && sudo python setup.py install")
    log.info("pololu running in test mode.")
    log.info("Ctrl-C to quit")

drivingSpeed = 0

def setup(robot_config):
    global drivingSpeed
    drivingSpeed = robot_config.getint('pololu', 'driving_speed')
    
def move(args):
    command = args['button']['command']
    if direction == 'f':
	      motors.setSpeeds(drivingSpeed, drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)
    if direction == 'b':
	      motors.setSpeeds(-drivingSpeed, -drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)
    if direction == 'l':
	      motors.setSpeeds(-drivingSpeed, drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)
    if direction == 'r':
	      motors.setSpeeds(drivingSpeed, -drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)

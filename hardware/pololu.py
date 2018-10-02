try:
    from pololu_drv8835_rpi import motors, MAX_SPEED
except ImportError:
	print("You need to install drv8835-motor-driver-rpi")
    print("Please install drv8835-motor-driver-rpi for python and restart this script.")
    print("To install: cd /usr/local/src && sudo git clone https://github.com/pololu/drv8835-motor-driver-rpi")
    print("cd /usr/local/src/drv8835-motor-driver-rpi && sudo python setup.py install")
    print("Running in test mode.")
    print("Ctrl-C to quit")

drivingSpeed = 0

def setup(robot_config):
    global drivingSpeed
    drivingSpeed = robot_config.getint('pololu', 'driving_speed')
    
def move(args):
    command = args['command']
    if direction == 'F':
	      motors.setSpeeds(drivingSpeed, drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)
    if direction == 'B':
	      motors.setSpeeds(-drivingSpeed, -drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)
    if direction == 'L':
	      motors.setSpeeds(-drivingSpeed, drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)
    if direction == 'R':
	      motors.setSpeeds(drivingSpeed, -drivingSpeed)
	      time.sleep(0.3)
	      motors.setSpeeds(0, 0)

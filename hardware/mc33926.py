try:
    from dual_mc33926_rpi import motors, MAX_SPEED
except ImportError:
    print("You need to install dual-mc33926-motor-driver-rpi")
    print("Please install dual-mc33926-motor-driver-rpi for python and restart this script.")
    print("To install: cd /usr/local/src && sudo git clone https://github.com/pololu/dual-mc33926-motor-driver-rpi")
    print("cd /usr/local/src/dual-mc33926-motor-driver-rpi && sudo python setup.py install")
    print("Running in test mode.")
    print("Ctrl-C to quit")

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
              print("Forward")
    if direction == 'B':
              motors.enable()
              motors.setSpeeds(drivingSpeed, -drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()
              print("Backward")
    if direction == 'L':
              motors.enable()
              motors.setSpeeds(drivingSpeed, drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()
              print("Left")
    if direction == 'R':
              motors.enable()
              motors.setSpeeds(-drivingSpeed, -drivingSpeed)
              time.sleep(0.3)
              motors.setSpeeds(0, 0)
              motors.disable()
              print("Right")

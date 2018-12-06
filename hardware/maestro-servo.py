# You will need maestro.py from https://github.com/FRC4564/Maestro
#
# This is also just a place holder, it has not be tested with an actual
# bot.

import sys
import time
import logging
log = logging.getLogger('LR.hardware.maestro-servo')

try:
    import hardware.maestro
except ImportError:
    log.critical("You are missing the maestro.py file from the hardware subdirectory.")
    log.critical("Please download it from here https://github.com/FRC4564/Maestro")
    sys.exit()

servo = None

def setup(robot_config):
    global servo

    servo = maestro.Controller()
    servo.setAccel(0,4)
    servo.setAccel(1,4)
 
    servo.setTarget(0, 6000)
    servo.setTarget(1, 6000)
 
def move(args):
    direction = args['command']

    if direction == 'F':
        servo.setTarget(0, 12000)
        servo.setTarget(1, 12000)
        time.sleep(straightDelay)
        servo.setTarget(0, 6000)
        servo.setTarget(1, 6000)
    elif direction == 'B':
        servo.setTarget(0, 0)
        servo.setTarget(1, 0)
        time.sleep(straightDelay)
        servo.setTarget(0, 6000)
        servo.setTarget(1, 6000)
    elif direction == 'L':
        servo.setTarget(0, 0)
        servo.setTarget(1, 12000)
        time.sleep(turnDelay)
        servo.setTarget(0, 6000)
        servo.setTarget(1, 6000)
    elif direction == 'R':
        servo.setTarget(0, 12000)
        servo.setTarget(1, 0)
        time.sleep(turnDelay)
        servo.setTarget(0, 6000)
        servo.setTarget(1, 6000)


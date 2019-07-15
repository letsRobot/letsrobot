import logging
import sys
import time


import mod_utils
log = logging.getLogger('RemoTV.hardware.diddyborg')

try:
    import hardware.ThunderBorgLib as ThunderBorg
except:
    log.critical('Cannot start ThunderBorg. ThunderBorgLib.py missing. Do the following')
    log.critical('wget -O ~/examples.zip http://www.piborg.org/downlaods/thunderborg/examples.zip')
    log.critical('unzip ~/examples.zip')
    log.critical('cp ~/examples/ThunderBorg.py ~/remotv/hardware/ThunderBorgLib.py')
    sys.exit(1)


TB = ThunderBorg.ThunderBorg()
TB.Init()

leftMotorMax = None
rightMotorMax = None
sleepTime = None


def setup(robot_config):
    global leftMotorMax
    global rightMotorMax
    global sleepTime

    if not TB.foundChip:
        boards = ThunderBorg.ScanForThunderBorg()
        if len(boards) == 0:
            log.critical("No ThunderBorg found. Check you are attached.")
        else:
            log.critical(
                "No ThunderBorg found at address %02X, Found bords at" % TB.i2cAddress)
            for board in boards:
                log.critical('%02X (%d)' % (board, board))
            log.critical('Change the I2C address so that is is correct, e.g.')
            log.critical('TB.i2cAddress = 0x%02X' % boards[0])
        sys.exit(1)

    leftMotorMax = robot_config.getfloat('diddyborg', 'left_motor_max')
    rightMotorMax = robot_config.getfloat('diddyborg', 'right_motor_max')
    sleepTime = robot_config.getfloat('diddyborg', 'sleep_time')


def move(args):
    direction = args['button']['command'].upper()
    inverseRight = rightMotorMax * -1
    inverseLeft = leftMotorMax * -1

    if direction == 'F':
        TB.SetMotor1(inverseLeft)
        TB.SetMotor2(rightMotorMax)
    if direction == 'B':
        TB.SetMotor1(leftMotorMax)
        TB.SetMotor2(inverseRight)
    if direction == 'L':
        TB.SetMotor1(leftMotorMax)
        TB.SetMotor2(rightMotorMax)
    if direction == 'R':
        TB.SetMotor1(inverseLeft)
        TB.SetMotor2(inverseRight)

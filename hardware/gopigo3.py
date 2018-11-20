sys.path.append("/home/pi/Dexter/GoPiGo3/Software/Python")
import easygopigo3
import time

easyGoPiGo3=None
drive_time=None
turn_time=None

def setup(robot_config):
    global easyGoPiGo3
    global drive_time
    global turn_time

    easyGoPiGo3 = easygopigo3.EasyGoPiGo3()
    drive_time=robot_config.getfloat('gopigo2', 'drive_time')
    turn_time=robot_config.getfloat('gopigo2', 'turn_time')    

def move(args):
    command = args['command']
    e = easyGoPiGo3
    if command == 'L':
        e.set_motor_dps(e.MOTOR_LEFT, -e.get_speed())
        e.set_motor_dps(e.MOTOR_RIGHT, e.get_speed())
        time.sleep(turn_time)
        easyGoPiGo3.stop()
    if command == 'R':
        e.set_motor_dps(e.MOTOR_LEFT, e.get_speed())
        e.set_motor_dps(e.MOTOR_RIGHT, -e.get_speed())
        time.sleep(turn_time)
        easyGoPiGo3.stop()
    if command == 'F':
        easyGoPiGo3.forward()
        time.sleep(drive_time)
        easyGoPiGo3.stop()
    if command == 'B':
        easyGoPiGo3.backward()
        time.sleep(drive_time)
        easyGoPiGo3.stop()

    

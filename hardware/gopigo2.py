import gopigo
import time

drive_time=None
turn_time=None

def setup(robot_config):
    global drive_time
    global turn_time

    drive_time=robot_config.getfloat('gopigo2', 'drive_time')
    turn_time=robot_config.getfloat('gopigo2', 'turn_time')
    return    
    
def move(args):
    command = args['command']
    
    if command == 'L':
        gopigo.left_rot()
        time.sleep(0.15)
        gopigo.stop()
    if command == 'R':
        gopigo.right_rot()
        time.sleep(0.15)
        gopigo.stop()
    if command == 'F':
        gopigo.forward()
        time.sleep(0.35)
        gopigo.stop()
    if command == 'B':
        gopigo.backward()
        time.sleep(0.35)
        gopigo.stop()

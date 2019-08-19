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
    command = args['button']['command']
    
    if command == 'l':
        gopigo.left_rot()
        time.sleep(0.15)
        gopigo.stop()
    if command == 'r':
        gopigo.right_rot()
        time.sleep(0.15)
        gopigo.stop()
    if command == 'f':
        gopigo.forward()
        time.sleep(0.35)
        gopigo.stop()
    if command == 'b':
        gopigo.backward()
        time.sleep(0.35)
        gopigo.stop()

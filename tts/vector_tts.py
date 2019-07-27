# This is a dummy file to allow the automatic loading of modules without error on none.
import hardware.vector

vector = None
reserve_control = None

def setup(robot_config):
    global vector
    
    vector = hardware.vector.connect()
    return
   
def say(*args):
    message = args[0]
    vector.behavior.say_text(message, duration_scalar=0.75)
    return


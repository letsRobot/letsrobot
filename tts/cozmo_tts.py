import hardware.cozmo

def setup(robot_config):
    hardware.cozmo.setup_coz(robot_config)
    return
    
def say(*args):
    message = args[0]
    hardware.cozmo.say(message)
    return
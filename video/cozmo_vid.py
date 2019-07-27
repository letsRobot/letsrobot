# This is a dummy file to allow the automatic loading of modules without error on none.
import cozmo
import _thread as thread
import hardware.cozmo

def setup(robot_config):
    return
    
def start():
    try:
        thread.start_new_thread(hardware.cozmo.run_video, ())
    except KeyboardInterrupt as e:
        pass        
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

    return

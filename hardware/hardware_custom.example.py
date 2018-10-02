import mod_utils
import hardware.max7219
# Example for adding custom code to the controller
module = None

def setup(robot_config):
    global module
    # Your custom setup code goes here
    
 
 
    # Call the setup handler for max7219 LEDs
    hardware.max7219.setup(robot_config)
 
    # This code calls the default setup function for your hardware.
    # global module
    
#    module = __import__("hardware."+robot_config.get('robot', 'type'), fromlist=[robot_config.get('robot', 'type')])
    module = mod_utils.import_module('hardware', robot_config.get('robot', 'type'))
    module.setup(robot_config)
    
def move(args):
    # Your custom command interpreter code goes here
    
    
    
    # Call the command handler for max7219 LEDs
    hardware.max7219.move(args)
    
    # This code calls the default command interpreter function for your hardware.
    module.move(args)
    
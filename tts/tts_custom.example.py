import os
import mod_utils
# Example for adding custom code to the controller
hw_num = None
module = None

def setup(robot_config):
    global hw_num
    global module
    
    hw_num = robot_config.getint('tts', 'hw_num')
    # Your custom setup code goes here
    
 
    # Load the appropriate tts module and call the default tts setup routine
    module = mod_utils.import_module('tts', robot_config.get('tts', 'type'))
    module.setup(robot_config)
       
def say(*args):
    message = args[0]

    # Check the username on the chat message, and play a sound before the tts
    # message for particular users.
    # check if we are doing a simple say, or a chat tts message
    if len(args) > 1:
        user = args[1]['name']
        if user == 'jill':
            prefix = "harken.mp3"
        elif user == 'Geddy':
            prefix = "tremble.mp3"
        elif user == 'unacceptableuse':
            prefix = "relax.mp3"
        elif user == 'roboempress':
            prefix = "run.mp3"
        elif user == 'mikey':
            prefix = "meander.mp3"
        else:
            prefix = None
                
        if prefix != None:
            os.system('/usr/bin/mpg123-alsa -a hw:%d,0 %s' % (hw_num, prefix))

    # Your custom tts interpreter code goes here

    
    
    # This code calls the default command interpreter function for your hardware.
    if len(args) == 1:
        module.say(message)
    else:
        module.say(message, args[1])

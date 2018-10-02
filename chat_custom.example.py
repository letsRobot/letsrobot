import re
import os

# example for adding a custom chat handler
main_chat_handler = None


# Reboot function, to be added to the extended chat commands.
def reboot(*args):
    os.system('sudo shutdown -r now')
    exit()  

def setup(robot_config, chat_handler):
    global main_chat_handler
    
    # Any chat related setup code goes here


    
    # Add a reboot command to the extended chat commands
    if robot_config.getboolean('tts', 'ext_chat'):
        import extended_command
        extended_command.add_command('.reboot', reboot)    
    
    main_chat_handler = chat_handler
    
    
def handle_chat(args):
    # Your custom chat handling code goes here


    
    # Replace and mention of "john madden" with "the anti-christ"
    temp = re.compile(re.escape('john madden'), re.IGNORECASE)
    args['message'] = temp.sub('the anti-christ', args['message'])
     
    # Call the main chat handler
    main_chat_handler(args)




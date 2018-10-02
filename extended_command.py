from __future__ import print_function
import os
import networking
import tts.tts as tts
import schedule
import robot_util

# TODO 
# If I pull the send_video stuff into controller, the ability to restart the ffmpeg process would
# be useful

# /stationary only able to move left and right.
#/mod username
#/unmod username
#/stop username
#/unstop username
#/tts volume (int)
#/mic mute
#/mic unmute
#/xcontrol username
#/xcontrol username (int time)
#/xcontrol off
#/speed (int)


# Cant DO
# Can't do anything that requires server side stuff. Ban and timoue are do-able, 
# only on at the bot level.
#(blocking a user also bans them from your channel)
#/block username
#/unblock username


# Done
#/devmode on
#/devmode off
#/anon control on
#/anon control off
#/anon tts on
#/anon tts off
#/anon off
#/anon on
#/tts mute
#/tts unmute
#/brightness (int)
#/contrast (int)
#/saturation (int)
#/ban username
#/unban username
#/timeout username
#/untimeout username

move_handler = None
dev_mode = None
dev_mode_mods = False
anon_control = True
owner = None
v4l2_ctl = None
robot_id = None
api_key = None
stationary = None
banned=[]
mods=[]

def setup(robot_config):
    global owner
    global v4l2_ctl
    global robot_id
    global api_key
    global buttons_json
    
    owner = robot_config.get('robot', 'owner')
    v4l2_ctl = robot_config.get('misc', 'v4l2-ctl')
    robot_id = robot_config.get('robot', 'robot_id')

    if robot_config.has_option('robot', 'api_key'):
        api_key = robot_config.get('robot', 'api_key')
        if api_key == "":
            api_key = None
    
    mods = networking.getOwnerDetails(owner)['moderators']
#    mods = networking.getOwnerDetails(owner)['robocaster']['moderators']
    print("Moderators :", mods)

# check if the user is the owner or moderator, 0 for not, 1 for moderator, 2 for owner
def is_authed(user):
    if user == owner:
        return(2)
    elif user in mods:
        return(1)
    else:
        return(0)

# add a new command handler, this will also allow for overriding existing ones.
def add_command(command, function):
    global commands
    commands[command] = function
    
def anon_handler(command, args):
    global anon_control

    if len(command) > 1:
        if is_authed(args['name']): # Moderator
            if command[1] == 'on':
                anon_control = True
                tts.unmute_anon_tts()
                robot_util.setAnonControl(True, robot_id, api_key)
            elif command[1] == 'off':
                anon_control = False
                tts.mute_anon_tts()
                robot_util.setAnonControl(False, robot_id, api_key)
            elif len(command) > 3:
                if command[1] == 'control':
                    if command[2] == 'on':
                        anon_control = True
                        robot_util.setAnonControl(True, robot_id, api_key)
                    elif command[2] == 'off':
                        anon_control = False
                        robot_util.setAnonControl(False, robot_id, api_key)
                elif command[1] == 'tts':
                    if command[2] == 'on':
                        tts.unmute_anon_tts()
                    elif command[2] == 'off':
                        tts.mute_anon_tts()
    print("anon_control : " + str(anon_control))

def ban_handler(command, args):
    global banned
    
    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            banned.append(user)
            print(user + " added to ban list")
            tts.mute_user_tts(user)            

def unban_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            if user in banned:
                banned.remove(user)
                print(user + " removed from ban list")
                tts.unmute_user_tts(user)            

def timeout_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            banned.append(user)
            schedule.single_task(5, untimeout_user, user)
            print(user + " added to timeout list")
            tts.mute_user_tts(user)            
            
    
def untimeout_user(user):
    global banned

    if user in banned:  
        banned.remove(user)
        print(user + " timeout expired")
        tts.unmute_user_tts(user)            


def untimeout_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            if user in banned:
                banned.remove(user)
                print(user = " removed from timeout list")
                tts.unmute_user_tts(user)            
    

def public_mode_handler(command, args):
    if len(command) > 1:
        if api_key != None:
            if is_authed(args['name']) == 2: # Owner
                if command[1] == 'on':
                    robot_util.setAllowed('roboempress', robot_id, api_key)
                    robot_util.setPrivateMode(True, robot_id, api_key)
                elif command[1] == 'off':
                    robot_util.setPrivateMode(False, robot_id, api_key)
    
def devmode_handler(command, args):
    global dev_mode
    global dev_mode_mods
   
    if len(command) > 1:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'on':
                dev_mode = True
                dev_mode_mods = False
                if api_key != None:
                    robot_util.setDevMode(True, robot_id, api_key)
            elif command[1] == 'off':
                dev_mode = False
                if api_key != None:
                    robot_util.setDevMode(False, robot_id, api_key)
            elif command[1] == 'mods':
                dev_mode = True
                dev_mode_mods = True
    print("dev_mode : " + str(dev_mode))
    print("dev_mode_mods : " + str(dev_mode_mods))

def mic_handler(command, args):
    if is_authed(args['name']) == 1: # Owner
        if len(command) > 1:
            if command[1] == 'mute':
                if api_key != None:
                    robot_util.setMicEnabled(True, robot_id, api_key)
                # Mic Mute
                return
            elif command[1] == 'unmute':
                if api_key != None:
                    robot_util.setMicEnabled(False, robot_id, api_key)
                # Mic Unmute
                return

def tts_handler(command, args):
    print("tts :", tts)
    if len(command) > 1:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'mute':
                print("mute")
                tts.mute_tts()
                return
            elif command[1] == 'unmute':
                tts.unmute_tts()
                return
            elif command[1] == 'vol':
                # TTS int volume command
                return

def stationary_handler(command, args):
    global stationary
    if is_authed(args['name']) == 2: # Owner
        stationary = not stationary
        print ("stationary is ", stationary)

def global_chat_handler(command, args):
    if len(command) > 1:
        if api_key != None:
            if is_authed(args['name']) == 2: # Owner
                if command[1] == 'on':
                    robot_util.setGlobalChat(False, robot_id, api_key)
                    return
                elif command[1] == 'off':
                    robot_util.setGlobalChat(True, robot_id, api_key)
                    return

def word_filter_handler(command, args):
    if len(command) > 1:
        if api_key != None:
            if is_authed(args['name']) == 2: # Owner
                if command[1] == 'on':
                    robot_util.setWordFilter(True, robot_id, api_key)
                    return
                elif command[1] == 'off':
                    robot_util.setWordFilter(False, robot_id, api_key)
                    return

def show_exclusive_handler(command, args):
    if len(command) > 1:
        if api_key != None:
            if is_authed(args['name']) == 2: # Owner
                if command[1] == 'on':
                    robot_util.setShowExclusive(False, robot_id, api_key)
                    return
                elif command[1] == 'off':
                    robot_util.setShowExclusive(True, robot_id, api_key)
                    return

def brightness(command, args):
    if len(command) > 1:
        if is_authed(args['name']): # Moderator
            os.system(v4l2_ctl + " --set-ctrl brightness=" + command[1])
            print("brightness set to " + command[1])

def contrast(command, args):
    if len(command) > 1:
        if is_authed(args['name']): # Moderator
            os.system(v4l2_ctl + " --set-ctrl contrast=" + command[1])
            print("contrast set to " + command[1])

def saturation(command, args):
    if len(command) > 2:
        if is_authed(args['name']): # Moderator
            os.system(v4l2_ctl + " --set-ctrl saturation=" + command[1])
            print("saturation set to " + command[1])
	
# This is a dictionary of commands and their handler functions
commands={    '.anon'       :    anon_handler,
	            '.ban'        :    ban_handler,
	            '.unban'      :    unban_handler,
	            '.timeout'    :    timeout_handler,
	            '.untimout'   :    untimeout_handler,
              '.devmode'    :    devmode_handler,
	            '.mic'        :    mic_handler,
	            '.tts'        :    tts_handler,
	          '.global_chat':    global_chat_handler,
              '.public'    :    public_mode_handler,
              '.show_exclusive':     show_exclusive_handler,
              '.word_filter':    word_filter_handler,
              '.brightness' :    brightness,
              '.contrast'   :    contrast,    
              '.saturation' :    saturation,
              '.stationary' :    stationary_handler
	        }

def handler(args):
    command = args['message']
# TODO : This will not work with robot names with spaces, update it to split on ']'
# [1:]
    command = command.split(']')[1:][0].split(' ')[1:]
    print(command)
    
    if command != None:
        if command[0] in commands:
            commands[command[0]](command, args)

# This function checks the user sending the command, and if authorized
# call the move handler.
def move_auth(args):
    user = args['user']
    anon = args['anonymous']
    
    if stationary:
        direction = args['command']
        if direction == 'F' or direction == 'B':
            print("No forward for you.....")
            return 
               
    if anon_control == False and anon:
        return
    elif dev_mode_mods:
        if is_authed(user):
            move_handler(args)
        else:
            return
    elif dev_mode:
        if is_authed(user) == 2: # owner
            move_handler(args)
        else:
            return
    elif user not in banned: # Check for banned and timed out users
        move_handler(args)
 
    return

import os
import networking
import tts.tts as tts
import schedule
import robot_util
import logging

log = logging.getLogger('LR.extended_command')

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
robot_id = None
api_key = None
stationary = None
exclusive = False
exclusive_mods = False 
exclusive_user = ''
banned=[]
mods=[]
whiteList=[]
whiteListCommand=[]

def setup(robot_config):
    global owner
    global robot_id
    global api_key
    global buttons_json
    
    owner = robot_config.get('robot', 'owner')
    robot_id = robot_config.get('robot', 'robot_id')

    if robot_config.has_option('robot', 'api_key'):
        api_key = robot_config.get('robot', 'api_key')
        if api_key == "":
            api_key = None
    
    mods = networking.getOwnerDetails(owner)['moderators']
#    mods = networking.getOwnerDetails(owner)['robocaster']['moderators']
    if robot_config.has_option('misc', 'global_mods'):
        if robot_config.getboolean('misc', 'global_mods'):
           mods = mods + networking.getFrontPage()['admins']
    log.info("Moderators : %s", mods)

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
            log.info("anon chat command called by %s", args['name'])
            if command[1] == 'on':
                log.info("Anon control / TTS enabled")
                anon_control = True
                tts.unmute_anon_tts()
                robot_util.setAnonControl(True, robot_id, api_key)
            elif command[1] == 'off':
                log.info("Anon control / TTS disabled");
                anon_control = False
                tts.mute_anon_tts()
                robot_util.setAnonControl(False, robot_id, api_key)
            elif len(command) > 3:
                if command[1] == 'control':
                    if command[2] == 'on':
                        log.info("Anon control enabled")
                        anon_control = True
                        robot_util.setAnonControl(True, robot_id, api_key)
                    elif command[2] == 'off':
                        log.info("Anon control disabled")
                        anon_control = False
                        robot_util.setAnonControl(False, robot_id, api_key)
                elif command[1] == 'tts':
                    if command[2] == 'on':
                        log.info("Anon TTS enabled")
                        tts.unmute_anon_tts()
                    elif command[2] == 'off':
                        log.info("Anon TTS disabled")
                        tts.mute_anon_tts()
    log.debug("anon_control : %s", str(anon_control))

def whitelist_handler(command, args):
    global whiteList
    global whiteListCommand
    
    if len(command) > 2:
        if is_authed(args['name']) == 2: # Owner
            user = command[2]
            if command[1] == 'add':
                whiteList.append(user)
                log.info("%s added to whitelist", args['name'])
            elif command[1] == 'del':
                whiteList.remove(user)
                log.info("%s removed from whitelist", args['name'])
            elif command[1] == 'command':
                if len(command) > 3:
                    new_command = command[3]
                    if command[2] == 'add':
                        whiteListCommand.append(new_command)
                        log.info("%s added to command whitelist" % new_command)
                    elif command[2] == 'del':
                        whiteListCommand.remove(new_command)
                        log.inf("%s removed from command whitelist" % new_command)

def exclusive_handler(command, args):
    global exclusive
    global exclusive_user
    global exclusive_mods

    log.debug("exclusive_handler : %s %s", command, args)

    if len(command) >= 2:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'off':
                exclusive = False
                log.info("Exclusive control disabled")
                return
            elif len(command) < 3:
                exclusive_user = command[1]
                exclusive = True
                log.info("%s given exclusive control", command[1])
                return
            elif (len(command) >= 2) and (command[1] == 'mods'):
                if command[2] == 'on':
                   exclusive_mods = True
                   log.info("Enabling mod control during exclusive")
                   return
                elif command[2] == 'off':
                   exclusive_mods = False
                   log.info("Disabling mod control during exclusive")
                   return


def ban_handler(command, args):
    global banned
    
    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            banned.append(user)
            log.info("%s added %s to ban list", args['name'], user)
            tts.mute_user_tts(user)            

def unban_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            if user in banned:
                banned.remove(user)
                log.info("%s removed %s from ban list", args['name'], user)
                tts.unmute_user_tts(user)            

def timeout_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            banned.append(user)
            schedule.single_task(5, untimeout_user, user)
            log.info("%s added %s to timeout list", args['name'], user)
            tts.mute_user_tts(user)            
            
    
def untimeout_user(user):
    global banned

    if user in banned:  
        banned.remove(user)
        log.info("%s timeout expired", user)
        tts.unmute_user_tts(user)            


def untimeout_handler(command, args):
    global banned

    if len(command) > 1:
        user = command[1]
        if is_authed(args['name']): # Moderator
            if user in banned:
                banned.remove(user)
                log.info("%s removed %s from timeout list", args['name'], user)
                tts.unmute_user_tts(user)            
    

def public_mode_handler(command, args):
    if len(command) > 1:
        if api_key != None:
            if is_authed(args['name']) == 2: # Owner
                if command[1] == 'on':
                    log.info("Owner enabled private mode")
                    robot_util.setPrivateMode(True, robot_id, api_key)
                elif command[1] == 'off':
                    log.info("Owner disabled private mode")
                    robot_util.setPrivateMode(False, robot_id, api_key)
    
def devmode_handler(command, args):
    global dev_mode
    global dev_mode_mods
   
    if len(command) > 1:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'on':
                log.info("Owner enabled dev mode")
                dev_mode = True
                dev_mode_mods = False
                if api_key != None:
                    robot_util.setDevMode(True, robot_id, api_key)
            elif command[1] == 'off':
                log.info("Owner disabled dev mode")
                dev_mode = False
                if api_key != None:
                    robot_util.setDevMode(False, robot_id, api_key)
            elif command[1] == 'mods':
                log.info("Owner enabled dev mode with mod control")
                dev_mode = True
                dev_mode_mods = True
    log.debug("dev_mode : %s", str(dev_mode))
    log.debug("dev_mode_mods : %s", str(dev_mode_mods))

#TODO : Since audio / video has been integrated into the server, this should
# probably be updated to mute the mic directly, rather than just doing it on
# the server settings. 
def mic_handler(command, args):
    if is_authed(args['name']) == 1: # Owner
        if len(command) > 1:
            if command[1] == 'mute':
                if api_key != None:
                    log.info("Owner disabled mic")
                    robot_util.setMicEnabled(True, robot_id, api_key)
                # Mic Mute
                return
            elif command[1] == 'unmute':
                if api_key != None:
                    log.info("owner enabled mic")
                    robot_util.setMicEnabled(False, robot_id, api_key)
                # Mic Unmute
                return

def tts_handler(command, args):
    log.debug("tts : %s", tts)
    if len(command) > 1:
        if is_authed(args['name']) == 2: # Owner
            if command[1] == 'mute':
                log.info("Owner muted TTS")
                tts.mute_tts()
                return
            elif command[1] == 'unmute':
                log.info("Owner unmuted TTS")
                tts.unmute_tts()
                return
            elif command[1] == 'vol':
                if len(command) > 2:
                    log.info("Owner changed TTS Volume")
                    tts.volume(command[2])
                return

def stationary_handler(command, args):
    global stationary
    if is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            if command[1] == 'on':
                stationary = True
            elif command[1] == 'off':
                stationary = False
        else:
            stationary = not stationary
        log.info("stationary is %s", stationary)

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
              '.stationary' :    stationary_handler,
              '.table'      :    stationary_handler,
              '.whitelist'  :    whitelist_handler,
              '.exclusive'  :    exclusive_handler
	        }

def handler(args):
    command = args['message']
# TODO : This will not work with robot names with spaces, update it to split on ']'
# [1:]

    try:	
        command = command.split(']')[1:][0].split(' ')[1:]
        log.debug("command : %s", command)
    except IndexError: # catch empty messages
        return
    
    if command != None:
        if command[0] in commands:
            commands[command[0]](command, args)

# This function checks the user sending the command, and if authorized
# call the move handler.
def move_auth(args):
    user = args['user']
    anon = args['anonymous']
   
    # Check if stationary mode is enabled
    if stationary:
        direction = args['command']
        if direction == 'F' or direction == 'B':
            log.debug("No forward for you.....")
            return 

    # Check if command is in the whitelist required commands
    if args['command'] in whiteListCommand:
        if user not in whiteList:
            log.debug("%s not authed for command %s" % (user, args['command']))
            return    

    # check if exclusive control is enabled
    if exclusive and (user != owner):
        if exclusive_mods:
            if user not in mods:
                if user != exclusive_user: 
                    log.debug("%s not authed for exclusive control", user)
                    return
        if user != exclusive_user: 
            log.debug("%s not authed for exclusive control", user)
            return
    elif exclusive:
        log.debug("%s %s is authed", user, args['command'])
               
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

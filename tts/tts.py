import os
import sys
import re
import audio_util
import logging
import platform
import time

log = logging.getLogger('RemoTV.tts')

if (sys.version_info > (3, 0)):
    import importlib

type = 'none'
tts_module = None
mute = False
mute_anon = None
delay_tts = False
delay = 0
urlRegExp = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"   #pylint: disable=W1401
url_filter = None
hw_num = None
banned=[]
tts_queue=[]
tts_deleted=[]

def setup(robot_config):
    global type
    global tts_module
    global mute_anon
    global url_filter
    global hw_num
    global delay_tts
    global delay
    
    type = robot_config.get('tts', 'type')
    mute_anon = not robot_config.getboolean('tts', 'anon_tts')
    url_filter = robot_config.getboolean('tts', 'filter_url_tts')
    
    if robot_config.has_option('tts', 'delay_tts') and robot_config.has_option('tts', 'delay'):
        delay_tts = robot_config.getboolean('tts', 'delay_tts')
        delay = robot_config.getint('tts', 'delay')

# TODO: Delay TTS may not currently be via, and messenger no longer exist
#       and sending messages to chat cannot currently be disabled.
#    if delay_tts and not robot_config.getboolean('messenger', 'enable'):
#        log.error("Warning! delayed TTS requires messenger.")
#        log.error("delayed TTS disabled.")
#        delay_tts = False
  
    # get playback device hardware num from name.
    if robot_config.has_option('tts', 'speaker_device'): 
        audio_device = robot_config.get('tts', 'speaker_device')
    else:
        log.warn("controller.conf is out of date. Consider updating.")
        audio_device = robot_config.get('tts', 'audio_device')

    # convert the device to hw num if not on windows
    if platform.system() != "Windows":
        if audio_device != '':
            temp_hw_num = audio_util.getSpeakerByName(audio_device.encode('utf-8'))
            if temp_hw_num != None:
                if robot_config.has_option('tts', 'speaker_num'):
                    robot_config.set('tts', 'speaker_num', str(temp_hw_num))
                else:
                    log.warn("controller.conf is out of date. Consider updating.")
                    robot_config.set('tts', 'hw_num', str(temp_hw_num))
    
    if robot_config.has_option('tts', 'speaker_num'):
        hw_num = robot_config.get('tts', 'speaker_num')
    else:
        log.warn("controller.conf is out of date. Consider updating.")
        hw_num = robot_config.get('tts', 'hw_num')
    
    #import the appropriate tts handler module.
    log.debug("loading module tts/%s", type)
    if robot_config.getboolean('misc', 'custom_tts'):
        if os.path.exists('tts/tts_custom.py'):
            if (sys.version_info > (3, 0)):
                tts_module = importlib.import_module('tts.tts_custom')
            else:
                tts_module = __import__('tts.tts_custom', fromlist=['tts_custom'])
        else:
            log.info("Unable to find tts/tts_custom.py")    
            if (sys.version_info > (3, 0)):
                tts_module = importlib.import_module('tts.'+type)
            else:
                tts_module = __import__("tts."+type, fromlist=[type])    
    else:
        if (sys.version_info > (3, 0)):
            tts_module = importlib.import_module('tts.'+type)
        else:
            tts_module = __import__("tts."+type, fromlist=[type])    
        
    #call the tts handlers setup function
    tts_module.setup(robot_config)

def say(args):
    global tts_queue
    global tts_deleted
    
    if mute:
        exit()
    else:
        #check the number of arguments passed, and hand off as appropriate to the tts handler
        if not isinstance(args, dict):
            log.debug("message : %s", args)
            tts_module.say(args)
        else:
            message = args["message"]
            log.debug("message : %s", message)
            if delay_tts:
                log.info('TTS message delayed')
                tts_queue.append(args[1]['_id'])
                time.sleep(delay)
                tts_queue.remove(args[1]['_id'])
                if args[1]['_id'] in tts_deleted:
                    tts_deleted.remove(args[1]['_id'])
                    log.info('{} deleted before TTS played!'.format(args[1]['_id']))
                    return()
                else:
                    log.info('{} now being played.'.format(args[1]['_id']))
            user = args['sender']
            if url_filter:
                if re.search(urlRegExp, message):
                    log.info('message blocked for URL')
                    exit()
            if user not in banned: 
                tts_module.say(message, args)
 
def mute_tts():
    global mute
    mute = True
    log.info("TTS muted")    

def unmute_tts():
    global mute
    mute = False
    log.info("TTS unmuted")    
    
def mute_anon_tts():
    global mute_anon
    mute_anon = True
    log.info("Anonymous TTS muted")    
    
def unmute_anon_tts():
    global mute_anon
    mute_anon = False
    log.info("Anonymous TTS unmuted")
        
def mute_user_tts(user):
    global banned
    banned.append(user)
    log.info(user + " TTS muted")
    
def unmute_user_tts(user):
    global banned
    if user in banned:
        banned.remove(user)
        log.info(user + " TTS unmuted")
        
def volume(vol):
    try:
        new_vol = int(vol)
    except ValueError:
        log.debug("Not a valid volume level %s" % vol)
        return
        
    new_vol = new_vol % 101
    
    try:
        tts_module.volume(vol)
    except AttributeError:
        new_hw_num = hw_num[0]
        log.info("Setting volume to %d" % new_vol)
        os.system("amixer -c %s set PCM %s%%" % (new_hw_num, new_vol))


    
def onHandleChatMessageRemoved(*args):
   global tts_deleted
   log.debug("MessageRemoved for {} received".format(args[0]['message_id']))
   if args[0]['message_id'] in tts_queue and args[0] not in tts_deleted:
      tts_deleted.append(args[0]['message_id'])

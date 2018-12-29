import os
import sys
import re
import audio_util
import logging
import platform

log = logging.getLogger('LR.tts')


if (sys.version_info > (3, 0)):
    import importlib

type = 'none'
tts_module = None
mute = False
mute_anon = None
urlRegExp = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
url_filter = None
hw_num = None
banned=[]

def setup(robot_config):
    global type
    global tts_module
    global mute_anon
    global url_filter
    global hw_num
    
    type = robot_config.get('tts', 'type')
    mute_anon = not robot_config.getboolean('tts', 'anon_tts')
    url_filter = robot_config.getboolean('tts', 'filter_url_tts')

    # get playback device hardware num from name.
    audio_device = robot_config.get('tts', 'audio_device')

    # convert the device to hw num if not on windows
    if platform.system() != "Windows":
        if audio_device != '':
            temp_hw_num = audio_util.getSpeakerByName(audio_device.encode('utf-8'))
            if temp_hw_num != None:
                robot_config.set('tts', 'hw_num', str(temp_hw_num))
    
    hw_num = robot_config.get('tts', 'hw_num')
    
    if type != 'none':
        # set volume level

        # tested for 3.5mm audio jack
        #if robot_config.getint('tts', 'tts_volume') > 50:
            #os.system("amixer set PCM -- -100")

        # tested for USB audio device
        os.system("amixer -c %d cset numid=3 %d%%" % ( robot_config.getint('tts', 'hw_num'), robot_config.getint('tts', 'tts_volume')))


    #import the appropriate tts handler module.
    log.debug("loading module tts/%s", type);    
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

def say(*args):
    message = args[0]
    
    if mute:
        exit()
    else:
        #check the number of arguments passed, and hand off as appropriate to the tts handler
        if len(args) == 1:
            tts_module.say(message)
        else:
            user = args[1]['name']
            if mute_anon and args[1]['anonymous'] == True:
                exit()
            if url_filter:
                if re.search(urlRegExp, message):
                    exit()
            if user not in banned: 
                tts_module.say(message, args[1])
    
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
        log.info("Setting volume to %d" % new_vol)
        os.system("amixer set PCM -- 100%d%%" % new_vol)
        os.system("amixer -c %s cset numid=3 %d%%" % (hw_num, new_vol))
    


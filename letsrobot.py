from __future__ import print_function

# TODO move all defs to the top of the file, out of the way of the flow of execution.
# TODO full python3 support will involve installing the adafruit drivers, not using the ones from the repo

import traceback
import argparse
import robot_util
import os.path
import networking
import time
import schedule
import sys
import watchdog
import logging
import logging.handlers

if (sys.version_info > (3, 0)):
    import importlib
    import _thread as thread
else:
    import thread
 
from threading import Timer

# fail gracefully if configparser is not installed
try:
    from configparser import ConfigParser
    robot_config = ConfigParser()
except ImportError:
    print("Missing configparser module (python -m pip install configparser)")
    sys.exit()

try: 
    robot_config.readfp(open('letsrobot.conf'))
except IOError:
    print("unable to read letsrobot.conf, please check that you have copied letsrobot.sample.conf to letsrobot.conf and modified it appropriately.")
    sys.exit()
except:
    print ("Error in letsrobot.conf:", sys.exc_info()[0])
    sys.exit()

handlingCommand = False    
chat_module = None
move_handler = None

# pass the lock to robot_util so the controller can be terminated from outside.
terminate = thread.allocate_lock()
robot_util.terminate = terminate

# Enable logging, based upon the settings in the conf file.
log = logging.getLogger('LR')
log.setLevel(logging.DEBUG)
console_handler=logging.StreamHandler()
console_handler.setLevel(logging.getLevelName(robot_config.get('logging', 'console_level')))
console_formatter=logging.Formatter('%(asctime)s - %(filename)s : %(message)s','%H:%M:%S')
console_handler.setFormatter(console_formatter)
file_handler=logging.handlers.RotatingFileHandler(robot_config.get('logging', 'log_file'),
        maxBytes=robot_config.getint('logging', 'max_size'),
        backupCount=robot_config.getint('logging', 'num_backup'))
file_handler.setLevel(logging.getLevelName(robot_config.get('logging', 'file_level')))
file_formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s','%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)

log.addHandler(console_handler)
log.addHandler(file_handler)
log.critical('LetsRobot Controller Starting up')

# Log all unhandled exceptions.
def exceptionLogger(exctype, value, tb):
    log.critical("Unhandled exception of type : {}".format(exctype),exc_info=(exctype, value, tb))
sys.excepthook = exceptionLogger

# This is required to allow us to get True / False boolean values from the
# command line    
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')    

# TODO assess these and other options in the config to see which ones are most 
# appropriate to be overidden from the command line.
# check the command line for and config file overrides.
parser = argparse.ArgumentParser(description='start robot control program')
parser.add_argument('--robot-id', help='Robot ID', default=robot_config.get('robot', 'robot_id'))
parser.add_argument('--info-server', help="Server that robot will connect to for information about servers and things", default=robot_config.get('misc', 'info_server'))
parser.add_argument('--type', help="Serial or motor_hat or gopigo2 or gopigo3 or l298n or motozero or pololu", default=robot_config.get('robot', 'type'))
parser.add_argument('--video', default=robot_config.get('camera', 'type'))
parser.add_argument('--custom-hardware', type=str2bool, default=robot_config.getboolean('misc', 'custom_hardware'))
parser.add_argument('--custom-tts', type=str2bool, default=robot_config.getboolean('misc', 'custom_tts'))
parser.add_argument('--custom-chat', type=str2bool, default=robot_config.getboolean('misc', 'custom_chat'))
parser.add_argument('--custom-video', type=str2bool, default=robot_config.getboolean('misc', 'custom_video'))
parser.add_argument('--ext-chat-command', type=str2bool, default=robot_config.getboolean('tts', 'ext_chat'))
parser.add_argument('--secure-cert', type=str2bool, default=robot_config.getboolean('misc', 'secure_cert'))
parser.add_argument('--right-wheel-forward-speed', type=int)
parser.add_argument('--right-wheel-backward-speed', type=int)
parser.add_argument('--left-wheel-forward-speed', type=int)
parser.add_argument('--left-wheel-backward-speed', type=int)

parser.add_argument('--no-mic', dest='no_mic', action='store_true')
parser.set_defaults(no_mic=False)
parser.add_argument('--no-camera', dest='no_camera', action='store_true')
parser.set_defaults(no_camera=False)
commandArgs = parser.parse_args()

log.debug('command line arguments : %s', commandArgs)

# push command line variables back into the config
robot_config.set('robot', 'robot_id', str(commandArgs.robot_id))
robot_config.set('robot', 'type', commandArgs.type)
robot_config.set('misc', 'info_server', commandArgs.info_server)
robot_config.set('misc', 'custom_hardware', str(commandArgs.custom_hardware))
robot_config.set('misc', 'custom_tts', str(commandArgs.custom_tts))
robot_config.set('misc', 'custom_chat', str(commandArgs.custom_chat))
robot_config.set('tts', 'ext_chat', str(commandArgs.ext_chat_command))
robot_config.set('misc', 'secure_cert', str(commandArgs.secure_cert))

if commandArgs.no_mic:
    robot_config.set('camera', 'no_mic', 'True')

if commandArgs.no_camera:
    robot_config.set('camera', 'no_camera', 'True')

# set variables pulled from the config
robotID = commandArgs.robot_id
infoServer = commandArgs.info_server
ext_chat = commandArgs.ext_chat_command
no_chat_server = robot_config.getboolean('misc', 'no_chat_server')
enable_async = robot_config.getboolean('misc', 'enable_async')
auto_wifi = robot_config.getboolean('misc', 'auto_wifi')
secret_key = robot_config.get('misc', 'secret_key')

if ext_chat:
    import extended_command


# Functions

# TODO impliment a exclusive control function in hardware / tts / chat custom.
# this will probably mean a dummy function in all the handlers.
def handle_exclusive_control(args):
        if 'status' in args and 'robot_id' in args and args['robot_id'] == robotID:

            status = args['status']

        if status == 'start':
                log.info("start exclusive control")
        if status == 'end':
                log.info("end exclusive control")
                
                
def handle_chat_message(args):
    log.info("chat message received: %s", args)

    if ext_chat:
        extended_command.handler(args)
            
    rawMessage = args['message']
    withoutName = rawMessage.split(']')[1:]
    message = "".join(withoutName)

    try:
        if message[1] == ".":
            exit()
        else:
            tts.say(message, args)
    except IndexError:
        exit()
    
def configWifiLogin(secretKey):
    WPA_FILE_TEMPLATE = robot_config.get('misc', 'wpa_template')
    
    url = 'https://%s/get_wifi_login/%s' % (infoServer, secretKey)
    try:
        log.debug("GET %s", url)
        response = urllib2.urlopen(url).read()
        responseJson = json.loads(response)
        log.debug("get wifi login response: %s", response)

        with open("/etc/wpa_supplicant/wpa_supplicant.conf", 'r') as originalWPAFile:
            originalWPAText = originalWPAFile.read()

        wpaText = WPA_FILE_TEMPLATE.format(name=responseJson['wifi_name'], password=responseJson['wifi_password'])


        log.debug('original WPAText ( %s )', originalWPAText)
        log.debug('new WPAText ( %s )', wpaText)
        
        if originalWPAText != wpaText:

            wpaFile = open("/etc/wpa_supplicant/wpa_supplicant.conf", 'w')        

            print(wpaText)
            print()
            wpaFile.write(wpaText)
            wpaFile.close()

            log.info('Updated WIFI settings')
            say("Updated wifi settings. I will automatically reset in 10 seconds.")
            time.sleep(8)
            log.info('Rebooting...')
            say("Reseting")
            time.sleep(2)
            os.system("reboot")
        
    except:
        log.error("exception while configuring setting wifi %s", url)
        log.debug("wifi settings traceback", exc_info=1)

# TODO changeVolumeNormal() and handleLoudCommand() dont belong here, should
# be in a custom handler
def changeVolumeNormal():
    os.system("amixer -c 2 cset numid=3 %d%%" % robot_config.getint('tts', 'tts_volume'))

def handleLoudCommand(seconds):
    os.system("amixer -c 2 cset numid=3 %d%%" % 100)
    schedule.single_task(seconds, changeVolumeNormal)
    
def handle_command(args):
        global handlingCommand
        handlingCommand = True

        # catch move commands that happen before the controller has fully
        # loaded and set a move handler.
        if move_handler == None:
           return

        if 'command' in args and 'robot_id' in args and args['robot_id'] == robotID:
        
            log.debug('got command : %s', args)

            move_handler(args)

# TODO WALL and LOUD don't belong here, should be in custom handler.
            command = args['command']
            if command in ("SOUND2", "WALL", "LOUD"):
                handlingCommand = False
            
            if command == 'LOUD':
                handleLoudCommand(25)

            if commandArgs.type == 'motor_hat':
                if command == 'WALL':
                    handleLoudCommand(25)
                    os.system("aplay -D plughw:2,0 /home/pi/wall.wav")
                if command == 'SOUND2':
                    handleLoudCommand(25)
                    os.system("aplay -D plughw:2,0 /home/pi/sound2.wav")
                                                        
        handlingCommand = False
       

def on_handle_command(*args):
   if handlingCommand and not enable_async:
       return
   else:
       thread.start_new_thread(handle_command, args)

def on_handle_exclusive_control(*args):
   thread.start_new_thread(handle_exclusive_control, args)

def on_handle_chat_message(*args):
   if chat_module == None:
       thread.start_new_thread(handle_chat_message, args)
   else:
       thread.start_new_thread(chat_module.handle_chat, args)
   
# if auto_wifi is enabled, schdule a task for it.
def auto_wifi_task():
    if secret_key is not None:
         configWifiLogin(secret_key)
    t = Timer(10, auto_wifi_task)
    t.daemon = True
    t.start()

def restart_controller(command, args):
    if extended_command.is_authed(args['name']) == 2: # Owner
        terminate.acquire()

                    
# TODO : This really doesn't belong here, should probably be in start script.
# watch dog timer
if robot_config.getboolean('misc', 'watchdog'):
    import os
    os.system("sudo modprobe bcm2835_wdt")
    os.system("sudo /usr/sbin/service watchdog start")

log.info("info server : %s", infoServer)

# Load and start TTS
log.info("Loading tts")
import tts.tts as tts
tts.setup(robot_config)

# Connect to the networking sockets
log.info("Loading networking")
networking.setupSocketIO(robot_config)
controlSocketIO = networking.setupControlSocket(on_handle_command)
chatSocket = networking.setupChatSocket(on_handle_chat_message)
appServerSocketIO = networking.setupAppSocket(on_handle_exclusive_control)

# If messenger is enabled, connect a chat socket for return messages
if robot_config.getboolean('messenger', 'enable'):
    log.info("Loading messenger")
    messengerSocket = networking.setupMessengerSocket()

# If custom hardware extensions have been enabled, load them if they exist. Otherwise load the default
# controller for the specified hardware type.
log.info("Loading hardware module")
log.debug("Loading module hardware/%s", commandArgs.type)
if commandArgs.custom_hardware:
    if os.path.exists('hardware/hardware_custom.py'):
        if (sys.version_info > (3, 0)):
              module = importlib.import_module('hardware.hardware_custom')
        else:
            module = __import__('hardware.hardware_custom', fromlist=['hardware_custom'])
    else:
        log.warning("Unable to find hardware/hardware_custom.py")    
        if (sys.version_info > (3, 0)):
            module = importlib.import_module('hardware.'+commandArgs.type)
        else:
            module = __import__("hardware."+commandArgs.type, fromlist=[commandArgs.type])
else:
    if (sys.version_info > (3, 0)):
        module = importlib.import_module('hardware.'+commandArgs.type)
    else:
        module = __import__("hardware."+commandArgs.type, fromlist=[commandArgs.type])

#call the hardware module setup function
module.setup(robot_config)
move_handler = module.move

# Load the video handler
log.info("Loading video module")
log.debug("Loading module video/%s", commandArgs.video)
if commandArgs.custom_video:
    if os.path.exists('video/video_custom.py'):
        if (sys.version_info > (3, 0)):
            video_module = importlib.import_module('video.video_custom')
        else:
            video_module = __import__('video.video_custom', fromlist=['video_custom'])
    else:
        log.warning("Unable to find video/video_custom.py")    
        if (sys.version_info > (3, 0)):
            video_module = importlib.import_module('video.'+commandArgs.video)
        else:
            video_module = __import__("video."+commandArgs.video, fromlist=[commandArgs.video])
else:
    if (sys.version_info > (3, 0)):
        video_module = importlib.import_module('video.'+commandArgs.video)
    else:
        video_module = __import__("video."+commandArgs.video, fromlist=[commandArgs.video])

# Setup the video encoding
video_module.setup(robot_config)
video_module.start()

#load the extended chat commands
if ext_chat:
    log.info("Loading extended chat commands")
    extended_command.setup(robot_config)
    extended_command.move_handler=move_handler
    move_handler = extended_command.move_auth
    extended_command.add_command('.restart', restart_controller)

# Load a custom chat handler if enabled and exists
if commandArgs.custom_chat:
    if os.path.exists('chat_custom.py'):
        if (sys.version_info > (3, 0)):
            chat_module = importlib.import_module('chat_custom')
        else:
            chat_module = __import__('chat_custom', fromlist=['chat_custom'])

        chat_module.setup(robot_config, handle_chat_message)
    
    else:
       log.warning("Unable to find chat_custom.py")
    
# add auto wifi task
if auto_wifi:
    log.info("Adding auto wifi task")
    auto_wifi_task()

import atexit
atexit.register(log.debug, "Attempting to clean up and exit nicely")

log.critical('LetsRobot Controller Started')
while not terminate.locked():
    time.sleep(1)
    watchdog.watch()

log.critical('LetsRobot Controller Exiting')
sys.exit()

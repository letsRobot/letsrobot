import requests
import sys
import robot_util
import json
import schedule
import platform
import subprocess
import tts.tts as tts
import watchdog
import logging

from socketIO_client import SocketIO, LoggingNamespace

if (sys.version_info > (3, 0)):
#    import _thread as thread
    import urllib.request as urllib2
else:
#    import thread
    import urllib2

log = logging.getLogger('LR.networking')

controlHostPort = None
chatHostPort = None
videoPort = None
audioPort = None
infoServer = None
apiServer = None
robot_id = None
camera_id = None

messengerEnabled = None
messengerHost = None
messengerPort = None
messengerName = None
messengerUsername = None
messengerPassword = None
messengerQueue = []

appServerSocketIO = None
controlSocketIO = None
chatSocket = None
messengerSocket = None
no_chat_server = None
secure_cert = None

onHandleChatMesasge = None

#bootMessage = None

def getControlHostPort():
    url = 'https://%s/get_control_host_port/%s?version=2' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getControlHostPort : %s", response)
    return json.loads(response)

def getChatHostPort():
    url = 'https://%s/get_chat_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getChatHostPort : %s", response)
    return json.loads(response)

def getFrontPage():
    url = 'https://%s/api/v1/robocasters/internal/frontpage' % apiServer
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getFrontPage : %s", response)
    return json.loads(response)
     
    
def getOwnerDetails(username):
    url = 'https://%s/api/v1/accounts/%s' % (apiServer, username)
#    url = 'https://api.letsrobot.tv/api/v1/robocasters/%s' % (username)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getOwnerDetails : %s", response)
    return json.loads(response)
    
def getVideoPort():
    url = 'https://%s/get_video_port/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getVideoPort : %s", response)
    return json.loads(response)['mpeg_stream_port']

def getAudioPort():
    url = 'https://%s/get_audio_port/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getAudioPort : %s", response)
    return json.loads(response)['audio_stream_port']

def getWebsocketRelayHost():
    url = 'https://%s/get_websocket_relay_host/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getWebsocketRelayHost : %s", response)
    return json.loads(response)
    
def getOnlineRobotSettings(robotID):
    url = 'https://%s/api/v1/robots/%s' % (apiServer, robotID)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    log.debug("getOnlineRobotSettings : %s", response)
    return json.loads(response)

def getMessengerAuthToken():
    url = 'https://%s/api/v1/authenticate' % (apiServer)
    payload = {'username': messengerUsername, 'password': messengerPassword}
    authToken = robot_util.getAuthToken(url, payload)
    log.debug("getMessengerAuthToken : %s", authToken)
    return authToken
    
def waitForAppServer():
    while True:
        try:
            appServerSocketIO.wait(seconds=1)
        except AttributeError:
            log.warning("Warning: App Server Socket not connected.");

def waitForControlServer():
    while True:
        try:
            controlSocketIO.wait(seconds=1)        
        except AttributeError:
            log.warning("Warning: Control Server Socket not connected.");

def waitForChatServer():
    global chatSocket

    while True:
        try:
            chatSocket.wait(seconds=1)        
        except AttributeError:
            log.warning("Warning: Chat Server Socket not connected.");
        except IndexError:
            log.error("Error: Chat Server Socket has FAILED");
            startListenForChatServer()
            return
        
def waitForMessengerServer():
    while True:
        if len(messengerQueue):
            messengerSocket.emit('chat_message', messengerQueue.pop(0))
        try:
            messengerSocket.wait(seconds=1)        
        except AttributeError:
            log.warning("Warning: Messenger Chat Socket not connected.")
            startListenForMessengerServer()
            return
        
def startListenForAppServer():
    watchdog.start("AppServerListen", waitForAppServer)

def startListenForControlServer():
    watchdog.start("ControlServerListen", waitForControlServer)

def startListenForChatServer():
    global chatSocket

    chatSocket = SocketIO(chatHostPort['host'], chatHostPort['port'], LoggingNamespace, transports='websocket')

    log.info("Connected to chat socket.io")
    chatSocket.on('chat_message_with_name', onHandleChatMessage)
    chatSocket.on('connect', onHandleChatConnect)
    chatSocket.on('reconnect', onHandleChatReconnect)
    chatSocket.on('disconnect', onHandleChatDisconnect)
    watchdog.start("ChatServerListen", waitForChatServer)
    return chatSocket

def startListenForMessengerServer():
    global messengerSocket

    cookie = getMessengerAuthToken()

    if not cookie.status_code == 200:
        log.error('ERROR : Messenger username / password rejected by server')
        sys.exit()

    messengerSocket = SocketIO('https://%s' % messengerHost, messengerPort, LoggingNamespace, cookies={'connect.sid': cookie.cookies['connect.sid']}, transports='websocket')

    log.info("Connected to messenger chat socket.io")
    messengerSocket.on('connect', onHandleMessengerConnect)
    messengerSocket.on('reconnect', onHandleMessengerReconnect)
    messengerSocket.on('disconnect', onHandleMessengerDisconnect)

    watchdog.start("MessengerServerListen", waitForMessengerServer)
    return messengerSocket
   
def onHandleAppServerConnect(*args):
    identifyRobotID()    
    log.info("app socket.io connect")


def onHandleAppServerReconnect(*args):
    identifyRobotID()
    log.info("app server socket.io reconnect")
    
def onHandleAppServerDisconnect(*args):    
    log.info("app server socket.io disconnect")
 
def onHandleChatConnect(*args):
    identifyRobotID()
    log.info("chat socket.io connect")

def onHandleChatReconnect(*args):
    identifyRobotID()
    log.info("chat socket.io reconnect")
    
def onHandleChatDisconnect(*args):
    log.info("chat socket.io disconnect")

def onHandleControlConnect(*args):
    identifyRobotID()    
    log.info("control socket.io connect")

def onHandleControlReconnect(*args):
    identifyRobotID()
    log.info("control socket.io reconnect")
    
def onHandleControlDisconnect(*args):
    log.info("control socket.io disconnect")
    newControlHostPort = getControlHostPort()
    if newControlHostPort['port'] != controlHostPort['port']:
        log.warn('control host port changed!')
        robot_util.terminate_controller() 
 
def onHandleMessengerConnect(*args):
    log.info("messenger chat socket.io connect")

def onHandleMessengerReconnect(*args):
    log.info("messenger chat socket.io reconnect")
    
def onHandleMessengerDisconnect(*args):
    log.info("messenger chat socket.io disconnect")


def setupSocketIO(robot_config):
    global infoServer
    global apiServer

    global controlHostPort
    global chatHostPort
    global videoPort
    global audioPort

    global robot_id
    global camera_id

    global no_chat_server
    global secure_cert

    global messengerEnable
    global messengerHost
    global messengerPort
    global messengerName
    global messengerUsername
    global messengerPassword
    #global bootMessage

    robot_id = robot_config.get('robot', 'robot_id')
    camera_id = robot_config.getint('robot', 'camera_id')
    infoServer = robot_config.get('misc', 'info_server')
    apiServer =robot_config.get('misc', 'api_server')
    no_chat_server = robot_config.getboolean('misc', 'no_chat_server')
    secure_cert = robot_config.getboolean('misc', 'secure_cert')

    messengerEnable = robot_config.get('messenger', 'enable')
    messengerHost = robot_config.get('messenger', 'host')
    messengerPort = robot_config.getint('messenger', 'port')
    messengerUsername = robot_config.get('messenger', 'username')
    messengerPassword = robot_config.get('messenger', 'password')
    messengerName = robot_config.get('messenger', 'robot_name')

    #bootMessage = robot_config.get('tts', 'boot_message')

    controlHostPort = getControlHostPort()
    chatHostPort = getChatHostPort()
    videoPort = getVideoPort()
    audioPort = getAudioPort()

    schedule.repeat_task(60, identifyRobot_task)
    
    log.info("using socket io to connect to control %s", controlHostPort)
    log.info("using socket io to connect to chat %s", chatHostPort)
    log.info("using video port %d" % videoPort)
    log.info("using audio port %d" % audioPort)

    if robot_config.getboolean('misc', 'check_internet'):
        #schedule a task to check internet status
        schedule.task(robot_config.getint('misc', 'check_freq'), internetStatus_task)


def setupControlSocket(on_handle_command):
    global controlSocketIO
    log.debug("Connecting socket.io to control host port", controlHostPort)
    controlSocketIO = SocketIO(controlHostPort['host'], int(controlHostPort['port']), LoggingNamespace, transports='websocket')
    log.info("Connected to control socket.io")
    startListenForControlServer()
    controlSocketIO.on('connect', onHandleControlConnect)
    controlSocketIO.on('reconnect', onHandleControlReconnect)    
    controlSocketIO.on('disconnect', onHandleControlDisconnect)
    controlSocketIO.on('command_to_robot', on_handle_command)
    return controlSocketIO

def setupChatSocket(on_handle_chat_message):
    global onHandleChatMessage

    if not no_chat_server:
        log.debug('Connecting socket.io to chat host port', chatHostPort)
        onHandleChatMessage = on_handle_chat_message
        startListenForChatServer()
        return chatSocket
    else:
        log.info("chat server connection disabled")

def setupAppSocket(on_handle_exclusive_control):
    global appServerSocketIO
    log.debug("Connecting to socket.io to app server")
    appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace, transports='websocket')
    log.info("Connected to app server")
    startListenForAppServer()
    appServerSocketIO.on('exclusive_control', on_handle_exclusive_control)
    appServerSocketIO.on('connect', onHandleAppServerConnect)
    appServerSocketIO.on('reconnect', onHandleAppServerReconnect)
    appServerSocketIO.on('disconnect', onHandleAppServerDisconnect)
    return appServerSocketIO

def setupMessengerSocket():
    global messengerSocket
    
    if not no_chat_server:
        log.debug('Connecting socket.io to messenger chat host port : %s %s', messengerHost, messengerPort)
        startListenForMessengerServer()
        return messengerSocket
    else:
        log.info("messenger chat server connection disabled")


def sendChargeState(charging):
    chargeState = {'robot_id': robot_id, 'charging': charging}
    try:
        appServerSocketIO.emit('charge_state', chargeState)
    except AttributeError:
        log.error("Error: Can't update server on charge state, no app socket")
    log.debug("charge state : %s", chargeState)

def sendOnlineState(state):
    onlineState = {'send_video_process_exists': state, 'camera_id': camera_id}
    try:
        appServerSocketIO.emit('send_video_status', onlineState)
    except AttributeError:
        log.error("Error: Can't update server on charge state, no app socket")
    log.debug("online state: %s" % onlineState)

def ipInfoUpdate():
    try:
        appServerSocketIO.emit('ip_information', 
            {'ip': subprocess.check_output(["hostname", "-I"]).decode('utf-8'), 'robot_id': robot_id})
    except AttributeError:
        log.error("Error: Cant send ip address update, no app socket")

def identifyRobotID():
    """tells the server which robot is using the connection"""
    controlSocketIO.emit('robot_id', robot_id)
    log.debug("Sending identify robot id message")
    if not no_chat_server and not chatSocket == None:
        chatSocket.emit('identify_robot_id', robot_id);
    if not appServerSocketIO == None:
        appServerSocketIO.emit('identify_robot_id', robot_id);
   
#schedule a task to tell the server our robot id.
def identifyRobot_task():
    # tell the server what robot id is using this connection
    identifyRobotID()
    
    if platform.system() == 'Linux':
        ipInfoUpdate()
    
def isInternetConnected():
    try:
        urllib2.urlopen('https://www.google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

lastInternetStatus = False
def internetStatus_task():
    global bootMessage
    global lastInternetStatus
    internetStatus = isInternetConnected()
    if internetStatus != lastInternetStatus:
        if internetStatus:
            tts.say("ok")
            log.info("internet connected")
        else:
            log.info("missing internet connection")
            tts.say("missing internet connection")
    lastInternetStatus = internetStatus

def sendChatMessage(message):
    new_message = "[%s] %s" % (messengerName, message)

    log.debug ("%s %s %s" % (new_message, messengerName, robot_id)) 
    chat_message = { 'message': new_message,
                     'robot_id': robot_id,
                     'robot_name': messengerName,
                     'secret': "iknowyourelookingatthisthatsfine" }

    if messengerEnable:
        if not no_chat_server:
            messengerQueue.append(chat_message)


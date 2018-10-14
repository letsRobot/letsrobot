from __future__ import print_function

import requests

import sys
import robot_util
import json
import schedule
import platform
import subprocess
import tts.tts as tts
import watchdog

from socketIO_client import SocketIO, LoggingNamespace

if (sys.version_info > (3, 0)):
#    import _thread as thread
    import urllib.request as urllib2
else:
#    import thread
    import urllib2

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
debug_messages = None

onHandleChatMesasge = None

def getControlHostPort():
    url = 'https://%s/get_control_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    return json.loads(response)

def getChatHostPort():
    url = 'https://%s/get_chat_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    return json.loads(response)
    
def getOwnerDetails(username):
    url = 'https://%s/api/v1/accounts/%s' % (apiServer, username)
#    url = 'https://api.letsrobot.tv/api/v1/robocasters/%s' % (username)
    response = robot_util.getWithRetry(url, secure=secure_cert)
    return json.loads(response)
    
def getVideoPort():
    url = 'https://%s/get_video_port/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)['mpeg_stream_port']

def getAudioPort():
    url = 'https://%s/get_audio_port/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)['audio_stream_port']

def getWebsocketRelayHost():
    url = 'https://%s/get_websocket_relay_host/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)
    
def getOnlineRobotSettings(robotID):
    url = 'https://%s/api/v1/robots/%s' % (apiServer, robotID)
    response = robot_util.getWithRetry(url).decode('utf-8')
    return json.loads(response)

def getMessengerAuthToken():
    url = 'https://%s/api/v1/authenticate' % (apiServer)
    payload = {'username': messengerUsername, 'password': messengerPassword}
    authToken = robot_util.getAuthToken(url, payload)
    return authToken
    
def waitForAppServer():
    while True:
        try:
            appServerSocketIO.wait(seconds=1)
        except AttributeError:
            if debug_messages:
                print("Warning: App Server Socket not connected.");

def waitForControlServer():
    while True:
        try:
            controlSocketIO.wait(seconds=1)        
        except AttributeError:
            if debug_messages:
                print("Warning: Control Server Socket not connected.");

def waitForChatServer():
    global chatSocket

    while True:
        try:
            chatSocket.wait(seconds=1)        
        except AttributeError:
            if debug_messages:
                print("Warning: Chat Server Socket not connected.");
        except IndexError:
                print("Error: Chat Server Socket has FAILED");
                startListenForChatServer()
                return
        
def waitForMessengerServer():
    while True:
        if len(messengerQueue):
            messengerSocket.emit('chat_message', messengerQueue.pop(0))
        try:
            messengerSocket.wait(seconds=1)        
        except AttributeError:
            if debug_messages:
                print("Warning: Messenger Chat Socket not connected.");a
                startListenForMessengerServer()
                return
        
def startListenForAppServer():
    watchdog.start("AppServerListen", waitForAppServer)

def startListenForControlServer():
    watchdog.start("ControlServerListen", waitForControlServer)

def startListenForChatServer():
    global chatSocket

    chatSocket = SocketIO(chatHostPort['host'], chatHostPort['port'], LoggingNamespace)

    print("Connected to chat socket.io")
    chatSocket.on('chat_message_with_name', onHandleChatMessage)
    chatSocket.on('connect', onHandleChatConnect)
    chatSocket.on('reconnect', onHandleChatReconnect)
    if debug_messages:
        chatSocket.on('disconnect', onHandleChatDisconnect)
    watchdog.start("ChatServerListen", waitForChatServer)
    return chatSocket

def startListenForMessengerServer():
    global messengerSocket

    cookie = getMessengerAuthToken()

    if not cookie.status_code == 200:
        print('ERROR : Messenger username / password rejected by server')
        sys.exit()

    messengerSocket = SocketIO('https://%s' % messengerHost, messengerPort, LoggingNamespace, cookies={'connect.sid': cookie.cookies['connect.sid']})

    print("Connected to messenger chat socket.io")
    messengerSocket.on('connect', onHandleMessengerConnect)
    messengerSocket.on('reconnect', onHandleMessengerReconnect)
    if debug_messages:
        messengerSocket.on('disconnect', onHandleMessengerDisconnect)

    watchdog.start("MessengerServerListen", waitForMessengerServer)
    return messengerSocket
   
def onHandleAppServerConnect(*args):
    identifyRobotID()    
    if debug_messages:
        print
        print("app socket.io connect")
        print


def onHandleAppServerReconnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("app server socket.io reconnect")
        print
    
def onHandleAppServerDisconnect(*args):    
    print
    print("app server socket.io disconnect")
    print
 
def onHandleChatConnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("chat socket.io connect")
        print

def onHandleChatReconnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("chat socket.io reconnect")
        print
    
def onHandleChatDisconnect(*args):
    print
    print("chat socket.io disconnect")
    print

def onHandleControlConnect(*args):
    identifyRobotID()    
    if debug_messages:
        print
        print("control socket.io connect")
        print

def onHandleControlReconnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("control socket.io reconnect")
        print
    
def onHandleControlDisconnect(*args):
    print
    print("control socket.io disconnect")
    print

 
def onHandleMessengerConnect(*args):
    if debug_messages:
        print
        print("messenger chat socket.io connect")
        print

def onHandleMessengerReconnect(*args):
    if debug_messages:
        print
        print("messenger chat socket.io reconnect")
        print
    
def onHandleMessengerDisconnect(*args):
    print
    print("messenger chat socket.io disconnect")
    print


#TODO: Fix this to setup a new control socket instead of terminatition the program.    
#    newControlHostPort = getControlHostPort() #Reget control port will start if it closed for whatever reason
#    if controlHostPort['port'] != newControlHostPort['port']: #See if the port is not the same as before
#        print "restart: control host port changed"
#        sys.exit(1) #Auto restart script will restart if the control port is not the same (which is unlikely)

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
    global debug_messages

    global messengerEnable
    global messengerHost
    global messengerPort
    global messengerName
    global messengerUsername
    global messengerPassword

    debug_messages = robot_config.getboolean('misc', 'debug_messages') 
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

    controlHostPort = getControlHostPort()
    chatHostPort = getChatHostPort()
    videoPort = getVideoPort()
    audioPort = getAudioPort()

    schedule.repeat_task(60, identifyRobot_task)
    
    if debug_messages:   
        print("using socket io to connect to control", controlHostPort)
        print("using socket io to connect to chat", chatHostPort)
        print("using video port %d" % videoPort)
        print("using audio port %d" % audioPort)

    if robot_config.getboolean('misc', 'check_internet'):
        #schedule a task to check internet status
        schedule.task(robot_config.getint('misc', 'check_freq'), internetStatus_task)


def setupControlSocket(on_handle_command):
    global controlSocketIO
    if debug_messages:
        print("Connecting socket.io to control host port", controlHostPort)
    controlSocketIO = SocketIO(controlHostPort['host'], int(controlHostPort['port']), LoggingNamespace)
    print("Connected to control socket.io")
    startListenForControlServer()
    controlSocketIO.on('connect', onHandleControlConnect)
    controlSocketIO.on('reconnect', onHandleControlReconnect)    
    if debug_messages:
        controlSocketIO.on('disconnect', onHandleControlDisconnect)
    controlSocketIO.on('command_to_robot', on_handle_command)
    return controlSocketIO

def setupChatSocket(on_handle_chat_message):
    global onHandleChatMessage

    if not no_chat_server:
        if debug_messages:
            print('Connecting socket.io to chat host port', chatHostPort)
        onHandleChatMessage = on_handle_chat_message
        startListenForChatServer()
        return chatSocket
    else:
        print("chat server connection disabled")

def setupAppSocket(on_handle_exclusive_control):
    global appServerSocketIO
    if debug_messages:
        print("Connecting to socket.io to app server")
    appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace)
    print("Connected to app server")
    startListenForAppServer()
    appServerSocketIO.on('exclusive_control', on_handle_exclusive_control)
    appServerSocketIO.on('connect', onHandleAppServerConnect)
    appServerSocketIO.on('reconnect', onHandleAppServerReconnect)
    if debug_messages:
        appServerSocketIO.on('disconnect', onHandleAppServerDisconnect)
    return appServerSocketIO

def setupMessengerSocket():
    global messengerSocket
    
    if not no_chat_server:
        if debug_messages:
            print('Connecting socket.io to messenger chat host port', "%s %s" % (messengerHost, messengerPort))
        startListenForMessengerServer()
        return messengerSocket
    else:
        print("messenger chat server connection disabled")


def sendChargeState(charging):
    chargeState = {'robot_id': robot_id, 'charging': charging}
    try:
        appServerSocketIO.emit('charge_state', chargeState)
    except AttributeError:
        if debug_messages:
            print("Error: Can't update server on charge state, no app socket")
    print("charge state:", chargeState)

def sendOnlineState(state):
    onlineState = {'send_video_process_exists': state, 'camera_id': camera_id}
    try:
        appServerSocketIO.emit('send_video_status', onlineState)
    except AttributeError:
        if debug_messages:
            print("Error: Can't update server on charge state, no app socket")
    print("online state: %s" % onlineState)

def ipInfoUpdate():
    try:
        appServerSocketIO.emit('ip_information', 
            {'ip': subprocess.check_output(["hostname", "-I"]).decode('utf-8'), 'robot_id': robot_id})
    except AttributeError:
        if debug_messages:
            print("Error: Cant send ip address update, no app socket")

def identifyRobotID():
    """tells the server which robot is using the connection"""
    if debug_messages:
        print("Sending identify robot id message")
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
    global lastInternetStatus
    internetStatus = isInternetConnected()
    if internetStatus != lastInternetStatus:
        if internetStatus:
            tts.say("ok")
        else:
            tts.say("missing internet connection")
    lastInternetStatus = internetStatus

def sendChatMessage(message):
    new_message = "[%s] %s" % (messengerName, message)

    print ("%s %s %s" % (new_message, messengerName, robot_id)) 
    chat_message = { 'message': new_message,
                     'robot_id': robot_id,
                     'robot_name': messengerName,
                     'secret': "iknowyourelookingatthisthatsfine" }

    if messengerEnable:
        if not no_chat_server:
            messengerQueue.append(chat_message)


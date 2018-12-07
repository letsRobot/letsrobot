import requests
import time
import traceback
import ssl
import sys
import json
import logging

if (sys.version_info > (3, 0)):
    import urllib.request as urllib2
    from urllib.error import HTTPError
else:
    import urllib2
    from urllib2 import HTTPError

log = logging.getLogger('LR.robot_util')

terminate=None

def terminate_controller():
    log.info('Attempting to terminate controller...')
    if terminate != None:
        terminate.acquire()


# TODO : Think about rewriting this, and using request.

def getWithRetry(url, secure=True):
    for retryNumber in range(2000):
        try:
            log.debug("GET %s", url)
            if secure:
                response = urllib2.urlopen(url).read()
            else:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                response = urllib2.urlopen(url, context=ctx).read()
            break
        except:
            log.exception("could not open url %s", url)
            #traceback.print_exc()
            time.sleep(2)

    return response.decode('utf-8')

server_panels = '[{"button_panels":[{"button_panel_label": "movement controls","buttons": [{"label": "Left", "command": "L"}, {"label": "Right", "command": "R"}, {"label": "Forward", "command": "F"}, {"label": "Backward","command": "B"}]}]}]'

def getAuthToken(url, payload):  
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    return response

# This function passes data to the server api to update the robot settings.
def sendRobotSettings(data, robot_id, api_key):
    if not api_key == "":
        req = urllib2.Request('https://api.letsrobot.tv/api/v1/robots/%s' % robot_id, json.dumps(data).encode('utf-8') )
        req.add_header('Authorization', 'Bearer %s' % api_key)
        req.add_header('Content-Type', 'application/json')
        try:
            f = urllib2.urlopen(req)
        except HTTPError:
            #log.debug(api_key)
            log.error("Unable to update robot config on server! check API key")
            return False
        response = f.read()
        f.close()
        log.debug("sendRobotSettings : %s", response)

# This function allows you to set multiple values at once.
def updateRobotSettings(robot_id, api_key, **kwargs ):
    data = {}
    if (sys.version_info > (3, 0)):
        for key, value in kwargs.items():
            data[key] = value
    else:
        for key, value in kwargs.iteritems():
            data[key] = value

    sendRobotSettings(data, robot_id, api_key)

def setPrivateMode(mode, robot_id, api_key):
    data = {}
    data['public'] = mode
    sendRobotSettings(data, robot_id, api_key)

def setDevMode(mode, robot_id, api_key):
    data = {}
    data["dev_mode"] = mode
    sendRobotSettings(data, robot_id, api_key)

def setAnonControl(mode, robot_id, api_key):
    data = {}
    data["anonymous_control"] = mode
    sendRobotSettings(data, robot_id, api_key)

def setGlobalChat(mode, robot_id, api_key):
    data = {}
    data["non_global_chat"] = mode
    sendRobotSettings(data, robot_id, api_key)

def setWordFilter(mode, robot_id, api_key):
    data = {}
    data["profanity_filter"] = mode
    sendRobotSettings(data, robot_id, api_key)

def setShowExclusive(mode, robot_id, api_key):
    data = {}
    data["no_exclusive_control_button"] = mode
    sendRobotSettings(data, robot_id, api_key)

def setTTSMute(mode, robot_id, api_key):
    data = {}
    data["mute_text-to-speech"] = mode
    sendRobotSettings(data, robot_id, api_key)

def setMicEnabled(mode, robot_id, api_key):
    data = {}
    data["mic_enabled"] = mode
    sendRobotSettings(data, robot_id, api_key)

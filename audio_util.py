import subprocess
import re
import logging

log = logging.getLogger('RemoTV.audio_util')

def getAudioDeviceByName(name, command):
    text = subprocess.check_output(command)
    log.debug("devices : %s", text)
    lines = text.splitlines()
    for line in lines[1:]:
        if name in line:
            result = re.match("card (.*?):", line.decode('utf8'))
            try:
               device = int(result.group(1))
               log.info("Found Audio Device : %s", line)
               return(device)
            except:
               log.debug("Not a valid audio device match : %s", line)
    else:
        log.error("Unable to find Audio Device : %s", name)

# get microphone device number
def getMicByName(name):
    return(getAudioDeviceByName(name, ['arecord', '-l']))
    
# get speaker device number:w
def getSpeakerByName(name):
    return(getAudioDeviceByName(name, ["aplay", "-l"]))


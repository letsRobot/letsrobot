import subprocess
import re

def getAudioDeviceByName(name, command):
	text = subprocess.check_output(command)
	lines = text.splitlines()
	for line in lines:
		if name in line:
			print ("Found Audio Device : ", line)
			result = re.match("card (.*?):", line)
			return int(result.group(1))
        else:
            print("Unable to find Audio Device : ", name)

# get microphone device number
def getMicByName(name):
    return(getAudioDeviceByName(name, ['arecord', '-l']))
    
# get speaker device number:w
def getSpeakerByName(name):
    return(getAudioDeviceByName(name, ["aplay", "-l"]))


import os
import tempfile
import uuid
import logging

log = logging.getLogger('LR.tts.espeak')

tempDir = None
male = None
voice_number = None
hw_num = None

def setup(robot_config):
    global tempDir
    global male
    global voice_number
    global hw_num

    male = robot_config.getboolean('espeak', 'male')
    voice_number = robot_config.getint('espeak', 'voice_number')
    hw_num = robot_config.getint('tts', 'hw_num')

    #set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    log.info("TTS temporary directory : %s", tempDir)

def say(*args):
    message = args[0]
    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    if male:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+m%d -s 170 --stdout | aplay -D plughw:%d,0' %(voice_number, hw_num) )
    else:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+f%d -s 170 --stdout | aplay -D plughw:%d,0' % (voice_number, hw_num) )
    os.remove(tempFilePath)    

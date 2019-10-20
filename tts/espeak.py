import os
import tempfile
import uuid
import logging

log = logging.getLogger('RemoTV.tts.espeak')

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
    
    if robot_config.has_option('tts', 'speaker_num'):
        hw_num = robot_config.get('tts', 'speaker_num')
    else:
        hw_num = robot_config.get('tts', 'hw_num')


    #set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    log.info("TTS temporary directory : %s", tempDir)

def say(*args):
    message = args[0]
    message = message.encode('ascii', 'ignore')
    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "wb")
    f.write(message)
    f.close()

    if male:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+m{} -s 170 --stdout | aplay -D plughw:{}'.format(voice_number, hw_num) )
    else:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+f{} -s 170 --stdout | aplay -D plughw:{}'.format(voice_number, hw_num) )
    os.remove(tempFilePath)    

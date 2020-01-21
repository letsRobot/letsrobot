import os
import tempfile
import uuid
import logging

log = logging.getLogger('RemoTV.tts.espeak')

tempDir = None
male = None
voice_number = None
hw_num = None
espeak_path = None

def setup(robot_config):
    global tempDir
    global male
    global voice_number
    global hw_num
    global espeak_path

    male = robot_config.getboolean('espeak', 'male')
    voice_number = robot_config.getint('espeak', 'voice_number')
    
    if robot_config.has_option('tts', 'speaker_num'):
        hw_num = robot_config.get('tts', 'speaker_num')
    else:
        hw_num = robot_config.get('tts', 'hw_num')

    if robot_config.has_option('espeak', 'espeak_path'):
        espeak_path = robot_config.get('espeak', 'espeak_path')
    else:
        if os.name == 'nt':
            espeak_path = '"c:\\Program Files (x86)\\eSpeak\\command_line\\espeak.exe"'
        else:
            espeak_path = '/usr/bin/espeak'

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
        espeak_command = espeak_path + ' -v en-us+m{} -s 170'.format(voice_number)
    else:
        espeak_command = espeak_path + ' -v en-us+f{} -s 170'.format(voice_number)

    if os.name == 'nt':
        os.system('type ' + tempFilePath + ' | ' + espeak_command )
    else:
        os.system('cat ' + tempFilePath + ' | ' + espeak_command + ' --stdout | aplay -D plughw:{}'.format(hw_num) )

    os.remove(tempFilePath)    

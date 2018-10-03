from __future__ import print_function
import os
import tempfile
import uuid

tempDir = None
debug_messages = None
male = None
voice_number = None
hw_num = None

def setup(robot_config):
    global debug_messages
    global tempDir
    global male
    global voice_number
    global hw_num

    debug_messages = robot_config.get('misc', 'debug_messages')
    male = robot_config.getboolean('espeak', 'male')
    voice_number = robot_config.getint('espeak', 'voice_number')
    hw_num = robot_config.getint('tts', 'hw_num')

    #set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    if debug_messages:
       print("TTS temporary directory:", tempDir)

def say(*args):
    message = args[0]
    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    if male:
        os.system('cat ' + tempFilePath + ' | espeak --stdout | aplay -D plughw:%d,0' % hw_num)
    else:
        os.system('cat ' + tempFilePath + ' | espeak -ven-us+f%d -s170 --stdout | aplay -D plughw:%d,0' % (voice_number, hw_num) )
    os.remove(tempFilePath)    

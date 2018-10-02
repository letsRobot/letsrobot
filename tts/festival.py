from __future__ import print_function
import os
import tempfile
import uuid

tempDir = None
debug_messages = None
hw_num = None

def setup(robot_config):
    global debug_messages
    global tempDir
    global hw_num
    
    debug_messages = robot_config.get('misc', 'debug_messages')
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

    os.system('text2wave -o ' + tempFilePath +'.wav ' + tempFilePath)
    os.system('aplay -D plughw:%d,0 ' % hw_num + tempFilePath + '.wav')
    os.remove(tempFilePath + '.wav')
    os.remove(tempFilePath)
    

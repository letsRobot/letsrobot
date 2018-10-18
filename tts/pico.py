from __future__ import print_function
import os
import tempfile
import uuid

tempDir = None
debug_messages = None
pico_voice = None
hw_num = None

def setup(robot_config):
    global debug_messages
    global tempDir
    global pico_voice
    global hw_num

    debug_messages = robot_config.get('misc', 'debug_messages')
    pico_voice = robot_config.get('pico', 'voice')
    hw_num = robot_config.getint('tts', 'hw_num')

    #set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    if debug_messages:
       print("TTS temporary directory:", tempDir)

def say(*args):
    message = args[0]
    tempWaveFilePath = os.path.join(tempDir, "wave_" + str(uuid.uuid4()) + ".wav")
    message.replace("\\", r"\\")
    message.replace("'", r"\'")
    message.replace('"', r'\"')
    print( pico_voice );
    print( 'lang=' + pico_voice + 'message=' + message );
    os.system( 'pico2wave --lang=' + pico_voice + ' --wave=' + tempWaveFilePath + ' \"' + message + '\"' )
    os.system( 'aplay ' + tempWaveFilePath + ' -D plughw:%d,0' % hw_num )
    os.remove(tempWaveFilePath)

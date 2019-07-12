import os
import tempfile
import uuid
import logging

log = logging.getLogger('RemoTV.tts.pico')

tempDir = None
pico_voice = None
hw_num = None


def setup(robot_config):
    global tempDir
    global pico_voice
    global hw_num

    pico_voice = robot_config.get('pico', 'voice')
    if robot_config.has_option('tts', 'speaker_num'):
        hw_num = robot_config.getint('tts', 'speaker_num')
    else:
        hw_num = robot_config.getint('tts', 'hw_num')

    # set the location to write the temp file to
    tempDir = tempfile.gettempdir()
    log.info("TTS temporary directory: {}".format(tempDir))


def say(*args):
    message = args[0]
    tempWaveFilePath = os.path.join(
        tempDir, "wave_" + str(uuid.uuid4()) + ".wav")
    message.replace("\\", r"\\")
    message.replace("'", r"\'")
    message.replace('"', r'\"')
    log.info('lang=%s message=%s', pico_voice, message)
    os.system('pico2wave --lang=' + pico_voice + ' --wave=' +
              tempWaveFilePath + ' \"' + message + '\"')
    os.system('aplay ' + tempWaveFilePath + ' -D plughw:{}'.format(hw_num))
    os.remove(tempWaveFilePath)

# pylint: disable=no-member

import os
import tempfile
import uuid
import logging
import sys

log = logging.getLogger('LR.tts.google_cloud')
tempDir = None
client = None
voice = None
hwNum = None
devNum = None
audio_config = None
keyFile = None
languageCode = None
voicePitch = 0.0
voiceSpeakingRate = 1.0
ssmlEnabled = None

try:
    from google.oauth2 import service_account
    from google.cloud import texttospeech
except:
    log.critical("Google cloud libraries cloud not be loaded. Are they installed?")
    log.critical("Run python -m pip install google-cloud-texttospeech")
    sys.exit(1)

def setup(robot_config):
    global tempDir
    global client
    global voice
    global hwNum
    global audio_config
    global keyFile
    global languageCode
    global voicePitch
    global voiceSpeakingRate
    global ssmlEnabled
    global devNum

    ssmlEnabled = robot_config.getboolean('google_cloud', 'ssml_enabled')
    voice = robot_config.get('google_cloud', 'voice')
    keyFile = robot_config.get('google_cloud', 'key_file')
    languageCode = robot_config.get('google_cloud', 'language_code')
    voicePitch = robot_config.getfloat('google_cloud', 'voice_pitch')
    voiceSpeakingRate = robot_config.getfloat(
        'google_cloud', 'voice_speaking_rate')

    try:
        hwNum = robot_config.getint('tts', 'speaker_num')
    except:
        hwNum = robot_config.getint('tts', 'hw_num')

    if robot_config.has_option('tts', 'device_number'):
        devNum = robot_config.getint('tts', 'device_number')
    else:
        devNum = 0

    client = texttospeech.TextToSpeechClient(
        credentials=service_account.Credentials.from_service_account_file(
            keyFile)
    )

    voice = texttospeech.types.VoiceSelectionParams(
        name=voice,
        language_code=languageCode
    )

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        pitch=voicePitch,
        speaking_rate=voiceSpeakingRate
    )

    tempDir = tempfile.gettempdir()

def say(*args):
    global client
    global voice
    global hwNum
    global audio_config
    global ssmlEnabled
    global devNum

    message = args[0]
    message = message.strip()
    if ssmlEnabled:
        message = "<speak>" + message + "</speak>"
        try:
            log.debug("Trying SSML Synthesis")
            synthesis_input = texttospeech.types.SynthesisInput(ssml=message)
            log.debug("SSML synthesis successful")
        except:
            log.error("SSML synthesis failed!")
            pass
    else:
        synthesis_input = texttospeech.types.SynthesisInput(text=message)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    tempFilePath = os.path.join(tempDir, "wav_" + str(uuid.uuid4()) + ".wav")

    with open(tempFilePath, 'wb') as out:
        out.write(response.audio_content)
        os.system('aplay ' + tempFilePath + ' -D plughw:{},{}'.format(hwNum, devNum))

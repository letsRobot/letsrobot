# pylint: disable=no-member

import os
import tempfile
import uuid
import logging

from google.oauth2 import service_account
from google.cloud import texttospeech

log = logging.getLogger('LR.tts.google_cloud')

ssmlEnabled = None
tempDir = None
client = None
voice = None
hwNum = None
audio_config = None
keyFile = None
languageCode = None
voicePitch = 0.0
voiceSpeakingRate = 1.0

def setup(robot_config):
    global ssmlEnabled
    global tempDir
    global client
    global voice
    global hwNum
    global audio_config
    global keyFile
    global languageCode
    global voicePitch
    global voiceSpeakingRate

    ssmlEnabled = robot_config.getboolean('google_cloud', 'ssml_enabled')
    voice = robot_config.get('google_cloud', 'voice')
    keyFile = robot_config.get('google_cloud', 'key_file')
    hwNum = robot_config.getint('tts', 'hw_num')
    languageCode = robot_config.get('google_cloud', 'language_code')
    voicePitch = robot_config.getfloat('google_cloud', 'voice_pitch')
    voiceSpeakingRate = robot_config.getfloat(
        'google_cloud', 'voice_speaking_rate')

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

    message = args[0]
    message = message.strip()

    if message.startswith("<speak>") and ssmlEnabled:
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
        os.system('aplay ' + tempFilePath + ' -D plughw:%d,0' % hwNum)

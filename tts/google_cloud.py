# pylint: disable=no-member

import os
import tempfile
import uuid
import logging
import sys
import random

log = logging.getLogger('LR.tts.google_cloud')
tempDir = None
client = None
voice = None
hwNum = None
audio_config = None
keyFile = None
languageCode = None
voicePitch = 0.0
voiceSpeakingRate = 1.0
ssmlEnabled = None
randomVoices = None
useWavenet = None

try:
    from google.oauth2 import service_account
    from google.cloud import texttospeech
except:
    log.critical("Google cloud libraries cloud not be loaded. Are they installed?")
    log.critical("Run python -m pip install google-cloud-texttospeech")
    sys.exit(1)

waveNetList = [
    'en-US-Wavenet-A', 'en-US-Wavenet-B', 'en-US-Wavenet-C', 'en-US-Wavenet-D', 'en-US-Wavenet-E', 'en-US-Wavenet-F',
    'en-GB-Wavenet-A', 'en-GB-Wavenet-B', 'en-GB-Wavenet-C', 'en-GB-Wavenet-D',
    'en-AU-Wavenet-A', 'en-AU-Wavenet-B', 'en-AU-Wavenet-C', 'en-AU-Wavenet-D'
]

standardList = [
    'en-US-Standard-B', 'en-US-Standard-C', 'en-US-Standard-D', 'en-US-Standard-E',
    'en-GB-Standard-A', 'en-GB-Standard-B', 'en-GB-Standard-C', 'en-GB-Standard-D',
    'en-AU-Standard-A', 'en-AU-Standard-B', 'en-AU-Standard-C', 'en-AU-Standard-D'
]

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
    global randomVoices
    global useWavenet

    ssmlEnabled = robot_config.getboolean('google_cloud', 'ssml_enabled')
    voice = robot_config.get('google_cloud', 'voice')
    keyFile = robot_config.get('google_cloud', 'key_file')
    languageCode = robot_config.get('google_cloud', 'language_code')
    voicePitch = robot_config.getfloat('google_cloud', 'voice_pitch')
    voiceSpeakingRate = robot_config.getfloat(
        'google_cloud', 'voice_speaking_rate')

    if robot_config.has_option('google_cloud', 'random_voices'):
        randomVoices = robot_config.getboolean('google_cloud', 'random_voices')
    else:
        randomVoices = False

    if robot_config.has_option('google_cloud', 'use_WaveNet'):
        useWavenet = robot_config.getboolean('google_cloud', 'use_WaveNet')
    else:
        useWavenet = False

    if robot_config.has_option('tts', 'speaker_num'):
        hwNum = robot_config.get('tts', 'speaker_num')
    else:
        hwNum = robot_config.get('tts', 'hw_num')

    client = texttospeech.TextToSpeechClient(
        credentials=service_account.Credentials.from_service_account_file(
            keyFile)
    )

    if not randomVoices:
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
    global randomVoices
    global waveNetList
    global standardList

    if randomVoices:
        if useWavenet:
            voiceList = waveNetList
        else:
            voiceList = standardList
        voiceName = random.choice(voiceList)
        voiceEncoding = voiceName[0:4]
        voice = texttospeech.types.VoiceSelectionParams(
            name=voiceName,
            language_code=voiceEncoding
        )

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
        os.system('aplay ' + tempFilePath + ' -D plughw:{}'.format(hwNum))

# pylint: disable=no-member

import logging
import os
import random
import tempfile
import uuid

from google.cloud import texttospeech
from google.oauth2 import service_account

log = logging.getLogger('RemoTV.tts.google_cloud')

audio_config = None
client = None
hwNum = None
keyFile = None
languageCode = None
randomVoices = None
ssmlEnabled = None
standardVoices = None
tempDir = None
voice = None
voiceList = []
voicePitch = 0.0
voiceSpeakingRate = 1.0


def setup(robot_config):
    global audio_config
    global client
    global hwNum
    global keyFile
    global languageCode
    global randomVoices
    global ssmlEnabled
    global standardVoices
    global tempDir
    global voice
    global voiceList
    global voicePitch
    global voiceSpeakingRate

    ssmlEnabled = robot_config.getboolean('google_cloud', 'ssml_enabled')
    voice = robot_config.get('google_cloud', 'voice')
    keyFile = robot_config.get('google_cloud', 'key_file')

    if robot_config.has_option('google_cloud', 'random_voices'):
        randomVoices = robot_config.getboolean('google_cloud', 'random_voices')
        standardVoices = robot_config.getboolean(
            'google_cloud', 'standard_voices')
    else:
        randomVoices = False

    if robot_config.has_option('tts', 'speaker_num'):
        hwNum = robot_config.get('tts', 'speaker_num')
    else:
        hwNum = robot_config.getint('tts', 'hw_num')

    voicePitch = robot_config.getfloat('google_cloud', 'voice_pitch')
    voiceSpeakingRate = robot_config.getfloat(
        'google_cloud', 'voice_speaking_rate'
    )

    client = texttospeech.TextToSpeechClient(
        credentials=service_account.Credentials.from_service_account_file(
            keyFile)
    )

    if randomVoices:
        voices = client.list_voices().voices
        for voice in voices:
            if standardVoices:
                if 'Standard' in voice.name:
                    voiceList.append(voice.name)
            else:
                if 'Wavenet' in voice.name:
                    voiceList.append(voice.name)
    else:
        voice = texttospeech.types.VoiceSelectionParams(
            name=voice,
            language_code=voice[:5]
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

    if randomVoices:
        voiceSelection = random.choice(voiceList)
        voice = texttospeech.types.VoiceSelectionParams(
            name=voiceSelection,
            language_code=voiceSelection[:5]
        )

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    tempFilePath = os.path.join(tempDir, "wav_" + str(uuid.uuid4()) + ".wav")

    with open(tempFilePath, 'wb') as out:
        out.write(response.audio_content)
        os.system('aplay ' + tempFilePath + ' -D plughw:{}'.format(hwNum))

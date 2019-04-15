# pylint: disable=no-member

import logging
import os
import random
import sys
import tempfile
import uuid

import mod_utils
import networking

audio_config = None
client = None
fallback_tts = None
hwNum = None
keyFile = None
languageCode = None
log = logging.getLogger('LR.tts.google_cloud')
messenger = None
randomVoices = None
ssmlEnabled = None
tempDir = None
robot_voice = None
users = {}
voicePitch = 0.0
voices = [
    'ar-XA-Wavenet-A', 'ar-XA-Wavenet-B', 'ar-XA-Wavenet-C', 'da-DK-Wavenet-A',
    'de-DE-Wavenet-A', 'de-DE-Wavenet-B', 'de-DE-Wavenet-C', 'de-DE-Wavenet-D',
    'en-AU-Wavenet-A', 'en-AU-Wavenet-B', 'en-AU-Wavenet-C', 'en-AU-Wavenet-D',
    'en-GB-Wavenet-A', 'en-GB-Wavenet-B', 'en-GB-Wavenet-C', 'en-GB-Wavenet-D',
    'en-IN-Wavenet-A', 'en-IN-Wavenet-B', 'en-IN-Wavenet-C', 'en-US-Wavenet-A',
    'en-US-Wavenet-B', 'en-US-Wavenet-C', 'en-US-Wavenet-D', 'en-US-Wavenet-E',
    'en-US-Wavenet-F', 'fr-CA-Wavenet-A', 'fr-CA-Wavenet-B', 'fr-CA-Wavenet-C',
    'fr-CA-Wavenet-D', 'fr-FR-Wavenet-A', 'fr-FR-Wavenet-B', 'fr-FR-Wavenet-C',
    'fr-FR-Wavenet-D', 'hu-HU-Wavenet-A', 'it-IT-Wavenet-A', 'ja-JP-Wavenet-A',
    'ko-KR-Wavenet-A', 'ko-KR-Wavenet-B', 'ko-KR-Wavenet-C', 'ko-KR-Wavenet-D',
    'nb-NO-Wavenet-A', 'nb-NO-Wavenet-B', 'nb-NO-Wavenet-C', 'nb-NO-Wavenet-D',
    'nb-NO-Wavenet-E', 'nl-NL-Wavenet-A', 'nl-NL-Wavenet-B', 'nl-NL-Wavenet-C',
    'nl-NL-Wavenet-D', 'nl-NL-Wavenet-E', 'pl-PL-Wavenet-A', 'pl-PL-Wavenet-B',
    'pl-PL-Wavenet-C', 'pl-PL-Wavenet-D', 'pl-PL-Wavenet-E', 'pt-BR-Wavenet-A',
    'pt-PT-Wavenet-A', 'pt-PT-Wavenet-B', 'pt-PT-Wavenet-C', 'pt-PT-Wavenet-D',
    'ru-RU-Wavenet-A', 'ru-RU-Wavenet-B', 'ru-RU-Wavenet-C', 'ru-RU-Wavenet-D',
    'sk-SK-Wavenet-A', 'sv-SE-Wavenet-A', 'tr-TR-Wavenet-A', 'tr-TR-Wavenet-B',
    'tr-TR-Wavenet-C', 'tr-TR-Wavenet-D', 'tr-TR-Wavenet-E', 'uk-UA-Wavenet-A',
    'vi-VN-Wavenet-A', 'vi-VN-Wavenet-B', 'vi-VN-Wavenet-C', 'vi-VN-Wavenet-D',
]
voiceSpeakingRate = 1.0

try:
    from google.oauth2 import service_account
    from google.cloud import texttospeech
except:
    log.critical(
        "Google cloud libraries cloud not be loaded. Are they installed?")
    log.critical(
        "Run python -m pip install --upgrade google-cloud-texttospeech")
    sys.exit(1)


def new_voice(command, args):
    global users
    if not args['anonymous']:
        user = args['name']
        if len(command) > 1:
            if command[1] in voices:
                users[user] = command[1]
        else:
            users[user] = random.choice(voices)

        if messenger:
            networking.sendChatMessage(
                ".{} your voice is now {}".format(user, users[user]))


def setup(robot_config):
    global audio_config
    global client
    global fallback_tts
    global hwNum
    global keyFile
    global languageCode
    global messenger
    global randomVoices
    global ssmlEnabled
    global tempDir
    global robot_voice
    global voicePitch
    global voiceSpeakingRate

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        pitch=voicePitch,
        speaking_rate=voiceSpeakingRate
    )

    client = texttospeech.TextToSpeechClient(
        credentials=service_account.Credentials.from_service_account_file(
            keyFile)
    )

    fallback_tts = mod_utils.import_module('tts', 'espeak')
    fallback_tts.setup(robot_config)
    if robot_config.has_option('tts', 'speaker_num'):
        hwNum = robot_config.get('tts', 'speaker_num')
    else:
        hwNum = robot_config.get('tts', 'hw_num')
    keyFile = robot_config.get('google_cloud', 'key_file')
    languageCode = robot_config.get('google_cloud', 'language_code')
    messenger = robot_config.getboolean('messenger', 'enable')
    if robot_config.has_option('google_cloud', 'random_voices'):
        randomVoices = robot_config.getboolean('google_cloud', 'random_voices')
    else:
        randomVoices = False
    tempDir = tempfile.gettempdir()
    ssmlEnabled = robot_config.getboolean('google_cloud', 'ssml_enabled')
    robot_voice = robot_config.get('google_cloud', 'voice')
    voicePitch = robot_config.getfloat('google_cloud', 'voice_pitch')
    voiceSpeakingRate = robot_config.getfloat(
        'google_cloud', 'voice_speaking_rate')

    if not randomVoices:
        voice = texttospeech.types.VoiceSelectionParams(
            name=voice,
            language_code=languageCode
        )
    else:
        if robot_config.getboolean('tts', 'ext_chat'):
            import extended_command
            extended_command.add_command('.new_voice', new_voice)


def say(*args):
    message = args[0].strip()
    response = None
    user = args[1]['name']

    if randomVoices:
        if args[1]['anonymous']:
            voice = 'en-US-Wavenet-A'
        else:
            if user not in users:
                users[user] = random.choice(voices)
            voice = users[user]
        log.info(user + " voice" + voice + ": " + message)
    else:
        voice = robot_voice
    if ssmlEnabled:
        message = "<speak>" + message + "</speak>"
        try:
            log.debug("Trying SSML Synthesis")
            synthesis_input = texttospeech.types.SynthesisInput(ssml=message)
            log.debug("SSML synthesis successful")
        except:
            log.error("SSML synthesis failed! Falling back on espeak")
            fallback_tts.say(message, args[1])
    else:
        synthesis_input = texttospeech.types.SynthesisInput(text=message)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    tempFilePath = os.path.join(tempDir, "wav_" + str(uuid.uuid4()) + ".wav")

    with open(tempFilePath, 'wb') as out:
        out.write(response.audio_content)
        os.system('aplay ' + tempFilePath + ' -D plughw:{}'.format(hwNum))

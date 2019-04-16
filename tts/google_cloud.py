# pylint: disable=no-member

import logging
import os
import random
import sys
import tempfile
import uuid

import mod_utils
import networking

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
users = {}
messenger = None

try:
    from google.oauth2 import service_account
    from google.cloud import texttospeech
except:
    log.critical(
        "Google cloud libraries cloud not be loaded. Are they installed?")
    log.critical("Run python -m pip install google-cloud-texttospeech")
    sys.exit(1)

voiceList = [
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


def new_voice(command, args):
    global users

    if not args['anonymous']:
        user = args['name']
        if len(command) > 1:
            if command[1] in voiceList:
                users[user] = command[1]
            else:
                users[user] = random.choice(voiceList)
        if messenger:
            networking.sendChatMessage(
                ".{} your voice is now {}".format(user, users[user]))


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
    global messenger

    ssmlEnabled = robot_config.getboolean('google_cloud', 'ssml_enabled')
    voice = robot_config.get('google_cloud', 'voice')
    keyFile = robot_config.get('google_cloud', 'key_file')
    languageCode = robot_config.get('google_cloud', 'language_code')
    voicePitch = robot_config.getfloat('google_cloud', 'voice_pitch')
    voiceSpeakingRate = robot_config.getfloat(
        'google_cloud', 'voice_speaking_rate')
    messenger = robot_config.getboolean('messenger', 'enable')

    if robot_config.has_option('google_cloud', 'random_voices'):
        randomVoices = robot_config.getboolean('google_cloud', 'random_voices')
    else:
        randomVoices = False

    if robot_config.has_option('tts', 'speaker_num'):
        hwNum = robot_config.get('tts', 'speaker_num')
    else:
        hwNum = robot_config.get('tts', 'hw_num')

    client = texttospeech.TextToSpeechClient(
        credentials=service_account.Credentials.from_service_account_file(
            keyFile)
    )

    if randomVoices:
        import extended_command
        extended_command.add_command('.new_voice', new_voice)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        pitch=voicePitch,
        speaking_rate=voiceSpeakingRate
    )

    tempDir = tempfile.gettempdir()


def say(*args):
    global voice

    message = args[0].encode('utf-8').strip()
    message = "<speak>" + message + "</speak>"
    response = None
    synthesis_input = None
    synthesis_voice = None

    if (len(args) == 1):    # simple say
        synthesis_voice = texttospeech.types.VoiceSelectionParams(
            name=voice,
            language_code=languageCode
        )
    else:
        try:
            user = args[1]['name']
            if randomVoices:
                if (args[1]['anonymous']):
                    synthesis_voice = texttospeech.types.VoiceSelectionParams(
                        name="en-US-Standard-A",
                        language_code="en-US"
                    )
                else:
                    if user not in users:
                        users[user] = random.choice(voiceList)
                    name = users[user]
                    synthesis_voice = texttospeech.types.VoiceSelectionParams(
                        name=name,
                        language_code=name[0:4]
                    )
                    log.info("{} voice {}: {}".format(
                        user, users[user], message))
            else:

                synthesis_voice = texttospeech.types.VoiceSelectionParams(
                    name=voice,
                    language_code=languageCode
                )

        except Exception as e:
            log.exception(e)
            pass

        synthesis_input = texttospeech.types.SynthesisInput(ssml=message)

        response = client.synthesize_speech(
            synthesis_input, synthesis_voice, audio_config)

        tempFilePath = os.path.join(
            tempDir, "wav_" + str(uuid.uuid4()) + ".wav")

        with open(tempFilePath, 'wb') as out:
            out.write(response.audio_content)
            os.system('aplay ' + tempFilePath +
                      ' -D plughw:{}'.format(hwNum))

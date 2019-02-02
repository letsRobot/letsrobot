import os
import tempfile
import uuid
import logging

from google.cloud import texttospeech, storage

log = logging.getLogger('LR.tts.google_cloud')

tempDir = None
client = None
voice = None
hwNum = None
audio_config = None
keyFile = None
languageCode = None

client = None


def setup(robot_config):
    global tempDir
    global client
    global voice
    global hwNum
    global audio_config
    global keyFile
    global languageCode

    

    voice = robot_config.get('google_cloud', 'voice')
    keyFile = robot_config.get('google_cloud', 'key_file')
    hwNum = robot_config.getint('tts', 'hw_num')    
    languageCode = robot_config.get('google_cloud', 'language_code')

    client = texttospeech.TextToSpeechClient(
        credentials=storage.Client.from_service_account_json(keyFile)
    )
    
    voice = texttospeech.types.VoiceSelectionParams(
        name=voice,
        language_code=languageCode
    )

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16
    )
    
    tempDir = tempfile.gettempdir()

def say(*args):
    global client
    global voice
    global hwNum
    global audio_config

    message = args[0]

    synthesis_input = texttospeech.types.SynthesisInput(text=message)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    tempFilePath = os.path.join(tempDir, "wav_" + str(uuid.uuid4()) + ".wav")

    with open(tempFilePath, 'wb') as out:
        out.write(response.audio_content)
        os.system('aplay ' + tempFilePath + ' -D plughw:%d,0' % hwNum)

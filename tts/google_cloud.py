import os
import tempfile
import uuid
import logging

from google.cloud import texttospeech

log = logging.getLogger('LR.tts.google_cloud')

tempDir = None
client = None
voice = None
hwNum = None
audio_config = None

client = None


def setup(robot_config):
    global tempDir
    global client
    global voice
    global hwNum
    global audio_config

    client = texttospeech.TextToSpeechClient()

    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") == None:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/key.json"
        log.info("setting tts env variable")

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16
    )

    hwNum = robot_config.getint('tts', 'hw_num')

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

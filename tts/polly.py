import mod_utils
import boto3
from botocore.exceptions import ClientError
from subprocess import Popen, PIPE
import os
import random
import networking
import logging

log = logging.getLogger('LR.tts.polly')

client = None
polly = None
random_voice = None
#voices = [ 'Nicole', 'Russell', 'Amy', 'Brian', 'Emma', 'Raveena', 'Ivy', 'Joanna', 'Joey', 'Justin',
#             'Kendra', 'Kimberly', 'Matthew', 'Salli', 'Geraint' ]
voices = [ 'Geraint', 'Gwyneth', 'Mads', 'Naja',  'Hans', 'Marlene', 'Nicole', 'Russell', 'Amy', 'Brian', 'Emma', 'Raveena', 'Ivy', 'Joanna', 'Joey',
 'Justin', 'Kendra', 'Kimberly', 'Salli', 'Conchita', 'Enrique', 'Miguel', 'Penelope', 'Chantal', 'Celine', 'Mathieu', 'Dora', 'Karl', 'Carla',
 'Giorgio', 'Mizuki', 'Liv', 'Lotte', 'Ruben', 'Ewa', 'Jacek', 'Jan', 'Maja', 'Ricardo', 'Vitoria', 'Cristiano',  'Ines', 'Carmen', 'Maxim', 'Tatyana', 
 'Astrid', 'Filiz', 'Takumi' ]             
users = {}
robot_voice = None
hw_num = None
fallback_tts = None
messenger = None

def new_voice(command, args):
    global users

    if (args['anonymous'] != True):
        user = args['name']
        if len(command) > 1:
            if command[1] in voices:
                users[user] = command[1]
            else:
                users[user] = random.choice(voices)

        if messenger:
            networking.sendChatMessage(".%s your voice is now %s" %(user, users[user]))

def setup(robot_config):
    global client
    global polly
    global robot_voice
    global users
    global hw_num
    global random_voice
    global fallback_tts
    global messenger
    
    owner = robot_config.get('robot', 'owner')
    owner_voice = robot_config.get('polly', 'owner_voice')
    robot_voice = robot_config.get('polly', 'robot_voice')
    hw_num = robot_config.getint('tts', 'hw_num')
    random_voice = robot_config.getboolean('polly', 'random_voices')

    access_key=robot_config.get('polly', 'access_key')
    secrets_key=robot_config.get('polly', 'secrets_key')
    region_name=robot_config.get('polly', 'region_name')
    messenger = robot_config.getboolean('messenger', 'enable')
    
    client = boto3.Session(aws_access_key_id=access_key,
                            aws_secret_access_key=secrets_key,
                            region_name=region_name)

    polly = boto3.client('polly', aws_access_key_id=access_key,
                            aws_secret_access_key=secrets_key,
                            region_name=region_name)
                            
    users[owner] = owner_voice
    users['jill'] = 'Amy'

    if random_voice: # random voices enabled
        if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add voice command
            import extended_command
            extended_command.add_command('.new_voice', new_voice)
            
    # Setup the fallback tts
    fallback_tts = mod_utils.import_module('tts', 'espeak')
    fallback_tts.setup(robot_config)

def say(*args):
    message = args[0]
    response = None

    if (len(args) == 1): # simple say
        try:
            response = polly.synthesize_speech(
                OutputFormat = 'mp3',
                VoiceId = robot_voice,
                Text = message,
            )
            log.info("Say : " + message)
        except ClientError:
            log.error("TTS Error! Falling back on espeak.")
            fallback_tts.say(message)
        
    else:
        user = args[1]['name']

        if random_voice:
            if (args[1]['anonymous'] == True):
                voice = 'Mizuki'
            else:
                if user not in users:
                    users[user] = random.choice(voices)
                voice = users[user]    
        
            log.info(user + " voice " + voice + ": " + message)
        else:
            voice = robot_voice
 
        try:   
            response = polly.synthesize_speech(
                OutputFormat = 'mp3',
                VoiceId = voice,
                Text = message,
            )
        except ClientError:
            log.error("TTS Error! Falling back on espeak.")
            fallback_tts.say(message, args[1])

    if "AudioStream" in response:
#     out = open ('/tmp/polly.mp3', 'w+')
#     out.write(response['AudioStream'].read())
#     out.close()
#     player = Popen(['/usr/bin/mpg123-alsa', '-a', 'hw:1,1', '-q', '/tmp/polly.mp3'], stdin=PIPE, bufsize=1)
#     os.remove('/tmp/polly.mp3')
        play = Popen(['/usr/bin/mpg123-alsa', '-a', 'hw:%d,0' % hw_num, '-q', '-'], stdin=PIPE, bufsize=1)
        play.communicate(response['AudioStream'].read())
            


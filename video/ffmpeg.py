#   TODO :  Look at making it so the ffmpeg process toggles a boolean, that is 
# used to update the server with online state appropriately. 

import audio_util
import networking
import watchdog
import subprocess
import shlex
import schedule
import extended_command
import atexit
import os
import sys
import logging
import robot_util
import time
log = logging.getLogger('RemoTV.video.ffmpeg')

robotKey=None
server=None
no_mic=True
no_camera=True
mic_off=False

x_res = 640
y_res = 480

ffmpeg_location = None
v4l2_ctl_location = None

audio_hw_num = None
audio_device = None
audio_codec = None
audio_channels = None
audio_bitrate = None
audio_sample_rate = None
video_codec = None
video_bitrate = None
video_filter = ''
video_device = None
audio_input_format = None
audio_input_options = None
audio_output_options = None
video_input_options = None
video_output_options = None
video_start_count = 0

video_process = None
audio_process = None

brightness=None
contrast=None
saturation=None

def setup(robot_config):
    global robotKey
    global no_mic
    global no_camera

    global stream_key
    global server

    global x_res
    global y_res

    global ffmpeg_location
    global v4l2_ctl_location

    global audio_hw_num
    global audio_device
    global audio_codec
    global audio_channels
    global audio_bitrate
    global audio_sample_rate
    global video_codec
    global video_bitrate
    global video_filter
    global video_device
    global audio_input_format
    global audio_input_options
    global audio_output_options
    global video_input_format
    global video_input_options
    global video_output_options

    global brightness
    global contrast
    global saturation

    robotKey = robot_config.get('robot', 'robot_key')
    server = robot_config.get('misc', 'server')
 
    no_mic = robot_config.getboolean('camera', 'no_mic')
    no_camera = robot_config.getboolean('camera', 'no_camera')

    ffmpeg_location = robot_config.get('ffmpeg', 'ffmpeg_location')
    v4l2_ctl_location = robot_config.get('ffmpeg', 'v4l2-ctl_location')

    x_res = robot_config.getint('camera', 'x_res')
    y_res = robot_config.getint('camera', 'y_res')

    if not no_camera:
        if robot_config.has_option('camera', 'brightness'):
            brightness = robot_config.get('camera', 'brightness')
        if robot_config.has_option('camera', 'contrast'):
            contrast = robot_config.get('camera', 'contrast')
        if robot_config.has_option('camera', 'saturation'):
            saturation = robot_config.get('camera', 'saturation')
        
        video_device = robot_config.get('camera', 'camera_device')
        video_codec = robot_config.get('ffmpeg', 'video_codec')
        video_bitrate = robot_config.get('ffmpeg', 'video_bitrate')        
        video_input_format = robot_config.get('ffmpeg', 'video_input_format')
        video_input_options = robot_config.get('ffmpeg', 'video_input_options')
        video_output_options = robot_config.get('ffmpeg', 'video_output_options')

        if robot_config.has_option('ffmpeg', 'video_filter'):
            video_filter = robot_config.get('ffmpeg', 'video_filter')
            video_filter = '-vf %s' % video_filter

        if robot_config.getboolean('tts', 'ext_chat'):
            extended_command.add_command('.video', videoChatHandler)
            extended_command.add_command('.brightness', brightnessChatHandler)
            extended_command.add_command('.contrast', contrastChatHandler)
            extended_command.add_command('.saturation', saturationChatHandler)
        
    if not no_mic:
        if robot_config.has_option('camera', 'mic_num'):
            audio_hw_num = robot_config.get('camera', 'mic_num')
        else:
            log.warn("controller.conf is out of date. Consider updating.")
            audio_hw_num = robot_config.get('camera', 'audio_hw_num')
        if robot_config.has_option('camera', 'mic_device'):
            audio_device = robot_config.get('camera', 'mic_device')
        else:
            audio_device = robot_config.get('camera', 'audio_device')

        audio_codec = robot_config.get('ffmpeg', 'audio_codec')
        audio_bitrate = robot_config.get('ffmpeg', 'audio_bitrate')        
        audio_sample_rate = robot_config.get('ffmpeg', 'audio_sample_rate')
        audio_channels = robot_config.get('ffmpeg', 'audio_channels')
        audio_input_format = robot_config.get('ffmpeg', 'audio_input_format')
        audio_input_options = robot_config.get('ffmpeg', 'audio_input_options')
        audio_output_options = robot_config.get('ffmpeg', 'audio_output_options')

        if robot_config.getboolean('tts', 'ext_chat'):
            extended_command.add_command('.audio', audioChatHandler)

        # resolve device name to hw num, unless under windows
        if audio_input_format != "dshow":
            if audio_device != '':
                temp_hw_num = audio_util.getMicByName(audio_device.encode('utf-8'))
                if temp_hw_num != None:
                    audio_hw_num = temp_hw_num       

        # format the device for hw number if using alsa
        if audio_input_format == 'alsa':
            audio_device = 'hw:' + str(audio_hw_num)

def start():
    if not no_camera:
        watchdog.start("FFmpegCameraProcess", startVideoCapture)
        
    if not no_mic:
        if not mic_off:
#        watchdog.start("FFmpegAudioProcess", startAudioCapture)
            watchdog.start("FFmpegAudioProcess", startAudioCapture)

def startVideoCapture():
    global video_process
    global video_start_count

    while not networking.authenticated:
        time.sleep(1)

    video_start_count += 1
    log.debug("Video start count : %s", video_start_count)

#    if video_start_count % 10 == 0:
#    server refresh

    # set brightness
    if (brightness is not None):
        log.info("setting brightness : %s", brightness)
        os.system("v4l2-ctl -c brightness={brightness}".format(brightness=brightness))

    # set contrast
    if (contrast is not None):
        log.info("setting contrast : %s", contrast)
        os.system("v4l2-ctl -c contrast={contrast}".format(contrast=contrast))

    # set saturation
    if (saturation is not None):
        log.info("setting saturation : %s", saturation)
        os.system("v4l2-ctl -c saturation={saturation}".format(saturation=saturation))

    if networking.internetStatus:
    
       videoCommandLine = ('{ffmpeg} -f {input_format} -framerate 25 -video_size {xres}x{yres}'
                        ' -r 25 {in_options} -i {video_device} {video_filter}'
                        ' -f mpegts -codec:v {video_codec} -b:v {video_bitrate}k -bf 0'
                        ' -muxdelay 0.001 {out_options}'
                        ' http://{server}:1567/transmit?name={channel}-video')
                        
       videoCommandLine = videoCommandLine.format(ffmpeg=ffmpeg_location,
                            input_format=video_input_format,
                            in_options=video_input_options,
                            video_device=video_device, 
                            video_filter=video_filter,
                            video_codec=video_codec,
                            video_bitrate=video_bitrate,
                            out_options=video_output_options,
                            server=server,
                            channel=networking.channel,
                            xres=x_res, 
                            yres=y_res)

       log.debug("videoCommandLine : %s", videoCommandLine)
       try:
          video_process=subprocess.Popen(shlex.split(videoCommandLine))
       except OSError: # Can't find / execute ffmpeg
          log.critical("ERROR: Can't find / execute ffmpeg, check path in conf")
          robot_util.terminate()

       if video_process != None:
          try:
             atexit.unregister(atExitVideoCapture) # Only python 3
          except AttributeError:
             pass
          atexit.register(atExitVideoCapture)
          video_process.wait()
    else:
       log.debug("No Internet/Server : sleeping video start for 15 seconds")
       time.sleep(15)

def atExitVideoCapture():
    try:
        video_process.terminate
    except OSError: # process is already terminated
        pass


def stopVideoCapture():
    if video_process != None:
        watchdog.stop('FFmpegCameraProcess')
        video_process.terminate()
    
def restartVideoCapture(): 
    stopVideoCapture()
    watchdog.start("FFmpegCameraProcess", startVideoCapture)

def startAudioCapture():
    global audio_process

    while not networking.authenticated:
        time.sleep(1)

    audioCommandLine = '{ffmpeg} -f {audio_input_format}'
    if audio_input_format != "avfoundation":
        audioCommandLine += ' -ar {audio_sample_rate} -ac {audio_channels}'
    audioCommandLine += (' {in_options} -i {audio_device} -f mpegts'
                         ' -codec:a {audio_codec}  -b:a {audio_bitrate}k'
                         ' -muxdelay 0.001 {out_options}'
                         ' http://{server}:1567/transmit?name={channel}-audio')

    audioCommandLine = audioCommandLine.format(ffmpeg=ffmpeg_location,
                            audio_input_format=audio_input_format,
                            audio_sample_rate=audio_sample_rate,
                            audio_channels=audio_channels,
                            in_options=audio_input_options,
                            audio_device=audio_device,
                            audio_codec=audio_codec,
                            audio_bitrate=audio_bitrate,
                            out_options=audio_output_options,
                            server=server,
                            channel=networking.channel)
                            
    log.debug("audioCommandLine : %s", audioCommandLine)
    try:
        audio_process=subprocess.Popen(shlex.split(audioCommandLine))
    except OSError: # Can't find / execute ffmpeg
        log.critical("ERROR: Can't find / execute ffmpeg, check path in conf")
        robot_util.terminate()

    if audio_process != None:
       try:
           atexit.unregister(atExitVideoCapture) # Only python 3
       except AttributeError:
           pass
       atexit.register(atExitAudioCapture)
       audio_process.wait()
    
def atExitAudioCapture():
    try:
        audio_process.terminate
    except OSError: # process is already terminated
        pass

# Windows command
#    audioCommandLine = 'c:/ffmpeg/bin/ffmpeg.exe -f dshow -ar 44100 -ac %d -audio_buffer_size 250 -i audio="%s" -f mpegts -codec:a libtwolame -b:a 32k -muxdelay 0.001 http://%s:%s/%s/640/480/' % (robotSettings.mic_channels, 'TOSHIBA Web Camera - HD', audioHost, audioPort, robotSettings.stream_key)

#    return subprocess.Popen(shlex.split(audioCommandLine))    
   
def stopAudioCapture():
    if audio_process != None:
        watchdog.stop('FFmpegAudioProcess')
        audio_process.terminate()

def restartAudioCapture():
    stopAudioCapture()
    if not mic_off:
        watchdog.start("FFmpegAudioProcess", startAudioCapture)

def videoChatHandler(command, args):
    global video_process
    global video_bitrate

    if len(command) > 1:
        if extended_command.is_authed(args['sender']) == 2: # Owner
            if command[1] == 'start':
                if not video_process.returncode == None:
                    watchdog.start("FFmpegCameraProcess", startVideoCapture)
            elif command[1] == 'stop':
                stopVideoCapture()
            elif command[1] == 'restart':
                restartVideoCapture()
            elif command[1] == 'bitrate':
                if len(command) > 1:
                    if len(command) == 3:
                        try:
                            int(command[2])
                            video_bitrate = command[2]
                            restartVideoCapture()
                        except ValueError: # Catch someone passing not a number
                            pass
                    networking.sendChatMessage(".Video bitrate is %s" % video_bitrate)
        else:
            networking.sendChatMessge("command only available to owner")


def brightnessChatHandler(command, args):
    global brightness
    if len(command) > 1:
        if extended_command.is_authed(args['sender']): # Moderator
            try:
                new_brightness = int(command[1])
            except ValueError:
                exit() #Not a number    
            if new_brightness <= 255 and new_brightness >= 0:
                brightness = new_brightness
                os.system(v4l2_ctl_location + " --set-ctrl brightness=" + str(brightness))
                log.info("brightness set to %.2f" % brightness)

def contrastChatHandler(command, args):
    global contrast
    if len(command) > 1:
        if extended_command.is_authed(args['sender']): # Moderator
            try:
                new_contrast = int(command[1])
            except ValueError:
                exit() #not a number
            if new_contrast <= 255 and new_contrast >= 0:
                contrast = new_contrast
                os.system(v4l2_ctl_location + " --set-ctrl contrast=" + str(contrast))
                log.info("contrast set to %.2f" % contrast)

def saturationChatHandler(command, args):
    if len(command) > 2:
        if extended_command.is_authed(args['sender']): # Moderator
            try:
                new_saturation = int(command[1])
            except ValueError:
                exit() #not a number
            if new_saturation <= 255 and new_saturation >= 0:
                saturation = new_saturation
                os.system(v4l2_ctl_location + " --set-ctrl saturation=" + str(saturation))
                log.info("saturation set to %.2f" % saturation)

def audioChatHandler(command, args):
    global audio_process
    global audio_bitrate

    if len(command) > 1:
        if extended_command.is_authed(args['sender']) == 2: # Owner
            if command[1] == 'start':
                mic_off = false
                if audio_process.returncode != None:
                    watchdog.start("FFmpegAudioProcess", startAudioCapture)
            elif command[1] == 'stop':
                stopAudioCapture()
            elif command[1] == 'restart':
                mic_off = false
                stopAudioCapture()
                watchdog.start("FFmpegAudioProcess", startAudioCapture)
            elif command[1] == 'bitrate':
                if len(command) > 1:
                    if len(command) == 3:
                        try:
                            int(command[2])
                            audio_bitrate = command[2]
                            restartAudioCapture()
                        except ValueError: # Catch someone passing not a number
                            pass
                    networking.sendChatMessage(".Audio bitrate is %s" % audio_bitrate)


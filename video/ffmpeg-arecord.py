#from video.ffmpeg import *
from video.ffmpeg_process import *
import video.ffmpeg as ffmpeg
import networking
import logging
import time

log = logging.getLogger('RemoTV.video.ffmpeg-arecord')


arecord_path = None
arecord_format = None

# This is a pretty ugly way to overload the startAudioCapture(), but it's also
# the only way that seems to work. Otherwise, when called internally to the 
# ffmpeg module, the original function gets called.
def setup(robot_config):
    ffmpeg.setup(robot_config)
    ffmpeg.setup=setupArecord
    ffmpeg.setup(robot_config)
    ffmpeg.startAudioCapture=startAudioCapture

def setupArecord(robot_config):
    global arecord_path
    global arecord_format
 
    # do additional setup stuff
    arecord_path = robot_config.get('ffmpeg-arecord', 'arecord_path')
    arecord_format = robot_config.get('ffmpeg-arecord', 'arecord_format')

def startAudioCapture():
    audioCommandLine = ('{arecord} -D hw:{audio_hw_num} -c {audio_channels}'
                       ' -f {arecord_format} -r {audio_sample_rate} |'
                       ' {ffmpeg} -i - -ar {audio_sample_rate} -f mpegts'
                       ' -codec:a {audio_codec}  -b:a {audio_bitrate}k'
                       ' -bufsize 8192k -muxdelay 0.001 {out_options}'
                       ' http://{server}:1567/transmit?name={channel}-audio')

    while not networking.authenticated:
        time.sleep(1)

    audioCommandLine = audioCommandLine.format(arecord=arecord_path,
                            arecord_format=arecord_format,
                            ffmpeg=ffmpeg.ffmpeg_location,
                            audio_sample_rate=ffmpeg.audio_sample_rate,
                            audio_channels=ffmpeg.audio_channels,
                            in_options=ffmpeg.audio_input_options,
                            audio_hw_num=ffmpeg.audio_hw_num,
                            audio_codec=ffmpeg.audio_codec,
                            audio_bitrate=ffmpeg.audio_bitrate,
                            out_options=ffmpeg.audio_output_options,
                            server=ffmpeg.server,
                            channel=networking.channel_id)

    log.debug("audioCommandLine : %s", audioCommandLine)
    ffmpeg.startFFMPEG(audioCommandLine, 'ffmpeg-arecord Audio',  ffmpeg.atExitAudioCapture, 'audio_process')

def start():
   ffmpeg.start()





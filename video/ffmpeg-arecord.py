#from video.ffmpeg import *
import video.ffmpeg as ffmpeg
import logging

log = logging.getLogger('LR.video.ffmpeg-arecord')


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
                       ' http://{audio_host}:{audio_port}/{stream_key}/640/480/')

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
                            audio_host=ffmpeg.audioHost,
                            audio_port=ffmpeg.audioPort,
                            stream_key=ffmpeg.stream_key)

    log.debug("audioCommandLine : %s", audioCommandLine)
    ffmpeg.audio_process=ffmpeg.subprocess.Popen(audioCommandLine, shell=True)
    ffmpeg.atexit.register(ffmpeg.atExitAudioCapture)
    ffmpeg.audio_process.wait()
    try:
        ffmpeg.atexit.unregister(ffmpeg.atExitVideoCapture) # Only python 3
    except AttributeError:
        pass

def start():
   ffmpeg.start()





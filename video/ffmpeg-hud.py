# will require sudo apt-get install python-imaging
# Note the rate at which hud frames are produced seems to need to be a lot 
# higher than the rate ffmpeg is expecting them to prevent lag.

#from video.ffmpeg import *
import video.ffmpeg as ffmpeg
import logging
import time
import os
from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger('LR.video.ffmpeg-hud')

# This is a pretty ugly way to overload the startAudioCapture(), but it's also
# the only way that seems to work. Otherwise, when called internally to the 
# ffmpeg module, the original function gets called.
def setup(robot_config):
    ffmpeg.setup(robot_config)
    ffmpeg.setup=setupHUD
    ffmpeg.setup(robot_config)
    ffmpeg.startVideoCapture=startVideoCapture

def setupHUD(robot_config):
 
    # do additional setup stuff
    return

def startVideoCapture():
    global x_res
    global y_res
    x_res = ffmpeg.y_res
    y_res = ffmpeg.x_res

    # set brightness
    if (ffmpeg.brightness is not None):
        log.info("setting brightness : %s", ffmpeg.brightness)
        os.system("v4l2-ctl -c brightness={brightness}".format(brightness=ffmpeg.brightness))

    # set contrast
    if (ffmpeg.contrast is not None):
        log.info("setting contrast : %s", ffmpeg.contrast)
        os.system("v4l2-ctl -c contrast={contrast}".format(contrast=ffmpeg.contrast))

    # set saturation
    if (ffmpeg.saturation is not None):
        log.info("setting saturation : %s", ffmpeg.saturation)
        os.system("v4l2-ctl -c saturation={saturation}".format(saturation=ffmpeg.saturation))


    videoCommandLine = ('{ffmpeg} -f {input_format} -framerate 25 -video_size {xres}x{yres}'
                        ' -r 25 {in_options} -i {video_device}'
                        ' -f image2pipe -r 2 -vcodec png -i - {video_filter}'
                        ' -filter_complex "overlay" -f mpegts -codec:v {video_codec}'
                        ' -b:v {video_bitrate}k -bf 0 -muxdelay 0.001 {out_options}'
                        ' http://{video_host}:{video_port}/{stream_key}/{xres}/{yres}/')

    videoCommandLine = videoCommandLine.format(ffmpeg=ffmpeg.ffmpeg_location,
                            input_format=ffmpeg.video_input_format,
                            in_options=ffmpeg.video_input_options,
                            video_device=ffmpeg.video_device,
                            video_filter=ffmpeg.video_filter,
                            video_codec=ffmpeg.video_codec,
                            video_bitrate=ffmpeg.video_bitrate,
                            out_options=ffmpeg.video_output_options,
                            video_host=ffmpeg.videoHost,
                            video_port=ffmpeg.videoPort,
                            xres=ffmpeg.x_res,
                            yres=ffmpeg.y_res,
                            stream_key=ffmpeg.stream_key)

    log.debug("videoCommandLine : %s", videoCommandLine)
    ffmpeg.video_process=ffmpeg.subprocess.Popen(ffmpeg.shlex.split(videoCommandLine), stdin=ffmpeg.subprocess.PIPE)
    ffmpeg.atexit.register(ffmpeg.atExitVideoCapture)
    #ffmpeg.video_process.wait()

    while True:
        image = drawHUD()
        try:
            image.save(ffmpeg.video_process.stdin, 'PNG')
        except (IOError, ValueError):
            log.debug("exception writing image to pipe")
            break
        time.sleep(0.1) 

    try:
        ffmpeg.atExitVideoCapture()
        ffmpeg.video_process.stdin.close()
        ffmpeg.atexit.unregister(ffmpeg.atExitVideoCapture) # Only python 3
    except AttributeError:
        log.debug("exception closing ffmpeg thread and pipe")
        pass

def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return (temp.replace("temp=",""))

def getWifiStats():
    cmd = "awk 'NR==3 {print $3,\"|\",$4}' /proc/net/wireless"
    strQualityDbm = os.popen(cmd).read()

    if strQualityDbm:
        strQualityDbmSplit = strQualityDbm.split('|')
        strQuality = strQualityDbmSplit[0].strip()
        strDbm = strQualityDbmSplit[1].strip()

        qualityInt = int(float(strQuality))
        qualityPercent = qualityInt * 10/7

        dbmInt = int(float(strDbm))
        return "{0}% {1}dBm".format(qualityPercent, dbmInt)
    else:
        return "Not Found"

def drawHUD():
    image = Image.new("RGBA", (x_res, y_res), color = (0,0,0,0))
    draw = ImageDraw.Draw(image)
    draw.text((20, 70), "Testing 123", fill=(255,255,255))
    draw.text((20, 100), "CPU Temp : %s" % measure_temp())
    draw.text((20, 130), "WiFi : %s" % getWifiStats())
    return(image) 

def start():
    ffmpeg.start()

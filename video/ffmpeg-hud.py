# will require 'sudo apt-get install python-imaging' and 'pip install psutil'
# Note the rate at which hud frames are produced seems to need to be a lot 
# higher than the rate ffmpeg is expecting them to prevent lag.
#
# Note : Currently there is no way to customize this, so copy it to a different
# file and edit that file, if yo wish to make modifications. So as not to break
# git pull.

#from video.ffmpeg import *
import video.ffmpeg as ffmpeg
import logging
import time
import os
from PIL import Image, ImageDraw, ImageFont
import extended_command
import psutil
import datetime

log = logging.getLogger('LR.video.ffmpeg-hud')

hud_correct = False
hud_correct_x = 0
hud_correct_y = 0

# This is a pretty ugly way to overload the startAudioCapture(), but it's also
# the only way that seems to work. Otherwise, when called internally to the 
# ffmpeg module, the original function gets called.
def setup(robot_config):
    ffmpeg.setup(robot_config)
    ffmpeg.setup=setupHUD
    ffmpeg.setup(robot_config)
    ffmpeg.startVideoCapture=startVideoCapture

    extended_command.add_command('.hud', HUDChatHandler)

def setupHUD(robot_config):
 
    # do additional setup stuff
    return

def startVideoCapture():
    global x_res
    global y_res
    global hud_correct
    x_res = ffmpeg.x_res
    y_res = ffmpeg.y_res

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
                        ' -f image2pipe -r 2 -vcodec png -thread_queue_size 1'
                        ' -i - {video_filter}'
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
    HUD = drawBaseHUD()

    while True:
        if hud_correct:
            x_res = hud_correct_x
            y_res = hud_correct_y
            hud_correct = False
            HUD = drawBaseHUD()

        image = drawHUD(HUD)
        try:
            image.save(ffmpeg.video_process.stdin, 'PNG')
        except (IOError, ValueError):
            log.debug("exception writing image to pipe")
            break
        time.sleep(0.05) 

    try:
        ffmpeg.atExitVideoCapture()
        ffmpeg.video_process.stdin.close()
        ffmpeg.atexit.unregister(ffmpeg.atExitVideoCapture) # Only python 3
    except AttributeError:
        log.debug("exception closing ffmpeg thread and pipe")
        pass

def HUDChatHandler(command, args):
    global hud_correct
    global hud_correct_x
    global hud_correct_y

    if len(command) > 3:
        if extended_command.is_authed(args['name']): # Moderator
            if command[1] == 'correct':
                try:
                    new_x_res = int(command[2])
                    new_y_res = int(command[3])
                except ValueError:
                    return #Not a number
                log.info("correcting HUD resolution to %dx%d", new_x_res, new_y_res)
                hud_correct_x = new_x_res
                hud_correct_y = new_y_res
                hud_correct = True


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

def drawrect(drawcontext, xy, outline=None, width=0):
    (x1, y1), (x2, y2) = xy
    points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
    drawcontext.line(points, fill=outline, width=width)

# This draws all the basic elements / layout of the hud that does not change.
# It is drawn once. 
def drawBaseHUD():
    image = Image.new("RGBA", (x_res, y_res), color = (0,0,0,0))
    image_draw = ImageDraw.Draw(image)

    logo_pos = x_res / 6
    logo = Image.open('video/LRWebLogox256.png')
    logo.thumbnail((logo_pos, logo_pos))
    image.paste(logo, (x_res - logo_pos - 6, 9), logo)
    image_draw.rectangle(((3, y_res-25), (x_res-3, y_res-5)), (0,64,0,128), (0,255,0))
    drawrect(image_draw, [(2,2),(x_res-4,y_res-4)], outline=(0,255,0), width=3)
    image_draw.line(((3,y_res-25),(x_res-3, y_res-25)), fill=(0,255,0), width=3)
    image_draw.line(((logo_pos, y_res-4),(logo_pos, y_res-25)), fill=(0,255,0), width=3)
    image_draw.line(((logo_pos*3, y_res-4),(logo_pos*3, y_res-25)), fill=(0,255,0), width=3)
    image_draw.line(((logo_pos*5, y_res-4),(logo_pos*5, y_res-25)), fill=(0,255,0), width=3)

    return image

# This draws all the elements of the hud that change, it is called repeatedly.
def drawHUD(HUD):
    image = HUD.copy()
    draw = ImageDraw.Draw(image)

    text_spacing = x_res / 6
    cpu_usage = psutil.cpu_percent(percpu=True)
    time = datetime.datetime.now()
    time = time.strftime("Time : %a %y/%m/%d %H:%M:%S")

    draw.text((10, y_res-20), "Temp : %s" % measure_temp())
    draw.text((text_spacing+5, y_res-20), "Usage : %s%% %s%% %s%% %s%%" % tuple(cpu_usage))
    draw.text(((3*text_spacing)+5, y_res-20), time)
    draw.text(((5*text_spacing)+5, y_res-20), "WiFi : %s" % getWifiStats())

    return(image) 

def start():
    ffmpeg.start()

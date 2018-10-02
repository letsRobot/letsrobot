import time
import cozmo
import _thread as thread
import sys
import networking
import schedule
import extended_command
import PIL

coz = None
video_port = ""
camera_id = 0
infoServer = None
annotated = False
flipped = 0
colour = False

def set_colour(command, args):
    global colour 
    if extended_command.is_authed(args['name']) == 2:
        colour = not colour
        coz.camera.color_image_enabled = colour


def set_annotated(command, args):
    global annotated
    if extended_command.is_authed(args['name']) == 2:
        annotated = not annotated

def set_flipped(command, args):
    global flipped
    if extended_command.is_authed(args['name']) == 2:
        flipped = not flipped

def setup(robot_config):
    global camera_id
    global infoServer
    global video_port
    global annotated
    global colour
    
    camera_id = robot_config.get('robot', 'camera_id')
    infoServer = robot_config.get('misc', 'info_server')
    video_port = getVideoPort()
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    
    extended_command.add_command('.annotate', set_annotated)
    extended_command.add_command('.color', set_colour)
    extended_command.add_command('.colour', set_colour)

    try:
        thread.start_new_thread(cozmo.connect, (run,))
    except KeyboardInterrupt as e:
        pass        
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

    while not coz:
        try:
           time.sleep(0.5)
           print("not coz")
        except (KeyboardInterrupt, SystemExit):
           sys.exit()

    if robot_config.has_section('cozmo'):
        send_online_status = robot_config.getboolean('cozmo', 'send_online_status')
        annotated = robot_config.getboolean('cozmo', 'annotated')
        colour = robot_config.getboolean('cozmo', 'colour')
    else:
        send_online_status = True
    
    if send_online_status:
        print("Enabling online status")
        schedule.repeat_task(10, updateServer);

def getVideoPort():
    import robot_util
    import json
    url = 'https://%s/get_video_port/%s' % (infoServer, camera_id)
    response = robot_util.getWithRetry(url)
    return(json.loads(response)['mpeg_stream_port'])

# Tell the server we are online
def updateServer():
    print("Updating Server")
    try:
        networking.appServerSocketIO.emit('send_video_status', {'send_video_process_exists': True,
                               'ffmpeg_process_exists': True,
                               'camera_id':camera_id})
    except AttributeError:
        print("Error: No appServerSocketIO");

def getCozmo():
    return coz

def run(coz_conn):
    global coz
    coz = coz_conn.wait_for_robot()
    coz.enable_stop_on_cliff(True)

    # Turn on image receiving by the camera
    coz.camera.image_stream_enabled = True

    coz.say_text( "hey everyone, lets robot!", in_parallel=True)

    while True:
        time.sleep(0.25)

        from subprocess import Popen, PIPE
        from sys import platform

        #Frames to file
        #p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', '25', '-i', '-', '-vcodec', 'mpeg1video', '-qscale', '5', '-r', '25', 'outtest.mpg'], stdin=PIPE)
        
        if platform.startswith('linux') or platform == "darwin":
            #MacOS/Linux
            p = Popen(['/usr/local/bin/ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', '25', '-i', '-', '-vcodec', 'mpeg1video', '-r', '25', "-f","mpegts","http://letsrobot.tv:"+str(video_port)+"/hello/320/240/"], stdin=PIPE)
        elif platform.startswith('win'):
            #Windows
            import os
            if not os.path.isfile('c:/ffmpeg/bin/ffmpeg.exe'):
               print("Error: cannot find c:\\ffmpeg\\bin\\ffmpeg.exe check ffmpeg is installed. Terminating controller")
               thread.interrupt_main()
               thread.exit()

            p = Popen(['c:/ffmpeg/bin/ffmpeg.exe', '-nostats', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', '25', '-i', '-', '-vcodec', 'mpeg1video', '-r', '25','-b:v', '400k', "-f","mpegts","http://letsrobot.tv:"+str(video_port)+"/hello/320/240/"], stdin=PIPE)
        
        try:
            while True:
                if coz:
                    image = coz.world.latest_image
                    if image:
                        if annotated:
                            image = image.annotate_image()
                        else:
                            image = image.raw_image
                        image.save(p.stdin, 'PNG')
                else:
                    time.sleep(.1)
            p.stdin.close()
            p.wait()
        except cozmo.exceptions.SDKShutdown:
            p.stdin.close()
            p.wait()
            pass               

def say(*args):
    global coz
    message = args[0]

    try:
        coz.say_text(message, duration_scalar=0.75)
    except cozmo.exceptions.RobotBusy:
        return False


import mod_utils
import time
import _thread as thread
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
import tts.tts as tts
import extended_command
import networking

coz = None
is_headlight_on = False
forward_speed = 75
turn_speed = 50
volume = 100
charging = 0
charge_low = 3.5
charge_high = 4.5
low_battery = 0
stay_on_dock = 0

default_anims_for_keys = ["anim_bored_01",  # 0 drat
                          "anim_poked_giggle",  # 1 giggle
                          "anim_pounce_success_02",  # 2 wow
                          "anim_bored_event_02",  # 3 tick tock
                          "anim_bored_event_03",  # 4 pong face
                          "anim_petdetection_cat_01",  # 5 surprised meow
                          "anim_petdetection_dog_03",  # 6 dog reaction
                          "anim_reacttoface_unidentified_02",  # 7 look up
                          "anim_upgrade_reaction_lift_01",  # 8 excited
                          "anim_speedtap_wingame_intensity02_02"  # 9 back up quick
                         ]  

def play_anim(command, args):
    if len(command) > 1:
        try:
            coz.play_anim(command[1]).wait_for_completed()
        except ValueError:
            try:
                coz.play_anim_trigger( getattr(cozmo.anim.Triggers, command[1]) ).wait_for_completed()
            except:           
                pass
        except:
            pass
            
def set_forward_speed(command, args):
    global forward_speed
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            try:
                forward_speed=int(command[1])
                print("forward_speed set to : %d" % forward_speed)
            except ValueError:
                pass

def set_turn_speed(command, args):
    global turn_speed
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            try:
                turn_speed=int(command[1])
                print("turn_speed set to : %d" % turn_speed)
            except ValueError:
                pass

def set_volume(command, args):
    global volume
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            try:
                tmp=int(command[1])
                volume=(tmp % 101)
                coz.set_robot_volume(volume/100)
                print("volume set to : %d" % volume)
            except ValueError:
                pass

def set_charging(command, args):
    global charging
    global low_battery
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            try: 
                if command[1] == "on":
                    low_battery = 1
                    if coz.is_on_charger:
                        charging = 1
                elif command[1] == "off":
                    low_battery = 0
                    charging = 0
                print("charging set to : %d" % charging)
                networking.sendChargeState(charging)
            except ValueError:
                pass

def set_stay_on_dock(command, args):
    global stay_on_dock
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            try: 
                if command[1] == "on":
                    stay_on_dock = 1
                elif command[1] == "off":
                    stay_on_dock = 0
                print("stay_on_dock set to : %d" % stay_on_dock)
            except ValueError:
                pass

def setup(robot_config):
    global forward_speed
    global turn_speed
    global coz
    global volume
    global charge_high
    global charge_low
    global stay_on_dock
    
    coz = tts.tts_module.getCozmo()
    mod_utils.repeat_task(30, check_battery, coz)

    if robot_config.has_section('cozmo'):
        forward_speed = robot_config.getint('cozmo', 'forward_speed')
        turn_speed = robot_config.getint('cozmo', 'turn_speed')
        volume = robot_config.getint('cozmo', 'volume')
        charge_high = robot_config.getfloat('cozmo', 'charge_high')
        charge_low = robot_config.getfloat('cozmo', 'charge_low')
        stay_on_dock = robot_config.getboolean('cozmo', 'stay_on_dock')

    if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add motor commands
        extended_command.add_command('.anim', play_anim)
        extended_command.add_command('.forward_speed', set_forward_speed)
        extended_command.add_command('.turn_speed', set_turn_speed)
        extended_command.add_command('.vol', set_volume)
        extended_command.add_command('.charge', set_charging)
        extended_command.add_command('.stay', set_stay_on_dock)

    coz.set_robot_volume(volume/100) # set volume


def light_cubes(robot: cozmo.robot.Robot):
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'

    if cube1 is not None:
        cube1.set_lights(cozmo.lights.red_light)
    else:
        cozmo.logger.warning("Cozmo is not connected to a LightCube1Id cube - check the battery.")

    if cube2 is not None:
        cube2.set_lights(cozmo.lights.green_light)
    else:
        cozmo.logger.warning("Cozmo is not connected to a LightCube2Id cube - check the battery.")

    if cube3 is not None:
        cube3.set_lights(cozmo.lights.blue_light)
    else:
        cozmo.logger.warning("Cozmo is not connected to a LightCube3Id cube - check the battery.")

def dim_cubes(robot: cozmo.robot.Robot):
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'

    if cube1 is not None:
        cube1.set_lights_off()
    else:
        cozmo.logger.warning("Cozmo is not connected to a LightCube1Id cube - check the battery.")

    if cube2 is not None:
        cube2.set_lights_off()
    else:
        cozmo.logger.warning("Cozmo is not connected to a LightCube2Id cube - check the battery.")

    if cube3 is not None:
        cube3.set_lights_off()
    else:
        cozmo.logger.warning("Cozmo is not connected to a LightCube3Id cube - check the battery.")

def sing_song(robot: cozmo.robot.Robot):
    # scales is a list of the words for Cozmo to sing
    scales = ["Doe", "Ray", "Mi", "Fa", "So", "La", "Ti", "Doe"]

    # Find voice_pitch_delta value that will range the pitch from -1 to 1 over all of the scales
    voice_pitch = -1.0
    voice_pitch_delta = 2.0 / (len(scales) - 1)

    # Move head and lift down to the bottom, and wait until that's achieved
    robot.move_head(-5) # start moving head down so it mostly happens in parallel with lift
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(degrees(-25.0)).wait_for_completed()

    # Start slowly raising lift and head
    robot.move_lift(0.15)
    robot.move_head(0.15)

    # "Sing" each note of the scale at increasingly high pitch
    for note in scales:
        robot.say_text(note, voice_pitch=voice_pitch, duration_scalar=0.3).wait_for_completed()
        voice_pitch += voice_pitch_delta
        print(voice_pitch)

def check_battery( robot: cozmo.robot.Robot ):
    global charging
    global low_battery

    batt = robot.battery_voltage
    print( "COZMO BATTERY: " + str(batt) )
    if not charging:
        if ( batt < charge_low ):
            robot.say_text("battery low")
            low_battery= 1
    else:
        if batt > charge_high:
            low_battery = 0
            charging = 0
            robot.say_text("finished charging")
    networking.sendChargeState(charging)
        
def move(args):
    global charging
    global coz
    global is_headlight_on
    global low_battery
    command = args['command']

    try:
        if coz.is_on_charger and not charging:
            if low_battery:
                print("Started Charging")
                charging = 1
            else:
                if not stay_on_dock:
                    coz.drive_off_charger_contacts().wait_for_completed()

        if command == 'F':
            #causes delays #coz.drive_straight(distance_mm(10), speed_mmps(50), False, True).wait_for_completed()
            coz.drive_wheels(forward_speed, forward_speed, forward_speed*4, forward_speed*4 )
            time.sleep(0.7)
            coz.drive_wheels(0, 0, 0, 0 )
        elif command == 'B':
            #causes delays #coz.drive_straight(distance_mm(-10), speed_mmps(50), False, True).wait_for_completed()
            coz.drive_wheels(-forward_speed, -forward_speed, -forward_speed*4, -forward_speed*4 )
            time.sleep(0.7)
            coz.drive_wheels(0, 0, 0, 0 )
        elif command == 'L':
            #causes delays #coz.turn_in_place(degrees(15), False).wait_for_completed()
            coz.drive_wheels(-turn_speed, turn_speed, -turn_speed*4, turn_speed*4 )
            time.sleep(0.5)
            coz.drive_wheels(0, 0, 0, 0 )
        elif command == 'R':
            #causes delays #coz.turn_in_place(degrees(-15), False).wait_for_completed()
            coz.drive_wheels(turn_speed, -turn_speed, turn_speed*4, -turn_speed*4 )
            time.sleep(0.5)
            coz.drive_wheels(0, 0, 0, 0 )

        #move lift
        elif command == 'W':
            coz.set_lift_height(height=1).wait_for_completed()
        elif command == 'S':
            coz.set_lift_height(height=0).wait_for_completed()

        #look up down
        #-25 (down) to 44.5 degrees (up)
        elif command == 'A':
            #head_angle_action = coz.set_head_angle(degrees(0))
            #clamped_head_angle = head_angle_action.angle.degrees
            #head_angle_action.wait_for_completed()
            coz.move_head(-1.0)
            time.sleep(0.35)
            coz.move_head(0)
        elif command == 'Q':
            #head_angle_action = coz.set_head_angle(degrees(44.5))
            #clamped_head_angle = head_angle_action.angle.degrees
            #head_angle_action.wait_for_completed()
            coz.move_head(1.0)
            time.sleep(0.35)
            coz.move_head(0)

        #toggle light
        elif command =='V':
            print( "cozmo light was ", is_headlight_on )
            is_headlight_on = not is_headlight_on
            coz.set_head_light(enable=is_headlight_on)
            time.sleep(0.35)

        #animations from example
        elif command.isdigit():
            coz.play_anim(name=default_anims_for_keys[int(command)]).wait_for_completed()
    
        #things to say with TTS disabled
        elif command == 'sayhi':
            tts.say( "hi! I'm cozmo!" )
        elif command == 'saywatch':
            tts.say( "watch this" )
        elif command == 'saylove':
            tts.say( "i love you" )
        elif command == 'saybye':
            tts.say( "bye" )
        elif command == 'sayhappy':
            tts.say( "I'm happy" )
        elif command == 'saysad':
            tts.say( "I'm sad" )
        elif command == 'sayhowru':
            tts.say( "how are you?" )
        
        #cube controls
        elif command == "lightcubes":
            print( "lighting cubes" )
            light_cubes( coz )
        elif command == "dimcubes":
            print( "dimming cubes" )
            dim_cubes( coz )

        #sing song example
        elif command == "singsong":
            print( "singing song" )
            sing_song( coz )

    except cozmo.exceptions.RobotBusy:
        return False

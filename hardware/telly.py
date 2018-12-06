import robot_util
import mod_utils
import extended_command
import logging
log = logging.getLogger('LR.hardware.telly')

module = None
ser = None

def setup(robot_config):
    global module
    global ser
       
    module = mod_utils.import_module('hardware', 'serial_board')
    ser = module.setup(robot_config)

    if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add motor commands
        extended_command.add_command('.set', set_eeprom)
        
def move(args):
    module.move(args)

def set_eeprom(command, args):
    if is_authed(args['name']) == 1: # Owner
        if len(command) >= 2: 
            try:
                if command[1] == 'left':
                    setting = int(command[3]) # This is here to catch NAN errors
                    if command[2] == 'forward':
                        robot_util.sendSerialCommand(ser, "lwfs " + str(setting))
                        log.info("left_wheel_forward_speed set to %d", setting)
                    elif command[2] =='backward':
                        robot_util.sendSerialCommand(ser, "lwbs " + str(setting))
                        log.info("left_wheel_backward_speed set to %d", setting)
                elif command[1] == 'right':
                    setting = int(command[3]) # This is here to catch NAN errors
                    if command[2] == 'forward':
                        robot_util.sendSerialCommand(ser, "rwfs " + str(setting))
                        log.info("right_wheel_forward_speed set to %d", setting)
                    elif command[2] =='backward':
                        robot_util.sendSerialCommand(ser, "rwbs " + str(setting))
                        log.info("right_wheel_backward_speed set to %d", setting)
                elif command[1] == 'straight':
                    setting = int(command[2])
                    robot_util.sendSerialCommand(ser, "straight-distance " + str(int(setting * 255)))
                    log.info("straigh_delay set to %d", setting)
                elif command[1] == 'turn':
                    setting = int(command[2])
                    robot_util.sendSerialCommand(ser, "turn-distance " + str(int(setting * 255)))
                    log.info("turn_delay set to %d", setting)
                elif command[1] == 'brightness':
                    setting = int(command[2]) # This is here to catch NAN errors
                    robot_util.sendSerialCommand(ser, "led-max-brightness " + str(setting))
                    log.info("led_man_brightness to %d", setting)
            except ValueError:
                pass

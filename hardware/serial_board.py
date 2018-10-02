from __future__ import print_function
import serial
import sys

ser = None

def sendSerialCommand(ser, command):


    print(ser.name)         # check which port was really used
    ser.nonblocking()

    # loop to collect input
    #s = "f"
    #print("string:", s)
    print(str(command.lower()))
    ser.write(command.lower().encode('utf8') + "\r\n")     # write a string
    #ser.write(s)
    ser.flush()

    #while ser.in_waiting > 0:
    #    print("read:", ser.read())

    #ser.close()

def setup(robot_config):
    global ser
    serialDevice = robot_config.get('serial', 'serial_device')
    # initialize serial connection

#TODO add baud rate to config file
    serialBaud = robot_config.get('serial', 'serial_baud')
    print("baud:", serialBaud)
    try:
        ser = serial.Serial(serialDevice, serialBaud, timeout=1)  # open serial
    except:
        print("error: could not open serial port")
        try:
            ser = serial.Serial('/dev/ttyACM0', serialBaud, timeout=1)  # open serial
        except:
            print("error: could not open serial port /dev/ttyACM0")
            try:
                ser = serial.Serial('/dev/ttyUSB0', serialBaud, timeout=1)  # open serial
            except:
                print("error: could not open serial port /dev/ttyUSB0")
                try:
                    ser = serial.Serial('/dev/ttyUSB1', serialBaud, timeout=1)  # open serial
                except:
                    print("error: could not open serial port /dev/ttyUSB1")
                    try:
                        ser = serial.Serial('/dev/ttyUSB2', serialBaud, timeout=1)  # open serial
                    except:
                        print("error: could not open serial port /dev/ttyUSB2")

    if ser is None:
        print("error: could not find any valid serial port")
        sys.exit()
        
    return(ser)
    
def move(args):
    command = args['command']
    # need to verify args for key position
    #if robot_config.get('serial', 'serial_keyposition') && args['keyposition']:
        #command = args['command']+'_'+args['keyposition']
    sendSerialCommand(ser, command)
	
from __future__ import print_function
import serial
import sys

ser = None
debug_messages = None

def sendSerialCommand(ser, command):

    if debug_messages:
       print("serial send: ", str(command.lower()))
    ser.write(command.lower().encode('utf8') + b"\r\n")     # write a string
    #ser.write(s)
    ser.flush()

    #while ser.in_waiting > 0:
    #    print("read:", ser.read())

    #ser.close()

def setup(robot_config):
    global ser
    global debug_messages

    serial_device = robot_config.get('serial', 'serial_device')
    debug_messages = robot_config.getboolean('misc', 'debug_messages')
    serialBaud = robot_config.getint('serial', 'baud_rate')

    # initialize serial connection
    try:
        ser = serial.Serial(serialDevice, serialBaud, timeout=0, write_timeout=0)  # open serial
    except:
        print("error: could not open serial port")
        try:
            ser = serial.Serial('/dev/ttyACM0', serialBaud, timeout=0, write_timeout=0)  # open serial
        except:
            print("error: could not open serial port /dev/ttyACM0")
            try:
                ser = serial.Serial('/dev/ttyUSB0', serialBaud, timeout=0, write_timeout=0)  # open serial
            except:
                print("error: could not open serial port /dev/ttyUSB0")
                try:
                    ser = serial.Serial('/dev/ttyUSB1', serialBaud, timeout=0, write_timeout=0)  # open serial
                except:
                    print("error: could not open serial port /dev/ttyUSB1")
                    try:
                        ser = serial.Serial('/dev/ttyUSB2', serialBaud, timeout=0, write_timeout=0)  # open serial
                    except:
                        print("error: could not open serial port /dev/ttyUSB2")

    if ser is None:
        print("error: could not find any valid serial port")
        sys.exit()
   
    if debug_messages: 
       print("Serial Connected")
       print("port:", ser.name)
       print("baud:", serialBaud)

    return(ser)
    
def move(args):
    command = args['command']
    sendSerialCommand(ser, command)

import serial
import serial.tools.list_ports as ports
import sys
import logging
import robot_util
log = logging.getLogger('RemoTV.hardware.serial_board')

ser = None
serialDevice = None
serialBaud = None
restarts = 0

def sendSerialCommand(ser, command):
    global restarts

    try:
        log.info("serial send: %s", str(command.lower()))
        ser.write(command.lower().encode('utf8') + b"\r\n")     # write a string
        ser.flush()
        restarts = 0
    except:
        log.debug("Attempting to restart serial")
        try:
            ser.close()
        except:
            pass
        connectSerial(serialDevice, serialBaud)


def searchSerial(name):
    for port in ports.comports():
        if name in port.description or \
           name in port.hwid or \
           name in port.manufacturer:
            return port.device
    return None

def fallbackSerial():
    for port in ports.comports():
        if not port.device == "/dev/ttyAMA0":
            yield port.device
        else:
            log.debug("Serial Fallback ignoring onboard bluetooth serial")
    log.debug("No more possible serial ports")

def setup(robot_config):
    global serialDevice
    global serialBaud

    serialDevice = robot_config.get('serial', 'serial_device')
    serialBaud = robot_config.getint('serial', 'baud_rate')

    if robot_config.has_option('serial', 'serial_name'):
        deviceName = robot_config.get('serial', 'serial_name')
        device = searchSerial(deviceName)
        if device != None:           
            serialDevice = device
            log.info("Serial port named {} found at {}".format(deviceName, device))
        else:
            log.info("Serial port named {} NOT FOUND".format(deviceName))       

    connectSerial(serialDevice, serialBaud)
    
    if ser is None:
        log.critical("error: could not connect to any valid serial port")
        robot_util.terminate_controller()

def connectSerial(serialDevice, serialBaud):
    global ser
    global restarts
    restarts = restarts + 1

    ser = None
    
    # initialize serial connection
    try:
        ser = serial.Serial(serialDevice, serialBaud, timeout=0, write_timeout=0)  # open serial
    except:
        log.error("Could not open serial port {}".format(serialDevice))
        ports = fallbackSerial()
        for port in ports:     
            try:
                ser = serial.Serial(port, serialBaud, timeout=0, write_timeout=0)  # open serial
                break
            except:
                log.error("Could not open serial port {}".format(port))

    if ser is None:
        log.critical("Error: could not find any valid serial port")
        if restarts >= 20:
            log.critical("Error: too many attemtps to reconnect serial")
            robot_util.terminate_controller()
    else:              
        log.info("Serial Connected")
        log.debug("port: {}".format(ser.name))
        log.debug("baud: {}".format(ser.baudrate))

    return(ser)
    
def move(args):
    command = args['button']['command']
    sendSerialCommand(ser, command)

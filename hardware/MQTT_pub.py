import logging
log = logging.getLogger('LR.hardware.mqtt')

try:
    import paho.mqtt.client as mqttc
except ImportError:
    log.critical("You need to install the paho mqtt client")

ser = None

def sendMQTTCommand(ser, command):

    log.info("serial send: ", str(command.lower()))
    ser.write(command.lower().encode('utf8') + b"\r\n")     # write a string
    ser.flush()

def setup(robot_config):
    global ser

    serial_device = robot_config.get('serial', 'serial_device')
    serialBaud = robot_config.getint('serial', 'baud_rate')

    # initialize serial connection
    try:
        ser = serial.Serial(serialDevice, serialBaud, timeout=0, write_timeout=0)  # open serial
    except:
        log.error("error: could not open serial port")
        try:
            ser = serial.Serial('/dev/ttyACM0', serialBaud, timeout=0, write_timeout=0)  # open serial
        except:
            log.error("error: could not open serial port /dev/ttyACM0")
            try:
                ser = serial.Serial('/dev/ttyUSB0', serialBaud, timeout=0, write_timeout=0)  # open serial
            except:
                log.error("error: could not open serial port /dev/ttyUSB0")
                try:
                    ser = serial.Serial('/dev/ttyUSB1', serialBaud, timeout=0, write_timeout=0)  # open serial
                except:
                    log.error("error: could not open serial port /dev/ttyUSB1")
                    try:
                        ser = serial.Serial('/dev/ttyUSB2', serialBaud, timeout=0, write_timeout=0)  # open serial
                    except:
                        log.error("error: could not open serial port /dev/ttyUSB2")

    if ser is None:
        log.critical("error: could not find any valid serial port")
        sys.exit()
   
        log.info("Serial Connected")
        log.debug("port:", ser.name)
        log.debug("baud:", serialBaud)

    return(ser)
    
def move(args):
    command = args['command']
    sendMQTTCommand(command)

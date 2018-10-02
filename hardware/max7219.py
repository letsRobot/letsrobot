import spidev

columns = [0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8]
LEDOn = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF] 
LEDOff = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]
LEDEmoteSmile = [0x0,0x0,0x24,0x0,0x42,0x3C,0x0,0x0]
LEDEmoteSad = [0x0,0x0,0x24,0x0,0x0,0x3C,0x42,0x0]
LEDEmoteTongue = [0x0,0x0,0x24,0x0,0x42,0x3C,0xC,0x0]
LEDEmoteSurprise = [0x0,0x0,0x24,0x0,0x18,0x24,0x24,0x18]
spi = None

def setup(robot_config):
    global LEDEmoteSmile
    global LEDEmoteSad
    global LEDEmoteTongue
    global LEDEmoteSuprise
    global module
    global spi
    
    #LED controlling
    spi = spidev.SpiDev()
    spi.open(0,0)
    #VCC -> RPi Pin 2
    #GND -> RPi Pin 6
    #DIN -> RPi Pin 19
    #CLK -> RPi Pin 23
    #CS -> RPi Pin 24
    
    # decoding:BCD
    spi.writebytes([0x09])
    spi.writebytes([0x00])
    # Start with low brightness
    spi.writebytes([0x0a])
    spi.writebytes([0x03])
    # scanlimit; 8 LEDs
    spi.writebytes([0x0b])
    spi.writebytes([0x07])
    # Enter normal power-mode
    spi.writebytes([0x0c])
    spi.writebytes([0x01])
    # Activate display
    spi.writebytes([0x0f])
    spi.writebytes([0x00])
    rotate = robot_config.getint('max7219', 'ledrotate')
    if rotate == 180:
        LEDEmoteSmile = LEDEmoteSmile[::-1]
        LEDEmoteSad = LEDEmoteSad[::-1]
        LEDEmoteTongue = LEDEmoteTongue[::-1]
        LEDEmoteSurprise = LEDEmoteSurprise[::-1]
    SetLED_Off()
            
def SetLED_On():
    for i in range(len(columns)):
        spi.xfer([columns[i],LEDOn[i]])

def SetLED_Off():
    for i in range(len(columns)):
        spi.xfer([columns[i],LEDOff[i]])

def SetLED_E_Smiley():
    for i in range(len(columns)):
        spi.xfer([columns[i],LEDEmoteSmile[i]]) 

def SetLED_E_Sad():
    for i in range(len(columns)):
        spi.xfer([columns[i],LEDEmoteSad[i]])

def SetLED_E_Tongue():
    for i in range(len(columns)):
        spi.xfer([columns[i],LEDEmoteTongue[i]])

def SetLED_E_Surprised():
    for i in range(len(columns)):
        spi.xfer([columns[i],LEDEmoteSurprise[i]])

def SetLED_Low():
    # brightness MIN
    spi.writebytes([0x0a])
    spi.writebytes([0x00])

def SetLED_Med():
    #brightness MED
    spi.writebytes([0x0a])
    spi.writebytes([0x06])

def SetLED_Full():
    # brightness MAX
    spi.writebytes([0x0a])
    spi.writebytes([0x0F])
        
def move(args):
    command = args['command']
    
    if command == 'LED_OFF':
        SetLED_Off()
    if command == 'LED_FULL':
        SetLED_On()
        SetLED_Full()
    if command == 'LED_MED':
        SetLED_On()
        SetLED_Med()
    if command == 'LED_LOW':
        SetLED_On()
        SetLED_Low()
    if command == 'LED_E_SMILEY':
        SetLED_On()
        SetLED_E_Smiley()
    if command == 'LED_E_SAD':
        SetLED_On()
        SetLED_E_Sad()
    if command == 'LED_E_TONGUE':
        SetLED_On()
        SetLED_E_Tongue()
    if command == 'LED_E_SURPRISED':
        SetLED_On()
        SetLED_E_Suprised()

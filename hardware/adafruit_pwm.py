import logging
import time

log = logging.getLogger('RemoTV.hardware.adafruit_pwm')

try:
    import Adafruit_PCA9685
except ImportError:
    log.critical("You need to install Adafruit_PCA9685")
    log.critical("Please install Adafruit_PCA9685 for python and restart this script.")
    log.critical("To install: pip install adafruit_pca9685")

pwm = None

def setup(robot_config):
    global pwm
    pwm = Adafruit_PCA9685.PCA9685(int(robot_config.get('adafruit_pwm', 'address'),16)) 
    pwm.set_pwm_freq(robot_config.getint('adafruit_pwm', 'pwm_freq'))      # Set frequency to 60 Hz
    
def move(args):
    command = args['button']['command']
    
    log.debug("move adafruit pwm command : %s", command)
        
    if command == 'l':
        pwm.set_pwm(1, 0, 300) # turn left
        pwm.set_pwm(0, 0, 445) # drive forward
        time.sleep(0.5)
        pwm.set_pwm(1, 0, 400) # turn neutral
        pwm.set_pwm(0, 0, 335) # drive neutral

    if command == 'r':
        pwm.set_pwm(1, 0, 500) # turn right
        pwm.set_pwm(0, 0, 445) # drive forward
        time.sleep(0.5)
        pwm.set_pwm(1, 0, 400) # turn neutral
        pwm.set_pwm(0, 0, 335) # drive neutral

    if command == 'bl':
        pwm.set_pwm(1, 0, 300) # turn left
        pwm.set_pwm(0, 0, 270) # drive backward
        time.sleep(0.5)
        pwm.set_pwm(1, 0, 400) # turn neutral
        pwm.set_pwm(0, 0, 335) # drive neutral

    if command == 'br':
        pwm.set_pwm(1, 0, 500) # turn right
        pwm.set_pwm(0, 0, 270) # drive backward
        time.sleep(0.5)
        pwm.set_pwm(1, 0, 400) # turn neurtral
        pwm.set_pwm(0, 0, 335) # drive neutral

        
    if command == 'f':
        pwm.set_pwm(0, 0, 445) # drive forward
        time.sleep(0.3)
        pwm.set_pwm(0, 0, 345) # drive slowly forward
        time.sleep(0.4)
        pwm.set_pwm(0, 0, 335) # drive neutral
    if command == 'b':
        pwm.set_pwm(0, 0, 270) # drive backward
        time.sleep(0.3)
        pwm.set_pwm(0, 0, 325) # drive slowly backward
        time.sleep(0.4)
        pwm.set_pwm(0, 0, 335) # drive neutral

    if command == 'S2INC': # neutral
        pwm.set_pwm(2, 0, 300)

    if command == 'S2DEC':
        pwm.set_pwm(2, 0, 400)

    if command == 'POS60':
        pwm.set_pwm(2, 0, 490)        

    if command == 'NEG60':
        pwm.set_pwm(2, 0, 100)                
    


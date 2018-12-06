from Adafruit_PWM_Servo_Driver import PWM
import logging
log = logging.getLogger('LR.hardware.adafruit_pwm')

def setup(robot_config):
    pwm = PWM(int(robot_config.get('adafruit_pwm', 'address'),16)) 
    pwm.setPWMFreq(robot_config.getint('adafruit_pwm', 'pwm_freq'))      # Set frequency to 60 Hz
    
def move(args):
    command = args['command']
    
    log.debug("move adafruit pwm command : %s", command)
        
    if command == 'L':
        pwm.setPWM(1, 0, 300) # turn left
        pwm.setPWM(0, 0, 445) # drive forward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neutral
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'R':
        pwm.setPWM(1, 0, 500) # turn right
        pwm.setPWM(0, 0, 445) # drive forward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neutral
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'BL':
        pwm.setPWM(1, 0, 300) # turn left
        pwm.setPWM(0, 0, 270) # drive backward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neutral
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'BR':
        pwm.setPWM(1, 0, 500) # turn right
        pwm.setPWM(0, 0, 270) # drive backward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neurtral
        pwm.setPWM(0, 0, 335) # drive neutral

        
    if command == 'F':
        pwm.setPWM(0, 0, 445) # drive forward
        time.sleep(0.3)
        pwm.setPWM(0, 0, 345) # drive slowly forward
        time.sleep(0.4)
        pwm.setPWM(0, 0, 335) # drive neutral
    if command == 'B':
        pwm.setPWM(0, 0, 270) # drive backward
        time.sleep(0.3)
        pwm.setPWM(0, 0, 325) # drive slowly backward
        time.sleep(0.4)
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'S2INC': # neutral
        pwm.setPWM(2, 0, 300)

    if command == 'S2DEC':
        pwm.setPWM(2, 0, 400)

    if command == 'POS60':
        pwm.setPWM(2, 0, 490)        

    if command == 'NEG60':
        pwm.setPWM(2, 0, 100)                
    


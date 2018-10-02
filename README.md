# LetsRobot.tv


## Open Robot Control Code For Connecting to LetsRobot.tv 

LetsRobot.tv is a site for interacts with other using telepresence robots. User create their own robots and add them to the site.
https://letsrobot.tv

## Installing robot control and video scripts on a Raspberry Pi


The RasPi will need the following things install so it can talk to your motor and talk to the internet.

1. Install python serial, gnutls, python-dev, espeak, and python-smbus:

   ```
   sudo apt-get install python-serial python-dev libgnutls28-dev espeak python-smbus python-pip git
   ```


2. Install configparser and socket.io client for python:

   ```
   sudo pip install socketIO-client configparser
   ```


3. Install alsa-lib
   ```
   cd ~
   mkdir src
   cd ~/src
   wget ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.25.tar.bz2 
   tar xjf alsa-lib-1.0.25.tar.bz2
   cd ~/src/alsa-lib-1.0.25 
   ./configure --host=arm-unknown-linux-gnueabi 
   make -j4 
   sudo make install
   ```

4. Install x264
   ```
   cd ~/src
   git clone git://git.videolan.org/x264
   cd x264
   ./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
   make -j4
   sudo make install
   ```

5. Install FFmpeg
   ```
   cd ~/src
   git clone https://github.com/FFmpeg/FFmpeg.git
   cd FFmpeg
   ./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --enable-gnutls --extra-libs=-ldl
   make -j4
   sudo make install
   ```


## Bring your Bot to life: Programs to run on the Raspberry Pi

1. Start by cloning the LetsRobot repository
   ```
   cd ~
   git clone https://github.com/letsrobot/letsrobot
   cd letsrobot
   ```

2. Go to new robot page to create a robot. If you already have one, go to manage robots. There you'll find your Robot ID and Camera ID.

3. These two scripts need to be running in the background to bring your robot to life: controller.py and send_video.py. Here are instructions about how to start them. Copy the 'start_robot' Script from runmyrobot/Scripts to the pi home folder

   ```
   cp ~/letsrobot/scripts/start_robot ~/
   ```

4. Edit the script so you can adjust the settings for controller.py and send_video.py.  
   ```
   nano ~/start_robot
   ```  
   Change YOURROBOTID and YOURCAMERAID to your robots robot ID and camera ID. You are provided with both IDs when you create a new bot on the website in step 2.


5. Copy letsrobot.sample.conf to letsrobot.conf

   ```
   cp letsrobot.sample.conf letsrobot.conf
   ```

## Configure the controller

1. Edit the letsrobot.conf file created in the previous section.
   ```
   nano letsrobot.conf
   ```
2. Configure the [robot] section
   * owner should be the username you have registered the robot under on the LetsRobot site.
   * robot_id should be the robot ID for your robot, obtained in step 2 of the Bring your Bot to life section.
   * camera_id should be the camera ID for your robot, obtained in same step as robot ID.
   * turn_delay is only used by the motor_hat, mdd10 and telly. This changes how long your bot turns for. I suggest you leave this at the default value until after you bot is moving.
   * straight_delay is only used by the motor_hat, mdd10 and telly. This changes how long your bot turns for. I suggest you leave this at the default value until after you bot is moving.
   * type should be the hardware type for the motor controller of your bot. Available types are currently.
      * adafruit_pwm
      * cozmo
      * gopigo2
      * gopigo3
      * l298n
      * maestro-servo
      * max7219
      * mc33926
      * mdd10
      * motor_hat
      * motozero
      * none
      * owi_arm
      * pololu
      * serial_board
      * telly
   * Configure your hardwares section. Each hardware type can have their own section it the controller. Look through the file for a section named the same as your hardware controller. If the section exists, read through it and adjust the variable as required.

3. Configure the [tts] section 
   * tts_volume This is the volume level you want your bot to start with.
   * anon_tts This allows you to enable or disable anonymous users access to your bots TTS features.
   * filter_url_tts This option allows URLs pasted into chat to be blocked from the TTS function.
   * ext_chat This enables or disables the extended chat functions.
   * hw_hum This is the ALSA hardware number for your pi. 0 is the first sound card and should work for most bots.
   * type should be the type of TTS software you are using. The currently supported TTS types are. espeak was installed in the previous steps, and makes a good default tts.
      * espeak
      * fesitval
      * Amazon Polly
      * cozmo_tts

## Start scripts on boot
1. Use crontab to start the start_robot script on booting:

   ```
   crontab -e
   ```

2. insert following line and save:

   ```
   @reboot /bin/bash /home/pi/start_robot
   ```

That's it!

## How does this work

We use ffmpeg to stream audio and socket.io to send control messages.

## How to contribute

The is a community project. Making your own bot? Adding your own control stuff? Cool! We'd like to hear from you.


# Hardware Compatibility
---
The following hardware is supported.

* Adafruit Motor Hat
* Adafruit PWM / Servo Hat
* Anki Cozmo
* GoPiGo 2
* GoPiGo 3
* L298N Dual Motor Controller
* Pololu Maestro Servo Controller (experimental)
* MAX7219 SPI Led Driver
* Pololu Dual MC33926 Motor Driver (experimental)
* Pololu DRV8835 Dual Motor Driver
* Cytron MDD10 10 Amp Motor Driver
* MotoZero 4 Motor Controller
* OWI 535 Robotic Arm (USB controller)
* Serial Based controllers (Parallaxy or Arduinos)

Missing something?, you can add it, open source! Instructions for adding new hardware can be found [here.](EXTENDING_CONTROLLER.md)

## Chat Commands
When ext_chat is enabled, the following chat commands are available. To use, just type them into the chat box on your bots page. These chat commands have no effect on how the site behaves, they only affect the bot. There are some functions that duplicate functions on the site. These changes are not saved and are lots on reboot.

* `.devmode X` Set dev mode. In dev mode, only the owner can drive. If demode is set to mods, your local mods can also drive [on|off|mods].
* `.anon control X` Sets if anonymous users can drive your bot [on|off].
* `.anon tts X` Sets if anonymous users messages are passed to TTS [on|of].
* `.anon X` Sets both anonymous control and tts access [on|off].
* `.tts X` Mute the bots TTS [mute|unmute]
* `.ban NAME` Ban user NAME from controlling your bots
* `.unban NAME` remove user NAME from the ban list
* `.timeout NAME` Timeout user NAME from controlling your bots for 5 minutes
* `.untimout NAME` remove user NAME from the timeout list.
* `.brightness X` set the camera brightness [0..255]
* `.contrast X` set the camera contrast [0..255]
* `.saturation X` set the camera saturation [0..255]
* `.stationary` Toggles stationary mode on and off. When enabled, forward / backward commands will be blocked.

Hardware modules can have their own hardware specific TTS commands.

# Instructions for Specific Hardware Configurations

## Cozmo

For Anki Cozmo on Mac or Linux, please see the intructions [here](COZMO_MAC.md).
For Windows instructions, please see the instructions [here](COZMO_WIN.md).

## GoPiGo3

For GoPiGo3, you will need to install the gopigo3 python module (which is different than older versions). It will need to be installed with the installation script from Dexter. Also, PYTHONPATH needs to be set to "/home/pi/Dexter/GoPiGo3/Software/Python"

Refer to this:
https://github.com/DexterInd/GoPiGo3
   ```
   sudo git clone http://www.github.com/DexterInd/GoPiGo3.git /home/pi/Dexter/GoPiGo3
   sudo bash /home/pi/Dexter/GoPiGo3/Install/install.sh
   sudo reboot
   ```

## Adafruit Motor Hat

Install [motor HAT software](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/installing-software):

## Adafruit PWM / Servo Hat
Install [PWM / Servo hat software](https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/using-the-python-library)

## Pololu Maestro Servo Controller
Install [Maestro Servon controller library]( https://github.com/FRC4564/Maestro) into the hardware/ subdirectory.

## Pololu DRV8835 Motor Driver
Install [DRV8835 Motor Driver library](https://github.com/pololu/drv8835-motor-driver-rpi)

<<<<<<< HEAD
## Pololu MC33926 Motor Driver
Install [MC33926 Motor Driver library](https://github.com/pololu/dual-mc33926-motor-driver-rpi)

# High Level Overview

![robot client topology](https://raw.githubusercontent.com/letsrobot/letsrobot/master/documentation/RobotClientTopology.png)

The robot client connects via websockets to the API service to retrieve configuration information, to the chat to receive chat messages, the video/audio relays to send its camera and microphone capture, and to the control service to receive user commands.

## Interfaces: 
Control server via socket.io
Application server via socket.io and HTTP
Chat server via socket.io
Sends video stream via websockets
Sends audio stream via websockets

## Responsibilities:
Capturing Audio and Video
Relays commands to robot hardware
Text to Speech
Supports remote login for diagnostics and updates
Configuration updates from the web client (partially implemented)

## Detailed Description:
The robot client connects to four external services: API Service, Chat Service, Video/Audio Service, and the Control Service.

#### API Service
Provides information about which host and port to connect to for the chat service, video/audio service, and control service

#### Chat Service
Relays chat messages sent from the web clients to the robot

#### Video/Audio Service
The robot client streams ffmpeg output to the video/audio service

#### Control Service
Relays control messages sent from the web clients to the robot

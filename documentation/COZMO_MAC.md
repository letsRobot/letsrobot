# CozmoRemoTV
Host Anki Cozmo on remo.tv

## Pre-setup

### install socketIO-client for python3
```sh
python3 -m pip install socketIO-client configparser
```
## Setup instructions:

Setup the Cozmo SDK on your computer using their instructions:

* http://cozmosdk.anki.com/docs/initial.html#installation

Edit `controller.conf`

* Enter your owner, robot_key, etc. from remo.tv
* change [robot] `type=none` to `type=cozmo`
* change [tts] `type=none` to `type=cozmo_tts`
* change [ffmpeg] `type=ffmpeg-arecord` to `type=none`
* Save file as controller.conf

## Extra Mac setup instructions:
## install ffmpeg:
brew install ffmpeg

## Starting Cozmo:

* Using the Cozmo app enter SDK mode and connect your mobile device to the host machine.
* Execute the LetsRobot controller using 
```sh 
   $ cd ~/remotv
   $ python3 controller.py
```
* For audio streaming, you need a second instance of the controller with a separate conf file with the following changes
```python
   [robot]
   type=none

   [camera]
   no_camera=true

   [tts]
   type=none
```
* All other changes remain the same. To execute, run
```sh
   $ cd ~/remotv
   $ python3 controller.py
```

* If you don't want to, or cannot run another terminal window, `screen` is a helpful tool for running commands concurrently.

```sh
   $ sudo apt install screen
   $ screen
```
 * To detach from a screen session, type `^A d`. To Reattach a detached screen session, type `screen -r`.

## Update the Let's Robot robot configuration to have these custom controls:
A proper method for changing controls is not yet implemented. You can send a `POST` request to `http://dev.remo.tv:3231/api/controls/make` with a `BEARER` authorization header containing your JWT token. Your token can be found in your browsers `LocalStorage` or you can make another `POST` request documented [here](https://documenter.getpostman.com/view/7535161/S1a34nhU?version=latest#2319b7c3-7415-43e6-a086-c1e1b0c27688). The body of your controls request should have the following structure. This example is designed to work out of the box with the existing Cozmo controls.

```json
{
   "channel_id": "your-channel-id",
   "buttons": [
      { "label": "Left",         "hot_key": "a", "command": "L" },
      { "label": "Right",        "hot_key": "d", "command": "R" },
      { "label": "Forward",      "hot_key": "w", "command": "F" },
      { "label": "Backward",     "hot_key": "s", "command": "B" },
      { "label": "Look Up",      "hot_key": "q", "command": "Q" },
      { "label": "Look Down",    "hot_key": "z", "command": "A" },
      { "label": "Lift Up",      "hot_key": "e", "command": "W" },
      { "label": "Lift Down",    "hot_key": "c", "command": "S" },
      { "label": "Light Toggle", "hot_key": "x", "command": "V"},
      { "label": "Drat",         "hot_key": "0", "command": "0" },
      { "label": "Giggle",       "hot_key": "1", "command": "1" },
      { "label": "Wow",          "hot_key": "2", "command": "2" },
      { "label": "Tick Tock",    "hot_key": "3", "command": "3" },
      { "label": "Ping Pong",    "hot_key": "4", "command": "4" },
      { "label": "Meow",         "hot_key": "5", "command": "5" },
      { "label": "WufWuf",       "hot_key": "6", "command": "6" },
      { "label": "LookUp",       "hot_key": "7", "command": "7" },
      { "label": "Excite",       "hot_key": "8", "command": "8" },
      { "label": "BackUp",       "hot_key": "9", "command": "9" },
      { "label": "Hello",        "hot_key": "",  "command": "sayhi" },
      { "label": "Watch This",   "hot_key": "",  "command": "saywatch" },
      { "label": "Love You",     "hot_key": "",  "command": "saylove" },
      { "label": "Bye",          "hot_key": "",  "command": "saybye" },
      { "label": "Happy",        "hot_key": "",  "command": "sayhappy" },
      { "label": "Sad",          "hot_key": "",  "command": "saysad" },
      { "label": "How Are You",  "hot_key": "",  "command": "sayhowru" },
      { "label": "Sing Song",    "hot_key": "",  "command": "singsong" },
      { "label": "Light Cubes",  "hot_key": "",  "command": "lightcubes" },
      { "label": "Dim Cubes",    "hot_key": "",  "command": "dimcubes" }
   ]
}
```


## Cozmo Chat Commands
In addition to the standard chat commands, Cozmo has several specific chat commands available to the owner. You can type these into the chat box on the robot page.

* `.anim NAME` this will play the NAME animation.
* `.forward_speed ###` this will allow you to adjust how fast Cozmo moves forward / backwards.
* `.turn_speed ###` this will adjust how far Cozmo turns left and right.
* `.vol ###` This turns Cozmos volume up or down [0...100].
* `.charge X` If Cozmo is on the dock, force the changin g state. If Cozmo is off the dock, mark the charging state to start as soon as Cozmo docks [on|off].
* `.stay X` Set Cozmo to stay locked in the dock, regardless of charge state [on|off].
* `.annotate` Enable  / Disable the annotated view, to see what Cozmo is seeing.
* `.color` or `.colour` Enable / Disable colour. Colour reduces the resolution of the video.

## Note for audio streaming on MacOS:
NOTE : These instructions are out of date. The current method to stream audio involves changing the audio_input_format to avfoundation, video type to ffmpeg and no_camera to true.

The `startAudioCaptureLinux` function in send_video.py calls ffmpeg with alsa input. If you want to stream audio from your mac use `-f avfoundation -i ":0"` in place of `-f alsa -ar 44100 -ac %d -i hw:%d`.

For example:

```python
audioCommandLine = '/usr/local/bin/ffmpeg -f avfoundation -i ":0" -f mpegts -codec:a mp2 -b:a 128k -muxdelay 0.001 http://dev.remo.tv:1567/transmit?name=%s-audio' % (channelID)
```

# CozmoLetsRobot
Host Anki Cozmo on LetsRobot.tv from a windows based computer.

## Pre-setup

### install python3 

Download and setup the latest version of python3 for windows.

* https://www.python.org/downloads/windows/

### install ffmpeg

Download the latest version of ffmpeg for windows. Click the windows icon under more download options, then click the windows builds link. Then click to select 32/64 bit and click download build.

* https://www.ffmpeg.org/download.html#build-windows

Unzip the files into c:\ffmpeg so the ffmpeg.exe file is located at C:\ffmpeg\bin\ffmpeg.exe

### install socketIO-client for python3
pip install socketIO-client configparser

## Setup instructions:

Setup the Cozmo SDK on your computer using their instructions for windows:

* http://cozmosdk.anki.com/docs/initial.html#installation

Clone Nocturnal's fork of the runmyrobot scripts:

* git clone https://github.com/Nocturnal42/runmyrobot.git

Edit runmyrobot/letsrobot.sample.conf:

* Enter your owner, robot_id, camera_id from LetsRobot.tv
* change [robot] `type=none` to `type=cozmo`
* change [tts] `type=none` to `type=cozmo_tts`
* change [ffmpeg] `type=ffmpeg` to `type=none`
* Save file as letsrobot.conf
* examine the [cozmo] section and change variables as appropriate

## Starting Cozmo:

* Using the Cozmo app enter SDK mode and connect your mobile device to the host machine.
* Execute the LetsRobot controller using `python controller.py`

## Update the Let's Robot robot configuration to have these custom controls:
Please see [Customizing Your UI](https://letsrobot.readme.io/docs/customizing-your-ui) for more help
```
[  
   {  
      "button_panels":[  
         {  
            "button_panel_label":"movement controls",
            "buttons":[  
               {  
                  "label":"Left",
                  "command":"L"
               },
               {  
                  "label":"Right",
                  "command":"R"
               },
               {  
                  "label":"Forward",
                  "command":"F"
               },
               {  
                  "label":"Backward",
                  "command":"B"
               },
               {  
                  "label":"LookUp",
                  "command":"Q"
               },
               {  
                  "label":"LookDown",
                  "command":"A"
               },
               {  
                  "label":"LiftUp",
                  "command":"W"
               },
               {  
                  "label":"LiftDown",
                  "command":"S"
               },
               {  
                  "label":"LightToggle",
                  "command":"V"
               }
            ]
         },
         {  
            "button_panel_label":"animation controls",
            "buttons":[  
               {  
                  "label":"drat",
                  "command":"0"
               },
               {  
                  "label":"giggle",
                  "command":"1"
               },
               {  
                  "label":"wow",
                  "command":"2"
               },
               {  
                  "label":"tick tock",
                  "command":"3"
               },
               {  
                  "label":"ping pong",
                  "command":"4"
               },
               {  
                  "label":"meow",
                  "command":"5"
               },
               {  
                  "label":"wufwuf",
                  "command":"6"
               },
               {  
                  "label":"lookup",
                  "command":"7"
               },
               {  
                  "label":"excite",
                  "command":"8"
               },
               {  
                  "label":"backup",
                  "command":"9"
               }
            ]
         },
         {  
            "button_panel_label":"say something cute",
            "buttons":[  
               {  
                  "label":"hello",
                  "command":"sayhi"
               },
               {  
                  "label":"watch this",
                  "command":"saywatch"
               },
               {  
                  "label":"love you",
                  "command":"saylove"
               },
               {  
                  "label":"bye",
                  "command":"saybye"
               },
               {  
                  "label":"happy",
                  "command":"sayhappy"
               },
               {  
                  "label":"sad",
                  "command":"saysad"
               },
               {  
                  "label":"howru",
                  "command":"sayhowru"
               }
            ]
         },
         {  
            "button_panel_label":"more fun stuff",
            "buttons":[  
               {  
                  "label":"singsong",
                  "command":"singsong",
                  "premium":true,
                  "price":1000000
               },
               {  
                  "label":"lightcubes",
                  "command":"lightcubes",
                  "premium":true,
                  "price":0
               },
               {  
                  "label":"dimcubes",
                  "command":"dimcubes",
                  "premium":true,
                  "price":0
               }
            ]
         }
      ]
   }
]
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


## Note for audio streaming:

To stream audio you will need to have a microphone or webcam with microphone attached to your computer. First you need to determine the device name for your microphone.

c:\ffmpeg\bin\ffmpeg.exe -list_devices true -f dshow -i dummy

This will list the available input devices. The device name is contained between "" like so, "Microphone (2- Logitech G533 Gaming Headset)".

Edit send_video.py and locate the line that starts with 'audioCommandLine = ', comment this line out by adding a # to the start of the line. Several lines below that should be another windows version of the audioCommandLine, uncomment it by removing the # at the begining of the line.

On the line you just uncommented, find the part that reads 'TOSHIBA Web Camera - HD' and replace it with the audio device name you found earlier.

Save the changes and execute python send_video.py YOURCAMERAID 0 --no-camera, replace YOURCAMERAID with the camera id for your robot.


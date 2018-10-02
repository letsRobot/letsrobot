# Extending Controller Functions

The controller is designed to make modifying the functionality as easy as possible, while still allowing the core code to be updated without requiring users to modify the controller with their custom functionality every time.

## Adding New Hardware Support

Adding new hardware to the controller is fairly simple. Create a new .py file in the hardware directory. The name you give this file becomes the name for this hardware type in the configuration file. This file needs to contain two functions, as shown in this example.

```python
def setup(robot_config):
    # Your hardware setup code goes here
    return

def move(args):
    command = args['command']
    
    if command == 'F':
        # Your hardware movement code for forward goes here
        return
    elif command == 'B':
        # Your hardware movement code for backwards goes here
        return
    elif command == 'L':
        # Your hardware movement code for left goes here
        return
    elif command == 'R':
        # Your hardware movement code for right goes here
        return
   return
```
### setup() function

The ```setup()``` function is passed the ConfigParser object for the letsrobot.conf file. You can create a new section for your hardware in the letsrobot.conf file, and store configuration variables there. Variables in the configuration can be accessed with ```robot_config.get(section, option)```, ```robot_config.getint(section, option)``` and ```robot_config.getboolean(section, option)```.

Any initial hardware setup should happen when the ```setup()``` function is called. This function is only called once.

### move() function
The ```move()``` function is passed the object containing the command for the robot received from the server. 

```
{u'robot_id': u'49345483', u'command': u'F', u'user': {u'username': u'Nocturnal', u'anonymous': False}, u'key_position': u'down'}
```
It should be mostly self explainitory, The most important part is the ```'command'```. The ```move()``` function should use the provided command to determine how to move robot. If your hardware needs a specific start and stop instructions to move, with a pause between, you should import the ```time``` module and use it's ```sleep()``` function.

```python
    GPIO.output(StepPinForward, GPIO.HIGH)
    time.sleep(sleeptime)
    GPIO.output(StepPinForward, GPIO.LOW)
```

The controller will block, and ignore any other commands from the server until the ```move()``` function finishes. If you want to impliment your own blocking, or impliment proper asynchronous movement commands, you can disable the blocking by setting ```enable_async=True``` in the misc
section of letsrobot.conf

## Adding New TTS Support

This is almost exactly the same as adding new hardware. Create a new .py file in the tts directory. The name you give this file becomes the name for this tts type in the configuration file. This file needs to contain two functions, as shown in this example.

```python
def setup(robot_config):
    return

def say(*args):
    message = args[0]
    
    if (len(args) == 1): # simple say
        # Your code for tts related to internal say messages goes here
        return
    else:
        # Your code for tts related to chat messages goes here
    
    return
```

### setup() function

The ```setup()``` function is passed the ConfigParser object for the letsrobot.conf file. You can create a new section for your tts in the letsrobot.conf file, and store configuration variables there. Variables in the configuration can be accessed with ```robot_config.get(section, option)```, ```robot_config.getint(section, option)``` and ```robot_config.getboolean(section, option)```.

Any initial tts setup should happen when the ```setup()``` function is called. This function is only called once.

### say() function

The ```say()``` function is called in one of two ways. There is a simple say called like so ```tts.say('The internet is not connected')```. This is used by other modules and parts of the controller to report things to the owner. There is also ```tts.say(message, args)```, this is how chat messages are passed. It's up to you if you want to handle them the same or differently.

The first argument will always be the plain text message. The second argument, if it exists, will be the chat message object that was sent to the robot from the server. It looks like this.

```
{u'non_global': True, u'name': u'Nocturnal', u'username_color': u'#F16B74', u'robot_id': u'49345483', u'message': u'[huNGRycat] This is a chat message', u'_id': u'59ec950fb70002183b2c4e22', u'anonymous': False, u'room': u'Nocturnal'}
```

This should also be mostly self explainitory. ```'non_global'``` represents if the chat room is global or the robocasters specific chat room. ```'message'``` differs from the message passed as the first argument in that it also contains the name of the robot in the message.

The actual code required to take the text message, and play it as audio should reside in this function.


## Extending Existing Hardware

When the ```custom_hardware``` option in the ```misc``` section of letsrobot.conf is set to true, the controller will look for a file named ```hardware_custom.py``` in the hardware directory. If that file exists it will load  that instead of the file relating to the hardware type specified in letsrobot.conf.

In this way, existing hardware functions can be modified and extended, or entirely replaced. Though if you are replacing the functions entirely, you may be better off creating a new hardware type instead.

The ```hardware_custom.py``` file needs to have the same two function, as outlined for new hardware above, but in order to extend functionality there is a slight difference.

```python
import mod_utils
module=None

def setup(robot_config):
    # Your custom setup code goes here



    # This code calls the default setup function for your hardware.
    # global module
    module = mod_utils.import_module('hardware', robot_config.get('robot', 'type')])
    module.setup(robot_config)

def move(args):
    command = args['command']
    # Your custom command interpreter code goes here

    if command=='FLIP':
        # Hardware instuction to make your robot flip go here

    # This code calls the default command interpreter function for your hardware.
    module.move(command)


```

This example adds a hypothetical ```FLIP``` instruction for your robot, to the existing hardware controller.

The ```setup()``` function includes code to import the hardware controller you are extending into `module`. It also calls the setup function for that module.

The ```move()``` function has a command interpeter similar to the one in hardware module you are extending, except this one
only needs to contain the commands that aren't handled in the hardware module. After the custom command interpreter has run, it should call the ```move()``` command from the hardware module, to handle the non custom commands.


## Extending Existing TTS

This is very similar to extending existing hardware as outlined above. Except that where extending hardware involes adding new functions, extending TTS is more about modifying the way messages are handled.

When the ```custom_tts``` option in the ```misc``` section of letsrobot.conf is set to true, the controller will look for a file named ```tts_custom.py``` in the tts directory. If that file exists it will load that instead of the file relating to the tts type specified in letsrobot.conf.

In this way, existing tts functions can be modified and extended, or entirely replaced. Though if you are replacing the functions entirely, you may be better off creating a new hardware type instead.

The ```tts_custom.py``` file needs to have the same two function, as outlined for new TTS above, but in order to extend functionality there is a slight difference.

```python
import mod_utils
module=None

def setup(robot_config):
    # Your custom setup code goes here



    # This code calls the default setup function for your tts.
    # global module
    module = mod_utils.import_module('tts', robot_config.get('tts', 'type'))
    module.setup(robot_config)

def say(*args):
    message = args[0]
    # Your custom tts interpreter code goes here



    if len(args) == 1: # simple say
        module.say('robot says')
        module.say(message)
    else:
        user = args[1]['name']
        module.say(user + ' says')
        module.say(message, args[1])
        
```

This example will cause your robot to prefix all simple say messages with 'robot says' and all chat messages with '(user who wrote the message) says'.

The ```setup()``` function includes code to import the hardware controller you are extending into `module`. It also calls the setup function for that module.

The ```say()``` function should modify the message or tts function before calling, the ```say()``` command from the tts module, to handle the actualy text conversion to sound.


## Extending Chat Handling

This is similar to extending TTS, and many things could be done in either. The difference between the two, is that extending the chat handler, inserts the code before the chat handler (and the extended command handler) is run. While extending TTS puts the code inside the chat handler. In theory you could use this to replace the chat handler, extended command handler and TTS system with something entirely your own.

Simple say messages are not seen by the chat handler.

When the ```custom_chat``` option in the ```misc``` section of letsrobot.conf is set to true, the controller will look for a file named ```chat_custom.py``` in the same directory as the controller. If that file exists it will load that file, and call it instead of the chat handler.

The ```chat_custom.py``` file needs to contain two functions, similar to those required by the other custom handlers.

```python
main_chat_handler = None

def setup(robot_config, chat_handler):
    global main_chat_handler
    main_chat_handler = chat_handler
    # Any chat related setup code goes here


def handle_chat(args):
    # Your custom chat handling code goes here



    if args['anonymous']:
        if args['message'][0] != '.'
            main_chat_handler(args)
    else:
        main_chat_handler(args)
```

This example will block anonymous users from attempting to access any of the extended commands.

### setup() function

The ```setup()``` function takes two arguments. The robot_config object containing the details of the letsrobot.conf files, and a function object for the controllers chat handler function. In order to allow this function to be called later in the ```handle_chat()``` function, it should be stored in a global variable.

### handle_chat() Function

The ```handle_chat()``` function takes one argument. The chat message object passed to the controller for the robot by the server. This is the same object that is passed as the optional second argument to the tts ```say()``` function.

```
{u'non_global': True, u'name': u'Nocturnal', u'username_color': u'#F16B74', u'robot_id': u'49345483', u'message': u'[huNGRycat] This is a chat message', u'_id': u'59ec950fb70002183b2c4e22', u'anonymous': False, u'room': u'Nocturnal'}
```

Once the function has examined or modified the object, it should pass it off to the main chat handler (or not, if you decide to drop the message entirely).

## chat_custom.example.py

This example shows how to use the ```extended_command``` module to add an additional ```.reboot``` command, to reboot the controller. This is not exclusive to chat_custom, it can be done anywhere. 

It also shows how to replace all mentions of 'john madden' in chat with 'the antichrist' for tts. This could also be done in tts_custom.
r
## tts_custom.example.py

This example shows how to play a custom sound file for specific users, before their tts chat message is played.

## hardware_custom.example.py

This example shows how to add max7219 led support to your chosen hardware controller. 


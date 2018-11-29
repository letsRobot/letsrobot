# Transitioning from RunMyRobot to LetsRobot

## Passing Arugments
Previously, all settings for the bots were made as parameter arguments in `start_robot`. Now, almost all customization occurs in a new file called `letsrobot.conf`. A template can be found called `letsrobot.sample.conf`. **Some** parameter arguments are still accepted, and will override the settings in `letsrobot.conf`, but are generally recommended for one-time changes.

## `start_robot`
The biggest change, is now only one file is called to get a robot online; `letsrobot.py` which handles what used to be handled by `controller.py` and `send_video.py`, with some exceptions mentioned later. You do not need to pass arguments via this file anymore.

## Your `type` may have changed
Some of the names for your robot `type` may have changed. Make sure yours is set correctly.
* `serial` --> `serial_board`

## Extended Chat
When `ext_chat` is enabled, the following chat commands are available. To use, just type them into the chat box on your bots page. These chat commands have no effect on how the site behaves, they only affect the bot. There are some functions that duplicated functions on the site. These changes are not saved and are lost on reboot.
* `.devmode X` Set dev mode. In dev mode, only the owner can drive. If devmode is set to mods, your local mods can also drive [on|off|mods].
* `.anon control X` Sets if anon users can drive your bot [on|off].
* `.anon tts X` Sets of anonymous users messages are passed to TTS [on|off].
* `.anon X` Sets both anonymous control and TTS access [on|off].
* `.tts X` Mute the bots TTS [mute|unmute].
* `.ban NAME` Ban user NAME from controller your bots.
* `.unban NAME ` Remove user NAME from ban list
* `.timeout NAME` Timeout user NAME from controlling our bot for 5 minutes.
* `.untimeout NAME` remove user NAME from timeout list
* `.brightness X` Set the camera brightness [0...255]
* `.contrast X` Set the camera contrast [0...255]
* `.saturation X` Set the camera saturation [0...255]
* `.stationary` Toggles stationary mode. When enabled, forward/backward commands will be blocked.

## Native support for more bots
This repository supports all previous bots that ran the previous `runmyrobot` repository, plus Anki Cozmo, and Pololu Maestro controlled robots.

## Extending your controller with custom software
You should not extend your controller by editing directly in `letsrobot.py`. Instead, follow the directions [here](https://github.com/letsrobot/letsrobot/blob/master/documentation/EXTENDING_CONTROLLER.md).

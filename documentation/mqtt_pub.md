# MQTT Publish controller
[MQTT](http://mqtt.org/) is a Machine-to-Machine communication protocol supporting a lightweight publish/subscribe message transport. It is commonly used in IoT and home automation applications. This LetsRobt Hardware controller will allow commands recieved from the LetsRobot site to be published to a MQTT Broker. Various remote robots, devices, and software can subscribe to the MQTT Broker to recieve messages. This configuration will allow the command processing to be decoupled from the LetsRobot Client software both in software processing and, if you choose, the network/system location.

![MQTT Publish Topography](https://raw.githubusercontent.com/Papershaper/letsrobot/master/documentation/mqtt_pub_topography.png)
      
## Potential Uses
Using the MQTT Pub hardward with LetsRobot, you can broadcast the command messages from the site to many different devices in your robot environment. It would also be possible to publish messages to devices that already have a MQTT interface.

A common example would be to seperate the video/audio streaming services from the command processing software. That is you could support a camera with video that is on a seperate computer/RPI than the robot or robots.

## mqtt_pub description
The mqtt_pub.py script is a implementation of the LetsRobot Client Hardware Controller. The script uses the Eclipse foundation Paho Python library.

It contains methods for ```setup()``` and ```move()```. On ```setup()``` the script will load all configurations. It will create a mqtt client and attach handlers for connection, disconnection, and message publishing. 

When ```move()``` is called, the script will attempt a connection to the configured MQTT Broker, publish the 'command' arguments, and disconnect.

The mqtt_pub script does not contain the MQTT Broker, or Subscription methods.

## MQTT Requirements and MQTT components
To use the mqtt_pub script, the mqtt library 'paho' must be installed on the machine with the Letsrobot client software. Instructions for the installation of paho mqtt can be found [here](https://pypi.org/project/paho-mqtt/)

In addition, to use the mqtt capabilities, a MQTT Broker must be available to be connected and running. The Mosquitto project has a Broker as well as command line publish and subscribe clients. Information on Mosquitto can be found [here](https://mosquitto.org/).  Information on installing a Mosquitto Broker on a RaspberryPI can be found [here](https://www.switchdoc.com/2018/02/tutorial-installing-and-testing-mosquitto-mqtt-on-raspberry-pi/)

Finally, the robot that will use the MQTT message stream will need to have software that can subscribe to the MQTT Broker then take action on the messages. This software is not difficult to write using the paho library in python. 

## mqtt_pub Configuration
to use the mqtt_pub controller software it must be configured to operate in the letsrobot.conf file.

At the top section of the file, set the hardward controller type to "mqtt_pub"
```python
type=mqtt_pub
```

Find the "[mqtt_pub]" section to configure the Broker and Topic information.
the following changes are needed:
* host - should be set to the IP address of the Broker that you are publishing to
* port - Typically this is 1883, check your broker for the exact port
* topic - this is the information group that the Broker/Subscribers listen to. as default this is set to "LR/command"

```python
[mqtt_pub]
# If you are using MQTT you need to supply the host IP address, port, and Topic
# host should be the IP address where the MQTT broker is running
# the port typically is 1883 for MQTT
# the topic is your choice, but it needs to match with the robot subscribers
host = 192.168.178.88   
port = 1883
topic = LR/command
```

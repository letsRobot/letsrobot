# MQTT Publish controller
MQTT is a lightweight Machine-to-Machine communication protocol. It is commonly used in IoT and home automation applications. This LetsRobt Hardware controller will allow commands recieved from the LetsRobot site to be published to a MQTT Broker. Various remote robots, devices, and software can subscribe to the MQTT Broker to recieve messages. This configuration will allow the command processing to be decoupled from the LetsRobot Client software both in software processing and, if you choose, the network/system location.
![MQTT Publish Topography](letsrobot/documentation/mqtt_pub_topography.png)
      

## Potential Uses

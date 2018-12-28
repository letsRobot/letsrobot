import logging
log = logging.getLogger('LR.hardware.mqtt_pub')

try:
    import paho.mqtt.client as mqttc
except ImportError:
    log.critical("paho mqtt did not load. You need to install the paho mqtt client")

#define variables here
mqtthost=None
mqttPort=None
mqttTopic=None
mqttClient=None

def sendmqttCommand(command):
    global mqttClient
    log.info("mqtt pub send: %s ", command)
    
    try:
        mqttClient.connect(mqtthost, mqttPort)
    except:
        log.error("failed to connect to MQTT Broker")
    
    rc = mqttClient.publish(mqttTopic,command)
    mqttClient.disconnect()

def on_publish(client,userdata,rc):
    log.debug("command published")
    
def on_disconnect(client,userdata,rc):
    log.debug("disconnected")
    
def setup(robot_config):
    global mqtthost
    global mqttPort
    global mqttTopic
    global mqttClient

    mqtthost = robot_config.get('mqtt_pub', 'host')
    mqttPort = robot_config.getint('mqtt_pub', 'port')
    mqttTopic = robot_config.get('mqtt_pub', 'topic')
    mqttClient = mqttc.Client("robot")      #TODO client can b the robot ID
    
    mqttClient.on_publish = on_publish
    mqttClient.on_disconnect = on_disconnect
    
    #for this publish method, we will open the connection and send single commands
    #TODO consider opening connection with keep alive in set up, then restore/when sending
    
def move(args):
    command = args['command']
    sendmqttCommand(command)

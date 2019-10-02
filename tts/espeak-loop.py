import espeak

def setup(robot_config):
    espeak.setup(robot_config)

def say(*args):
    message = args[0]
    message = message.encode('ascii', 'ignore')
    tempFilePath = espeak.os.path.join(espeak.tempDir, "text_" + str(espeak.uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    if espeak.male:
        espeakCommand = 'espeak -v en-us+m{} -s 170 --stdout'
    else:
        espeakCommand = 'espeak -v en-us+f{} -s 170 --stdout'
    espeakCommand = espeakCommand.format(espeak.voice_number)

    aplayCommand = 'aplay -D plughw:{}'.format(espeak.hw_num)
    soxCommand = 'sox -t wav - -p pad 0 0.25 | sox -t sox - -t wav -'

    espeak.os.system('cat ' + tempFilePath + ' | ' + espeakCommand + ' | ' + soxCommand + ' | ' + aplayCommand )
    espeak.os.remove(tempFilePath)    

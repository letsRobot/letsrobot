from __future__ import print_function
import subprocess
import thread
import networking

keyfile = None
host = None

def setupReverseSsh(robot_config):
    global keyfile
    global host
    
    keyfile = robot_config.get('misc', 'reverse_ssh_key_file')
    host = robot_config.get('misc', 'reverse_ssh_host')

    networking.appServerSocketIO.on('reverse_ssh_8872381747239', reverse_ssh.startReverseSshProcess)
    networking.appServerSocketIO.on('end_reverse_ssh_8872381747239', reverse_ssh.endReverseSshProcess)


def handleStartReverseSshProcess(args):
    print("starting reverse ssh")
    appServerSocketIO.emit("reverse_ssh_info", "starting")

    returnCode = subprocess.call(["/usr/bin/ssh",
                                  "-X",
                                  "-i", keyfile,
                                  "-N",
                                  "-R", "2222:localhost:22",
                                  host])

    appServerSocketIO.emit("reverse_ssh_info", "return code: " + str(returnCode))
    print("reverse ssh process has exited with code", str(returnCode))

    
def handleEndReverseSshProcess(args):
    print("handling end reverse ssh process")
    resultCode = subprocess.call(["killall", "ssh"])
    print("result code of killall ssh:", resultCode)

def startReverseSshProcess(*args):
   thread.start_new_thread(handleStartReverseSshProcess, args)

def endReverseSshProcess(*args):
   thread.start_new_thread(handleEndReverseSshProcess, args)

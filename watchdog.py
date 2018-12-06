#TODO: Count restarts during a time period, and terminate if too high.
#      Add a vital flag to a process, if restart fails, program will terminate. 
#      

from threading import Thread
import logging

log = logging.getLogger('LR.watchdog')

watches={}


def watch():
    global watches
    
    for (name, process) in watches.items():
        if not process[0].is_alive():
            log.error("Process "+name+" not running, restarting")
            start(name, process[1], *process[2], **process[3])
         
def start(name, startFunction, *args, **kwargs):
    global watches
    thread = Thread(target=startFunction, args=args, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()
    watches[name] = [thread, startFunction, args, kwargs]

def stop(name):
    del watches[name]


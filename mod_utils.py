from schedule import task, repeat_task, single_task
import sys
if (sys.version_info > (3, 0)):
    import importlib
    
def import_module(location, type):
    if (sys.version_info > (3, 0)):
        module = importlib.import_module(location+'.'+type)
    else:
        module = __import__(location+"."+type, fromlist=[type])
    
    return(module)
              
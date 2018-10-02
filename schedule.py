# TODO: Low priority, kwargs support
from threading import Timer
def task(wait, task_handler, *args):
    new_args = [wait, task_handler]
    for a in args:
        new_args.append(a)
    t=Timer(wait, task, new_args)
    t.daemon = True
    t.start()
    task_handler(*args);
    return t

def repeat_task(wait, task_handler, *args):
    new_args = [wait, task_handler]
    for a in args:
        new_args.append(a)
    t=Timer(wait, task, new_args)
    t.daemon = True
    t.start()
    return t
    
def single_task(wait, task_handler, *args):
    t=Timer(wait, task_handler, args)
    t.daemon = True
    t.start()
    return t
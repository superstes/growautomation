
# from core.utils.debug import debugger
# from core.utils.debug import Log

from multiprocessing import Process
from time import sleep as time_sleep


def process(initiator, start=False):
    # debugger("service - thread_function |'%s'" % initiator)
    if initiator.find('sensor') != -1:
        obj = initiator.replace('sensor_', '')
        # debugger("service - thread_function |using sensor module for object '%s'" % obj)
        from core.snake import Balrog
        function = Balrog(obj).start
    elif initiator.find('profile') != -1:
        obj = initiator.replace('profile_', '')
        # debugger("service - thread_function |using check module for object '%s'" % obj)
        from core.sparrow import Profile
        function = Profile(obj).parse
    elif initiator.find('backup') != -1:
        # debugger("service - thread_function |using backup module")
        from core.backup import Backup
        function = Backup().start
    else: return False
    try:
        work = Process(target=function)
        if start:
            # debugger("service - thread_function |'%s' starting process" % initiator)
            # Log("Starting process for object '%s'" % initiator, level=4).write()
            work.start()
            count = 0
            while True:
                if not work.is_alive():
                    work.join()
                    # debugger("service - thread_function |'%s' process shutdown gracefully" % initiator)
                    # Log("Stopping process for object '%s' after finishing task" % initiator, level=4).write()
                    return True
                elif count > 30:
                    # debugger("service - thread_function |'%s' process timeout" % initiator)
                    # Log("Stopping process for object '%s' because of timeout" % initiator, level=1).write()
                    work.terminate()
                    work.join()
                    return False
                else:
                    time_sleep(3)
                    count += 1
                    # debugger("service - thread_function |'%s' process termination" % initiator)
                    # Log("Stopping process for object '%s' because of service termination" % initiator, level=2).write()

                    # return False

    except (ValueError, NameError, UnboundLocalError, AttributeError):
        # debugger("service - thread_function |'%s' action '%s', invalid function to process '%s - %s'"
        #          % (initiator, 'start' if start else 'init', type(function), function))
        # Log("Invalid function to process for object '%s' - action - '%s', function '%s - %s'"
        #     % (initiator, 'start' if start else 'init', type(function), function), level=2).write()
        try:
            work.terminate()
            work.join()
        except NameError:
            pass

        return False

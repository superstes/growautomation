#!/usr/bin/python3.8
# This file is part of Growautomation
#     Copyright (C) 2020  René Pascal Rath
#
#     Growautomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.4

from core.smallant import debugger
from core.smallant import VarHandler
from core.smallant import Log

from multiprocessing import Process
from time import sleep as time_sleep


def process(initiator, start=False):
    debugger("service - thread_function |'%s'" % initiator)
    if initiator.find('sensor') != -1:
        debugger("service - thread_function |'%s' using sensor module" % initiator)
        from core.snake import Balrog
        function = Balrog(initiator).start
    elif initiator.find('check') != -1:
        debugger("service - thread_function |'%s' using check module" % initiator)
        return False
        # from core.parrot import ThresholdCheck.start
        # function = ThresholdCheck(initiator)
    elif initiator.find('backup') != -1:
        debugger("service - thread_function |'%s' using backup module" % initiator)
        from core.backup import Backup
        function = Backup().start
    try:
        work = Process(target=function)
        if start:
            debugger("service - thread_function |'%s' starting process" % initiator)
            Log("Starting process for object '%s'" % initiator, level=4).write()
            work.start()
            count = 0
            while True:
                if not work.is_alive():
                    work.join()
                    debugger("service - thread_function |'%s' process shutdown gracefully" % initiator)
                    Log("Stopping process for object '%s' after finishing task" % initiator, level=4).write()
                    return True
                elif count > 30:
                    debugger("service - thread_function |'%s' process timeout" % initiator)
                    Log("Stopping process for object '%s' because of timeout" % initiator, level=1).write()
                    work.terminate()
                    work.join()
                    return False
                else:
                    _ = VarHandler(name='service_stop').get()
                    if _ == '1' or _ is False:
                        debugger("service - thread_function |'%s' process termination" % initiator)
                        Log("Stopping process for object '%s' because of service termination" % initiator, level=2).write()
                        work.terminate()
                        work.join()
                        return False
                time_sleep(3)
                count += 1
    except (ValueError, NameError, UnboundLocalError, AttributeError):
        debugger("service - thread_function |'%s' action '%s', invalid function to process '%s - %s'"
                 % (initiator, 'start' if start else 'init', type(function), function))
        Log("Invalid function to process for object '%s' - action - '%s', function '%s - %s'"
            % (initiator, 'start' if start else 'init', type(function), function), level=2).write()
        return False

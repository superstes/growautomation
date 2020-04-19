#!/usr/bin/python3
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

# ga_version 0.3

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from sys import argv as sys_argv
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
import signal

from ga.core.config import Config
from ga.core.owl import DoSql
from ga.core.ant import LogWrite
from ga.core.owl import debugger

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class Balrog:
    def __init__(self, sensor):
        self.sensor = sensor
        self.processed_list = []
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.devicetype() if self.sensor in Config(output="name", table="object", filter="class = 'sensor'").get() else self.device(self.sensor)

    def devicetype(self):
        device_list = []
        for device in Config(output="name", table="object", filter="class = '%s'" % self.sensor).get():
            if not Config(setting="timer", belonging=device).get(): device_list.append(device)
        [self.device(device) for device in device_list]
        # ask for threading support when sensor-functions are added

    def device(self, device):
        if device in self.processed_list: return False
        else:
            connection = Config(setting="connection", belonging=device).get()
            if connection == "direct":
                function = Config(setting="function", belonging=Config(output="class", table="object", setting=device).get())
                output, error = subprocess_popen(["/usr/bin/python3 %s %s %s" % (function, Config(setting="port", belonging=device).get(), device)],
                                                 shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
                output_str, error_str = output.decode("ascii"), error.decode("ascii")
            elif connection == "downlink":
                self.downlink(device, Config(setting="downlink", belonging=device).get())
            else: return False

    def downlink(self, device, downlink):
        def start(setting, data):
            # start downlink function with downlink settings and data (if needed)

        downlink_type = Config(output="class", table="object", setting=downlink).get()
        downlink_type_opp = Config(setting="output_per_port", belonging=downlink_type).get()
        if downlink_type_opp == "1":
            # get downlink setting and start()
        elif downlink_type_opp == "0":
            # check if self.sensor is devicetype -> yes check if other devices are connected to the same downlink type (minus processed list)
            # add those devices + their downlink ports to a dict and add to self.processed list
            # funny stuff for str/list/dict -> define default input/output for sensor-/downlink functions!!
            # start()
        else: return False

        # settings
        # portcount int,  bool, output_format str;list;dict, output_format_delimeter
        # downlink = downlink device
        # downlink function:
        # for device append downlink to list
        # for dl in downlinklist
        #   check if device is enabled
        #   get devicetype -> append to downlinktypelist
        # for downlinktype in downlinktypelist
        #   get typesettings
        #   check if type is enabled
        #
        # for dl in downlinklist
        #   get devicesettings
        #   overwrite typesettings with devicesettings
        #   each device on downlink
        #     add portdict[port]=device_name
        #     compare to portcount of downlink -> add dev-null members for ports which are not in use
        # get data from downlink function -> sensor function(downlinksetting_dict, portdict)
        # zip the

    def database(self):
        print("write data from device or downlink function into db")

    def stop(self):
        print("finish whatever you're doing and go die")
        raise SystemExit

# random settings

# class old:
    # will not be needed often -> should be queried manually if needed
    # namemaxletters = 10
    # namemaxnumbers = 100
    # sensortime = "10"		        #How often should the sensordata be written to the database (minutes)
    # sensorahtdisabled = "no"
    # sensorehdisabled = "no"
    # adcdisabled = ["adc02"]
    # adcconnected = {"adc01": "i2c-1", "adc02": "i2c-2"}
    # ahtadisabled = ["ahta02"]
    # ahtaconnected = {"ahta01": "26", "ahta02": "19"}
    # ehbdisabled = ["ehb02"]
    # ehbconnected = {"ehb01": {"adc01": "0"}, "ehb02": {"adc02": "1"}}
    # actiontypes = {"eh": ("pump", "win"), "aht": ("win")}
    # actionblock01 = {"sensor": {"eh": ("ehb01", "ehb02"), "aht": ("ahta01", "ahta02")}, "action": {"win": ("wina02")}}
    # actionblock02 = {"sensor": {"eh": ("ehb01", "ehb02")}, "action": {"pump": ("pumpa01", "pumpa04"), "win": ("wina01")}}
    # pumpdisabled = []
    # pumpconnected = ("pumpa01", "pumpa04")
    # pumpactivation = "60"		#The pump will be activated if the humidity falls under this value
    # pumptime = 10 #600		    #Runtime in seconds
    # windisabled = {}
    # winconnected = {"win01": {"fwd": "20", "rev": "21"}, "win02": {"fwd": "16", "rev": "12"}}
    # winopentime = 5
    # psua01password = "PASSWORD"
    # psua01ip = "IP"
    # psua01webport = 8080
    # psua01outlets = {"1": "pumpa01", "2": "pumpa02", "3": "pumpa03", "4": ""}
    # psua02password = "PASSWORD"
    # psua02ip = "IP"
    # psua02webport = 8080
    # psua02outlets = {"1": "pumpa04", "2": "", "3": "", "4": ""}

try: Balrog(sys_argv[1])
except IndexError:
    LogWrite("No sensor provided. Exiting.")
    raise SystemExit
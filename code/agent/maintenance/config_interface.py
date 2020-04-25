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

from ga.core.config import Config
from ga.core.owl import DoSql
from ga.core.ant import ShellOutput
from ga.core.ant import ShellInput
from ga.core.ant import LogWrite
from ga.core.smallant import debugger
from ga.core.smallant import debug_init

from inspect import getfile as inspect_getfile
from inspect import currentframe as inspect_currentframe
from os import system as os_system
from sys import argv as sys_argv

LogWrite("Current module: %s" % inspect_getfile(inspect_currentframe()), level=2)


class GetObject:
    def __init__(self):
        self.object_dict, self.setting_dict, self.group_dict = {}, {}, {}
        self.object_downlink_list = []
        self.choose()

    def choose(self):
        try:
            if sys_argv[1] == "debug": debug_init()
        except (IndexError, NameError): pass
        ShellOutput("Growautomation - config change module", font="head", symbol="#")
        ShellOutput("Currently only adding of objects is supported", font="text")
        self.create_devicetype()
        # mode = ShellInput("Choose either to add, edit or delete growautomation configuration", poss=["add", "edit", "delete"], defaut="add", intype="free")
        # if mode is add -> insert if not exists
        # if mode is modify -> update if exists
        # if mode is remove -> ya'now

    # def add_core(self):
    #     ShellOutput("Add", font="head", symbol="#")
    #     ShellOutput("Please refer to the documentation if you are new to growautomation.\nLink: https://docs.growautomation.at", font="text")
    #     core_object_dict = {}
    #     core_object_dict["check"], core_object_dict["backup"], core_object_dict["sensor_master"] = "NULL", "NULL", "NULL"
    #     self.setting_dict["check"], self.setting_dict["check"] = {"range": 10, "function": "parrot.py"}, {"range": 10, "function": "parrot.py"}
    #     self.setting_dict["backup"], self.setting_dict["sensor_master"] = {"timer": 86400, "function": "backup.py"}, {"function": "snake.py"}
    #     self.object_dict["core"], self.object_dict["agent"] = core_object_dict, {GetConfig("hostname"): "NULL"}
    #     self.create_devicetype()

    def create_devicetype(self):
        dt_object_dict, dt_exist_list = {}, []
        for name in Config(output="name", filter="type = 'devicetype'", table="object").get(): dt_exist_list.append(name)
        debugger("confint - create_devicetype - dt_exist_list %s" % dt_exist_list)
        ShellOutput("Devicetypes", symbol="-", font="head")
        while_devicetype = ShellInput("Do you want to add devicetypes?\nInfo: must be created for every sensor/action/downlink hardware model; "
                                      "they provide per model configuration", True).get()
        while while_devicetype:
            ShellOutput(symbol="-", font="line")
            name, setting_dict = ShellInput("Provide a unique name - at max 20 characters long.\nAlready existing:\n%s" % dt_exist_list,
                                            default="AirHumidity", intype="free", poss=dt_exist_list, neg=True).get(), {}
            dt_object_dict[name] = ShellInput("Provide a type.", default="sensor", poss=["sensor", "action", "downlink"], intype="free").get()
            if ShellInput("Are all devices of this type connected the same way?\nInfo: If all devices are connected via gpio or downlink",
                          default=True).get() is True:
                setting_dict["connection"] = ShellInput("Are they connected via downlink or directly?\n"
                                                        "Info: 'downlink' => pe. analog to serial converter, 'direct' => gpio pin",
                                                        default="direct", poss=["downlink", "direct"], intype="free")
            else: setting_dict["connection"] = "specific"
            if setting_dict["connection"] != "downlink":
                setting_dict["function"] = ShellInput("Which function should be started for the devicetype?\n"
                                                      "Info: just provide the name of the file; they must be placed in the ga %s folder" % dt_object_dict[name],
                                                      default="%s.py" % name, intype="free", max_value=50).get()
                setting_dict["function_arg"] = ShellInput("Provide system arguments to pass to you function -> if you need it.\n"
                                                          "Info: pe. if one function can provide data to multiple devicetypes",
                                                          intype="free", min_value=0, max_value=75).get()
            if dt_object_dict[name] == "action":
                setting_dict["boomerang"] = ShellInput("Will this type need to reverse itself?\n"
                                                       "Info: pe. opener that needs to open/close", default=False).get()
                if setting_dict["boomerang"]:
                    setting_dict["boomerang_type"] = ShellInput("How will the reverse be initiated?",
                                                                default="threshold", poss=["threshold", "time"], intype="free").get()
                    if setting_dict["boomerang_type"] == "time":
                        setting_dict["boomerang_time"] = ShellInput("Provide the time after the action will be reversed.",
                                                                    default=1200, max_value=1209600, min_value=10).get()
                    reverse_function = ShellInput("Does reversing need an other function?", default=False).get()
                    if reverse_function:
                        setting_dict["boomerang_function"] = ShellInput("Provide the name of the function.", intype="free", max_value=50).get()
                        setting_dict["function_arg"] = ShellInput("Provide system arguments to pass to the reverse function -> if you need it.",
                                                                  intype="free", min_value=0, max_value=75).get()
            elif dt_object_dict[name] == "sensor":
                setting_dict["timer"] = ShellInput("Provide the interval to run the function in seconds.",
                                                   default=600, max_value=1209600, min_value=10).get()
                setting_dict["unit"] = ShellInput("Provide the unit for the sensor input.", default="°C", intype="free").get()
                setting_dict["threshold_max"] = ShellInput("Provide a maximum threshold value for the sensor.\n"
                                                           "Info: if this value is exceeded the linked action(s) will be started",
                                                           default=26, max_value=1000000, min_value=1).get()
                setting_dict["threshold_optimal"] = ShellInput("Provide a optimal threshold value for the sensor.\n"
                                                               "Info: if this value is reached the linked action(s) will be reversed",
                                                               default=20, max_value=1000000, min_value=1).get()

                setting_dict["timer_check"] = ShellInput("How often should the threshold be checked? Interval in seconds.",
                                                         default=3600, max_value=1209600, min_value=60).get()
            elif dt_object_dict[name] == "downlink":
                setting_dict["portcount"] = ShellInput("How many ports does this downlink provide?", default=4).get()
                setting_dict["output_per_port"] = ShellInput("Can the downlink output data per port basis?\n"
                                                             "(Or can it only output the data for all of its ports at once?)", default=False).get()
            self.setting_dict[name] = setting_dict
            dt_exist_list.append(name)
            debugger("confint - create_devicetype - settings %s" % setting_dict)
            while_devicetype = ShellInput("Want to add another devicetype?", default=True, style="info").get()
        self.object_dict["devicetype"] = dt_object_dict
        self.create_device()

    def create_device(self):
        d_object_dict, d_exist_list, dt_exist_dict, d_dl_list = {}, [], {}, []
        for name in Config(output="name", filter="type = 'device'", table="object").get(): d_exist_list.append(name)
        for nested in self.object_dict.values():
            for name, typ in dict(nested).items(): dt_exist_dict[name] = typ
        for name, typ in Config(output="name, class", filter="type = 'devicetype'", table="object").get(): dt_exist_dict[name] = typ
        for name, dt in Config(output="name,class", filter="type = 'device'", table="object").get():
            if Config(output="class", setting=dt, table="object").get() == "downlink": d_dl_list.append(name)
        d_dl_list.append("notinlist")

        def to_create(to_ask, info):
            debugger("confint - create_device - create %s" % to_ask)
            create, create_dict = ShellInput("Do you want to add a %s\nInfo: %s" % (to_ask, info), True).get(), {}
            while create:
                ShellOutput(symbol="-", font="line")
                name, setting_dict = ShellInput("Provide a unique name - at max 20 characters long.", default="%s01" % list(dt_exist_dict.keys())[0],
                                                intype="free", poss=d_exist_list, neg=True).get(), {}
                create_dict[name] = ShellInput("Provide its devicetype.", default=[dt for dt in list(dt_exist_dict.keys()) if name.find(dt) != -1],
                                               poss=d_exist_list, intype="free").get()
                if to_ask != "downlink":
                    dt_conntype = [conntype for dt, nested in self.setting_dict.items() if dt == create_dict[name] for setting, conntype in dict(nested).items()]
                    debugger("confint - create_device - dt_conntype %s" % dt_conntype)
                    if dt_conntype != "specific": setting_dict["connection"] = dt_conntype
                    else: setting_dict["connection"] = ShellInput("How is the device connected to the growautomation agent?\n"
                                                                  "Info: 'downlink' => pe. analog to serial converter, 'direct' => gpio pin",
                                                                  default="direct", poss=["downlink", "direct"], intype="free").get()

                    if setting_dict["connection"] == "downlink":
                        setting_dict["downlink"] = ShellInput("Provide the name of the downlink to which the device is connected to.\n"
                                                              "Info: the downlink must also be added as device", default=d_dl_list[0], poss=d_dl_list, intype="free").get()
                        if setting_dict["downlink"] == "notinlist":
                            setting_dict["downlink"] = ShellInput("Provide the exact name of the downlink-device to which this device is connected to.\n"
                                                                  "Info: You will need to add this downlink-device in the next run of this config_interface.\n"
                                                                  "Warning: If you misconfigure this connection the current %s will not work properly!" % to_ask,
                                                                  default="ads1115", intype="free").get()
                setting_dict["port"] = ShellInput("Provide the portnumber to which the device is/will be connected.", intype="free", min_value=1).get()
                self.setting_dict[name] = setting_dict
                d_exist_list.append(name)
                debugger("confint - create_device - settings %s" % setting_dict)
                if to_ask == "downlink": d_dl_list.append(name)
                create = ShellInput("Want to add another %s?" % to_ask, True, style="info").get()
            d_object_dict[to_ask] = create_dict

        def check_type(name):
            if len([x for key, value in self.object_dict.items() if key == "devicetype" for x in dict(value).values() if x == name]) > 0:
                return True
            else: return False

        if check_type("downlink"):
            ShellOutput("Downlinks", symbol="-", font="head")
            to_create("downlink", "if devices are not connected directly to the gpio pins you will probably need this one\n"
                                  "Check the documentation for more informations: https://docs.growautomation.at")
        d_dl_list.remove("notinlist")
        self.object_downlink_list = d_dl_list
        if check_type("sensor"):
            ShellOutput("Sensors", symbol="-", font="head")
            to_create("sensor", "any kind of device that provides data to growautomation")
        if check_type("action"):
            ShellOutput("Actions", symbol="-", font="head")
            to_create("action", "any kind of device that should react if the linked thresholds are exceeded")
        self.object_dict["device"] = d_object_dict
        self.create_group()

    def create_group(self):
        def to_create(to_ask, info, info_member):
            debugger("confint - create_group - create %s" % to_ask)
            create_count, create_dict, posslist = 0, {}, []
            create = ShellInput("Do you want to add a %s?\nInfo: %s" % (to_ask, info), True).get()
            if to_ask == "sector":
                intern_dev_list = [name for key, value in self.object_dict.items() if key == "device" for nested in dict(value).values() for name in dict(nested).keys()]
                db_dev_list = Config(output="name", filter="type = 'device'", table="object").get()
                posslist.extend(intern_dev_list), posslist.extend(db_dev_list)
                [posslist.remove(dev) for dev in self.object_downlink_list]
            elif to_ask == "link":
                posslist = dt_action_list
                posslist.extend(dt_sensor_list)
            debugger("confint - create_group - posslist %s" % posslist)
            while create:
                ShellOutput(symbol="-", font="line")
                member_list = []
                member_count, add_member = 0, True
                while add_member:
                    if member_count == 0: info = "\nInfo: %s" % info_member
                    else: info = ""
                    current_posslist = list(set(posslist) - set(member_list))
                    member_list.append(ShellInput("Provide a name for member %s%s." % (member_count + 1, info), poss=current_posslist, default=current_posslist[0], intype="free").get())
                    member_count += 1
                    if member_count > 1: add_member = ShellInput("Want to add another member?", default=True, style="info").get()
                create_dict[create_count] = member_list
                create_count += 1
                debugger("confint - create_group - members %s" % member_list)
                create = ShellInput("Want to add another %s?" % to_ask, default=True, style="info").get()
            return create_dict

        ShellOutput("Sectors", symbol="-", font="head")
        self.group_dict["sector"] = to_create("sector", "links objects which are in the same area", "must match one device")
        dt_action_list = [name for key, value in self.object_dict.items() if key == "devicetype" for name, typ in dict(value).items() if typ == "action"]
        dt_action_list.extend(Config(output="name", filter="type = 'devicetype' AND class = 'action'", table="object").get())
        dt_sensor_list = [name for key, value in self.object_dict.items() if key == "devicetype" for name, typ in dict(value).items() if typ == "sensor"]
        dt_sensor_list.extend(Config(output="name", filter="type = 'devicetype' AND class = 'sensor'", table="object").get())
        if len(dt_action_list) > 0 and len(dt_sensor_list) > 0:
            ShellOutput("Devicetype links", symbol="-", font="head")
            self.group_dict["link"] = to_create("link", "links action- and sensortypes\npe. earth humidity sensor with water pump", "must match one devicetype")
        self.write_config()

    def write_config(self):
        ShellOutput("Writing configuration to database", symbol="-", font="head")
        LogWrite("Writing configuration to database:\n\nobjects: %s\nsettings: %s\ngroups: %s" % (self.object_dict, self.setting_dict, self.group_dict), level=3)
        tmp_config_dump_path = "%s/maintainance/add_config.tmp" % Config("path_root").get()
        tmp_config_dump = open(tmp_config_dump_path)
        tmp_config_dump.write("%s\n%s\n%s" % (self.object_dict, self.setting_dict, self.group_dict))
        tmp_config_dump.close()

        def sql(command, query=False):
            if Config("setuptype").get() == "agent":
                if query: return DoSql(command, Config("sql_agent_user").get(), Config("sql_agent_pwd").get(), query=True).start()
                else: return DoSql(command, Config("sql_agent_user").get(), Config("sql_agent_pwd").get())
            else:
                if query: return DoSql(command, basic=True, query=True).start()
                else: return DoSql(command, basic=True)

        ShellOutput("Writing object configuration", font="text")
        sql("INSERT INTO ga.ObjectReference (author,name) VALUES ('setup','%s');" % Config("hostname").get())
        [sql("INSERT INTO ga.Category (author,name) VALUES ('setup','%s');" % key) for key in self.object_dict.keys()]
        object_count = 0
        for object_type, packed_values in self.object_dict.items():
            def unpack_values(values, parent="NULL"):
                count = 0
                for object_name, object_class in sorted(values.items()):
                    if object_class != "NULL":
                        sql("INSERT IGNORE INTO ga.ObjectReference (author,name) VALUES ('setup','%s');" % object_class)
                        object_class = "'%s'" % object_class
                    if parent != "NULL" and parent.find("'") == -1:
                        parent = "'%s'" % parent
                    sql("INSERT INTO ga.Object (author,name,parent,class,type) VALUES ('setup','%s',%s,%s,'%s');" % (object_name, parent, object_class, object_type))
                    count += 1
                return count
            if object_type == "device":
                for subtype, packed_subvalues in packed_values.items():
                    object_count += unpack_values(packed_subvalues, Config("hostname").get())
            else: object_count += unpack_values(packed_values)
        ShellOutput("%s objects were added" % object_count, style="info", font="text")

        ShellOutput("Writing object settings", font="text")
        setting_count = 0
        for object_name, packed_values in self.setting_dict.items():
            packed_values["enabled"] = 1
            for setting, data in sorted(packed_values.items()):
                if data == "": pass
                elif type(data) == bool:
                    if data is True: data = 1
                    else: data = 0
                sql("INSERT INTO ga.Setting (author,belonging,setting,data) VALUES ('setup','%s','%s','%s');" % (object_name, setting, data))
                setting_count += 1
        ShellOutput("%s object settings were added" % setting_count, style="info", font="text")

        ShellOutput("Writing group configuration", font="text")
        group_count, member_count = 0, 0
        for group_type, packed_values in self.group_dict.items():
            for group_id, group_member_list in packed_values.items():
                sql("INSERT IGNORE INTO ga.Category (author,name) VALUES ('setup','%s')" % group_type)
                sql("INSERT INTO ga.Grp (author,type) VALUES ('setup','%s');" % group_type)
                sql_gid = sql("SELECT id FROM ga.Grp WHERE author = 'setup' AND type = '%s' ORDER BY changed DESC LIMIT 1;" % group_type, query=True)
                for member in sorted(group_member_list):
                    sql("INSERT INTO ga.Grouping (author,gid,member) VALUES ('setup','%s','%s');" % (sql_gid, member))
                    member_count += 1
                group_count += 1
        ShellOutput("%s groups with a total of %s members were added" % (group_count, member_count), style="info", font="text")

        os_system("rm %s" % tmp_config_dump_path)


GetObject()

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
#     E-Mail: contact@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.5

try:
    from core.owl import DoSql
    from core.shared.shell import Output as ShellOutput
    from core.shared.shell import Input as ShellInput
    from core.shared.smallant import Log
    from core.shared.smallant import plural
    from core.shared.smallant import int_leading_zero
    from core.shared.smallant import ModifyIdiedDict
    from core.shared.ant import debugger
    from core.shared.varhandler import VarHandler
    from core.shared.smallant import list_remove_duplicates
except (ImportError, ModuleNotFoundError):
    from owl import DoSql
    from shell import Output as ShellOutput
    from shell import Input as ShellInput
    from smallant import Log
    from smallant import plural
    from smallant import int_leading_zero
    from smallant import ModifyIdiedDict
    from ant import debugger
    from smallant import VarHandler
    from smallant import list_remove_duplicates

from os import system as os_system
from sys import argv as sys_argv
from random import choice as random_choice
from sys import exc_info as sys_exc_info
import signal


def signal_handler(signum=None, stack=None):
    if debug: VarHandler().stop()
    try:
        raise SystemExit("Received signal %s - '%s'" % (signum, sys_exc_info()[0].__name__))
    except AttributeError:
        raise SystemExit("Received signal %s" % signum)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


class Create:
    def __init__(self, setup_config_dict=None):
        self.object_dict, self.setting_dict, self.group_dict, self.profile_dict = {}, {}, {}, {}
        self.current_dev_list, self.current_dt_dict, self.current_setting_dict, self.current_obj_list = [], {}, {}, []
        self.new_dt_dict, self.new_dev_dict = {}, {}
        self.object_downlink_list = []
        if setup_config_dict is not None:
            self.setup = True
            self.hostname = setup_config_dict['hostname']
            self.setuptype = setup_config_dict['setuptype']
            self.author = 'setup'
        else:
            self.setup = False
            from core.config import Config
            self.ConfigParser = Config
            self.hostname = Config('hostname').get()
            self.setuptype = Config('setuptype').get()
            self.author = 'maintenance'
        self.start()

    def _config(self, output=None, table=None, filter=None, setting=None, outtype=None, belonging=None):
        result = self.ConfigParser(output=output, table=table, filter=filter, setting=setting, belonging=belonging,
                                   empty=True).get(outtype)
        if result is False or (type(result) == str and result == 'False') or (type(result) == list and result[0] == False):
            if outtype == 'list': output = []
            else: output = ''
        else: output = result
        debugger("confint - config - output |'%s' '%s'" % (type(output), output))
        return output

    def start(self):
        # check if tmp_config_dump is currently in folder -> ask to load old config and try to import it into the db
        if self.setup:
            self.create_core()
            self.create_agent()
        else:
            self.current_obj_list = [name for name in self._config(output='name', table='object')]
        if self.create_devicetype() is not False:
            for grouping, nested in self.object_dict.items():
                for name, typ in dict(nested).items():
                    self.new_dt_dict[name] = typ
                    if grouping == 'core' or grouping == 'agent': continue
                    self.current_dt_dict[name] = typ
        if self.setup is False:
            for name, typ in self._config(output='name,class', filter="type = 'devicetype'", table='object', outtype='list'):
                self.current_dt_dict[name] = typ

        if self.create_device() is not False:
            self.current_dev_list = [name for key, value in self.object_dict.items() if key == 'device'
                                     for nested in dict(value).values() for name in dict(nested).keys()]
            self.new_dev_dict = {name: typ for key, value in self.object_dict.items() if key == 'device'
                                 for typ, nested in dict(value).items() for name in dict(nested).keys()}
            self.current_obj_list.extend(self.current_dev_list)
            for obj, nested in self.setting_dict.items():
                for setting, data in dict(nested).items():
                    self.current_setting_dict[obj] = setting
        if self.setup is False:
            self.current_dev_list.extend(self._config(output='name', filter="type = 'device'", table='object', outtype='list'))
            for setting, belonging in self._config(output='setting,belonging', outtype='list'):
                self.current_setting_dict[belonging] = setting

        self.create_custom_setting()
        self.create_group()
        self.write_config()

    def create_core(self):
        self.setting_dict = {'check': {'range': 10, 'function': 'sparrow.py'}, 'backup': {'timer': 86400, 'function': 'backup.py'},
                             'sensor_master': {'function': 'snake.py'},
                             'core_time': {'datatype': 'time'}, 'core_date': {'datatype': 'date'}}
        self.object_dict = {'core': {'check': 'NULL', 'backup': 'NULL', 'sensor_master': 'NULL', 'service': 'NULL'},
                            'agent': {self.hostname: 'NULL'},
                            'devicetype': {'core_time': 'sensor', 'core_date': 'sensor'},
                            'device': {'sensor': {'time': 'core_time', 'date': 'core_date'}}}

    def create_agent(self):
        agent_object_dict = {}
        # will manage the creation of all default settings of the controller
        # flag to overwrite/keep old config

    def create_devicetype(self):
        ShellOutput('Device Types', symbol='#', font='head')
        while_devicetype = ShellInput("Do you want to add devicetypes?\nInfo: must be created for every sensor/action/downlink "
                                      "hardware model\nthey provide per model configuration", True).get()
        if while_devicetype is False: return False
        dt_object_dict = {}
        debugger("confint - create_devicetype |obj_exist_list '%s'" % self.current_obj_list)
        ShellOutput('Devicetypes', symbol='-', font='head')
        while while_devicetype:
            ShellOutput(symbol='-', font='line')
            name = ShellInput("Provide a unique name - at max 20 characters long.\n", default='AirHumidity',
                              poss=self.current_obj_list, neg=True, max_value=20, min_value=2).get()
            setting_dict = {}
            setting_dict['enabled'] = 1
            # exits without message from setup if given
            dt_object_dict[name] = ShellInput('Provide a type.', default='sensor', poss=['sensor', 'action', 'downlink']).get()
            if dt_object_dict[name] != 'downlink':
                if ShellInput("Are all devices of this type connected the same way?\nInfo: If all devices are connected "
                              "via gpio or downlink",
                              default=True).get() is True:
                    setting_dict['connection'] = ShellInput("Are they connected via downlink or directly?\n"
                                                            "Info: 'downlink' => pe. analog to serial converter, 'direct' => gpio pin",
                                                            default='direct', poss=['downlink', 'direct']).get()
                else: setting_dict['connection'] = 'specific'
            else: setting_dict['connection'] = 'direct'
            if setting_dict['connection'] != 'downlink':
                setting_dict['function'] = ShellInput("Which function should be started for the devicetype?\n"
                                                      "Info: just provide the name of the file; they must be placed in the ga %s folder" % dt_object_dict[name],
                                                      default="%s.py" % name, intype='free', max_value=50).get()
                setting_dict['function_arg'] = ShellInput("Provide system arguments to pass to the function -> if you need it.\n"
                                                          "Info: pe. if one function can provide data to multiple devicetypes",
                                                          intype='free', min_value=0, max_value=75).get()
            if dt_object_dict[name] == 'action':
                setting_dict['boomerang'] = ShellInput("Will this type need to reverse itself?\n"
                                                       "Info: pe. opener that needs to open/close", default=False).get()
                if setting_dict['boomerang']:
                    setting_dict['boomerang_type'] = ShellInput('How will the reverse be initiated?',
                                                                default='threshold', poss=['threshold', 'time']).get()
                    if setting_dict['boomerang_type'] == 'time':
                        setting_dict['boomerang_time'] = ShellInput('Provide the time after the action will be reversed.',
                                                                    default=1200, max_value=1209600, min_value=10).get()
                    reverse_function = ShellInput('Does reversing need an other function?', default=False).get()
                    if reverse_function:
                        setting_dict['boomerang_function'] = ShellInput('Provide the name of the function.',
                                                                        default="%s.py" % name, intype='free', min_value=0,
                                                                        max_value=50).get()
                        setting_dict['boomerang_function_arg'] = ShellInput('Provide system arguments to pass to the reverse function '
                                                                            '-> if you need it.', intype='free', min_value=0,
                                                                            max_value=75).get()
            elif dt_object_dict[name] == 'sensor':
                setting_dict['timer'] = ShellInput('Provide the interval pull data from the sensor. (in seconds)',
                                                   default=600, max_value=1209600, min_value=10).get()
                setting_dict['unit'] = ShellInput('Provide the unit for the sensor input.', default='°C', intype='free').get()
                setting_dict['datatype'] = ShellInput('Provide the type of data the sensor provides.', default='number',
                                                      poss=['string', 'number']).get()
                # setting_dict['threshold_max'] = ShellInput("Provide a maximum threshold value for the sensor.\n"
                #                                            "Info: if this value is exceeded the linked action(s) will be started",
                #                                            default=26, max_value=1000000, min_value=1).get()
                # setting_dict['threshold_optimal'] = ShellInput("Provide a optimal threshold value for the sensor.\n"
                #                                                "Info: if this value is reached the linked action(s) will be reversed",
                #                                                default=20, max_value=1000000, min_value=1).get()
            elif dt_object_dict[name] == 'downlink':
                setting_dict['portcount'] = ShellInput('How many client-ports does this downlink provide?', default=4).get()
                setting_dict['output_per_port'] = ShellInput("Can the downlink output data per port basis?\n"
                                                             "(Or can it only output the data for all of its ports at once?)",
                                                             default=False).get()
            self.setting_dict[name] = setting_dict
            self.current_obj_list.append(name)
            debugger("confint - create_devicetype |settings '%s'" % setting_dict)
            while_devicetype = ShellInput('Want to add another devicetype?', default=True, style='info').get()
        self.object_dict['devicetype'] = dt_object_dict

    def create_device(self):
        ShellOutput('Devices', symbol='#', font='head')
        if ShellInput('Do you want to create devices?', default=True).get() is False: return False
        d_object_dict, d_dl_list = {}, []
        if self.setup is False:
            for name, dt in self._config(output='name,class', filter="type = 'device'", table='object', outtype='list'):
                if self._config(output='class', setting=dt, table='object') == 'downlink': d_dl_list.append(name)
        d_dl_list.append('notinlist')

        def to_create(to_ask, info):
            create = ShellInput("Do you want to add a %s\nInfo: %s" % (to_ask, info), default=True).get()
            create_dict = {}
            current_new_dt_list = [name for name, typ in self.new_dt_dict.items() if typ == to_ask]
            while create:
                ShellOutput(symbol='-', font='line')
                try: default_name = random_choice(current_new_dt_list)
                except IndexError: default_name = random_choice([dt for dt, typ in self.current_dt_dict.items() if typ == to_ask])
                name = ShellInput('Provide a unique name - at max 20 characters long.', default="%s01" % default_name,
                                  intype='free', poss=self.current_obj_list, neg=True, max_value=20, min_value=2).get()
                setting_dict = {}
                setting_dict['enabled'] = 1
                create_dict[name] = ShellInput('Provide its devicetype.', default=[dt for dt in list(self.current_dt_dict.keys())
                                                                                   if name.find(dt) != -1][0],
                                               poss=list(self.current_dt_dict.keys())).get()
                if to_ask != 'downlink':
                    if create_dict[name] in self.new_dt_dict.keys():
                        dt_conntype = [data for obj, nested in self.setting_dict.items() if obj == create_dict[name]
                                       for setting, data in dict(nested).items() if setting == 'connection'][0]
                    elif self.setup is False: dt_conntype = self._config(setting='connection', belonging=create_dict[name])
                    else: dt_conntype = 'specific'
                    debugger("confint - create_device |dt_conntype '%s'" % dt_conntype)
                    if dt_conntype != 'specific': setting_dict['connection'] = dt_conntype
                    else: setting_dict['connection'] = ShellInput("How is the device connected to the growautomation agent?\n"
                                                                  "Info: 'downlink' => pe. analog to serial converter, 'direct' => "
                                                                  "gpio pin", default='direct', poss=['downlink', 'direct']).get()

                    if setting_dict['connection'] == 'downlink':
                        setting_dict['downlink'] = ShellInput("Provide the name of the downlink to which the device is connected to.\n"
                                                              "Info: the downlink must also be added as device",
                                                              default=str(random_choice(d_dl_list)), poss=d_dl_list).get()
                        if setting_dict['downlink'] == 'notinlist':
                            setting_dict['downlink'] = ShellInput("Provide the exact name of the downlink-device to which this device "
                                                                  "is connected to.\nInfo: You will need to add this downlink-device "
                                                                  "in the next run of this config_interface.\nWarning: If you "
                                                                  "misconfigure this connection the current %s will not work properly!"
                                                                  % to_ask, default='ads1115', intype='free').get()
                # check how many ports are already connected minus the max dl ports -> poss/no-poss
                setting_dict['port'] = ShellInput('Provide the portnumber to which the device is/will be connected.', intype='free',
                                                  min_value=1).get()
                self.setting_dict[name] = setting_dict
                self.current_obj_list.append(name)
                debugger("confint - create_device |settings '%s'" % setting_dict)
                if to_ask == 'downlink': d_dl_list.append(name)
                create = ShellInput("Want to add another %s?" % to_ask, True, style='info').get()
            d_object_dict[to_ask] = create_dict

        def check_type(name):
            if len([dt for dt, typ in self.current_dt_dict.items() if typ == name]) > 0:
                return True
            else: return False

        if check_type('downlink'):
            ShellOutput('Downlinks', symbol='-', font='head')
            to_create('downlink', "if devices are not connected directly to the gpio pins you will probably need this one\n"
                                  "Check the documentation for further information: https://docs.growautomation.at")
        d_dl_list.remove('notinlist')
        self.object_downlink_list = d_dl_list
        if check_type('sensor'):
            ShellOutput('Sensors', symbol='-', font='head')
            to_create('sensor', 'any kind of device that provides data to growautomation')
        if check_type('action'):
            ShellOutput('Actions', symbol='-', font='head')
            to_create('action', 'any kind of device that should react if the linked thresholds are exceeded')
        self.object_dict['device'] = d_object_dict

    def create_custom_setting(self):
        ShellOutput('Custom Settings', symbol='#', font='head')

        def add_setting(object_name):
            def another():
                return ShellInput("Do you want to add another setting to the object %s" % object_name, default=False).get()
                # ValueError: too many values to unpack (expected 2)
            setting_exist_list = [setting for obj, nested in self.setting_dict.items() if obj == object_name
                                  for setting in dict(nested).keys()]
            if self.setup is False:
                setting_exist_list.extend(self._config(output='setting', filter="belonging = '%s'" % object_name, outtype='list'))
            change_dict, setting_count, setting_dict = {}, 0, {}
            while True:
                setting = ShellInput("Provide the setting name.\nInfo: max 30 chars & cannot already exist.", poss=setting_exist_list,
                                     intype='free', neg=True, max_value=30, min_value=2).get()
                data = ShellInput("Provide the setting data.\nInfo: max 100 chars", intype='free', max_value=100, min_value=1).get()
                setting_dict[setting] = data
                if another() is False: break
            if object_name in self.setting_dict.keys():
                tmp_dict = {key: val for obj, nested in self.setting_dict.items() if obj == object_name for key, val in dict(nested)}
                debugger("confint - add_setting |merge settings '%s'" % tmp_dict)
                setting_dict.update(tmp_dict)
            debugger("confint - add_setting |settings '%s'" % setting_dict)
            self.setting_dict[object_name] = setting_dict

        if ShellInput('Do you want to add custom settings?', default=True).get() is False: return False
        while True:
            option_list = self.current_dev_list
            option_list.extend(self.current_dt_dict.keys())
            object_to_edit = ShellInput("Choose one of the listed objects to edit.\n\nDeviceTypes:\n%s\nDevices:\n%s\n"
                                        % (list(self.current_dt_dict.keys()), self.current_dev_list),
                                        poss=option_list, default=random_choice(option_list)).get()
            add_setting(object_to_edit)
            if ShellInput('Do you want to add settings to another object?', default=True).get() is False: break

    def create_group(self):
        ShellOutput('Groups', symbol='#', font='head')
        if ShellInput('Do you want to create groups?', default=True).get() is False: return False

        def to_create(to_ask, info, info_member=None):
            create_dict, posslist, group_setting_dict, create = {}, [], {}, True
            if ShellInput("Do you want to add a %s?\nInfo: %s" % (to_ask, info), True).get() is False: return False
            group_name = ShellInput('Give the group an unique name!', max_value=20, min_value=2,
                                    neg=True, default='grp01', poss=grp_exist_list).get()
            description = ShellInput('Add a description to this group. (optional)', default='NULL', intype='free', min_value=0,
                                     max_value=50).get()
            if len(grp_exist_list) > 0:
                if ShellInput("Should this %s be nested under another group?" % to_ask, False).get() is True:
                    parent = ShellInput('Provide the name of the parent group.', default=str(random_choice(grp_exist_list)),
                                        poss=grp_exist_list).get()
                else: parent = 'NULL'
            else: parent = 'NULL'
            if to_ask == 'profile':
                group_setting_dict['timer'] = ShellInput("Provide the interval in which this profile should be checked! (in seconds)",
                                                         default=3600, max_value=2764800, min_value=60).get()
                group_setting_dict['enabled'] = 1
            else: group_setting_dict['enabled'] = 1

            # generate option lists
            if to_ask == 'profile':
                member_posslist, condi_posslist, sector_posslist = [], [], ['NULL']
                for dev, typ in self.new_dev_dict.items():
                    if typ == 'action': member_posslist.append(dev)
                    elif typ == 'sensor': condi_posslist.append(dev)
                if len(self.group_dict) > 0:
                    for typ, nested in self.group_dict.items():
                        if typ == 'sector':
                            for name in dict(nested).keys():
                                sector_posslist.append(name)
                condi_posslist.extend([name for name, typ in self.current_dt_dict.items() if typ == 'sensor'])
                if self.setup is False:
                    sector_posslist.extend(self._config(output='name', table='grp', filter="type = 'sector'", outtype='list'))
                    for dt, typ in {name: typ for name, typ in self.current_dt_dict.items()}.items():
                        if typ == 'action':
                            _ = self._config(table='object', output='name', filter="class = '%s'" % dt)
                            if type(_) == list: member_posslist.extend(_)
                            else: member_posslist.append(_)
                        elif typ == 'sensor':
                            _ = self._config(table='object', output='name', filter="class = '%s'" % dt)
                            if type(_) == list: condi_posslist.extend(_)
                            else: condi_posslist.append(_)
                # member_posslist.extend(sector_posslist)
            elif to_ask == 'sector':
                member_posslist = self.current_dev_list
                [member_posslist.remove(dev) for dev in self.object_downlink_list]
                debugger("confint - create_group |member_posslist '%s'" % member_posslist)
            else: return False

            while create:
                ShellOutput(symbol='-', font='line')

                # add condition profiles
                if to_ask == 'profile':
                    stage_dict, add_stage, parent_count, condi_count, new_stage_nr = {}, True, 0, 0, 1
                    profile_exist_list = list(self.profile_dict.keys())
                    dt_datatype_tuple_list = self._config(output='belonging,data', setting='datatype')
                    if self.setup is False:
                        profile_exist_list.extend(self._config(table='grp', output='name', filter="type = 'profile'", outtype='list'))
                    while add_stage:
                        def _show_profile_tree():
                            def _recursive_child_lookup(parent, whitespace):
                                # stage_dict {stage_id {'parent': stage_parent, 'data': { order_id: { setting: data} } } }
                                output_list = []
                                for sid, nested in stage_dict.items():
                                    stage_value_dict = dict(nested)
                                    if stage_value_dict['parent'] != parent: continue
                                    whitespace += 2
                                    output_list = ["%s> stage-id: %s" % ('-' * (whitespace + 1), sid)]
                                    condition_dict = dict(stage_value_dict['data'])
                                    for subid in sorted(condition_dict.keys()):
                                        _dict = condition_dict[subid]
                                        _desc = ", description: %s" % _dict['description'] if _dict['description'] != 'null' else ''
                                        if _dict['type'] == 'parent':
                                            output_list.append("%s-> order-id: %s. \"name: %s, operator: %s%s\""
                                                               % (' ' * whitespace, subid, _dict['name'], _dict['operator'], _desc))
                                            output_list.append(_recursive_child_lookup(parent=_dict['name'], whitespace=whitespace))
                                        else:
                                            output_list.append("%s-> order-id: %s. \"name: %s, condition: '%s %s %s', operator: %s%s\""
                                                               % (' ' * whitespace, subid, _dict['name'], _dict['object'],
                                                                  _dict['condi'], _dict['threshold'], _dict['operator'], _desc))
                                return "\n".join(output_list)
                            main_stage_list = [sid for sid, nested in stage_dict.items() if dict(nested)['parent'] == 'NULL']
                            if 1 < len(main_stage_list) > 1:
                                debugger('confint - create_group - profile - tree |more or less than one stage without parent')
                                # error/log/debug or whatever
                            else:
                                tree_view = _recursive_child_lookup(parent='NULL', whitespace=0)
                                _desc = "%s:\n" % description if description != 'null' else ''
                                ShellOutput("\nCurrent profile configuration:\n\n%s%s\n\n" % (_desc, tree_view), style='info')

                        ShellOutput(symbol='-', font='line')
                        stage_count, loop_condition = len(stage_dict), False
                        if stage_count > 0: _show_profile_tree()
                        posslist = ['add'] if stage_count == 0 else ['add', 'edit'] if stage_count == 1 else ['add', 'edit', 'delete']
                        if len(posslist) == 1: stage_action = posslist[0]
                        else: stage_action = ShellInput('Do you want to add, edit or delete a stage?', default='add',
                                                        poss=posslist).get()
                        parent_dict, parent_active_list, condition_name_list = {}, [], []
                        # stage_dict {stage_id {'parent': stage_parent, 'data': { order_id: { setting: data} } } }
                        for _sid, nested in stage_dict.items():
                            for key, value in dict(nested).items():
                                if key == 'parent' and value is not None:
                                    parent_active_list.append(value)
                                elif key == 'data':
                                    for condition in dict(value).values():
                                        condi_dict = dict(condition)
                                        if condi_dict['type'] == 'parent':
                                            parent_dict[condi_dict['name']] = _sid
                                        elif condi_dict['type'] == 'child':
                                            condition_name_list.append(condi_dict['name'])
                        condition_name_list.extend(parent_dict.keys())
                        possible_parent_dict = {name: sid for name, sid in parent_dict.items() if name not in parent_active_list}
                        debugger("confint - create_group - profile - prequesits |parent exist '%s', parent active '%s'"
                                 % (parent_dict, parent_active_list))
                        if stage_action == 'add':
                            if len(possible_parent_dict) < 1 and stage_count != 0:
                                ShellOutput('There is no free parent to add a stage to. '
                                            'You first need to add a parent to any stage.', style='warn')
                            else:
                                if stage_count != 0:
                                    stage_parent = ShellInput('Provide the parent under which this stage should be nested!',
                                                              poss=list(possible_parent_dict.keys()),
                                                              default=random_choice(list(possible_parent_dict.keys()))).get()
                                else: stage_parent = 'NULL'
                                current_stage, loop_condition = new_stage_nr, True
                        elif stage_action == 'edit':
                            current_stage = ShellInput('Provide the stage-id to edit!', default=str(list(stage_dict.keys())[0]),
                                                       poss=list(stage_dict.keys())).get('int')
                            loop_condition = True
                            stage_parent = dict(stage_dict[current_stage])['parent']
                        elif stage_action == 'delete':
                            stage_id_list = [str(key) for key in stage_dict.keys()]
                            current_stage = ShellInput('Provide the stage-id to delete!', default=stage_id_list[0],
                                                       poss=stage_id_list).get()
                            condition_dict = dict(dict(stage_dict[current_stage])['data'])
                            if any([dict(condition)['name'] for condition in condition_dict.values()]) in parent_active_list:
                                ShellOutput('You cannot delete a stage which has sub-stages configured.\n'
                                            'You must delete the sub-stages first!', style='err')
                            else: del stage_dict[current_stage]
                        else: stage_action, loop_condition, current_stage = 'add', True, 1
                        if loop_condition:
                            if stage_action != 'add':
                                condition_dict = dict(dict(stage_dict[current_stage])['data'])
                            else: condition_dict = {}
                            while loop_condition:
                                ShellOutput(symbol='-', font='line')
                                condi_count = len(condition_dict)
                                posslist = ['add'] if condi_count == 0 else ['add', 'edit'] if condi_count == 1 else ['add', 'edit', 'delete']
                                if len(posslist) == 1: condi_action = posslist[0]
                                else: condi_action = ShellInput('Do you want to add, edit or delete a condition?',
                                                                default='add', poss=posslist).get()
                                current_condi_name_list = [dict(condi)['name'] for condi in condition_dict.values()]
                                condition_name_list.extend(current_condi_name_list)
                                condition_name_list = list_remove_duplicates(condition_name_list)
                                if condi_action in ['add', 'edit']: new_condi_dict = {}
                                if condi_action in ['edit', 'delete']:
                                    while True:
                                        current_condi_name = ShellInput("Provide a name for the condition/parent which to %s"
                                                                        % condi_action, default=random_choice(current_condi_name_list),
                                                                        poss=current_condi_name_list).get()
                                        condi_found = False
                                        for order_id, condition in condition_dict.items():
                                            if dict(condition)['name'] == current_condi_name:
                                                current_condi_dict = {order_id: condition}
                                                condi_found = True
                                        if condi_found: break
                                        else: ShellOutput("The condition '%s' could not be found" % current_condi_name, style='err')
                                    if condi_action == 'edit':
                                        renew_config = ShellInput('Do you want to renew the whole config of this condition/parent?',
                                                                  default=False).get()
                                        if renew_config:
                                            current_condi_name_list.pop(current_condi_name)
                                            condition_dict = ModifyIdiedDict(condition_dict).delete(
                                                [key for key in current_condi_dict.keys()][0])
                                            condi_action = 'add'

                                def condi_input(setting, action='add', filter=None):
                                    if setting == 'name':
                                        return ShellInput('Provide a unique name for the condition/parent.\n'
                                                          'Info: a unique name inside of the profile', neg=True,
                                                          poss=condition_name_list, max_value=20, min_value=2, default='condi1').get()
                                    elif setting == 'object':
                                        return ShellInput('Provide a sensor/sensortype for the condition.', poss=condi_posslist,
                                                          default=random_choice(condi_posslist)).get()
                                    elif setting == 'sector':
                                        return ShellInput('Provide a sector to which to limit the condition. (optional)',
                                                          default='NULL', poss=sector_posslist).get()
                                    elif setting == 'data_source':
                                        return ShellInput("Where should the comparable data be sourced from?\n"
                                                          "Info: direct - we will read the data directly from the sensor (current state)",
                                                          default='database', poss=['database', 'direct']).get()
                                    elif setting == 'data_points':
                                        return ShellInput("How many data entries should be checked for this condition? (optional)\n"
                                                          "Info: if this condition is linked to a devicetype -> this amount "
                                                          "of entries will be checked for each of its devices.",
                                                          default='NULL', max_value=10000, min_value=1).get()
                                    elif setting == 'condi':
                                        if filter is None: _datatype = 'int'
                                        else:
                                            if filter in [dt for dt, data in dt_datatype_tuple_list]: _dt = filter
                                            else: _dt = self._config(table='object', output='class', setting=filter)
                                            _datatype = [data for dt, data in dt_datatype_tuple_list if dt == _dt][0]
                                        if _datatype not in ['int', 'float', 'time', 'date']:
                                            return ShellInput("Provide which condition must be true.\n"
                                                              "Info:\n  '=' - must be exactly the threshold\n"
                                                              "  '!' - must not be exactly the threshold\n",
                                                              poss=['!', '='], default='=').get()
                                        else:
                                            return ShellInput("Provide which condition must be true.\n"
                                                              "Info:\n  '<' - must be smaller than threshold\n"
                                                              "  '>' - must be bigger than threshold\n"
                                                              "  '=' - must be exactly the threshold\n"
                                                              "  '!' - must not be exactly the threshold\n",
                                                              poss=['!', '=', '<', '>'], default='>').get()
                                    elif setting == 'threshold':
                                        return ShellInput('Provide a threshold.', intype='free', max_value=20, min_value=1).get()
                                    elif setting == 'order_id':
                                        if len(condition_dict) > 0:
                                            _list = []
                                            for sid in sorted(condition_dict.keys()):
                                                _dict = dict(condition_dict[sid])
                                                if _dict['type'] == 'child':
                                                    _list.append("%s. \"name: %s, condition: '%s %s %s', operator: %s'\""
                                                                 % (sid, _dict['name'], _dict['object'], _dict['condi'],
                                                                    _dict['threshold'], _dict['operator']))
                                                else: _list.append("%s. \"name: %s, operator: %s'\""
                                                                   % (sid, _dict['name'], _dict['operator']))
                                            ShellOutput("\n\nCurrent in-stage placement:\n%s" % '\n'.join(_list), style='info')
                                        if action == 'add':
                                            posslist = [str(i) for i in range(1, len(condition_dict) + 2)]
                                        else: posslist = [str(i) for i in range(1, len(condition_dict) + 1)]
                                        return ShellInput('Choose the in-stage placement for this condition/parent.', poss=posslist,
                                                          default=posslist[-1]).get('int')
                                    elif setting == 'operator':
                                        return ShellInput("How should this condition/parent be linked to the next one on this stage?\n"
                                                          "Info: the processing priorities are the following:\n"
                                                          "  1. leading with '-',\n  2. 'not', \n  3. 'and' in it,\n  4. 'or' in it",
                                                          poss=['and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor', '-and',
                                                                '-or', '-not', '-nand', '-nor', '-xor', '-xnor'],
                                                          default=random_choice(['and', 'or'])).get()
                                    elif setting == 'description':
                                        return ShellInput('Provide a description for the condition/parent. (optional)', default='NULL',
                                                          intype='free', max_value=50, min_value=2).get()

                                if condi_action == 'add':
                                    condi_typ = ShellInput("Do you want to create a condition or a parent?\n"
                                                           "Info: a parent can have another sub-stage nested under it",
                                                           poss=['condition', 'parent'],
                                                           default=random_choice(['condition', 'parent'])).get()
                                    new_condi_dict['name'] = condi_input('name')
                                    if condi_typ == 'condition':
                                        new_condi_dict['type'] = 'child'
                                        new_condi_dict['object'] = condi_input('object')
                                        if new_condi_dict['object'] in self.current_dt_dict.keys():
                                            new_condi_dict['sector'] = condi_input('sector')
                                        else: new_condi_dict['sector'] = 'NULL'
                                        new_condi_dict['data_source'] = condi_input('data_source')
                                        if new_condi_dict['data_source'] == 'database':
                                            new_condi_dict['data_points'] = condi_input('data_points')
                                        new_condi_dict['condi'] = condi_input('condi', filter=new_condi_dict['object'])
                                        new_condi_dict['threshold'] = condi_input('threshold')
                                    else: new_condi_dict['type'] = 'parent'
                                    new_condi_dict['operator'] = condi_input('operator')
                                    new_condi_dict['description'] = condi_input('description')
                                    condition_dict = ModifyIdiedDict(condition_dict).add(condi_input('order_id'), new_condi_dict)
                                elif condi_action == 'edit':
                                    another_edit = True
                                    condi_setting_list = [_ for _2 in current_condi_dict.values() for _ in dict(_2).keys()]
                                    condi_setting_list.append('order_id')
                                    cur_sid = [key for key in current_condi_dict.keys()][0]
                                    cur_condi_dict = current_condi_dict[cur_sid]
                                    new_sid, new_condi_dict = cur_sid, cur_condi_dict.copy()
                                    while another_edit:
                                        if new_condi_dict != cur_condi_dict:
                                            ShellOutput("\n\nNew condition:\nOrder-id: '%s', Settings: '%s'" % (new_sid, new_condi_dict),
                                                        style='info')
                                        ShellOutput("\n\nCurrent condition:\nOrder-id: '%s', Settings: '%s'" % (cur_sid, cur_condi_dict),
                                                    style='info')
                                        to_edit = ShellInput('Provide the setting to edit.', poss=condi_setting_list,
                                                             default=random_choice(condi_setting_list)).get()
                                        if to_edit == 'order_id':
                                            new_sid = condi_input(to_edit, action='edit')
                                        elif to_edit == 'condi':
                                            new_condi_dict[to_edit] = condi_input(to_edit, filter=new_condi_dict['object'])
                                        else: new_condi_dict[to_edit] = condi_input(to_edit)
                                        another_edit = ShellInput('Want to edit another setting?', default=True).get()
                                    condition_dict = ModifyIdiedDict(condition_dict).edit(cur_sid, new_sid, new_condi_dict)
                                elif condi_action == 'delete':
                                    if current_condi_name in parent_active_list:
                                        ShellOutput("The parent '%s' is still in use! You must delete its sub-stage first!" %
                                                    current_condi_name, style='err')
                                    else: condition_dict = ModifyIdiedDict(condition_dict).delete([key for key in current_condi_dict.keys()][0])

                                def show_condi_config():
                                    output_list = []
                                    for oid, condi in condition_dict.items():
                                        setting_list = ["%s: %s" % (setting, data) for setting, data in dict(condi).items()]
                                        output_list.append("Order-id: '%s', Settings: \"%s\"" % (oid, ', '.join(setting_list)))
                                    ShellOutput("\n\n%s" % "\n".join(output_list), style='info')

                                show_condi_config()
                                loop_condition = ShellInput('Do you want to make further changes to this stage?',
                                                            default=True, style='info').get()
                            debugger("confint - create_group - profile - loop_condition |stage config '%s' '%s'"
                                     % (type(condition_dict), condition_dict))
                            if stage_action in ['add', 'edit'] and len(condition_dict) > 0:
                                stage_dict[current_stage] = {'parent': stage_parent, 'data': condition_dict}
                                if stage_action == 'add': new_stage_nr += 1
                            else: debugger("confint - create_group - profile - loop_condition |no condition in stage")

                        add_stage = ShellInput('Do you want to make further changes to this profile?', default=True, style='info').get()
                        if len(possible_parent_dict) > 1 and add_stage is False:
                            ShellOutput('There are unused parents configured! You need to delete or use them to proceed.', style='warn')
                            add_stage = True

                    self.profile_dict[group_name] = stage_dict

                # add group members
                member_list, current_posslist = [], member_posslist
                member_count, add_member = 0, True
                member_count_min = 2 if to_ask == 'sector' else 1
                while add_member:
                    if member_count == 0: info = "\nInfo: %s" % info_member
                    else: info = ''
                    member_list.append(ShellInput("Provide a name for member %s%s." % (member_count + 1, info),
                                                  poss=current_posslist, default=random_choice(current_posslist)).get())
                    member_count += 1
                    current_posslist = list(set(member_posslist) - set(member_list))
                    if member_count >= member_count_min:
                        if len(current_posslist) > 0:
                            add_member = ShellInput('Want to add another member?', default=True, style='info').get()
                        else: add_member = False
                grp_exist_list.append(group_name)
                create_dict[group_name] = {'setting': group_setting_dict, 'member': member_list, 'parent': parent, 'description': description}
                debugger("confint - create_group |members '%s'" % member_list)
                create = ShellInput("Want to add another %s?" % to_ask, default=True, style='info').get()
            return create_dict

        if self.setup is False:
            grp_exist_list = self._config(output='name', table='grp', outtype='list')
        else: grp_exist_list = []

        ShellOutput('Sectors', symbol='-', font='head')
        _ = to_create('sector', 'links objects which are in the same area', 'must match one device')
        if _ is not False: self.group_dict['sector'] = _
        ShellOutput('Action conditions', symbol='-', font='head')
        _ = to_create('profile', 'lets you configure conditions on which action should be started',
                      'action-devices/-devicetypes which to start or sector on which to limit the actions')
        if _ is not False: self.group_dict['profile'] = _

    def write_config(self):
        ShellOutput('Writing configuration to database', symbol='#', font='head')
        Log("Writing configuration to database:\n\nobjects: '%s'\nsettings: '%s'\ngroups: '%s'\nprofiles: '%s'"
            % (self.object_dict, self.setting_dict, self.group_dict, self.profile_dict), level=3).write()
        if self.setup is not True:
            tmp_config_dump = "%s/maintenance/add_config.tmp" % self._config(setting='path_root')
            with open(tmp_config_dump, 'w') as tmp:
                tmp.write("%s\n%s\n%s" % (self.object_dict, self.setting_dict, self.group_dict))

        ShellOutput('Writing object configuration', font='text')
        # dts {obj_type: {object_name: object_class}}
        # devs {obj_type: {obj_subtype: {object_name: object_class}}}
        insert_count, error_count = 0, 0
        for object_type, packed_values in self.object_dict.items():
            def unpack_values(values, parent='NULL'):
                count, error_count = 0, 0
                for object_name, object_class in sorted(values.items()):
                    if DoSql("INSERT INTO ga.Object (author,name,parent,class,type) VALUES ('%s','%s','%s','%s','%s');" %
                             (self.author, object_name, parent, object_class, object_type), write=True).start() is False:
                        error_count += 1
                    else: count += 1
                return count, error_count
            if object_type == 'device':
                for subtype, packed_subvalues in packed_values.items():
                    _, _2 = unpack_values(packed_subvalues, self.hostname)
                    error_count, insert_count = _2 + error_count, _ + insert_count
            else:
                _, _2 = unpack_values(packed_values)
                error_count, insert_count = _2 + error_count, _ + insert_count
        ShellOutput("added %s object%s" % (insert_count, plural(insert_count)), style='info', font='text')
        if error_count > 0:
            ShellOutput("%s error%s while inserting" % (error_count, plural(error_count)), style='err')
            Log("%s error%s while inserting" % (error_count, plural(error_count))).write()

        ShellOutput('Writing object settings', font='text')
        # {object: {'setting_name': 'setting_data'}}
        insert_count, error_count = 0, 0
        for object_name, packed_values in self.setting_dict.items():
            for setting, data in sorted(packed_values.items()):
                if data == '': continue
                elif type(data) == bool:
                    if data is True: data = 1
                    else: data = 0
                if DoSql("INSERT INTO ga.Setting (author,belonging,setting,data) VALUES ('%s','%s','%s','%s');"
                         % (self.author, object_name, setting, data), write=True).start() is False:
                    error_count += 1
                else: insert_count += 1
        ShellOutput("added %s object setting%s" % (insert_count, plural(insert_count)), style='info', font='text')
        if error_count > 0:
            ShellOutput("%s error%s while inserting" % (error_count, plural(error_count)), style='err')
            Log("%s error%s while inserting" % (error_count, plural(error_count))).write()

        ShellOutput('Writing group configuration', font='text')
        # {group_type: {group_name: {'setting': {setting_dict}, 'description': -, 'parent': -, 'member': [member_list]}}}
        insert_count, member_count, setting_count, error_count = 0, 0, 0, 0
        for group_type, nested in self.group_dict.items():
            for group_name, group_data in dict(nested).items():
                group_data_dict = dict(group_data)
                if group_data_dict['parent'] != 'NULL':
                    _parent_gid = DoSql("SELECT id FROM ga.Grp WHERE name = '%s';" % group_data_dict['parent']).start()
                else: _parent_gid = group_data_dict['parent']
                if DoSql("INSERT INTO ga.Grp (author,type,name,description,parent) VALUES ('%s','%s','%s','%s','%s');"
                         % (self.author, group_type, group_name, group_data_dict['description'], _parent_gid),
                         write=True).start() is False: error_count += 1
                else: insert_count += 1
                sql_gid = DoSql("SELECT id FROM ga.Grp WHERE author = '%s' AND type = '%s' ORDER BY changed DESC LIMIT 1;"
                                % (self.author, group_type)).start()
                if sql_gid is False: continue
                for member in sorted(group_data_dict['member']):
                    if DoSql("INSERT INTO ga.Member (author,gid,member) VALUES ('%s','%s','%s');"
                             % (self.author, sql_gid, member), write=True).start() is False:
                        error_count += 1
                    else: member_count += 1
                for setting, data in sorted(dict(group_data_dict['setting']).items()):
                    if DoSql("INSERT INTO ga.GrpSetting (author,belonging,setting,data) VALUES ('%s','%s','%s','%s');"
                             % (self.author, group_name, setting, data), write=True).start() is False:
                        error_count += 1
                    else: setting_count += 1
        ShellOutput("added %s group%s with a total of %s member%s and %s setting%s"
                    % (insert_count, plural(insert_count), member_count, plural(member_count), setting_count, plural(setting_count)),
                    style='info', font='text')
        if error_count > 0:
            ShellOutput("%s error%s while inserting" % (error_count, plural(error_count)), style='err')
            Log("%s error%s while inserting" % (error_count, plural(error_count))).write()

        ShellOutput('Writing profile configuration', font='text')
        # {group_name: {stage_id: {'parent': stage_parent, 'data': {order_id: {condition_dict}}}}}
        main_parent_list, parent_list, child_list, parent_id, group_count = [], [], [], 1, 0
        for group_name, nested in self.profile_dict.items():
            sql_gid = DoSql("SELECT id FROM ga.Grp WHERE author = '%s' AND name = '%s' ORDER BY changed DESC LIMIT 1;"
                            % (self.author, group_name)).start()
            if sql_gid is False: continue
            group_count += 1
            for order_id, also_nested in dict(nested).items():
                stage_dict = dict(also_nested)
                for sub_sid, condition_data in dict(stage_dict['data']).items():
                    _dict = dict(condition_data)
                    _dict['parent'] = stage_dict['parent']
                    _dict['order_id'] = sub_sid
                    _dict['gid'] = sql_gid
                    if _dict['type'] == 'parent':
                        _dict['parent_id'] = "%s%s" % (sql_gid, int_leading_zero(2, parent_id))
                        parent_id += 1
                        if _dict['parent'] == 'NULL':
                            main_parent_list.append(_dict)
                        else: parent_list.append(_dict)
                    else: child_list.append(_dict)

        def insert_parent(_list):
            _error_count, _parent_count = 0, 0
            for parent in _list:
                parent_dict = dict(parent)
                if DoSql("INSERT INTO ga.ProfileGrp (author,order_id,parent,parent_id,gid,operator,name,description) "
                         "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');"
                         % (self.author, parent_dict['order_id'], parent_dict['parent'], parent_dict['parent_id'], parent_dict['gid'],
                            parent_dict['operator'], parent_dict['name'], parent_dict['description'], ), write=True).start() is False:
                    _error_count += 1
                else: _parent_count += 1
            return _error_count, _parent_count

        parent_count, condi_count, error_count = 0, 0, 0
        _error_count, _parent_count = insert_parent(main_parent_list)
        error_count += _error_count
        parent_count += _parent_count
        _error_count, _parent_count = insert_parent(parent_list)
        error_count += _error_count
        parent_count += _parent_count

        _all_parent_list = main_parent_list
        _all_parent_list.extend(parent_list)
        for child in child_list:
            child_dict = dict(child)
            if child_dict['parent'] != 'NULL':
                _parent_id = [dict(_)['parent_id'] for _ in _all_parent_list if dict(_)['name'] == child_dict['parent']]
            else: _parent_id = child_dict['parent']
            if DoSql("INSERT INTO ga.Profile (author,order_id,parent,gid,object,sector,data_source,data_points,threshold,"
                     "condi,operator,name,description) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');"
                     % (self.author, child_dict['order_id'], _parent_id, child_dict['gid'], child_dict['object'], child_dict['sector'],
                        child_dict['data_source'], child_dict['data_points'], child_dict['threshold'], child_dict['condi'],
                        child_dict['operator'], child_dict['name'], child_dict['description'],),
                     write=True).start() is False: error_count += 1
            else: condi_count += 1
        ShellOutput("added %s profile%s with a total of %s parent%s and %s condition%s"
                    % (group_count, plural(group_count), parent_count, plural(parent_count), condi_count, plural(condi_count)),
                    style='info', font='text')
        if error_count > 0:
            ShellOutput("%s error%s while inserting" % (error_count, plural(error_count)), style='err')
            Log("%s error%s while inserting" % (error_count, plural(error_count))).write()

        if self.setup is not True: os_system("rm %s" % tmp_config_dump)


class Edit:
    def __init__(self, enabled_state=None):
        from core.config import Config
        self.Config, self.enabled_state = Config, enabled_state
        self.start()

    def start(self):
        object_list = ['exit']
        object_agent_list = self.Config(output='name', table='object', filter="type = 'agent'").get('list')
        object_dev_list = self.Config(output='name', table='object', filter="type = 'device'").get('list')
        object_dt_list = self.Config(output='name', table='object', filter="type = 'devicetype'").get('list')
        object_list.extend(object_dev_list)
        object_list.extend(object_agent_list)
        object_list.extend(object_dt_list)
        todo = 'edit' if self.enabled_state is None else self.enabled_state
        while True:
            object_to_edit = ShellInput("Choose one of the listed objects to edit or type 'exit'.\n\nAgents:\n%s\nDeviceTypes:\n%s\nDevices:\n%s\n"
                                        % (object_agent_list, object_dt_list, object_dev_list),
                                        poss=object_list, default=random_choice(object_list), intype='free').get()
            if object_to_edit == 'exit': return False
            if self.enabled_state is not None:
                self.edit_setting(object_to_edit, setting_name='enabled', setting_data=1 if self.enabled_state == 'enable' else 0)
            else:
                what_to_edit = ShellInput('Do you want to edit a object itself or its settings?', poss=['object', 'setting'],
                                          default='setting', intype='free').get()
                if what_to_edit == 'setting': self.edit_setting(object_to_edit)
                elif what_to_edit == 'object': self.edit_object(object_to_edit)
            if ShellInput('Do you want to %s another object?' % todo, default=True).get() is False: break

    def edit_setting(self, object_name, setting_name=None, setting_data=None):
        change_dict, setting_count, setting_error_count = {}, 0, 0
        if setting_name is not None and setting_data is not None:
            change_dict[setting_name] = setting_data
        else:
            setting_dict = {setting: data for setting, data in self.Config(output='setting,data', filter="belonging = '%s'" %
                                                                                                         object_name).get('list')}
            while True:
                setting = ShellInput('Choose the setting you want to edit.',
                                     poss=list(setting_dict.keys()), default=random_choice(list(setting_dict.keys())),
                                     intype='free').get()
                ShellOutput("\nIts current configuration: %s = %s" % (setting, [val for key, val in setting_dict.items() if
                                                                                key == setting][0]), style='info')
                data = ShellInput("Provide the new setting data.\n"
                                  "Warning: If you misconfigure any settings it may lead to unforeseen problems!",
                                  intype='free', max_value=100, min_value=1).get()
                change_dict[setting] = data
                if ShellInput("Do you want to edit another setting of the object %s" % object_name, default=True).get() is False: break
        for setting, data in change_dict.items():
            if DoSql("UPDATE ga.Setting SET data = '%s' WHERE belonging = '%s' AND setting = '%s';" % (data, object_name, setting),
                     write=True).start() is False:
                setting_error_count += 1
            else: setting_count += 1
        ShellOutput("added %s object setting%s" % (setting_count, plural(setting_count)), style='info', font='text')
        if setting_error_count > 0: ShellOutput("%s error%s while inserting" % (setting_error_count, plural(setting_error_count)), style='err')

    def edit_object(self, object_name):
        ShellOutput("This option isn't supported yet.")
        raise SystemExit
        # need to check dependencies -> add with new name and update settings+dependencies -> after that delete the old named obj
        # need to extend optional character blacklist for objects -> no whitespace etc.


def show():
    # add GrpSetting
    from core.config import Config
    object_list = ['exit']
    object_agent_list = Config(output='name', table='object', filter="type = 'agent'").get('list')
    object_dev_list = Config(output='name', table='object', filter="type = 'device'").get('list')
    object_dt_list = Config(output='name', table='object', filter="type = 'devicetype'").get('list')
    object_list.extend(object_dev_list)
    object_list.extend(object_agent_list)
    object_list.extend(object_dt_list)
    while True:
        object_name = ShellInput("The following objects exist:\n\nAgents:\n%s\nDeviceTypes:\n%s\nDevices:\n%s\n\n"
                                 "Choose the one to show the settings of or type 'exit'."
                                 % (object_agent_list, object_dt_list, object_dev_list),
                                 poss=object_list, default=random_choice(object_list), intype='free').get()
        if object_name == 'exit': break
        setting_list = ["'%s' = '%s'" % (setting, data) for setting, data in Config(output="setting,data",
                                                                                    filter="belonging = '%s'" % object_name).get('list')]
        ShellOutput("\n\nThe following settings exist for the object '%s':\n\n%s" % (object_name, ' | '.join(setting_list)))
        ShellOutput(font='line', symbol='-')
    return True


class Delete:
    def __init__(self):
        self.start()

    def start(self):
        ShellOutput("Deletion of objects isn't supported yet.")
        return False


def setup(setup_dict=None):
    if setup_dict is None:
        setup_dict = {}
        setup_dict['hostname'] = ShellInput(prompt='Provide the name of this growautomation host.', default='gacon01').get()
        setup_dict['setuptype'] = ShellInput(prompt="Setup as growautomation standalone, agent or server?\n"
                                                    "Agent and Server setup is disabled for now. It will become available after further testing!",
                                             poss='standalone', default='standalone').get()  # ['agent', 'standalone', 'server']
        setup_dict['path_root'] = ShellInput(prompt='Want to choose a custom install path?', default='/etc/growautomation').get()
        setup_dict['log_level'] = ShellInput(prompt='Want to change the log level?', default='1', poss=['0', '1', '2', '3', '4', '5']).get()
        setup_dict['backup'] = ShellInput('Want to enable backup?', default=True).get()
        setup_dict['path_backup'] = ShellInput(prompt='Want to choose a custom backup path?', default='/mnt/growautomation/backup/').get()
        setup_dict['path_log'] = ShellInput(prompt='Want to choose a custom log path?', default='/var/log/growautomation').get()
    return Create(setup_config_dict=setup_dict)


def choose():
    ShellOutput('Growautomation - config change module', font='head', symbol='#')
    count = 0
    while True:
        count += 1
        if count > 1: ShellOutput(font='line', symbol='#')
        mode = ShellInput("Choose how you want to modify growautomation objects or type 'exit'.",
                          poss=['show', 'add', 'edit', 'enable', 'disable', 'delete', 'exit', 'setup'],
                          default='show', intype='free').get()
        if mode == 'show': start = show()
        elif mode == 'add': start = Create()
        elif mode == 'edit': start = Edit()
        elif mode == 'enable': start = Edit(enabled_state='enable')
        elif mode == 'disable': start = Edit(enabled_state='disable')
        elif mode == 'delete': start = Delete()
        elif mode == 'setup': start = setup()
        elif mode == 'exit': exit()
        else: raise SystemExit('Encountered unknown error while choosing config mode.')
        if start is False: continue


def exit():
    ShellOutput('\n\nBye!\nIt was a pleasure to serve you!')
    raise SystemExit


if __name__ == '__main__':
    try:
        if sys_argv[1] == 'debug':
            debug = True
            VarHandler(name='debug', data=1).set()
        else: debug = False
    except (IndexError, NameError): debug = False
    choose()

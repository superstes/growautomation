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
#     E-Mail: contact@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.5
# checks action profiles/conditions

from core.config import Config
from core.owl import DoSql
from core.ant import time_subtract
from core.ant import dict_sort_keys
from core.smallant import debugger
from core.smallant import list_remove_duplicates
from core.parrot import Action


class Status:
    def __init__(self, condition_dict):
        self.condition_dict = dict(condition_dict)
        self.device = self.condition_dict['object']
        devicetype = Config(output='class', table='object', setting=self.device)
        self.datatype = Config(setting='datatype', belonging=devicetype).get()
        
    def get(self):
        debugger("sparrow - status - get - input |condition_dict '%s' '%s'"
                 % (type(self.condition_dict), self.condition_dict))
        data = self._check()
        debugger("sparrow - status - get - output |condition_dict '%s' '%s', data '%s'"
                 % (type(self.condition_dict), self.condition_dict, data))
        return data
    
    def _check(self):
        condition = self.condition_dict['condition']
        data, threshold = self._get_data(), self.condition_dict['threshold']
        # checks if average data meets the condition
        if condition not in ['<', '>', '=', '!']:
            debugger("sparrow - status - check - error |provided condition '%s' '%s' not supported"
                     % (type(condition), condition))
            return None
        elif condition in ['<', '>'] and self.datatype == 'str':
            debugger("sparrow - status - check - error |provided condition '%s' '%s' doesn't work with "
                     "the configured datatype '%s'" % (type(condition), condition, self.datatype))
            return None
        elif condition in ['<', '>'] and type(data) not in [float, int]:
            debugger("sparrow - status - check - error |provided condition '%s' '%s' can only process float/int data"
                     % (type(condition), condition))
            return None
        else:
            output = False
            if condition in ['=', '!']:
                if data == threshold:
                    output = True
                if condition == '!':
                    output = not output
            elif condition in ['<', '>']:
                if data < threshold:
                    output = True
                if condition == '>':
                    output = not output
        debugger("sparrow - status - check - output |output '%s' '%s'" % (type(output), output))
        return output

    def _get_data(self):
        # check which data should be processed
        datapoints_configured = self.condition_dict['datapoints']
        if datapoints_configured is None:
            datapoints = _default_check_range = Config(setting='range', belonging='check').get('int')
        else: datapoints = int(datapoints_configured)
        if Config(table='object', setting=self.device).get() == 'devicetype':
            is_devicetype = True
            _timer = Config(setting='timer', belonging=self.device).get('int')
        else:
            is_devicetype = False
            own_devicetype = Config(table='object', output='class', setting=self.device).get()
            _timer = Config(setting='timer', belonging=self.device, exit=False, empty=True).get()
            if _timer is False:
                _timer = Config(setting='timer', belonging=own_devicetype).get('int')
        check_time = datapoints * _timer
        # get data from db
        time_now, time_before = time_subtract(check_time, both=True)
        if is_devicetype:
            device_process_list = Config(table='object', filter="class = '%s'" % self.device, output='name').get('list')
            data_list = []
            if self.condition_dict['sector'] is not None:
                sector_gid = Config(table='grp', output='gid', filter="name = '%s'" % self.condition_dict['sector']).get()
                sector_member_list = Config(table='member', setting=sector_gid).get('list')
                for device in sector_member_list:
                    if device in device_process_list:
                        data_list.append(Config(table='data', filter="changed between TIMESTAMP('%s') AND TIMESTAMP('%s') "
                                                                     "AND device = '%s' ORDER BY created desc"
                                                                     % (time_before, time_now, device)).get())
            else:
                for device in device_process_list:
                    data_list.append(Config(table='data', filter="changed between TIMESTAMP('%s') AND TIMESTAMP('%s') "
                                                                 "AND device = '%s' ORDER BY created desc"
                                                                 % (time_before, time_now, device)).get())
        else:
            data_list = Config(table='data', filter="changed between TIMESTAMP('%s') AND TIMESTAMP('%s') AND device = '%s' "
                                                    "ORDER BY created desc" % (time_before, time_now, self.device)).get()
        return self._get_average_data(data_list)

    def _get_average_data(self, data):
        debugger("sparrow - status - get_average_data - input |data '%s' '%s'" % (type(data), data))
        if type(data) == str:
            data = [data]
        if self.datatype is None:
            debugger("sparrow - status - get_average_data - error |device '%s' has no datatype configured" % self.device)
            output = None
        elif self.datatype == 'int':
            int_data_list = [int(_) for _ in data]
            output = sum(int_data_list) / len(data)
        elif self.datatype == 'float':
            float_data_list = [float(_) for _ in data]
            output = float(sum(float_data_list) / float(len(data)))
        elif self.datatype == 'str':
            last_datapoint = data[0]
            data_no_duplicates = list_remove_duplicates(data)
            if len(data_no_duplicates) > 1:
                output = last_datapoint
            else:
                output = data_no_duplicates[0]
        else:
            debugger("sparrow - status - get_average_data - error |configured datatype not supported, "
                     "device '%s', datatype '%s' '%s'" % (self.device, type(self.datatype), self.datatype))
            output = None
        debugger("sparrow - status - get_average_data - output |output '%s' '%s'" % (type(output), output))
        return output


class Profile:
    def __init__(self):
        self.gid = 1

    def parse(self):
        columns_to_get = 'id,stage_id,parent,object,sector,datapoints,threshold,condi,operator,name,description'
        profile_list = DoSql("SELECT %s FROM ga.Profile where gid = '%s';" % (columns_to_get, self.gid), test=False).start()

        profile_dict = {}
        for profile_entry in profile_list:
            pid, stage_id, parent, obj, sector, datapoints, threshold, condi, operator, name, description = profile_entry
            profile_dict["prof_%s" % pid] = {'stage_id': stage_id, 'parent': parent, 'object': obj, 'sector': sector,
                                             'datapoints': datapoints, 'threshold': threshold, 'condition':  condi,
                                             'operator': operator, 'name': name, 'description': description}

        columns_to_get = 'id,stage_id,parent,parent_id,operator,name,description'
        profilegrp_list = DoSql("SELECT %s FROM ga.ProfileGrp where gid = '%s';" % (columns_to_get, self.gid), test=False).start()
        for profile_entry in profilegrp_list:
            pid, stage_id, parent, parent_id, operator, name, description = profile_entry
            profile_dict["grp_%s" % pid] = {'stage_id': stage_id, 'parent': parent, 'parent_id': parent_id, 'operator': operator,
                                            'name': name, 'description': description}
        condition_hierarchy, work_list = [], list(profile_dict.values())
        for id, _ in profile_dict.items():
            _dict = dict(_)
            if (id.find('grp') != -1 and _dict['parent'] is None) or _dict['parent'] is None:
                condition_hierarchy.append(self.get_children(_dict, work_list))
        result = self._check_condition(condition_hierarchy)
        # debug
        if result is True:
            Action(Config(table='member', setting=self.gid).get('list').load())
        else:
            pass
            # Log
            # debug

    def get_children(self, process_dict, option_list):
        # builds condition hierarchy
        debugger("sparrow - profile - get_children - input |process_dict '%s' '%s', option_list '%s' '%s'"
                 % (type(process_dict), process_dict, type(option_list), option_list))
        process_dict = dict(process_dict)
        stage_id = process_dict['stage_id']
        del process_dict['stage_id']
        if 'parent_id' not in process_dict:
            output = {stage_id: process_dict}
        else:
            child_list = []
            for option in option_list:
                option_dict = dict(option)
                if option_dict['parent'] == dict(process_dict)['parent_id']:
                    _dict = self.get_children(option_dict, option_list)
                    child_list.append(_dict)
            if len(child_list) == 1:
                child_list = dict(child_list[0])
            output = {stage_id: child_list, 'operator': process_dict['operator']}
        debugger("sparrow - profile - get_children - output |output '%s' '%s'" % (type(output), output))
        return output

    def _check_condition(self, process_list):
        # pulls current data for condition processing from Status class
        process_list, result_dict, operator_dict = dict_sort_keys(process_list), {}, {}
        for data in process_list:
            debugger("sparrow - profile - check_condition - processing |'%s' '%s'" % (type(data), data))
            data_key_list, data_value_list = [], []
            for key, value in dict(data).items():
                data_key_list.append(key)
                data_value_list.append(value)
            stage_id, condition = data_key_list[0], data_value_list[0]
            if type(condition) == list:
                for member in condition:
                    member_dict = dict(member)
                    for sid, value in member_dict.items():
                        if type(value) == list:
                            result_dict[sid] = self._check_condition(value)
                            operator_dict[sid] = member_dict['operator']
                        elif type(value) == dict:
                            result_dict[sid] = Status(value).get()
                            operator_dict[sid] = value['operator']
                        else:
                            debugger("sparrow - profile - check_condition - processing |no match, sid '%s' '%s', value '%s' '%s'"
                                     % (type(sid), sid, type(value), value))
                            continue
                        debugger("sparrow - profile - check_condition - result |sid '%s' '%s', value '%s' '%s', result '%s', "
                                 "operator '%s'" % (type(sid), sid, type(value), value, result_dict[sid], operator_dict[sid]))
            else:
                condition = dict(condition)
                result_dict[stage_id] = Status(condition).get()
                operator_dict[stage_id] = condition['operator']
        debugger("sparrow - profile - check_condition - output |result '%s', operator '%s'" % (result_dict, operator_dict))
        return self._process_operator(result_dict, operator_dict)

    def _process_operator(self, result_dict, operator_dict):
        debugger("sparrow - profile - process_condition_stage - input |result '%s' '%s', operator '%s' '%s'"
                 % (type(result_dict), result_dict, type(operator_dict), operator_dict))
        operator_sorted_dict = {}
        operator_dict = {key: value for key, value in operator_dict.items() if value is not None}

        def _set_process_priorities(search):
            _dict = {}
            for sid, op in operator_dict.items():
                if search == '-':
                    if op.find(search) != -1:
                        op = op.replace('-', '')
                        _dict[sid] = op
                elif op == search:
                    _dict[sid] = op
            return _dict
        operator_sorted_dict.update(_set_process_priorities('-'))
        operator_sorted_dict.update(_set_process_priorities('not'))
        operator_sorted_dict.update(_set_process_priorities('and'))
        operator_sorted_dict.update(_set_process_priorities('or'))
        operator_dict = operator_sorted_dict
        operator_processed_list = []

        for sid, operator in operator_dict.items():
            if sid in operator_processed_list:
                continue
            my_result = [_res for _sid, _res in result_dict.items() if _sid == sid]
            next_sid = None
            for i in range(len(operator_dict.keys()) - len(operator_processed_list)):
                _ = sid + i
                if next_sid is not None:
                    continue
                if _ in [key for key in result_dict.keys()] and _ not in operator_processed_list:
                    next_sid = sid + i
            next_result = [_res for _sid, _res in result_dict.items() if _sid == next_sid]
            result_dict[next_sid] = self._get_operator_data(operator, [my_result, next_result])
            operator_processed_list.append(sid)
            del result_dict[sid]
        if len(result_dict) > 1:
            debugger("sparrow - profile - process_condition_stage - error |more than one result '%s' '%s'"
                     % (type(result_dict), result_dict))
        else:
            return [value for value in result_dict.values()]

    def _get_operator_data(self, operator: str, data_list: list):
        debugger("sparrow - profile - process_operator - input |operator '%s' '%s', data_list '%s' '%s'"
                 % (type(operator), operator, type(data_list), data_list))
        if len(data_list) < 2 or any(data_list) is None:
            debugger("sparrow - profile - process_operator - error |data_list either too short or has None values within it")
        if operator == 'not':
            if len(data_list) != 2:
                debugger("sparrow - profile - process_operator - not |data_list too long for 'not' processing")
                output = None
            else:
                if data_list[0] is False:
                    output = False
                elif data_list[1] is True:
                    output = False
                else:
                    output = True
        elif operator in ['and', 'nand']:
            if all(data_list) is True:
                output = True
            else:
                output = False
            if operator == 'nand':
                output = not output
        elif operator in ['or', 'nor']:
            if any(data_list) is True:
                output = True
            else:
                output = False
            if operator == 'nor':
                output = not output
        elif operator in ['xor', 'xnor']:
            if all(data_list) is False or all(data_list) is True:
                output = False
            else:
                output = True
            if operator == 'xnor':
                output = not output
        else:
            debugger('sparrow - profile - process_operator - error |no valid operator provided')
            output = None
        debugger("sparrow - profile - process_operator - output |output '%s' '%s'" % (type(output), output))
        return output


if __name__ == '__main__':
    Profile().parse()

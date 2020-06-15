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
from core.smallant import debugger
from core.smallant import Log
from core.smallant import internal_process
from core.smallant import list_remove_duplicates
from core.snake import Balrog

from time import sleep as time_sleep
from sys import argv as sys_argv


class Condition:
    def __init__(self, condition_dict, default_data_points, timer_tuple_list, group_tuple_list, member_tuple_list, placement):
        self.condition_dict, self.default_data_points, self.placement = dict(condition_dict), default_data_points, placement
        # condition_dict input format: {name: xx, order_id: xx, ...}
        self.timer_tuple_list, self.group_tuple_list, self.member_tuple_list = timer_tuple_list, group_tuple_list, member_tuple_list
        self.device = self.condition_dict['object']
        self.datatype, self.is_devicetype = None, None

    def check(self):
        debugger("sparrow - condition - check |input - condition_dict: '%s' '%s'"
                 % (type(self.condition_dict), self.condition_dict))

        _dt_list = Config(output='name', table='object', filter="type = 'devicetype'").get('list')
        if self.device in _dt_list:
            devicetype = self.device
            self.is_devicetype = True
        else:
            devicetype = Config(output='class', table='object', setting=self.device).get()
            self.is_devicetype = False
        self.datatype = Config(setting='datatype', belonging=devicetype).get()

        data_list = self._get_data()
        if data_list is None:
            debugger("sparrow - condition - check |error - could not pull data")
            return None

        avg_data = self._get_average_data(data_list)
        if avg_data is None:
            debugger("sparrow - condition - check |error - could calculate average data")
            return None

        data = self._process(avg_data)
        debugger("sparrow - condition - check |output - '%s' '%s'" % (type(data), data))
        return data

    def _process(self, data):
        # checks if average data meets the condition
        datatype = type(data)
        condition, threshold = self.condition_dict['condition'], datatype(self.condition_dict['threshold'])
        debugger("sparrow - condition - process |input - '%s %s %s'" % (data, condition, threshold))
        if condition not in ['<', '>', '=', '!']:
            debugger("sparrow - condition - process |error - provided condition '%s' '%s' not supported"
                     % (type(condition), condition))
            return None
        elif condition in ['<', '>'] and datatype not in [float, int]:
            debugger("sparrow - condition - process |error - provided condition '%s' '%s' can only process float/int data"
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
        debugger("sparrow - condition - process |output - '%s' '%s'" % (type(output), output))
        return output

    def _get_data(self):
        # check which data should be processed
        data_source = self.condition_dict['data_source']
        if self.datatype is None:
            debugger("sparrow - condition - data |error - device '%s' has no datatype configured" % self.device)
            return None
        elif self.datatype == 'int': self.datatype = int
        elif self.datatype == 'float': self.datatype = float
        elif self.datatype == 'str': self.datatype = str
        data = None

        if data_source == 'database':
            data_points_configured = self.condition_dict['data_points']
            if data_points_configured is None:
                data_points = self.default_data_points
            else: data_points = int(data_points_configured)
            if self.is_devicetype is True:
                _timer = Config(setting='timer', belonging=self.device).get('int')
            else:
                if self.device in [name for name, data in self.timer_tuple_list]:
                    _timer = [data for name, data in self.timer_tuple_list if name == self.device][0]
                else:
                    own_devicetype = Config(table='object', output='class', setting=self.device).get()
                    _timer = [data for name, data in self.timer_tuple_list if name == own_devicetype][0]
            if _timer is False:
                debugger("sparrow - condition - data |error - while looking up timer for device '%s'" % self.device)
                return None
            check_time = data_points * _timer
            # get data from db
            command = "created between TIMESTAMP('%s') AND TIMESTAMP('%s') AND device = '%s' ORDER BY created desc"
            time_now, time_before = time_subtract(check_time, both=True)
            if self.is_devicetype is True:
                device_process_list = Config(table='object', filter="class = '%s'" % self.device, output='name').get('list')
                data_list = []
                if self.condition_dict['sector'] is not None:
                    sector_gid = [gid for name, gid in self.group_tuple_list if name == self.condition_dict['sector']][0]
                    sector_member_list = [name for name, gid in self.member_tuple_list if gid == sector_gid]
                    for device in sector_member_list:
                        if device in device_process_list:
                            data_list.extend(Config(table='data', filter=command % (time_before, time_now, device)).get('list'))
                else:
                    for device in device_process_list:
                        data_list.extend(Config(table='data', filter=command % (time_before, time_now, device)).get('list'))
            else:
                data_list = Config(table='data', filter=command % (time_before, time_now, self.device)).get('list')
            data = data_list
        elif data_source == 'direct':
            retry_count = 1
            while True:
                if retry_count > 5:
                    debugger("sparrow - condition - data |error - could not directly pull data for device '%s'" % self.device)
                    return None
                data = internal_process(target=Balrog(sensor=self.condition_dict['object'], output='stdout').start, stdout=True)
                try:
                    data = self.datatype(data)
                    break
                except ValueError: time_sleep(3)
                retry_count += 1
        if data is False or data == [False]:
            debugger("sparrow - condition - data |error - could not pull data for device '%s' from database" % self.device)
            return None
        else: return data

    def _get_average_data(self, data):
        debugger("sparrow - condition - average_data |input - data: '%s' '%s'" % (type(data), data))
        if type(data) == str: data = [data]
        if self.datatype in [int, float]:
            int_data_list = [self.datatype(_) for _ in data]
            output = self.datatype(sum(int_data_list)) / self.datatype(len(data))
        elif self.datatype == str:
            last_datapoint = data[0]
            data_no_duplicates = list_remove_duplicates(data)
            if len(data_no_duplicates) > 1:
                output = last_datapoint
            else: output = data_no_duplicates[0]
        else:
            debugger("sparrow - condition - average_data |error - configured datatype not supported, "
                     "device '%s', datatype '%s' '%s'" % (self.device, type(self.datatype), self.datatype))
            output = None
        debugger("sparrow - condition - average_data |output - '%s' '%s'" % (type(output), output))
        return output


class Operator:
    def __init__(self, result_dict, placement):
        self.result_dict, self.work_dict, self.last_order_id, self.placement = result_dict, {}, None, placement
        # input format: { order_id: {result: xx, operator: yy} }

    def check(self):
        debugger("sparrow - operator - check |input - '%s' '%s'" % (type(self.result_dict), self.result_dict))
        self.last_order_id = sorted([order_id for order_id in self.result_dict.keys()])[-1]
        self.result_dict[self.last_order_id] = {'result': dict(self.result_dict[self.last_order_id])['result'], 'operator': None}
        self._set_process_priorities(['-', 'not', 'and', 'or', None])
        return self._process()

    def _set_process_priorities(self, prio_list):
        for prio in prio_list:
            prio_id = len(self.work_dict)
            for order_id, nested in self.result_dict.items():
                operator = dict(nested)['operator']

                def _add_to_dict(count):
                    _dict = {'order_id': order_id, 'operator': dict(nested)['operator'], 'result': dict(nested)['result']}
                    if _dict not in list(self.work_dict.values()):
                        count += 1
                        self.work_dict[count] = _dict
                    return count

                if operator is None and prio is not None:
                    continue
                elif operator is None or (prio == '-' and operator.find(prio) != -1) or operator == prio:
                    prio_id = _add_to_dict(prio_id)

    def _process(self):
        debugger("sparrow - operator - process |input - '%s' '%s'" % (type(self.work_dict), self.work_dict))
        # input: { prio_id: {'order_id': xx, 'operator': yy, 'result': zz} }

        priority_list = sorted(list(self.work_dict.keys()))
        for priority in priority_list:
            data_dict = dict(self.work_dict[priority])
            operator = data_dict['operator']
            if operator is None:
                debugger("sparrow - operator - process |info - skipping last order_id: '%s'" % data_dict)
                break

            order_id = int(data_dict['order_id'])
            order_id_list = [_id for _id in self.result_dict.keys()]
            try:
                compare_order_id = sorted([_id for _id in order_id_list if _id > order_id])[0]
            except IndexError:
                debugger("sparrow - operator - process |error - no comparable order_id found,"
                         "order_id_list: '%s', order_id: '%s'" % (order_id_list, order_id))
                continue
            compare_result = dict(self.result_dict[compare_order_id])['result']
            result = self._get_data(operator=operator, this_id=order_id, next_id=compare_order_id,
                                    data_list=[data_dict['result'], compare_result])
            if result is None:
                debugger("sparrow - operator - process |error - result is none")
                Log("Error while processing condition '%s %s %s' situated on %s"
                    % (data_dict['result'], operator, compare_result, self.placement), level=1).write()
                return None
            self.result_dict[compare_order_id] = {'operator': dict(self.result_dict[order_id])['operator'], 'result': result}
            del self.result_dict[order_id]

        if len(self.result_dict) == 1:
            return dict(self.result_dict[self.last_order_id])['result']
        else:
            debugger("sparrow - operator - process |error - more than one element left in result_dict: '%s' '%s'"
                     % (type(self.result_dict), self.result_dict))
            return None

    def _get_data(self, operator: str, data_list: list, this_id, next_id):
        debugger("sparrow - operator - data |input - operator: '%s' '%s', data_list: '%s' '%s', ids: '%s' '%s'"
                 % (type(operator), operator, type(data_list), data_list, this_id, next_id))
        if 2 < len(data_list) > 2:
            debugger("sparrow - operator - data |error - input list has length of '%s' must be 2" % len(data_list))
            # could be re-written to support longer lists for and/or/xor operations
            #   pe if a stage has only 'and' operations - would save processing
            return None
        elif None in data_list:
            debugger("sparrow - operator - data |error - input has None values within it")
            return None
        if operator == 'not':
            if data_list[0] is False:
                output = False
            elif data_list[1] is True:
                output = False
            else: output = True
        elif operator in ['and', 'nand']:
            if all(data_list) is True:
                output = True
            else: output = False
        elif operator in ['or', 'nor']:
            if any(data_list) is True:
                output = True
            else: output = False
        elif operator in ['xor', 'xnor']:
            if all(data_list) is False or all(data_list) is True:
                output = False
            else: output = True
        else:
            debugger('sparrow - operator - data |error - no valid operator provided')
            output = None
        if operator in ['nand', 'nor', 'xnor'] and output is not None:
            output = not output
        debugger("sparrow - operator - data |output - '%s' '%s'" % (type(output), output))
        return output


class Profile:
    def __init__(self, gid):
        self.gid = gid
        self.profile_dict, self.data_points, self.timer_tuple_list, self.group_tuple_list = {}, None, None, None
        self.member_tuple_list = None

    def parse(self):
        self._cache_data()
        self._prequesits()
        result = self._recursive_process_stage(None)
        debugger("sparrow - profile - parse |result: '%s' '%s'" % (type(result), result))
        print(result)
        if result is None:
            Log("Error processing action profile with id '%s' - received output 'None'\n"
                "Either the profile has an incorrect configuration or some data for its conditions could not be obtained."
                % self.gid, level=1).write()
        elif result is True:
            print('start action')

    def _cache_data(self):
        self.data_points = Config(setting='range', belonging='check').get('int')
        self.timer_tuple_list = Config(output='belonging,data', setting='timer').get('list')
        self.group_tuple_list = Config(table='grp', output='name,id', filter='id is NOT NULL').get('list')
        self.member_tuple_list = Config(table='member', output='member,gid', filter='gid is NOT NULL').get('list')

    def _prequesits(self):
        columns_to_get = 'id,order_id,parent,object,sector,data_source,data_points,threshold,condi,operator,name,description'
        profile_list = DoSql("SELECT %s FROM ga.Profile where gid = '%s';" % (columns_to_get, self.gid)).start()

        for profile_entry in profile_list:
            pid, order_id, parent, obj, sector, data_source, data_points, threshold, condi, operator, name, description = profile_entry
            self.profile_dict["prof_%s" % pid] = {'order_id': order_id, 'parent': parent, 'object': obj, 'sector': sector,
                                                  'data_source': data_source, 'data_points': data_points, 'threshold': threshold,
                                                  'condition': condi, 'operator': operator, 'name': name, 'description': description}

        columns_to_get = 'id,order_id,parent,parent_id,operator,name,description'
        profilegrp_list = DoSql("SELECT %s FROM ga.ProfileGrp where gid = '%s';" % (columns_to_get, self.gid)).start()
        for profile_entry in profilegrp_list:
            pid, order_id, parent, parent_id, operator, name, description = profile_entry
            self.profile_dict["grp_%s" % pid] = {'order_id': order_id, 'parent': parent, 'parent_id': parent_id, 'operator': operator,
                                                 'name': name, 'description': description}

    def _recursive_process_stage(self, parent):
        process_dict = {pid: profile for pid, profile in self.profile_dict.items() if dict(profile)['parent'] == parent}
        # get results for the conditions in this stage
        result_dict, placement = {}, 'main stage' if parent is None else "sub-stage of parent %s" % parent
        for profile in process_dict.values():
            profile_dict = dict(profile)
            if 'parent_id' in profile_dict:
                # if is parent -> process its substage and get result from it
                result = self._recursive_process_stage(profile_dict['parent_id'])
            else:
                # if is condition -> pass the condition settings to Status for data-processing
                result = Condition(condition_dict=profile_dict, default_data_points=self.data_points,
                                   timer_tuple_list=self.timer_tuple_list, group_tuple_list=self.group_tuple_list,
                                   member_tuple_list=self.member_tuple_list, placement=placement).check()
            result_dict[profile_dict['order_id']] = {'result': result, 'operator': profile_dict['operator']}
        if None in [dict(nested)['result'] for nested in result_dict.values()] or result_dict == {}:
            debugger("sparrow - profile - process |error - none result from Condition class: '%s'" % result_dict)
            Log("Error while processing condition data on %s" % placement).write()
        stage_result = Operator(result_dict=result_dict, placement=placement).check()
        debugger("sparrow - profile - process |output: '%s' '%s', parent: '%s'" % (type(stage_result), stage_result, parent))
        return stage_result


if __name__ == '__main__':
    try:
        gid = sys_argv[1]
        Profile(gid).parse()
    except IndexError:
        raise SystemExit('You need to pass the profiles group id as argument!')

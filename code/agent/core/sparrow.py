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
# checks action profiles

from core.owl import DoSql
from core.smallant import debugger

from random import getrandbits


class Check:
    def __init__(self):
        self.gid = 1

    def start(self):
        columns_to_get = 'id,stage_id,parent,object,threshold,condi,operator,name,description'
        profile_list = DoSql("SELECT %s FROM ga.Profile where gid = '%s';" % (columns_to_get, self.gid), test=False).start()

        profile_dict = {}
        for profile_entry in profile_list:
            pid, stage_id, parent, obj, threshold, condi, operator, name, description = profile_entry
            profile_dict["prof_%s" % pid] = {'stage_id': stage_id, 'parent': parent, 'object': obj, 'threshold': threshold,
                                             'condition':  condi, 'operator': operator, 'name': name, 'description': description}

        columns_to_get = 'id,stage_id,parent,parent_id,operator,name,description'
        profilegrp_list = DoSql("SELECT %s FROM ga.ProfileGrp where gid = '%s';" % (columns_to_get, self.gid), test=False).start()
        for profile_entry in profilegrp_list:
            pid, stage_id, parent, parent_id, operator, name, description = profile_entry
            profile_dict["grp_%s" % pid] = {'stage_id': stage_id, 'parent': parent, 'parent_id': parent_id, 'operator': operator,
                                            'name': name, 'description': description}
        final_list, work_list = [], list(profile_dict.values())
        for id, _ in profile_dict.items():
            _dict = dict(_)
            if (id.find('grp') != -1 and _dict['parent'] is None) or _dict['parent'] is None:
                final_list.append(self.get_children(_dict, work_list))
        print(self.check_condition(final_list))

    def get_children(self, process_dict, option_list):
        debugger("sparrow - get_children - input |process_dict '%s' '%s', option_list '%s' '%s'"
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
        debugger("sparrow - get_children - output |output '%s' '%s'" % (type(output), output))
        return output

    def sort_dict_keys(self, process_list):
        sorted_list, stage_id_count = [], 1
        while True:
            for stage_dict in process_list:
                if stage_id_count in stage_dict:
                    sorted_list.append(stage_dict)
            if stage_id_count >= len(process_list):
                break
            stage_id_count += 1
        return sorted_list

    def process_operator(self, operator: str, data_list: list):
        debugger("sparrow - process_operator - input |operator '%s' '%s', data_list '%s' '%s'"
                  % (type(operator), operator, type(data_list), data_list))
        if len(data_list) < 2 or any(data_list) is None:
            debugger("sparrow - process_operator - error |data_list either too short or has None values within it")
        if operator == 'not':
            if len(data_list) != 2:
                debugger("sparrow - process_operator - not |data_list too long for 'not' processing")
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
            debugger('sparrow - process_operator - error |no valid operator provided')
            output = None
        debugger("sparrow - process_operator - output |output '%s' '%s'" % (type(output), output))
        return output

    def get_condition_value(self, condition_dict):
        data = bool(getrandbits(1))
        debugger("sparrow - get_condition_value - output |condition_dict '%s' '%s', data '%s'" % (type(condition_dict), condition_dict, data))
        return data

    def process_condition_stage(self, result_dict, operator_dict):
        debugger("sparrow - process_condition_stage - input |result '%s' '%s', operator '%s' '%s'"
                  % (type(result_dict), result_dict, type(operator_dict), operator_dict))
        operator_sorted_dict = {}
        operator_dict = {key: value for key, value in operator_dict.items() if value is not None}

        def set_process_priorities(search):
            _dict = {}
            for sid, operator in operator_dict.items():
                if operator.find(search) != -1:
                    _dict[sid] = operator
            return _dict
        operator_sorted_dict.update(set_process_priorities('-'))
        operator_sorted_dict.update(set_process_priorities('not'))
        operator_sorted_dict.update(set_process_priorities('and'))
        operator_sorted_dict.update(set_process_priorities('or'))
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
            result_dict[next_sid] = self.process_operator(operator, [my_result, next_result])
            operator_processed_list.append(sid)
            del result_dict[sid]
        if len(result_dict) > 1:
            debugger("sparrow - process_condition_stage - error |more than one result '%s' '%s'" % (type(result_dict), result_dict))
        else:
            return [value for value in result_dict.values()]

    def check_condition(self, process_list):
        process_list, result_dict, operator_dict = self.sort_dict_keys(process_list), {}, {}
        for data in process_list:
            debugger("sparrow - check_condition - processing |'%s' '%s'" % (type(data), data))
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
                            result_dict[sid] = self.check_condition(value)
                            operator_dict[sid] = member_dict['operator']
                        elif type(value) == dict:
                            result_dict[sid] = self.get_condition_value(value)
                            operator_dict[sid] = value['operator']
                        else:
                            debugger("sparrow - check_condition - processing |no match, sid '%s' '%s', value '%s' '%s'" % (type(sid), sid, type(value), value))
                            continue
                        debugger("sparrow - check_condition - result |sid '%s' '%s', value '%s' '%s', result '%s', operator '%s'"
                                  % (type(sid), sid, type(value), value, result_dict[sid], operator_dict[sid]))
            else:
                condition = dict(condition)
                result_dict[stage_id] = self.get_condition_value(condition)
                operator_dict[stage_id] = condition['operator']
        debugger("sparrow - check_condition - output |result '%s', operator '%s'" % (result_dict, operator_dict))
        return self.process_condition_stage(result_dict, operator_dict)


if __name__ == '__main__':
    Check().start()

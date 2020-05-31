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

# ga_version 0.4

from core.config import Config
from core.smallant import debugger
from core.smallant import Log


class Check:
    def __init__(self, device: str, data, max_change_percent=35, local_debug=False):
        self.device, self.data, self.max_change_percent, self.local_debug = device, data, max_change_percent, local_debug
        self.last_data_list = []
        self.count_last_data_checked, self.min_change_percent = 5, self.max_change_percent * -1

    def _debug(self, output):
        if self.local_debug is None or self.local_debug is True:
            debugger(output)
        elif self.local_debug is False:
            return False

    def start(self):
        try:
            self.last_data_list = Config(setting=Config(setting='hostname', local_debug=self.local_debug).get(), table='data',
                                         filter="device = '%s' order by created desc limit %s" %
                                                (self.device,  self.count_last_data_checked), local_debug=self.local_debug).get('list')
            self._debug("data_check - start |'%s' last data list: '%s'" % (self.device, self.last_data_list))
        except SystemExit:
            return self._implicit_return()
        if type(self.data) == int:
            return self._digit(int)
        elif type(self.data) == float:
            return self._digit(float)
        else:
            return self._implicit_return()

    def _digit(self, digit_type):
        filtered_data_list = []
        for _ in self.last_data_list:
            try:
                digit_type(_)
                filtered_data_list.append(_)
            except (ValueError, NameError):
                continue
        self._debug("data_check - digit |'%s' filtered last data list: '%s'" % (self.device, filtered_data_list))
        if len(filtered_data_list) < 1: self._implicit_return()
        try:
            if len(filtered_data_list) < 2:
                data_base_avg = digit_type(filtered_data_list[0])
            else:
                list_sum = digit_type(0)
                for value in filtered_data_list:
                    list_sum += digit_type(value)
                data_base_avg = list_sum / digit_type(len(filtered_data_list))
        except ValueError:
            return self._implicit_return()
        data_base_percentage = 100 / data_base_avg
        data_change_percent = 100 - digit_type(self.data) * digit_type(data_base_percentage)
        self._debug("data_check - digit |'%s' data change: old_list '%s', new '%s', percent: '%.2f'"
                    % (self.device, filtered_data_list, self.data, data_change_percent))
        if data_change_percent < self.min_change_percent or data_change_percent > self.max_change_percent:
            self._debug("data_check - digit |'%s' error - output data change is not in acceptable range\n"
                        "data before '%s', now '%s', change in percent '%.2f', min change '%s', max change '%s'"
                        % (self.device, data_base_avg, self.data, data_change_percent, self.min_change_percent, self.max_change_percent))
            Log("Error - output change for device %s is not in acceptable range\n"
                "Average data before '%s', now '%s', change in percent '%.2f' (min change '%s', max change '%s')"
                % (self.device, data_base_avg, self.data, data_change_percent, self.min_change_percent, self.max_change_percent), level=2)
            return False
        return True

    def _implicit_return(self):
        return True

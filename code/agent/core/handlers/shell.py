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

# provides classes for shell input/output

try:
    from core.shared.smallant import format_output
except (ImportError, ModuleNotFoundError):
    from smallant import format_output

from colorama import Fore as colorama_fore
from getpass import getpass
from os import popen as os_popen


class Input:
    def __init__(self, prompt, default='', poss='', intype='', style='', posstype='', max_value=None, min_value=None, neg=False, lower=True, null=False):
        self.prompt, self.default, self.poss, self.intype, self.style = prompt, default, poss, intype, style
        self.posstype, self.max_value, self.min_value, self.neg, self.lower, self.null = posstype, max_value, min_value, neg, lower, null
        self.style_type, self.output = Output(style=style).colors(), ''
        self.lower, self.default_str, self.poss_str = '', '', ''

    def _string_check(self, to_check: str):
        # move functionality to shared string_check function?
        if self.max_value is None: self.max_value = 20
        if self.min_value is None: self.min_value = 2
        to_check = str(to_check)
        char_blacklist = "!$§?^´`µ{}()><|\\*ÄÖÜüöä@,\"'"
        if len(to_check) > self.max_value or len(to_check) < self.min_value:
            Output("Input error. Input must be between %s and %s characters long" % (self.min_value, self.max_value), style='warn', font='text')
            return False
        elif any((char in char_blacklist) for char in to_check):
            Output("Input error. Input must not include the following characters: %s" % char_blacklist, style='warn', font='text')
            return False
        else: return True

    def _poss_check(self):
        while_count = 0

        def _poss_error():
            if self.neg: Output("Input error. The following cannot be chosen: %s\n" % self.poss, style='warn', font='text')
            else: Output("Input error. Choose one of the following: %s\n" % self.poss, style='warn', font='text')
        while True:
            try:
                input_ok = False
                if while_count > 0: _poss_error()
                user_input = str(input(self.style_type + "\n%s%s%s%s%s\n > " %
                                       (self.prompt, self.poss_str, self.poss, self.default_str, self.default) +
                                       colorama_fore.RESET) or self.default)
                if self.posstype != '':
                    if self.posstype == 'int': user_input = int(user_input)
                    elif self.posstype == 'str': user_input = str(user_input)
                if self.null is False:
                    if user_input in ['False', 'None']: continue

                def _test(check):
                    type_check, test = type(self.default), False
                    try:
                        if type_check(check) == type_check(user_input): test = True
                    except ValueError:
                        if user_input == check: test = True
                    if test and type_check == str:
                        test = self._string_check(check)
                    return test
                if type(self.poss) == list:
                    for poss in self.poss:
                        if _test(poss) is True: input_ok = True
                else: input_ok = _test(self.poss)
                if self.neg: input_ok = not input_ok
                if input_ok: break
            except (KeyError, ValueError): _poss_error()
            while_count += 1
        return user_input

    def get(self, outtype=None):
        if self.poss != '' or type(self.default) == bool:
            if self.neg: self.poss_str = "\nNo Poss: "
            else: self.poss_str = "\nPoss: "
        if self.default != "": self.default_str = "\nDefault: "
        if type(self.default) == bool:
            while True:
                try:
                    self.output = {'true': True, 'false': False, 'yes': True, 'no': False, 'y': True,
                                   'n': False, 'f': False, 't': True, '': self.default}[
                        input(self.style_type + "\n%s%syes/no/true/false%s%s\n > " %
                              (self.prompt, self.poss_str, self.default_str, self.default) + colorama_fore.RESET)]
                    break
                except KeyError:
                    Output("WARNING: Invalid input please enter either yes/true/no/false!\n", style='warn', font='text')
            self.lower = False
        elif type(self.default) == str or self.default is None:
            if self.intype == 'pass' and self.default != '':
                getpass(prompt="\n%s\nRandom: %s\n > " % (self.prompt, self.default)) or "%s" % self.default
            elif self.intype == 'pass':
                getpass(prompt="\n%s\n > " % self.prompt)
            elif self.intype == 'passgen':
                if self.max_value is None: self.max_value = 20
                if self.min_value is None: self.min_value = 8
                while True:
                    user_input = int(input("\n%s%s%s%s%s\n > " % (self.prompt, self.poss_str, self.poss, self.default_str,
                                                                  self.default)) or "%s" % self.default)
                    if user_input < int(self.min_value) or user_input > int(self.max_value):
                        Output("Input error. Value should be between %s and %s.\n" %
                                    (self.min_value, self.max_value), style='warn', font='text')
                    else: break
                self.output = user_input
            elif self.intype == 'free' and self.poss == '':
                while True:
                    user_input = input(self.style_type + "\n%s%s%s\n > " % (self.prompt, self.default_str, self.default) +
                                       colorama_fore.RESET) or self.default
                    if self._string_check(user_input):
                        self.output = user_input
                        break
            elif self.poss != '': self.output = self._poss_check()
            else: self.output = input(self.style_type + "\n%s%s%s\n > " % (self.prompt, self.default_str, self.default) +
                                      colorama_fore.RESET) or "%s" % self.default
        elif type(self.default) == int:
            if self.min_value is None and self.max_value is None:
                self.max_value, self.min_value = 2592000, 1
            else:
                if self.max_value is None:
                    self.max_value = 2592000
                elif self.min_value is None:
                    self.min_value = 1
            while True:
                try: user_input = int(input("\n%s%s%s\n > " % (self.prompt, self.default_str, self.default)) or "%s" % self.default)
                except ValueError: user_input = 0
                if user_input < int(self.min_value) or user_input > int(self.max_value):
                    Output("Input error. Value should be between %s and %s." % (self.min_value, self.max_value), style='warn', font='text')
                else: break
            self.output, self.lower = user_input, False
        else: raise KeyError("Default value was neither str/int/bool/none | Value: '%s', '%s'" % (type(self.default), self.default))

        if outtype is not None:
            self.output = format_output(typ=outtype, data=self.output)
        if self.lower is False or type(self.output) != str: return self.output
        else: return self.output.lower()


class Output:
    def __init__(self, output=None, font='text', style='', symbol='#'):
        self.output,  self.style, self.symbol = output, style, symbol
        self._header() if font == 'head' else self._line if font == 'line' \
            else self._text() if self.output is not None else False

    def _header(self):
        print("\n")
        self._line()
        print("%s" % self.output)
        self._line()
        print("\n")

    def colors(self):
        return colorama_fore.YELLOW if self.style == 'warn' else colorama_fore.CYAN if self.style == 'info' \
            else colorama_fore.RED if self.style == 'err' \
            else colorama_fore.GREEN if self.style == 'succ' else ''

    def _text(self):
        print(self.colors() + "%s\n" % self.output + colorama_fore.RESET)

    def _line(self):
        shellhight, shellwidth = os_popen('stty size', 'r').read().split()
        print(self.symbol * (int(shellwidth) - 1))

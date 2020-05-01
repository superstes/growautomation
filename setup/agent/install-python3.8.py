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

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from os import popen as os_popen

repo_path = "/tmp/controller/setup/agent"
shellhight, shellwidth = os_popen('stty size', 'r').read().split()


def process(command):
    output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
    output_str, error_str = output.decode("ascii").strip(), error.decode("ascii").strip()
    return output_str


rpi_version = process("cat /proc/device-tree/model")
linux_version = process("lsb_release -a | grep Release: | sed 's/[^0-9]//g'")


def default_python():
    process("echo 'alias python=/usr/local/bin/python3.8' >> ~/.bashrc")
    process("source ~/.bashrc")


def compile():
    print("#" * (int(shellwidth) - 1))
    print("This process may take over an hour.\nDO NOT INTERUPT THIS PROCESS.\n")
    print("-" * (int(shellwidth) - 1))
    process("/bin/bash %s/compile_python3.8.sh" % repo_path)
    default_python()
    print("#" * (int(shellwidth) - 1))
    print("Process finished.")
    print("#" * (int(shellwidth) - 1))


def pre_compiled(script):
    print("#" * (int(shellwidth) - 1))
    print("Installing pre-compiled package.\n")
    process("tar -xvzf %s/%s" % (repo_path, script))
    default_python()
    print("#" * (int(shellwidth) - 1))
    print("Process finished.")
    print("#" * (int(shellwidth) - 1))


if rpi_version == "Raspberry Pi 3 Model B Rev 1.2":
    if linux_version == "10":
        pre_compiled("pre-compiled_python3.8_pi3brev1.2-buster.tar.gz")
    else: compile()
else: compile()

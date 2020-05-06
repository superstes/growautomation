#!/bin/bash
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


command -v "git" >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
  sudo apt-get update
  sudo apt-get install git -y
fi
cd /tmp
[[ -d controller ]] | git clone https://github.com/growautomation-at/controller.git --depth=1
cd controller/setup
/usr/bin/python3 python/install-python3.8.py $PWD
cp ../code/agent/core/*.py .
cp ../code/agent/maintenance/*.py .
/usr/bin/python3.8 setup_linux.py $1
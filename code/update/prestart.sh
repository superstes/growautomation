#!/bin/bash
# This file is part of GrowAutomation
#     Copyright (C) 2021  René Pascal Rath
#
#     GrowAutomation is free software: you can redistribute it and/or modify
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
#     Web: https://github.com/superstes/growautomation

# downloads the target version of the actual update script

TMP_DIR=$(ls /tmp | grep 'systemd-private-.*-apache2.service.*')
UPDATE_CONFIG="/tmp/${TMP_DIR}/tmp/ga_update.conf"
UPDATE_PATH='/var/lib/ga_update'

METHOD=$(cat $UPDATE_CONFIG | grep 'METHOD' | cut -d '=' -f2)

if [ "$METHOD" == 'online' ]
then
  VERSION=$(cat $UPDATE_CONFIG | grep 'VERSION' | cut -d '=' -f2)
  COMMIT=$(cat $UPDATE_CONFIG | grep 'COMMIT' | cut -d '=' -f2)

  if [ "$COMMIT" != 'None' ]
  then
    TAG=$COMMIT
  else
    TAG=$VERSION
  fi
  wget "https://raw.githubusercontent.com/superstes/growautomation/${TAG}/code/update/main.py" -o ${UPDATE_PATH}/tmp_main.py && rm ${UPDATE_PATH}/main.py && mv ${UPDATE_PATH}/tmp_main.py ${UPDATE_PATH}/main.py
  rm ${UPDATE_PATH}/tmp_main.py
  sleep 1
fi

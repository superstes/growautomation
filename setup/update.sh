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

now=$(date +'%m%d%Y_%H%M')
tmp_path=/tmp/growautomation_$now

echo ''
echo 'If you have configured a custom growautomation root path - you must pass it into this script as argument'
echo ''
echo 'This update script will overwrite the code of all core modules.'
echo 'This might lead to errors if your current version is not compatible!'
echo ''
echo 'Do you still want to continue? (Type yes or no)'

read really
if [[ $really == 'no' ]]
then
  echo 'User exited update script.'
  echo ''
  echo 'Goodbye!'
  exit 1
fi

mkdir -p $tmp_path
cd $tmp_path
git clone https://github.com/growautomation-at/controller.git --depth=1
if [[ $1 != '' ]]
then
  ga_path=$1
  if [ ! -d $ga_path ]
  then
    echo ''
    echo "Growautomation root path $ga_path does not exist"
    echo ''
    cd & rm -rf $tmp_path$tmppath
    exit 1
  fi
else
  ga_path=/etc/growautomation
  if [ ! -d $ga_path ]
  then
    echo ''
    echo 'No growautomation root path provided and default root path does not exist'
    echo ''
    cd & rm -rf $tmp_path
    exit 1
  fi
fi

echo 'Creating backup of current growautomation files'
mkdir $ga_path/backup
tar cfvz $tmp_path/update_$now.tar.gz $ga_path
mv $tmp_path/update_$now.tar.gz $ga_path/backup

echo 'Updating modules'
cp -r controller/code/agent/core/*.py $ga_path/core
cp -r controller/code/agent/maintenance/*.py $ga_path/maintenance
cp -r controller/code/agent/service/*.py $ga_path/service
chown -R growautomation:growautomation $ga_path
echo 'Restarting systemd service'
systemctl daemon-reload
sysetmctl restart growautomation.service
echo 'Cleaning up'
cd &rm -rf $tmppath

echo 'Update finished.'
echo 'Goodbye!'
echo ''
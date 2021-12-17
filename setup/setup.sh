#!/bin/bash

set -e

# GrowAutomation setup script

# just copy this script to the target system and execute it

# written for debian/ubuntu
# will start setup via ansible playbook
# config changes:
#   if you want to install it on a remote system =>
#     1. add your target host as an ansible host under './inventories/hosts.yml' and './inventories/host_vars/$HOSTNAME.yml' (you can copy the 'tmpl' host)
#     2. run this script with the same host as argument (must be exactly the same as in the inventory)
#   ga-settings can be changed under ./vars/main.yml (before you run the installation script)

# package installation
echo 'deb http://ppa.launchpad.net/ansible/ansible/ubuntu focal main' > /etc/apt/sources.list.d/ansible.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
apt update
apt install python3 python3-requests git --yes
apt-get install ansible --yes

# provided config
if [ -z $1 ]; then
  TARGET_VERSION=`python3 <<EOF
from requests import get
print(get('https://api.github.com/repos/superstes/growautomation/tags').json()[0]['name'])
EOF`

else
  TARGET_VERSION=$1
fi

if [ -z $2 ]; then
  TARGET_HOST='localhost'
else
  TARGET_HOST=$2
fi

if [ $TARGET_HOST != 'localhost' ]; then
  apt install sshpass --yes
fi

# downloading source code
SETUP_DIR="/tmp/ga_$(date '+%Y-%m-%d')"
git clone https://github.com/superstes/growautomation.git --depth 1 ${SETUP_DIR} --branch $TARGET_VERSION
cd $SETUP_DIR/setup

# installing ansible dependencies
mkdir $SETUP_DIR/setup/collections
ansible-galaxy collection install -r requirements.yml
ansible-galaxy install -r requirements.yml --roles-path $SETUP_DIR/setup/roles

echo ''
echo '###################################################################################'
echo '##################################### WARNING #####################################'
echo '###################################################################################'
echo 'This is the last time you can modify the config before the installation is started.'
echo '  You could:'
echo '  -> send this window to the background (Ctrl+Z)'
echo '  -> make your modifications'
echo '  -> and bring it back to the foreground (fg).'
echo ''
echo '###################################### INFO #######################################'
echo 'The following config files exist:'
echo "  main: ${SETUP_DIR}/setup/vars/main.yml"
echo '  remote hosts: (optional)'
echo "    - ${SETUP_DIR}/setup/inventories/hosts.yml"
echo "    - ${SETUP_DIR}/setup/inventories/host_vars/\${HOSTNAME}.yml"
echo ''
echo 'Do you want to continue? (yes/NO)'

read config_done
if [ $config_done == 'yes' ]; then
  ansible-playbook -K -i inventories/hosts.yml pb_setup.yml --limit ${TARGET_HOST} --extra-vars "ga_setup_clone_dir=${SETUP_DIR}" --extra-vars "ga_setup_release=${TARGET_VERSION}"
else
  echo 'User chose to stop the setup! Exiting!'
fi

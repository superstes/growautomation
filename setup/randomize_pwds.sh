#!/bin/bash

set -e

# GrowAutomation script to update credentials

# just copy this script to the target system and execute it

# written for debian/ubuntu
# config changes:
#   ga-settings can be changed by modifying the file ./vars/main.yml (before you run the installation script)
#   if you want to install it on a remote system =>
#     1. add your target host as an ansible host under './inventories/hosts.yml' and './inventories/host_vars/$HOSTNAME.yml' (you can copy the 'tmpl' host)
#     2. run this script with the same host as argument (must be exactly the same as in the inventory)


# package installation
echo 'deb http://ppa.launchpad.net/ansible/ansible/ubuntu focal main' > /etc/apt/sources.list.d/ansible.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 93C4A3FD7BB9C367
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
if [ ! -d "$SETUP_DIR" ]
then
  git clone https://github.com/superstes/growautomation.git --depth 1 ${SETUP_DIR} --branch ${TARGET_VERSION}
fi
cd $SETUP_DIR/setup

# installing ansible dependencies
rm -rf /usr/lib/python3/dist-packages/ansible_collections  # removing unused ansible collections (~500MB..)
ansible-galaxy collection install -r requirements.yml
ansible-galaxy install -r requirements.yml --roles-path $SETUP_DIR/setup/roles

# running ansible playbook
ansible-playbook -K -i inventories/hosts.yml pb_creds.yml --limit ${TARGET_HOST} --extra-vars "ga_setup_clone_dir=${SETUP_DIR}" --extra-vars "ga_setup_release=${TARGET_VERSION}"

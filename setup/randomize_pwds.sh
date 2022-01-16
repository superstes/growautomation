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


echo ''
echo '                              (&&&&&,'
echo '                              &&& &&&'
echo '                                (&.        &&&&&&&&&&&&&&&'
echo '                                (&.   &&&&            &&&'
echo '                                (&.&&&              &&&'
echo '                                (&&&             *&&&'
echo '                                (&.    &&%&&&&&&&'
echo '                                (&.                         &&* &&'
echo '         &&&&&&&&&&&&&&&&       (&.                &&&&&&   &&&&&&'
echo '          &&&             &&&   (&.                &&  &&     &&'
echo '            &&&              &&&(&.                  &&       &&'
echo '               &&&             &&&.                  &&       &&'
echo '                  (&&&&&&&&&    &&.                 &&&       &&'
echo '                                &&.            &&&&&          &&'
echo '                 &&&&&&         &&.      #&&&&                &&'
echo '                 &&  &&         &&.  &&&&                   ,&&&'
echo '                   &&           &&.  &&                &&&&&'
echo '                   &&           &&.  &&          .&&&&'
echo '                   &&,          &&.  &&     &&&&&'
echo '                        (&&&&&  &&.  &&&&&&'
echo '                            &&  &&.  &&'
echo '                            &&  &&.  &&'
echo ''

echo '###########################################################################'
echo '############## GrowAutomation  PASSWORD-RANDOMIZATION SCRIPT ##############'
echo '###########################################################################'

# package installation
echo ''
echo '### INSTALLING PACKAGES ###'
echo ''
echo 'deb http://ppa.launchpad.net/ansible/ansible/ubuntu focal main' > /etc/apt/sources.list.d/ansible.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 93C4A3FD7BB9C367
apt update
apt install python3 python3-requests git --yes
apt-get install ansible --yes

if [ -z "$1" ]; then
  # shellcheck disable=SC2006
  TARGET_VERSION=`python3 <<EOF
from requests import get
print(get('https://api.github.com/repos/superstes/growautomation/tags').json()[0]['name'])
EOF`

else
  TARGET_VERSION=$1
fi

if [ -z "$2" ]; then
  TARGET_HOST='localhost'
else
  TARGET_HOST='remote'
fi

if [ "$TARGET_HOST" != 'localhost' ]; then
  apt install sshpass --yes
fi

# downloading source code
SETUP_DIR="/tmp/ga_$(date '+%Y-%m-%d')"
if [ ! -d "$SETUP_DIR" ]
then
  echo ''
  echo '### DOWNLOADING CODE ###'
  echo ''
  git -c advice.detachedHead=false clone https://github.com/superstes/growautomation.git --depth 1 "${SETUP_DIR}" --branch "${TARGET_VERSION}"
fi
cd "$SETUP_DIR/setup"

# installing ansible dependencies
echo ''
echo '### DOWNLOADING ANSIBLE DEPENDENCIES ###'
echo ''
rm -rf /usr/lib/python3/dist-packages/ansible_collections  # removing unused ansible collections (~500MB..)
ansible-galaxy collection install -r requirements.yml
ansible-galaxy install -r requirements.yml --roles-path "$SETUP_DIR/setup/roles"

echo ''
echo '### STARTING SCRIPT ###'
echo ''

if [ "$TARGET_HOST" != 'localhost' ]; then
  ansible-playbook -i inventories/hosts.yml pb_creds.yml --limit "${TARGET_HOST}" --extra-vars "ga_setup_clone_dir=${SETUP_DIR}"
else
  ansible-playbook -c local -i inventories/hosts.yml pb_creds.yml --limit "${TARGET_HOST}" --extra-vars "ga_setup_clone_dir=${SETUP_DIR}"
fi

echo ''
echo '### FINISHED SCRIPT ###'
echo ''

echo 'Do you want to display the generated password? (YES/no)'
read -r ask_pwds
if [ "$ask_pwds" != 'no' ]; then
  echo ''
  echo '### BEGIN PASSWORDS ###'
  echo ''
  cat /etc/.ga_setup
  echo ''
  echo '### END PASSWORDS ###'
  echo ''
fi

echo ''
echo '### EXITING SCRIPT ###'

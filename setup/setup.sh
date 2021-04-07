#!/bin/bash

# GrowAutomation setup script

# just copy this script to the target system and execute it

# written for debian/ubuntu
# will start setup via ansible playbook
# config changes:
#   if you want to install it on a remote system =>
#     1. add your target host as an ansible host under './inventories/hosts.yml' and './inventories/host_vars/$HOSTNAME.yml' (you can copy the 'tmpl' host)
#     2. run this script with the same host as argument (must be exactly the same as in the inventory)
#   ga-settings can be changed under ./vars/main.yml (before you run the installation script)

SETUP_DIR="/tmp/ga_$(date '+%Y-%m-%d')"

if [ -z $1 ]; then
  TARGET_HOST='localhost'
else
  TARGET_HOST=$1
fi

sudo apt update
sudo apt install software-properties-common python python3 git --yes
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install ansible --yes

if [ $TARGET_HOST != 'localhost' ]; then
  sudo apt install sshpass --yes
fi

git clone https://github.com/superstes/growautomation.git --depth 1 ${SETUP_DIR}
cd $SETUP_DIR/setup
ansible-galaxy collection install -r requirements.yml

echo ''
echo '###################################################################################'
echo '##################################### WARNING #####################################'
echo '###################################################################################'
echo 'This is the last time you can modify the config before the installation is started.'
echo '  You could:'
echo '  -> send this window to the background (Ctrl+Z)'
echo '  -> make your modifications and'
echo '  -> bring it back to the foreground (fg).'
echo ''
echo '###################################### INFO #######################################'
echo 'The following config files exist:'
echo "  main: ${SETUP_DIR}/setup/vars/main.yml"
echo '  remote hosts (if needed):'
echo "    - ${SETUP_DIR}/setup/inventories/hosts.yml"
echo "    - ${SETUP_DIR}/setup/inventories/host_vars/\$HOSTNAME.yml"
echo ''
echo 'Do you want to continue? (yes/any=no)'

read config_done
if [ $config_done == 'yes' ]; then
  ansible-playbook -K -i inventories/hosts.yml ga.yml --limit ${TARGET_HOST} --extra-vars "setup_clone_dir=${SETUP_DIR}"
else
  echo 'User chose to stop the setup! Exiting!'
fi

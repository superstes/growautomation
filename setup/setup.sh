#!/bin/bash

# GrowAutomation setup script

# written for debian/ubuntu
# will start setup via ansible playbook
# config changes:
#   if you want to install it on a remote system =>
#     1. add your target host as an ansible host under './inventories/hosts.yml' and './inventories/host_vars/$HOSTNAME.yml' (you can copy the 'tmpl' host)
#     2. change the TARGET_HOST variable in this script (to the ansible hostname)
#   ga-settings can be changed under ./vars/main.yml (before you run the installation script)


TARGET_HOST='localhost'

sudo apt update
sudo apt install software-properties-common python python3 --yes
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install ansible --yes
ansible-galaxy collection install -r requirements.yml

if [ $TARGET_HOST != 'localhost' ]
then
  sudo apt install sshpass --yes
fi

ansible-playbook -K -i inventories/hosts.yml playbooks/ga.yml $TARGET_HOST

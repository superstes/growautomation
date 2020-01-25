#!/bin/python
import os
import sys
#check for root privileges
if os.getuid() != 0:
    sys.exit("This script needs to be run with root privileges!")
else:
    print("Starting Growautomation installation script.")
    print("The newest versions can be found at: https://git.growautomation.at")

ga_setuptype = str(input("Setup as growautomation standalone, agent or server? (Poss: agent,standalone,server - Default: standalone)").lower() or "standalone")
ga_linuxupgrade = str(input("Want to upgrade your software and distribution before growautomation installation? (Poss: yes,no - Default: yes)").lower() or "yes")
ga_rootpath = str(input("Want to choose a custom install path? (Default: /etc/growautomation)").lower() or "/etc/growautomation")
ga_logpath = str(input("Want to choose a custom log path? (Default: /var/log/growautomation)").lower() or "/var/log/growautomation")
ga_backup = str(input("Want to enable backup? (Poss: yes,no - Default: yes)").lower() or "yes")
if ga_backup == "yes":
    ga_backuppath = str(input("Want to choose a custom backup path? (Default: /mnt/growautomation/backup/)").lower() or "/mnt/growautomation/backup/")
    ga_backupmnt = str(input("Want to mount remote share as backup destination? Smb and nfs available. (Poss: yes,no - Default: no)").lower() or "no")
    if ga_backupmnt == "yes":
        ga_backupmnttype = str(input("Mount nfs or smb/cifs share as backup destination? (Poss: nfs,cifs,no - Default: nfs)").lower() or "no")
        ga_backupmntserver = str(input("Provide the server ip. (Poss: ip,no - Default: 192.168.0.201)").lower() or "192.168.0.201")
        ga_backupmntshare = str(input("Provide the share name. (Poss: share,no - Default: backup)").lower() or "backup")
        if ga_backupmnttype == "cifs":
            ga_backupmntusr = str(input("Provide username for share authentication. (Poss: user,no - Default: no)").lower() or "no")
            ga_backupmntpwd = str(input("Provide password for share authentication. (Poss: password,no - Default: no)").lower() or "no")
            ga_backupmntdom = str(input("Provide domain for share authentication. (Poss: domain,no - Default: workgroup)").lower() or "workgroup")

#Software packages
print("Installing software packages")
os.system("apt-get update")
if ga_linuxupgrade == "yes":
    os.system("apt-get dist-upgrade && apt-get upgrade")

if ga_setuptype == "agent" or ga_setuptype == "standalone":
    os.system("apt-get install python3 python3-pip python3-dev python-smbus git supervisor")

    #Modules
    print("Installing python packages")
    os.system("python3 -m pip install mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay")

if ga_setuptype == "server" or ga_setuptype == "standalone":
    os.system("apt-get install python3 mariadb-server git")

if ga_backup == "yes" and ga_backupmnt == "yes":
    if ga_backupmnttype == "nfs":
        os.system("apt install nfs-common")
    elif ga_backupmnttype == "cifs":
       os.system("apt install cifs-utils")

#Create folders
print("Setting up ga directories")
os.system("useradd growautomation")
os.system("mkdir -p " + ga_rootpath + " && chown -R growautomation:growautomation " + ga_rootpath)
os.system("mkdir -p " + ga_logpath + " && chown -R growautomation:growautomation " + ga_logpath)
os.system("mkdir -p " + ga_backuppath + " && chown -R growautomation:growautomation " + ga_backuppath)

if ga_backup == "yes" and ga_backupmnt == "yes":
    #setting up backup
    if ga_backupmnttype == "cifs":
        ga_backupmntcreds = "username=" + ga_backupmntusr + ",password=" + ga_backupmntpwd + ",domain=" + ga_backupmntdom
    else:
        ga_backupmntcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write(ga_backupmntserver + ":/" + ga_backupmntshare + " " + ga_backuppath + " " + ga_backupmnttype + " " + ga_backupmntcreds + " 0 0")
    ga_fstab.close()
    os.system("mount -a")
elif ga_backup == "no" or ga_backupmnt == "no":
    print("If you want to have a remote/an external backup destination - you must configure it on your own.")

#setting up growautomation code
os.system("cd /tmp && git clone https://github.com/growautomation-at/controller.git")
os.system("cp -r /tmp/controller/agentcode/*" + ga_rootpath)
os.system("PYVER=$(python3 --version | cut -c8-10) && ln -s /etc/growautomation/config /usr/local/lib/python$PYVER/dist-packages/GA")

if ga_setuptype == "server" or ga_setuptype == "standalone":
    #MariaDB setup
    print("Setting up database.\n Set a secure password and answer all other questions with Y/yes.")
    os.system("mysql -u root < /tmp/controller/setup/server/ga-databases.sql")
    os.system("mysql_secure_installation")
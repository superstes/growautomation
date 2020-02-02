#!/bin/python
import os
import getpass
from datetime import datetime
import random
import string

ga_version = "0.2.1"
ga_versionfile = "/etc/growautomation.version"

#shell output
def ga_shelloutputheader(output):
    shellhight, shellwidth = os.popen('stty size', 'r').read().split()
    print("\n")
    print('#' * (int(shellwidth) - 1))
    print("\n" + output + "\n")
    print('#' * (int(shellwidth) - 1))
    print("\n")

ga_setuplog = "/var/log/growautomation-setup.log"
def ga_setuplogfile(output):
    tmplog = open(ga_setuplog, "a")
    tmplog.write("\n------------------------------------------\n" + output + "\n")

def ga_setuplogfileplain(output):
    tmplog = open(ga_setuplog, "a")
    tmplog.write(output + "\n")

def ga_pwdgen(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def ga_fstabcheck():
    with open("/etc/fstab", 'r') as readfile:
        stringcount = readfile.read().count("Growautomation")
        if stringcount > 0:
            shellhight, shellwidth = os.popen('stty size', 'r').read().split()
            print('#' * (int(shellwidth) - 1))
            print("WARNING!\n"
                  "You already have one or more remote shares configured.\n"
                  "If you want to install new ones you should disable the old ones by editing the '/etc/fstab' file.\n"
                  "Just add a '#' in front of the old shares or delete those lines to disable them.\n"
                  "WARNING!")
            print('#' * (int(shellwidth) - 1) + "\n")

ga_setuplogfile(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
ga_setuplogredirect = " 2>&1 | tee -a " + ga_setuplog

#check for root privileges
if os.getuid() != 0:
    raise SystemExit("This script needs to be run with root privileges!")
else:
    ga_shelloutputheader("Starting Growautomation installation script.\n"
                   "The newest versions can be found at: https://git.growautomation.at")

#check if growautomation is already installed
if os.path.exists(ga_versionfile) = True:
    tmpfile = open(ga_versionfile)
    tmplines = tmpfile.readlines()
    for line in tmplines:
        if line.find("gaversion=") != -1:
            print("A version of growautomation is/was already installed on this system!\n\n"
                  "Installed version: " + line[11:] +
                  "\nReplace version: " + ga_version)
            ga_versionreplace = str(input("Do you want to replace it? (Poss: yes,no - Default: no)\n").lower()or "no")
#            if ga_versionreplace == "yes":
#                ga_versionreplaceconfig = str(input("Do you want to keep your old configuration? "
#                                                    "(Poss: yes,no - Default: no)\n").lower()or "no")
            if ga_versionreplace == "yes":
                ga_versionreplacebackup = str(input("Do you want to backup your old growautomation installation? "
                                                    "(Poss: yes,no - Default: yes)\n").lower()or "yes")
            elif ga_versionreplace == "no":
                raise SystemExit("Stopping installation script!")
        if line.fine("garoot=") != -1 and ga_versionreplace == "yes":
            ga_versionoldpath = line[8:]


#getting user inputs
ga_setuptype = str(input("Setup as growautomation standalone, agent or server? "
                         "(Poss: agent,standalone,server - Default: standalone)\n").lower() or "standalone")

ga_internalca = str(input("Need to import internal ca? Mainly needed if your firewall uses ssl inspection.\n"
                         "(Poss: yes,no - Default: no)\n").lower() or "no")
if ga_internalca == "yes":
    ga_internalcapath = str(input("Provide path to the ca file. "
                                  "(Poss: 'certpath',exit - Default: /etc/ssl/certs/internalca.cer)\n") or "/etc/ssl/certs/internalca.cer")

ga_linuxupgrade = str(input("Want to upgrade your software and distribution before growautomation installation? "
                            "(Poss: yes,no - Default: yes)\n").lower() or "yes")
if ga_versionreplace == "yes":
    ga_rootpath = str(input("Want to choose a custom install path? "
                            "(Default: " + ga_versionoldpath + ")\n").lower() or ga_versionoldpath)
else:
    ga_rootpath = str(input("Want to choose a custom install path? "
                            "(Default: /etc/growautomation)\n").lower() or "/etc/growautomation")
ga_backup = str(input("Want to enable backup? "
                      "(Poss: yes,no - Default: yes)\n").lower() or "yes")
if ga_backup == "yes":

    ga_backuppath = str(input("Want to choose a custom backup path? "
                              "(Default: /mnt/growautomation/backup/)\n").lower() or "/mnt/growautomation/backup/")
    ga_backupmnt = str(input("Want to mount remote share as backup destination? Smb and nfs available. "
                             "(Poss: yes,no - Default: yes)\n").lower() or "yes")
    if ga_backupmnt == "yes":
        ga_fstabcheck()
        ga_backupmnttype = str(input("Mount nfs or smb/cifs share as backup destination? "
                                     "(Poss: nfs,cifs,exit - Default: nfs)\n").lower() or "exit")
        ga_backupmntserver = str(input("Provide the server ip. "
                                       "(Poss: 'ip',exit - Default: 192.168.0.201)\n").lower() or "192.168.0.201")
        ga_backupmntshare = str(input("Provide the share name. "
                                      "(Poss: 'sharename',exit - Default: growautomation/backup)\n").lower() or "growautomation/backup")
        if ga_backupmntshare != "exit" and ga_backupmntserver != "exit" and ga_backupmnttype != "exit":
            if ga_backupmnttype == "cifs":
                ga_backupmntusr = str(input("Provide username for share authentication. "
                                            "(Poss: 'user',exit - Default: gabackup)\n").lower() or "gabackup")
                ga_backupmnttmppwd = ga_pwdgen(20)
                ga_backupmntpwd = getpass.getpass(prompt="Provide password for share authentication. "
                                                         "(Poss: 'password',exit - Default: " + ga_backupmnttmppwd + ")\n") or ga_backupmnttmppwd
                ga_backupmntdom = str(input("Provide domain for share authentication. "
                                            "(Poss: 'domain',exit - Default: workgroup)\n").lower() or "workgroup")
        else:
            print("Not mounting remote share for backup!\nCause: No sharetype, serverip or sharename provided.\n")

ga_logpath = str(input("Want to choose a custom log path? "
                       "(Default: /var/log/growautomation)\n").lower() or "/var/log/growautomation")
ga_logmnt = str(input("Want to mount remote share as log destination? Smb and nfs available. "
                      "(Poss: yes,no - Default: no)\n").lower() or "no")
if ga_logmnt == "yes":
    ga_fstabcheck()
    if ga_backup == "yes":
        if ga_backupmnt == "yes":
            ga_samemount = str(input("Use same server as for remote backup? "
                                  "(Poss: yes,no - Default: yes)\n").lower() or "yes")
            if ga_samemount == "yes":
                ga_logmnttype = ga_backupmnttype
                ga_logmntserver = ga_backupmntserver
            else:
                ga_logmnttype = str(input("Mount nfs or smb/cifs share as log destination? "
                                          "(Poss: nfs,cifs,exit - Default: nfs)\n").lower() or "exit")
                ga_logmntserver = str(input("Provide the server ip. "
                                            "(Poss: 'ip',exit - Default: 192.168.0.201)\n").lower() or "192.168.0.201")
    else:
        ga_logmnttype = str(input("Mount nfs or smb/cifs share as log destination? "
                                  "(Poss: nfs,cifs,exit - Default: nfs)\n").lower() or "exit")
        ga_logmntserver = str(input("Provide the server ip. "
                                    "(Poss: 'ip',exit - Default: 192.168.0.201)\n").lower() or "192.168.0.201")
    ga_logmntshare = str(input("Provide the share name. "
                               "(Poss: 'sharename',exit - Default: growautomation/log)\n").lower() or "growautomation/log")

    if ga_logmntshare != "exit" and ga_logmntserver != "exit" and ga_logmnttype != "exit" and ga_logmnttype == "cifs":
        if ga_backupmnt == "yes" and ga_backupmnttype == "cifs" and ga_samemount == "yes":
            ga_samemountcreds = str(input("Use same share credentials as for remote backup? "
                                              "(Poss: yes,no - Default: yes)\n").lower() or "yes")
            if ga_samemountcreds == "yes":
                ga_logmntusr = ga_backupmntusr
                ga_logmntpwd = ga_backupmntpwd
                ga_logmntdom = ga_backupmntdom
            else:
                ga_logmntusr = str(input("Provide username for share authentication. "
                                         "(Poss: 'user',exit - Default: galog)\n").lower() or "gabackup")
                ga_logmnttmppwd = ga_pwdgen(20)
                ga_logmntpwd = getpass.getpass(prompt="Provide password for share authentication. "
                                                      "(Poss: 'password',exit - Default: " + ga_logmnttmppwd + ")\n") or ga_logmnttmppwd
                ga_logmntdom = str(input("Provide domain for share authentication. "
                                         "(Poss: 'domain',exit - Default: workgroup)\n").lower() or "workgroup")
        else:
            ga_logmntusr = str(input("Provide username for share authentication. "
                                     "(Poss: 'user',exit - Default: galog)\n").lower() or "gabackup")
            ga_logmntpwd = getpass.getpass(prompt="Provide password for share authentication. "
                                                  "(Poss: 'password',exit - Default: 56XPOWPeM6dL)\n") or "56XPOWPeM6dL"
            ga_logmntdom = str(input("Provide domain for share authentication. "
                                     "(Poss: 'domain',exit - Default: workgroup)\n").lower() or "workgroup")
    else:
        ga_logmnt = "no"
        print("Not mounting remote share for logs!\nCause: No sharetype, serverip or sharename provided.\n")
else:
    ga_logmnttype = "exit"

ga_sqlbackuppwd = ga_pwdgen(20)

ga_setuplogfile("Setup information received:\n")
ga_setuplogfileplain("Basic vars: setuptype " + ga_setuptype + ", internalca " + ga_internalca + ", garootpath " + ga_rootpath + ",backup " + ga_backup + "\n")
if ga_backup == "yes":
    ga_setuplogfileplain("Backup vars: backuppath " + ga_backuppath + ", backupmnt " + ga_backupmnt + "\n")
    if ga_backupmnt == "yes":
        ga_setuplogfileplain("backupmnttype " + ga_backupmnttype + ", backupserver " + ga_backupmntserver + ", backupshare " + ga_backupmntshare + "\n")
        if ga_backupmnttype == "cifs":
            ga_setuplogfileplain("backupmntusr " + ga_backupmntusr + ", backupmntdom " + ga_backupmntdom + "\n")
ga_setuplogfileplain("Log vars: logpath " + ga_logpath + ", logmnt " + ga_logmnt + "\n")
if ga_logmnt == "yes":
    ga_setuplogfileplain("logmnttype " + ga_logmnttype + ", logserver " + ga_logmntserver + ", logshare " + ga_logmntshare + "\n")
    if ga_logmnttype == "cifs":
        ga_setuplogfileplain("logmntusr " + ga_logmntusr + ", logmntdom " + ga_logmntdom + "\n")


ga_shelloutputheader("Thank you for providing the setup informaiton.\nThe installation will start now.")
ga_setuplogfile("Starting installation.")

#Software packages
print("Installing software packages\n")
os.system("apt-get update" + ga_setuplogredirect)
if ga_linuxupgrade == "yes":
    os.system("apt-get -y dist-upgrade && apt-get -y upgrade" + ga_setuplogredirect)

if ga_setuptype == "agent" or ga_setuptype == "standalone":
    os.system("apt-get -y install python3 python3-pip python3-dev python-smbus git" + ga_setuplogredirect)
    if ga_internalca == "yes":
        os.system("git config --global http.sslCAInfo " + ga_internalcapath +
                  " && python3 -m pip config set global.cert " + ga_internalcapath + ga_setuplogredirect)

    #Modules
    print("Installing python packages\n")
    os.system("python3 -m pip install mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay" + ga_setuplogredirect)

if ga_setuptype == "server" or ga_setuptype == "standalone":
    os.system("apt-get -y install python3 mariadb-server git" + ga_setuplogredirect)

if (ga_backup == "yes" and ga_backupmnt == "yes") or (ga_logmnt == "yes"):
    if ga_backupmnttype == "nfs" or ga_logmnttype == "nfs":
        os.system("apt-get -y install nfs-common" + ga_setuplogredirect)
    elif ga_backupmnttype == "cifs" or ga_logmnttype == "cifs":
        os.system("apt-get -y install cifs-utils" + ga_setuplogredirect)

#Create folders
ga_shelloutputheader("Setting up directories")
ga_setuplogfile("Setting up directories")
os.system("useradd growautomation" + ga_setuplogredirect)
os.system("mkdir -p " + ga_backuppath + " && chown -R growautomation:growautomation " + ga_backuppath + ga_setuplogredirect)
if ga_versionreplace == "yes":
    os.system("echo 'gaversion=" + ga_version + "\ngaroot=" + ga_rootpath + "\n' > " + ga_versionfile + ga_setuplogredirect)
    if ga_versionreplacebackup == "yes":
        ga_versionoldbackup = ga_backuppath + "/install"
        os.system("mkdir " + ga_versionoldbackup + " && cp -r " + ga_versionoldpath + " " + ga_versionoldbackup + ga_setuplogredirect)
os.system("mkdir -p " + ga_rootpath + " && chown -R growautomation:growautomation " + ga_rootpath + ga_setuplogredirect)
os.system("mkdir -p " + ga_logpath + " && chown -R growautomation:growautomation " + ga_logpath + ga_setuplogredirect)

#setting up backup

if ga_backup == "yes" and ga_backupmnt == "yes":
    if ga_backupmnttype != "exit":
        ga_shelloutputheader("Mounting backup share")
        ga_setuplogfile("Mounting backup share")
        if ga_backupmnttype == "cifs":
            ga_backupmntcreds = "username=" + ga_backupmntusr + ",password=" + ga_backupmntpwd + ",domain=" + ga_backupmntdom
        else:
            ga_backupmntcreds = "auto"
        ga_fstab = open("/etc/fstab", 'a')
        ga_fstab.write("#Growautomation backup mount\n"
                       "//" + ga_backupmntserver + "/" + ga_backupmntshare + " " + ga_backuppath + " " +
                       ga_backupmnttype + " " + ga_backupmntcreds + " 0 0\n\n")
        ga_fstab.close()
        os.system("mount -a" + ga_setuplogredirect)
elif ga_backup == "no" or ga_backupmnt == "no":
    print("If you want to have a remote/an external backup destination - you must configure it on your own.\n")

# setting up logs

if ga_logmnt == "yes":
    if ga_logmnttype != "exit":
        ga_shelloutputheader("Mounting log share")
        ga_setuplogfile("Mounting log share")
        if ga_logmnttype == "cifs":
            ga_logmntcreds = "username=" + ga_logmntusr + ",password=" + ga_logmntpwd + ",domain=" + ga_logmntdom
        else:
            ga_logmntcreds = "auto"
        ga_fstab = open("/etc/fstab", 'a')
        ga_fstab.write("#Growautomation log mount\n"
                       "//" + ga_logmntserver + "/" + ga_logmntshare + " " + ga_logpath + " " +
                       ga_logmnttype + " " + ga_logmntcreds + " 0 0\n\n")
        ga_fstab.close()
        os.system("mount -a" + ga_setuplogredirect)
elif ga_logmnt == "no":
    print("If you want to have a remote/an external log destination - you must configure it on your own.\n")

#setting up growautomation code
ga_shelloutputheader("Setting up growautomation code")
ga_setuplogfile("Setting up growautomation code")
os.system("cd /tmp && git clone https://github.com/growautomation-at/controller.git" + ga_setuplogredirect)
os.system("cp -r /tmp/controller/code/agent/* " + ga_rootpath +
          " && PYVER=$(python3 --version | cut -c8-10) && ln -s /etc/growautomation/config "
          "/usr/local/lib/python$PYVER/dist-packages/GA" + ga_setuplogredirect)

if ga_setuptype == "server" or ga_setuptype == "standalone":
    #MariaDB setup
    ga_shelloutputheader("Setting up database.\nSet a secure password and answer all other questions with Y/yes.")
    ga_setuplogfile("Setting up database.")
    os.system("mysql -u root < /tmp/controller/setup/server/ga-databases.sql" + ga_setuplogredirect)
    os.system("echo \"UPDATE mysql.user SET Password=PASSWORD('" + ga_sqlbackuppwd + "') WHERE User='gabackup';\" | mysql -u root" + ga_setuplogredirect)
    os.system("echo \"FLUSH PRIVILEGES\" | mysql -u root" + ga_setuplogredirect)
    os.system("mysql_secure_installation" + ga_setuplogredirect)
    os.system("cp /tmp/controller/setup/server/ga.mysqldump.cnf /etc/mysql/conf.d/ && "
              "chmod 600 /etc/mysql/conf.d/ga.mysqldump.cnf" + ga_setuplogredirect)
    os.system("echo '\npassword=" + ga_sqlbackuppwd + "' >> /etc/mysql/conf.d/ga.mysqldump.cnf" + ga_setuplogredirect)


ga_shelloutputheader("Setup finished! Please reboot the system.")
#delete old fstab entries and replace them (ask user)
#systemd timer setup for agentdata and serverbackup
    #ga service check for python path /usr/bin/python3 and growautomation root -> change execstart execstop etc
    #add [Unit]After=mysqld.service to service if standalone installation
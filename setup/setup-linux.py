#!/bin/python
import os
import getpass
from datetime import datetime
import random
import string

# basic vars
ga_version = "0.2.1.2"
ga_versionfile = "/etc/growautomation.version"
ga_setuplog = "/var/log/growautomation-setup.log"
ga_setuplogredirect = " 2>&1 | tee -a " + ga_setuplog


# shell output
def ga_shelloutputheader(output):
    shellhight, shellwidth = os.popen('stty size', 'r').read().split()
    print("\n")
    print('#' * (int(shellwidth) - 1))
    print("\n" + output + "\n")
    print('#' * (int(shellwidth) - 1))
    print("\n")


def ga_setuplogfile(output):
    tmplog = open(ga_setuplog, "a")
    tmplog.write("\n------------------------------------------\n" + output + "\n")


def ga_setuplogfileplain(output):
    tmplog = open(ga_setuplog, "a")
    tmplog.write(output + "\n")


def ga_pwdgen(stringLength):
    chars = string.ascii_letters + string.digits + "!#-_"
    return ''.join(random.choice(chars) for i in range(stringLength))


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


def yesno(prompt):
    while True:
        try:
            return {"true": True, "false": False}[input(prompt).lower()]
        except KeyError:
            print("Invalid input please enter True or False!")


# prechecks
ga_setuplogfile(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# check for root privileges
if os.getuid() != 0:
    raise SystemExit("This script needs to be run with root privileges!")
else:
    ga_shelloutputheader("Starting Growautomation installation script.\n"
                             "The newest versions can be found at: https://git.growautomation.at")

# check if growautomation is already installed
if os.path.exists(ga_versionfile) is True:
    tmpfile = open(ga_versionfile)
    tmplines = tmpfile.readlines()
    for line in tmplines:
        if line.find("gaversion=") != -1:
            print("A version of growautomation is/was already installed on this system!\n\n"
                  "Installed version: " + line[11:] +
                  "\nReplace version: " + ga_version)
            ga_versionreplace = (yesno("Do you want to replace it? (Poss: true,false - Default: false)\n") or False)
#            if ga_versionreplace is True:
#                ga_versionreplaceconfig = str(input("Do you want to keep your old configuration? "
#                                                    "(Poss: yes,no - Default: no)\n").lower()or "no")
            if ga_versionreplace is True:
                ga_versionreplacebackup = (yesno("Do you want to backup your old growautomation installation? "
                                                 "(Poss: true,false - Default: true)\n") or True)
            elif ga_versionreplace is False:
                raise SystemExit("Stopping installation script!")
            if line.find("garoot=") != -1 and ga_versionreplace is True:
                ga_versionoldpath = line[8:]
        else:
            ga_versionreplace = False

# setup vars
ga_sqlbackuppwd = ga_pwdgen(20)
# getting user inputs
ga_setuptype = str(input("Setup as growautomation standalone, agent or server? "
                         "(Poss: agent,standalone,server - Default: standalone)\n").lower() or "standalone")

ga_internalca = (yesno("Need to import internal ca? Mainly needed if your firewall uses ssl inspection.\n"
                       "(Poss: true,false - Default: false)\n") or False)
if ga_internalca is True:
    ga_internalcapath = str(input("Provide path to the ca file. "
                                  "(Poss: 'certpath',exit - Default: /etc/ssl/certs/internalca.cer)\n") or "/etc/ssl/certs/internalca.cer")

ga_linuxupgrade = (yesno("Want to upgrade your software and distribution before growautomation installation? "
                         "(Poss: true,false - Default: true)\n") or True)
if ga_versionreplace is True:
    ga_rootpath = str(input("Want to choose a custom install path? "
                            "(Default: " + ga_versionoldpath + ")\n").lower() or ga_versionoldpath)
else:
    ga_rootpath = str(input("Want to choose a custom install path? "
                            "(Default: /etc/growautomation)\n").lower() or "/etc/growautomation")
ga_backup = (yesno("Want to enable backup? "
                   "(Poss: true,false - Default: true)\n") or True)
if ga_backup is True:

    ga_backuppath = str(input("Want to choose a custom backup path? "
                              "(Default: /mnt/growautomation/backup/)\n").lower() or "/mnt/growautomation/backup/")
    ga_backupmnt = (yesno("Want to mount remote share as backup destination? Smb and nfs available. "
                          "(Poss: true,false - Default: true)\n") or True)
    if ga_backupmnt is True:
        ga_fstabcheck()
        ga_backupmnttype = str(input("Mount nfs or smb/cifs share as backup destination? "
                                     "(Poss: nfs,cifs - Default: nfs)\n").lower() or "nfs")
        ga_backupmntserver = str(input("Provide the server ip. "
                                       "(Default: 192.168.0.201)\n").lower() or "192.168.0.201")
        ga_backupmntshare = str(input("Provide the share name. "
                                      "(Default: growautomation/backup)\n").lower() or "growautomation/backup")
        if ga_backupmnttype == "cifs":
            ga_backupmnttmppwd = ga_pwdgen(20)
            ga_backupmntusr = str(input("Provide username for share authentication. "
                                        "(Default: gabackup)\n").lower() or "gabackup")
            ga_backupmntpwd = getpass.getpass(prompt="Provide password for share authentication. "
                                                     "(Default: " + ga_backupmnttmppwd + ")\n") or ga_backupmnttmppwd
            ga_backupmntdom = str(input("Provide domain for share authentication. "
                                        "(Default: workgroup)\n").lower() or "workgroup")
        else:
            print("Not mounting remote share for backup!\nCause: No sharetype, serverip or sharename provided.\n")
else:
    ga_backupmnt = False
    ga_backupmnttype = "none"

ga_logpath = str(input("Want to choose a custom log path? "
                       "(Default: /var/log/growautomation)\n").lower() or "/var/log/growautomation")
ga_logmnt = (yesno("Want to mount remote share as log destination? Smb and nfs available. "
                   "(Poss: true,false - Default: false)\n") or False)
if ga_logmnt is True:
    ga_fstabcheck()
    if ga_backupmnt is True:
        ga_samemount = (yesno("Use same server as for remote backup? "
                              "(Poss: true,false - Default: true)\n") or True)
        if ga_samemount is True:
            ga_logmnttype = ga_backupmnttype
            ga_logmntserver = ga_backupmntserver
    else:
        ga_logmnttype = str(input("Mount nfs or smb/cifs share as log destination? "
                                  "(Poss: nfs,cifs - Default: nfs)\n").lower() or "nfs")
        ga_logmntserver = str(input("Provide the server ip. "
                                    "(Default: 192.168.0.201)\n").lower() or "192.168.0.201")
    ga_logmntshare = str(input("Provide the share name. "
                               "(Default: growautomation/log)\n").lower() or "growautomation/log")

    if ga_logmnttype == "cifs":
        ga_logmnttmppwd = ga_pwdgen(20)
        if ga_backupmnt is True and ga_backupmnttype == "cifs" and ga_samemount is True:
            ga_samemountcreds = (yesno("Use same share credentials as for remote backup? "
                                       "(Poss: true,false - Default: true)\n") or True)
            if ga_samemountcreds is True:
                ga_logmntusr = ga_backupmntusr
                ga_logmntpwd = ga_backupmntpwd
                ga_logmntdom = ga_backupmntdom
            else:
                ga_logmntusr = str(input("Provide username for share authentication. "
                                         "(Default: galog)\n").lower() or "gabackup")
                ga_logmntpwd = getpass.getpass(prompt="Provide password for share authentication. "
                                                      "(Default: " + ga_logmnttmppwd + ")\n") or ga_logmnttmppwd
                ga_logmntdom = str(input("Provide domain for share authentication. "
                                         "(Default: workgroup)\n").lower() or "workgroup")
        else:
            ga_logmntusr = str(input("Provide username for share authentication. "
                                     "(Default: galog)\n").lower() or "gabackup")
            ga_logmntpwd = getpass.getpass(prompt="Provide password for share authentication. "
                                                  "(Default: " + ga_logmnttmppwd + ")\n") or ga_logmnttmppwd
            ga_logmntdom = str(input("Provide domain for share authentication. "
                                     "(Default: workgroup)\n").lower() or "workgroup")
else:
    ga_logmnttype = "none"  # for nfs/cifs apt installation

ga_setuplogfile("Setup information received:\n")
ga_setuplogfileplain("Basic vars: setuptype %r, internalca %r, garootpath %r,backup %r\n"), (ga_setuptype, ga_internalca, ga_rootpath, ga_backup)
if ga_backup is True:
    ga_setuplogfileplain("Backup vars: backuppath " + ga_backuppath + ", backupmnt %r\n"), (ga_backupmnt)
    if ga_backupmnt is True:
        ga_setuplogfileplain(
            "backupmnttype " + ga_backupmnttype + ", backupserver " + ga_backupmntserver + ", backupshare " + ga_backupmntshare + "\n"), ()
        if ga_backupmnttype == "cifs":
            ga_setuplogfileplain("backupmntusr " + ga_backupmntusr + ", backupmntdom " + ga_backupmntdom + "\n")
ga_setuplogfileplain("Log vars: logpath " + ga_logpath + ", logmnt %r\n"), (ga_logmnt)
if ga_logmnt is True:
    ga_setuplogfileplain(
        "logmnttype " + ga_logmnttype + ", logserver " + ga_logmntserver + ", logshare " + ga_logmntshare + "\n")
    if ga_logmnttype == "cifs":
        ga_setuplogfileplain("logmntusr " + ga_logmntusr + ", logmntdom " + ga_logmntdom + "\n")

ga_shelloutputheader("Thank you for providing the setup informaiton.\nThe installation will start now.")

# software
ga_setuplogfile("Starting installation.")

print("Installing software packages\n")
os.system("apt-get update" + ga_setuplogredirect)
if ga_linuxupgrade is True:
    os.system("apt-get -y dist-upgrade && apt-get -y upgrade" + ga_setuplogredirect)

os.system("apt-get -y install python3 mariadb-server git" + ga_setuplogredirect)

if ga_setuptype == "agent" or ga_setuptype == "standalone":
    os.system("apt-get -y install python3 python3-pip python3-dev python-smbus git" + ga_setuplogredirect)
    if ga_internalca is True:
        os.system("git main --global http.sslCAInfo " + ga_internalcapath +
                  " && python3 -m pip main set global.cert " + ga_internalcapath + ga_setuplogredirect)
    print("Installing python packages\n")
    os.system(
        "python3 -m pip install mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay --default-timeout=100" + ga_setuplogredirect)

if (ga_backupmnt or ga_logmnt) is True:
    if ga_backupmnttype == "nfs" or ga_logmnttype == "nfs":
        os.system("apt-get -y install nfs-common" + ga_setuplogredirect)
    elif ga_backupmnttype == "cifs" or ga_logmnttype == "cifs":
        os.system("apt-get -y install cifs-utils" + ga_setuplogredirect)

# folders
# Create folders
ga_shelloutputheader("Setting up directories")
ga_setuplogfile("Setting up directories")
os.system("useradd growautomation" + ga_setuplogredirect)
os.system(
    "mkdir -p " + ga_backuppath + " && chown -R growautomation:growautomation " + ga_backuppath + ga_setuplogredirect)
if ga_versionreplace is True:
    os.system(
        "echo 'gaversion=" + ga_version + "\ngaroot=" + ga_rootpath + "\n' > " + ga_versionfile + ga_setuplogredirect)
    if ga_versionreplacebackup is True:
        ga_versionoldbackup = ga_backuppath + "/install"
        os.system(
            "mkdir " + ga_versionoldbackup + " && cp -r " + ga_versionoldpath + " " + ga_versionoldbackup + ga_setuplogredirect)
os.system("mkdir -p " + ga_rootpath + " && chown -R growautomation:growautomation " + ga_rootpath + ga_setuplogredirect)
os.system("mkdir -p " + ga_logpath + " && chown -R growautomation:growautomation " + ga_logpath + ga_setuplogredirect)


def mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
    ga_shelloutputheader("Mounting " + mname + " share")
    ga_setuplogfile("Mounting " + mname + " share")
    if mtype == "cifs":
        mcreds = "username=" + muser + ",password=" + mpwd + ",domain=" + mdom
    else:
        mcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write("#Growautomation " + mname + " mount\n"
                                                "//" + msrv + "/" + mshr + " " + mpath + " " +
                   mtype + " " + mcreds + " 0 0\n\n")
    ga_fstab.close()
    os.system("mount -a" + ga_setuplogredirect)

    # setting up growautomation code


ga_shelloutputheader("Setting up growautomation code")
ga_setuplogfile("Setting up growautomation code")
os.system("cd /tmp && git clone https://github.com/growautomation-at/controller.git" + ga_setuplogredirect)
os.system("cp -r /tmp/controller/code/agent/* " + ga_rootpath +
          " && PYVER=$(python3 --version | cut -c8-10) && ln -s /etc/growautomation/main "
          "/usr/local/lib/python$PYVER/dist-packages/GA" + ga_setuplogredirect)


def dbsrv():
    os.system("mysql -u root < /tmp/controller/setup/server/ga-databases.sql" + ga_setuplogredirect)


def dbag():
    os.system("mysql -u root < /tmp/controller/setup/agent/ga-databases.sql" + ga_setuplogredirect)


def dball():
    os.system(
        "echo \"UPDATE mysql.user SET Password=PASSWORD('" + ga_sqlbackuppwd + "') WHERE User='gabackup';\" | mysql -u root" + ga_setuplogredirect)
    os.system("echo \"FLUSH PRIVILEGES\" | mysql -u root" + ga_setuplogredirect)
    ga_shelloutputheader("Setting up database.\nSet a secure password and answer all other questions with Y/yes.")
    ga_setuplogfile("Setting up database.")
    os.system("mysql_secure_installation" + ga_setuplogredirect)
    os.system("cp /tmp/controller/setup/server/ga.mysqldump.cnf /etc/mysql/conf.d/ && "
              "chmod 600 /etc/mysql/conf.d/ga.mysqldump.cnf" + ga_setuplogredirect)
    os.system("echo '\npassword=" + ga_sqlbackuppwd + "' >> /etc/mysql/conf.d/ga.mysqldump.cnf" + ga_setuplogredirect)


########################################################################################################################

if ga_backupmnt is True:
    mounts("backup", ga_backupmntusr, ga_backupmntpwd, ga_backupmntdom, ga_backupmntserver, ga_backupmntshare,
           ga_backuppath, ga_backupmnttype)
if ga_logmnt is True:
    mounts("log", ga_logmntusr, ga_logmntpwd, ga_logmntdom, ga_logmntserver, ga_logmntshare, ga_logpath, ga_logmnttype)

if ga_setuptype == "server" or "standalone":
    dbsrv()

elif ga_setuptype == "agent":
    dbag()

dball()

ga_shelloutputheader("Setup finished! Please reboot the system.")
# delete old fstab entries and replace them (ask user)
# systemd timer setup for agentdata and serverbackup
# ga service check for python path /usr/bin/python3 and growautomation root -> change execstart execstop etc
# add [Unit]After=mysqld.service to service if standalone installation
# write setup config to sql server
# populate db.conf with credentials
# set db creds for db.conf dynamically
# add script to add users to db (prompt for pwd and username -> set db privileges)
# get server db infos if agent setup
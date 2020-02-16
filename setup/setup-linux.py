#!/usr/bin/python
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


import os
import getpass
from datetime import datetime
import random
import string

# basic vars
ga_version = "0.2.1.2"
ga_versionfile = "/etc/growautomation.version"
ga_setuplog = "/var/log/growautomation-setup.log"
ga_setuplogredirect = "2>&1 | tee -a %s" % ga_setuplog

########################################################################################################################

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
    tmplog.close()


def ga_setuplogfileplain(output):
    tmplog = open(ga_setuplog, "a")
    tmplog.write(output + "\n")
    tmplog.close()


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


def ga_input(prompt, default, poss="", intype=""):
    if type(default) == bool or (type(default) == str and (default == "yes" or default == "no")):
        while True:
            try:
                return {"true": True, "false": False, "yes": True, "no": False, "t": True, "f": False,
                        "": default}[input(prompt).lower()]
            except KeyError:
                print("Invalid input please enter True or False!")
    elif type(default) == str:
        if intype == "pass":
            getpass.getpass(prompt="%s (Random: %s)\n" % (prompt, default)) or "%s" % default
        elif intype == "passgen":
            while tmpinput < 8 or tmpinput > 99:
                if tmpinput < 8 or tmpinput > 99:
                    print("Input error. Value should be between 8 and 99.")
                tmpinputstr = input("%s (Poss: %s - Default: %s)\n" % (prompt, poss, default)).lower() or "%s" % default
                tmpinput = int(tmpinputstr)
            return tmpinput
        elif poss != "":
            return str(input("%s (Poss: %s - Default: %s)\n").lower() or "%s") % (prompt, poss, default, default)
        else:
            return str(input("%s (Default: %s)\n").lower() or "%s") % (prompt, default, default)


def ga_mountcreds(outtype, inputstr=""):
    if outtype == "usr":
        return ga_input("Provide username for share authentication.", inputstr)
    elif outtype == "pwd":
        return ga_input("Provide password for share authentication.", inputstr, intype="pass")
    elif outtype == "dom":
        return ga_input("Provide domain for share authentication.", "workgroup")

########################################################################################################################

# prechecks
ga_setuplogfile(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# check for root privileges
if os.getuid() != 0:
    raise SystemExit("This script needs to be run with root privileges!")
else:
    ga_shelloutputheader("Starting Growautomation installation script.\n"
                         "The newest versions can be found at: https://git.growautomation.at\n\n")
    ga_setupwarning = ga_input("WARNING!\nWe recommend using this installation script on dedicated systems.\n"
                               "This installation script won't check your already installed programs for compatibility "
                               "problems.\nIf you already use web-/database or other complex software on this system "
                               "you should back it up before installing this software.\nWe assume no liability for "
                               "problems that may be caused by this installation!\nPress y/yes if you want to "
                               "continue.", "no", "yes/no")
    if ga_setupwarning is False:
        print("You can also install this software manually through the setup manual.\n"
              "It can be found at: https://git.growautomation.at/tree/master/manual\n\n")
        raise SystemExit("Stopped growautomation installation.")

# check if growautomation is already installed
if os.path.exists(ga_versionfile) is True:
    tmpfile = open(ga_versionfile)
    tmplines = tmpfile.readlines()
    for line in tmplines:
        if line.find("gaversion=") != -1:
            print("A version of growautomation is/was already installed on this system!\n\n"
                  "Installed version: " + line[11:] +
                  "\nReplace version: %s" % ga_version)
            ga_versionreplace = ga_input("Do you want to replace it? (Poss: true,false", False)
#            if ga_versionreplace is True:
#                ga_versionreplaceconfig = str(input("Do you want to keep your old configuration? "
#                                                    "(Poss: yes,no - Default: no)\n").lower()or "no")
            if ga_versionreplace is True:
                ga_versionreplacebackup = ga_input("Do you want to backup your old growautomation installation?"
                                                   " (Poss: true,false -", True)
            elif ga_versionreplace is False:
                raise SystemExit("Stopping installation script!")
            if line.find("garoot=") != -1 and ga_versionreplace is True:
                ga_versionoldpath = line[8:]
        else:
            ga_versionreplace = False

########################################################################################################################

# setup vars
ga_setuppwdlength = ga_input("This setup will generate random passwords for you.\nPlease define the length of these random passwords!", "12", "8-99", "passgen")
ga_sqlrootpwd = ga_pwdgen(ga_setuppwdlength)
ga_sqlbackuppwd = ga_pwdgen(ga_setuppwdlength)
# getting user inputs
ga_setuptype = ga_input("Setup as growautomation standalone, agent or server? (Poss: agent,standalone,server -",
                        "standalone")

if ga_setuptype == "agent":
    ga_setup_yousure = ga_input("You should install the growautomation server component before installing the agent.\n"
          "Proceed with 'yes' if you have already installed the ga server or type 'no' to stop the installation.", False, "yes/no")
    if ga_setup_yousure is False:
        raise SystemExit("Stopped growautomation agent installation.")

ga_internalca = ga_input("Need to import internal ca? Mainly needed if your firewall uses ssl inspection.\n",
                         False, "true/false")
if ga_internalca is True:
    ga_internalcapath = ga_input("Provide path to the ca file.", "/etc/ssl/certs/internalca.cer")

ga_linuxupgrade = ga_input("Want to upgrade your software and distribution before growautomation installation?",
                           True, "true/false")
if ga_versionreplace is True:
    ga_rootpath = ga_input("Want to choose a custom install path?", ga_versionoldpath)
else:
    ga_rootpath = ga_input("Want to choose a custom install path?", "/etc/growautomation")
ga_backup = ga_input("Want to enable backup?", True, "true,false")


if ga_backup is True:
    ga_backuppath = ga_input("Want to choose a custom backup path? (", "/mnt/growautomation/backup/")
    ga_backupmnt = ga_input("Want to mount remote share as backup destination? Smb and nfs available.",
                            True, "true/false")
    if ga_backupmnt is True:
        ga_fstabcheck()
        ga_backupmnttype = ga_input("Mount nfs or smb/cifs share as backup destination?", "nfs", "nfs/cifs")
        ga_backupmntserver = ga_input("Provide the server ip.", "192.168.0.201")
        ga_backupmntshare = ga_input("Provide the share name.", "growautomation/backup")
        if ga_backupmnttype == "cifs":
            ga_backupmnttmppwd = ga_pwdgen(ga_setuppwdlength)
            ga_backupmntusr = ga_mountcreds("usr", "gabackup")
            ga_backupmntpwd = ga_mountcreds("pwd", ga_backupmnttmppwd)
            ga_backupmntdom = ga_mountcreds("dom")
        else:
            print("Not mounting remote share for backup!\nCause: No sharetype, serverip or sharename provided.\n")
else:
    ga_backupmnt = False
    ga_backupmnttype = "none"

ga_logpath = ga_input("Want to choose a custom log path?", "/var/log/growautomation")
ga_logmnt = ga_input("Want to mount remote share as log destination? Smb and nfs available.", False, "true/false")
if ga_logmnt is True:
    ga_fstabcheck()
    if ga_backupmnt is True:
        ga_samemount = ga_input("Use same server as for remote backup?", True, "true/false")
        if ga_samemount is True:
            ga_logmnttype = ga_backupmnttype
            ga_logmntserver = ga_backupmntserver
    else:
        ga_logmnttype = ga_input("Mount nfs or smb/cifs share as log destination?", "nfs", "nfs/cifs")
        ga_logmntserver = ga_input("Provide the server ip.", "192.168.0.201")
    ga_logmntshare = ga_input("Provide the share name.", "growautomation/log")

    if ga_logmnttype == "cifs":
        ga_logmnttmppwd = ga_pwdgen(ga_setuppwdlength)
        if ga_backupmnt is True and ga_backupmnttype == "cifs" and ga_samemount is True:
            ga_samemountcreds = ga_input("Use same share credentials as for remote backup?", True, "true/false")
            if ga_samemountcreds is True:
                ga_logmntusr = ga_backupmntusr
                ga_logmntpwd = ga_backupmntpwd
                ga_logmntdom = ga_backupmntdom
            else:
                ga_backupmntusr = ga_mountcreds("usr", "galog")
                ga_backupmntpwd = ga_mountcreds("pwd", ga_logmnttmppwd)
                ga_backupmntdom = ga_mountcreds("dom")
        else:
            ga_backupmntusr = ga_mountcreds("usr", "galog")
            ga_backupmntpwd = ga_mountcreds("pwd", ga_logmnttmppwd)
            ga_backupmntdom = ga_mountcreds("dom")
else:
    ga_logmnttype = "none"  # for nfs/cifs apt installation

if ga_setuptype == "agent":
    ga_sqlagentpwd = ga_pwdgen(ga_setuppwdlength)
    ga_serverip = ga_input("Provide the ip address of the growautomation server.", "192.168.0.201")
    ga_serversqlport = ga_input("Provide the mysql port of the growautomation server.", "3306")
    ga_serversqlusr = ga_input("Please provide the user used to connect to the database.", "gacon01")
    ga_serversqlpwd = ga_input("Please provide the password used to connect to the database.", ga_sqlagentpwd, intype="pass")

########################################################################################################################

ga_setuplogfile("Setup information received:\n")
ga_setuplogfileplain("Basic vars: setuptype %r, internalca %r, garootpath %r,backup %r\n"
                     % (ga_setuptype, ga_internalca, ga_rootpath, ga_backup))
if ga_backup is True:
    ga_setuplogfileplain("Backup vars: backuppath %s, backupmnt %r\n" % (ga_backuppath, ga_backupmnt))
    if ga_backupmnt is True:
        ga_setuplogfileplain(
            "backupmnttype %s, backupserver %s, backupshare %s\n"
            % (ga_backupmnttype, ga_backupmntserver, ga_backupmntshare))
        if ga_backupmnttype == "cifs":
            ga_setuplogfileplain("backupmntusr %s, backupmntdom %s\n" % (ga_backupmntusr, ga_backupmntdom))
ga_setuplogfileplain("Log vars: logpath %s, logmnt %r\n" % (ga_logpath, ga_logmnt))
if ga_logmnt is True:
    ga_setuplogfileplain(
        "logmnttype %s, logserver %s, logshare %s\n" % (ga_logmnttype, ga_logmntserver, ga_logmntshare))
    if ga_logmnttype == "cifs":
        ga_setuplogfileplain("logmntusr %s, logmntdom %s\n" % (ga_logmntusr, ga_logmntdom))

ga_shelloutputheader("Thank you for providing the setup information.\nThe installation will start now.")

########################################################################################################################

# software
ga_setuplogfile("Starting installation.")

print("Installing software packages\n")
os.system("apt-get update" + ga_setuplogredirect)
if ga_linuxupgrade is True:
    os.system("apt-get -y dist-upgrade && apt-get -y upgrade %s" % ga_setuplogredirect)

os.system("apt-get -y install python3 mariadb-server git %s" % ga_setuplogredirect)

if ga_setuptype == "agent" or ga_setuptype == "standalone":
    os.system("apt-get -y install python3 python3-pip python3-dev python-smbus git %s" % ga_setuplogredirect)
    if ga_internalca is True:
        os.system("git main --global http.sslCAInfo %s && python3 -m pip main set global.cert %s %s"
                  % (ga_internalcapath, ga_internalcapath, ga_setuplogredirect))
    print("Installing python packages\n")
    os.system("python3 -m pip install "
              "mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay "
              "--default-timeout=100 %s" % ga_setuplogredirect)

if (ga_backupmnt or ga_logmnt) is True:
    if ga_backupmnttype == "nfs" or ga_logmnttype == "nfs":
        os.system("apt-get -y install nfs-common %s" % ga_setuplogredirect)
    elif ga_backupmnttype == "cifs" or ga_logmnttype == "cifs":
        os.system("apt-get -y install cifs-utils %s" % ga_setuplogredirect)

# folders
# Create folders
ga_shelloutputheader("Setting up directories")
ga_setuplogfile("Setting up directories")
os.system("useradd growautomation %s" % ga_setuplogredirect)


def ga_foldercreate(tmppath):
    os.system("mkdir -p %s && chown -R growautomation:growautomation %s %s" % (tmppath, tmppath, ga_setuplogredirect))
    

ga_foldercreate(ga_backuppath)
if ga_versionreplace is True:
    if ga_versionreplacebackup is False: 
        os.system("mv %s /tmp" % ga_versionoldpath)
    else:
        ga_versionoldbackup = ga_backuppath + "/install"
        os.system("mkdir -p %s && mv %s %s %s" 
                  % (ga_versionoldbackup, ga_versionoldpath, ga_versionoldbackup, ga_setuplogredirect))
        os.system("mv %s %s" % (ga_versionfile, ga_versionoldbackup))
    tmpfile = open(ga_versionfile, 'w')
    tmpfile.write("gaversion=%s\ngaroot=%s\n" % (ga_version, ga_rootpath))
    tmpfile.close()
ga_foldercreate(ga_rootpath)
ga_foldercreate(ga_logpath)


def ga_mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
    ga_shelloutputheader("Mounting %s share" % mname)
    ga_setuplogfile("Mounting %s share" % mname)
    if mtype == "cifs":
        mcreds = "username=%s,password=%s,domain=%s" % (muser, mpwd, mdom)
    else:
        mcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write("#Growautomation %s mount\n//%s/%s %s %s %s 0 0\n\n" % (mname, msrv, mshr, mpath, mtype, mcreds))
    ga_fstab.close()
    os.system("mount -a %s" % ga_setuplogredirect)

    # setting up growautomation code


ga_shelloutputheader("Setting up growautomation code")
ga_setuplogfile("Setting up growautomation code")
os.system("cd /tmp && git clone https://github.com/growautomation-at/controller.git %s" % ga_setuplogredirect)
os.system("cp -r /tmp/controller/code/agent/* %s && PYVER=$(python3 --version | "
          "cut -c8-10) && ln -s /etc/growautomation/main /usr/local/lib/python$PYVER/dist-packages/GA %s" 
          % (ga_rootpath, ga_setuplogredirect))


def ga_dball():
    os.system("echo \"UPDATE mysql.user SET Password=PASSWORD('%s') WHERE User='gabackup';\" | mysql -u root %s"
              % (ga_sqlbackuppwd, ga_setuplogredirect))
    os.system("echo \"FLUSH PRIVILEGES\" | mysql -u root %s" % ga_setuplogredirect)
    ga_shelloutputheader("Set a secure password and answer all other questions with Y/yes.")
    ga_shelloutputheader("Example random password: %s\nMySql will not ask for the password if you start it (mysql -u root) locally"
                         " with sudo/root privileges. (set & forget)" % ga_sqlrootpwd)
    ga_setuplogfile("Setting up database.")
    os.system("mysql_secure_installation %s" % ga_setuplogredirect)
    tmpfile = open("/etc/mysql/conf.d/ga.mysqldump.cnf", 'a')
    tmpfile.write("[mysqldump]\nuser=gabackup\npassword=%s" % ga_sqlbackuppwd)
    tmpfile.close()

def ga_dbsrv():
    os.system("mysql -u root < /tmp/controller/setup/server/ga_db_setup.sql %s" % ga_setuplogredirect)


def ga_dbag():
    os.system("mysql -u root < /tmp/controller/setup/agent/ga_db_setup.sql %s" % ga_setuplogredirect)


def ga_dbsrv_addag():



########################################################################################################################


if ga_backupmnt is True:
    ga_mounts("backup", ga_backupmntusr, ga_backupmntpwd, ga_backupmntdom, ga_backupmntserver, ga_backupmntshare, 
              ga_backuppath, ga_backupmnttype)
if ga_logmnt is True:
    ga_mounts("log", ga_logmntusr, ga_logmntpwd, ga_logmntdom, ga_logmntserver, ga_logmntshare, ga_logpath, 
              ga_logmnttype)

ga_dball()

if ga_setuptype == "server" or "standalone":
    ga_dbsrv()

elif ga_setuptype == "agent":
    ga_dbag()



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
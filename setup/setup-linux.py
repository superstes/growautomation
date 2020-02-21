#!/usr/bin/python3
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

########################################################################################################################

# basic vars
ga_version = "0.2.1.2"
ga_version_file = "/etc/growautomation.version"
ga_setup_log = "/var/log/growautomation-setup.log"
ga_setup_log_redirect = "2>&1 | tee -a %s" % ga_setup_log

import os
from datetime import datetime
import getpass
import random
import string


########################################################################################################################


# shell output
def ga_setup_shelloutput_header(output):
    shellhight, shellwidth = os.popen('stty size', 'r').read().split()
    print("\n")
    print('#' * (int(shellwidth) - 1))
    print("\n" + output + "\n")
    print('#' * (int(shellwidth) - 1))
    print("\n")


def ga_setup_shelloutput_text(output):
    print("%s.\n" % output)
    ga_setup_log_write(output)


def ga_setup_log_write(output):
    tmplog = open(ga_setup_log, "a")
    tmplog.write("\n------------------------------------------\n" + output + "\n")
    tmplog.close()


def ga_setup_log_writeplain(output):
    tmplog = open(ga_setup_log, "a")
    tmplog.write(output + "\n")
    tmplog.close()


def ga_setup_check_version_file():
    tmpfile = open(ga_version_file, 'r')
    return tmpfile.readlines()


def ga_setup_pwd_gen(stringlength):
    chars = string.ascii_letters + string.digits + "!#-_"
    return ''.join(random.choice(chars) for i in  range(stringlength))


def ga_setup_fstabcheck():
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


def ga_setup_input(prompt, default=" ", poss=" ", intype=" "):
    if type(default) == bool:
        while True:
            try:
                return {"true": True, "false": False, "yes": True, "no": False, "y": True, "n": False,
                        "": default}[input("\n%s (Poss: yes/true/no/false - Default: %s)\n > "
                                           % (prompt, default)).lower()]
            except KeyError:
                print("WARNING: Invalid input please enter True or False!\n")
    elif type(default) == str:
        if intype == "pass" and default != " ":
            getpass.getpass(prompt="\n%s (Random: %s)\n > " % (prompt, default)) or "%s" % default
        elif intype == "pass":
            getpass.getpass(prompt="\n%s\n > " % prompt)
        elif intype == "passgen":
            tmpinput = 0
            while tmpinput < 8 or tmpinput > 99:
                if tmpinput < 8 or tmpinput > 99:
                    print("Input error. Value should be between 8 and 99.\n")
                tmpinputstr = str(input("\n%s (Poss: %s - Default: %s)\n > " % (prompt, poss, default)).lower()
                                  or "%s" % default)
                tmpinput = int(tmpinputstr)
            return tmpinput
        elif poss != " ":
            return str(input("\n%s (Poss: %s - Default: %s)\n > " % (prompt, poss, default)).lower() or "%s" % default)
        elif default != " ":
            return str(input("\n%s (Default: %s)\n > " % (prompt, default)).lower() or "%s" % default)
        else:
            return str(input("\n%s\n > " % prompt).lower())


def ga_mnt_creds(outtype, inputstr=""):
    if outtype == "usr":
        return ga_setup_input("Provide username for share authentication.", inputstr)
    elif outtype == "pwd":
        return ga_setup_input("Provide password for share authentication.", inputstr, intype="pass")
    elif outtype == "dom":
        return ga_setup_input("Provide domain for share authentication.", "workgroup")


def ga_mysql(dbuser, command, dbserver="", dbpwd=""):
    db = mysql.connector.connect(host=dbserver, user=dbuser, passwd=dbpwd, database="ga")
    dbcursor = db.cursor()
    dbcursor.execute(command)
    tmpvar = dbcursor.fetchall()
    dbcursor.close()
    db.close()
    return tmpvar


def ga_setup_varcheck(tmpvar, error):
    try:
        tmpvar
        return True
    except NameError:
        ga_setup_shelloutput_text("WARNING! %s" %error)
        return False


def ga_setup_configparser_mysql(user, pwd, table, name, server="", agent=""):
    if type(name) == list:
        if table == "agent":
            itemdatadict = {}
            for item in name:
                try:
                    data = ga_mysql(user, "FROM ga.AgentConfig SELECT data WHERE name = %s and agent = %s"
                                    % (item, agent), server, pwd)
                    itemdatadict[item] = data
                except mysql.connector.Error as error:
                    ga_setup_shelloutput_text("Error when retrieving config item %s from database:\n%s" % (item, error))
            return itemdatadict
        elif table == "server":
            itemdatadict = {}
            for item in name:
                try:
                    data = ga_mysql(user, "FROM ga.ServerConfig SELECT data WHERE name = %s" % item, server, pwd)
                    itemdatadict[item] = data
                except mysql.connector.Error as error:
                    ga_setup_shelloutput_text("Error when retrieving config item %s from database:\n%s" % (item, error))
            return itemdatadict
    elif type(name) == str:
        if table == "agent":
            try:
                data = ga_mysql(user, "FROM ga.AgentConfig SELECT data WHERE name = %s and agent = %s"
                                % (name, agent), server, pwd)
                return data
            except mysql.connector.Error as error:
                ga_setup_shelloutput_text("Error when retrieving config item %s from database:\n%s" % (name, error))
        elif table == "server":
            try:
                data = ga_mysql(user, "FROM ga.ServerConfig SELECT data WHERE name = %s" % name, server, pwd)
                return data
            except mysql.connector.Error as error:
                ga_setup_shelloutput_text("Error when retrieving config item %s from database:\n%s" % (name, error))

# def ga_setup_configparser_file(file, header, text, cuttext, count=4):
#     tmpfile = open(file)
#     tmpcount = 0
#     for line in tmpfile.readlines():
#         if line.find(header) != -1:
#             tmpcount = 1
#         if tmpcount > 0 and tmpcount < count:
#             if line.find(text) != -1:
#                 output = line[cuttext]
#         if tmpcount > 0:
#             tmpcount += 1
#     return output

def ga_setup_configparser_file(file, text):
    tmpfile = open(file)
    for line in tmpfile.readlines():
        if line.find(text) != -1:
            return line


def ga_setup_exit(shell, log):
    ga_setup_log_write("Exit. %s." % log)
    raise SystemExit("%s!\nYou can find the full setup log at %s." % (shell, ga_setup_log))


########################################################################################################################


ga_setup_log_write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# prechecks
ga_setup_shelloutput_header("Installing setup dependencies")

os.system("apt-get -y install python3-pip && python3 -m pip install mysql-connector-python %s" % ga_setup_log_redirect)
import mysql.connector


# check for root privileges
if os.getuid() != 0:
    ga_setup_exit("This script needs to be run with root privileges", "Script not started as root")

else:
    ga_setup_shelloutput_header("Starting Growautomation installation script\n"
                                "The newest versions can be found at: https://git.growautomation.at")
    ga_setupwarning = ga_setup_input("WARNING!\n\nWe recommend using this installation script on dedicated systems.\n"
                               "This installation script won't check your already installed programs for compatibility "
                               "problems.\nIf you already use web-/database or other complex software on this system "
                               "you should back it up before installing this software.\nWe assume no liability for "
                               "problems that may be caused by this installation!\nAccept the risk if you want to "
                               "continue.", False)
    if ga_setupwarning is False:
        ga_setup_exit("Script cancelled by user\nYou can also install this software manually through the setup manual.\n"
                     "It can be found at: https://git.growautomation.at/tree/master/manual",
                     "Setupwarning not accepted by user")

ga_setup_shelloutput_header("Checking if growautomation is already installed on the system.")

# check if growautomation is already installed
if os.path.exists(ga_version_file) is True or os.path.exists("/etc/growautomation") is True:
    ga_versionold = True
else:
    ga_versionold = False

if ga_versionold is True:
    for line in ga_setup_check_version_file():
        if line.find("gaversion=") != -1:
            print("A version of growautomation is/was already installed on this system!\n\n"
                  "Installed version: " + line[11:] +
                  "\nReplace version: %s" % ga_version)
            ga_versionold_replace = ga_setup_input("Do you want to replace it?", False)
            if ga_versionold_replace is True:
                ga_versionold_replace_migrate = ga_setup_input("Should we try to keep your old configuration and data?", False)
            if ga_versionold_replace is True:
                ga_versionold_replace_backup = ga_setup_input("Do you want to backup your old growautomation installation?", True)
            elif ga_versionold_replace is False:
                ga_setup_exit("Stopping script. Current installation should not be overwritten",
                             "Already installed ga should not be overwritten")
else:
    ga_setup_shelloutput_text("No previous growautomation installation found")

########################################################################################################################

# setup vars
ga_setup_shelloutput_header("Retrieving setup configuration through user input.")


def ga_config_var_base():
    ga_setup_type = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone",
                                   "agent/standalone/server")
    if ga_setup_type == "agent":
        ga_setup_yousure = ga_setup_input(
            "You should install/update the growautomation server component before the agent because of dependencies.\n"
            "Agree if you have already installed/updated the ga server or disagree to stop the "
            "installation.", False)
        # print("If you haven't created this agent on the server -> this is you last chance.\n"
        #       "Find more information about the creation of new agents at: "
        #       "https://git.growautomation.at/tree/master/manual/agent\n\n")
        if ga_setup_yousure is False:
            ga_setup_log_write("Exit. User has not installed the server before the agent.")
            raise SystemExit("Stopped growautomation agent installation.")
    ga_path_root = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation")
    if ga_setup_type == "agent":
        ga_config_name = ga_setup_input("Provide the name of this growautomation agent as configured on the server.",
                                        "gacon01")
    elif ga_setup_type == "server":
        ga_config_name = "gaserver"
    elif ga_setup_type == "standalone":
        ga_config_name = "gacon01"


def ga_config_var_setup():
    ga_setup_pwd_length = ga_setup_input("This setup will generate random passwords for you.\nPlease define the "
                                        "length of those random passwords!", "12", "8-99", "passgen")

    ga_setup_ca = ga_setup_input("Need to import internal ca for git/pip? Mainly needed if your firewall uses "
                                   "ssl inspection.\n", False)

    if ga_setup_ca is True:
        ga_setup_capath = ga_setup_input("Provide path to the ca file.", "/etc/ssl/certs/internalca.cer")

    ga_setup_linuxupgrade = ga_setup_input("Want to upgrade your software and distribution before growautomation "
                                     "installation?", True)


def ga_config_var_db():
    if ga_setup_type == "agent":
        while True:
            ga_sql_agent_pwd = ga_setup_pwd_gen(ga_setup_pwd_length)
            ga_sql_server_ip = ga_setup_input("Provide the ip address of the growautomation server.", "192.168.0.201")
            ga_serversqlport = ga_setup_input("Provide the mysql port of the growautomation server.", "3306")
            print("The following credentials can be found in the serverfile '$garoot/main/main.conf'\n")
            ga_sql_server_agent_usr = ga_setup_input("Please provide the user used to connect to the database.", ga_config_name)
            ga_sql_server_agent_pwd = ga_setup_input("Please provide the password used to connect to the database.",
                                                     ga_sql_agent_pwd, intype="pass")
            ga_sql_server_repl = ga_setup_input("Please provide sql replication user.", ga_config_name + "replica")
            ga_sql_server_replpwd = ga_setup_input("Please provide sql replication password.", ga_sql_server_agent_pwd)
            try:
                ga_mysql(ga_sql_server_agent_usr, "SELECT * FROM ga.AgentConfig ORDER BY A DESC LIMIT 10;",
                         ga_sql_server_ip, ga_sql_server_agent_pwd)
            except mysql.connector.Error as error:
                ga_setup_shelloutput_text("An error occoured when testing the sql connection:\n%s\n\n"
                                          "Try again." % error)
    elif ga_setup_type == "server" or ga_setup_type == "standalone":
        while True:
            a_sql_server_admin_usr = ga_setup_input("Please provide the user used to connect to the database.",
                                                    "gadmin")
            ga_sql_server_admin_pwd = ga_setup_input("Please provide the password used to connect to the database.",
                                                     intype="pass")
            try:
                ga_mysql(a_sql_server_admin_usr, "SELECT * FROM ga.AgentConfig ORDER BY A DESC LIMIT 10;",
                         dbpwd=ga_sql_server_admin_pwd)
            except mysql.connector.Error as error:
                ga_setup_shelloutput_text("An error occoured when testing the sql connection:\n%s\n\n"
                                          "Try again." % error)


def ga_config_var_certs():
    if ga_setup_type == "agent":
        ga_setup_shelloutput_text("The following certificates can be found in the serverpath '$garoot/ca/certs/'\n")
        ga_config_server_ca = ga_setup_input("Provide the path to the ca-certificate from your ga-server.",
                                             "%s/ssl/ca.cer.pem"
                                             % ga_path_root)
        ga_config_server_cert = ga_setup_input("Provide the path to the agent server certificate.", "%s/ssl/%s.cer.pem"
                                               % (ga_path_root, ga_config_name))
        ga_config_server_key = ga_setup_input("Provide the path to the agent server key.", "%s/ssl/%s.key.pem"
                                              % (ga_path_root, ga_config_name))

########################################################################################################################
# Config migration from old installation
if ga_versionold is True and ga_versionold_replace_migrate is True:
    for line in ga_setup_check_version_file():
        if line.find("garoot=") != -1:
            ga_path_root = line[8:]
        elif line.find("name=") != -1:
            ga_config_name = line[6:] 
        elif line.find("type=") != -1:
            ga_setup_type = line[6:]
    tmprootstate = ga_setup_varcheck(ga_path_root, "GA rootpath not found in old versionfile.")
    tmpnamestate = ga_setup_varcheck(ga_path_root, "GA agent name not found in old versionfile.")
    tmptypestate = ga_setup_varcheck(ga_path_root, "GA setup type not found in old versionfile.")
    if tmpnamestate is False or tmprootstate is False or tmptypestate is False:
        ga_setup_shelloutput_text("Old versionfile could not provide all needed data. Failing over to manual input.")
        ga_config_var_base()
    ga_config_var_setup()

    ga_setup_shelloutput_header("Checking for database credentials")
    if ga_setup_type == "server" or ga_setup_type == "standalone":
        ga_sql_server_admin_pwd = ga_setup_configparser_file("%s/main/main.conf" % ga_path_root, "serverpassword=")[10:]
        while True:
            try:
                ga_mysql("gadmin", "SELECT * FROM ga.AgentConfig ORDER BY A DESC LIMIT 10;", dbpwd=ga_sql_server_admin_pwd)
            except mysql.connector.Error as error:
                ga_setup_shelloutput_text("An error occoured when testing the sql connection:\n%s\n\n"
                                          "Automatic database configuration failed. Switching over to manual." % error)

            ga_config_var_db()

    elif ga_setup_type == "agent":
        ga_sql_server_agent_usr = ga_setup_configparser_file("%s/main/main.conf" % ga_path_root, "agentuser=")[10:]
        ga_sql_server_agent_pwd = ga_setup_configparser_file("%s/main/main.conf" % ga_path_root, "agentpassword=")[15:]
        ga_sql_server_ip = ga_setup_configparser_file("%s/main/main.conf" % ga_path_root, "serverip=")[10:]
        while True:
            try:
                ga_mysql(ga_sql_server_agent_usr, "SELECT * FROM ga.AgentConfig ORDER BY A DESC LIMIT 10;",
                         ga_sql_server_ip, ga_sql_server_agent_pwd)
            except mysql.connector.Error as error:
                ga_setup_shelloutput_text("An error occoured when testing the sql connection:\n%s\n\n"
                                          "Automatic database configuration failed. Switching over to manual." % error)
            ga_config_var_db()

    ga_setup_shelloutput_header("Retrieving existing configuration from database")
    ga_config_list_agent = ["path_root", "path_config", "path_sensors", "path_actions", "path_checks", "path_service",
                            "backup", "path_backup", "mnt_backup", "mnt_backup_type", "mnt_backup_server",
                            "mnt_backup_share", "mnt_backup_usr", "mnt_backup_pwd", "mnt_backup_dom", "path_log",
                            "mnt_log", "mnt_shared_creds", "mnt_shared_server", "mnt_shared_type", "mnt_log_type",
                            "mnt_log_server", "mnt_log_share", "mnt_log_usr", "mnt_log_pwd", "mnt_log_dom", "ga_ufw"]
    ga_config_list_server = []
    if ga_setup_type == "server":
        ga_setup_configparser_mysql(ga_sql_server_admin_usr, ga_sql_server_admin_pwd, "server", "ga_config_list_server")
    elif ga_setup_type == "standalone":
        ga_setup_configparser_mysql(ga_sql_server_admin_usr, ga_sql_server_admin_pwd, "agent", "ga_config_list_agent",
                                    agent=ga_config_name)
        ga_setup_configparser_mysql(ga_sql_server_admin_usr, ga_sql_server_admin_pwd, "server", "ga_config_list_server",
                                    agent=ga_config_name)
    elif ga_setup_type == "agent":
        ga_setup_configparser_mysql(ga_sql_server_admin_usr, ga_sql_server_admin_pwd, "agent", "ga_config_list_agent",
                                    ga_sql_server_ip, ga_config_name)

########################################################################################################################
# Configuration without migration
if ga_versionold is False:
    ga_config_var_base()
    ga_config_var_setup()
    
    ga_backup = ga_setup_input("Want to enable backup?", True)
    if ga_backup is True:
        ga_path_backup = ga_setup_input("Want to choose a custom backup path? (", "/mnt/growautomation/backup/")
        ga_mnt_backup = ga_setup_input("Want to mount remote share as backup destination? Smb and nfs available.",
                                True)
        if ga_mnt_backup is True:
            ga_setup_fstabcheck()
            ga_mnt_backup_type = ga_setup_input("Mount nfs or smb/cifs share as backup destination?", "nfs", "nfs/cifs")
            ga_mnt_backup_server = ga_setup_input("Provide the server ip.", "192.168.0.201")
            ga_mnt_backup_share = ga_setup_input("Provide the share name.", "growautomation/backup")
            if ga_mnt_backup_type == "cifs":
                ga_mnt_backup_tmppwd = ga_setup_pwd_gen(ga_setup_pwd_length)
                ga_mnt_backup_usr = ga_mnt_creds("usr", "gabackup")
                ga_mnt_backup_pwd = ga_mnt_creds("pwd", ga_mnt_backup_tmppwd)
                ga_mnt_backup_dom = ga_mnt_creds("dom")
            # else:
            #     ga_setup_shelloutput_text("Not mounting remote share for backup!\nCause: No sharetype, "
            #                               "serverip or sharename provided.\n")
    else:
        ga_mnt_backup = False
        ga_mnt_backup_type = "none"
    
    ga_path_log = ga_setup_input("Want to choose a custom log path?", "/var/log/growautomation")
    ga_mnt_log = ga_setup_input("Want to mount remote share as log destination? Smb and nfs available.", False)
    if ga_mnt_log is True:
        ga_setup_fstabcheck()
        if ga_mnt_backup is True:
            ga_mnt_samecreds = ga_setup_input("Use same server as for remote backup?", True)
            if ga_mnt_samecreds is True:
                ga_mnt_log_type = ga_mnt_backup_type
                ga_mnt_log_server = ga_mnt_backup_server
        else:
            ga_mnt_log_type = ga_setup_input("Mount nfs or smb/cifs share as log destination?", "nfs", "nfs/cifs")
            ga_mnt_log_server = ga_setup_input("Provide the server ip.", "192.168.0.201")
        ga_mnt_log_share = ga_setup_input("Provide the share name.", "growautomation/log")
    
        if ga_mnt_log_type == "cifs":
            ga_mnt_log_tmppwd = ga_setup_pwd_gen(ga_setup_pwd_length)
            def ga_mnt_log_creds():
                ga_mnt_backup_usr = ga_mnt_creds("usr", "galog")
                ga_mnt_backup_pwd = ga_mnt_creds("pwd", ga_mnt_log_tmppwd)
                ga_mnt_backup_dom = ga_mnt_creds("dom")
            if ga_mnt_backup is True and ga_mnt_backup_type == "cifs" and ga_mnt_samecreds is True:
                ga_mnt_samecreds = ga_setup_input("Use same share credentials as for remote backup?", True)
                if ga_mnt_samecreds is True:
                    ga_mnt_log_usr = ga_mnt_backup_usr
                    ga_mnt_log_pwd = ga_mnt_backup_pwd
                    ga_mnt_log_dom = ga_mnt_backup_dom
                else:
                    ga_mnt_log_creds()
            else:
                ga_mnt_log_creds()
    else:
        ga_mnt_log_type = "none"  # for nfs/cifs apt installation

########################################################################################################################
# always vars
ga_config_var_certs()

ga_ufw = ga_setup_input("Do you want to install the linux software firewall?\n"
                        "It will be configured for growautomation", True)

########################################################################################################################

ga_setup_log_write("Setup information received:\n")
ga_setup_log_writeplain("Basic vars: setuptype %s, internalca %s, garootpath %s,backup %s, ufw %s\n"
                     % (ga_setup_type, ga_setup_ca, ga_path_root, ga_backup, ga_ufw))
if ga_backup is True:
    ga_setup_log_writeplain("Backup vars: backuppath %s, backupmnt %r\n" % (ga_path_backup, ga_mnt_backup_))
    if ga_mnt_backup is True:
        ga_setup_log_writeplain(
            "backupmnttype %s, backupserver %s, backupshare %s\n"
            % (ga_mnt_backup_type, ga_mnt_backup_server, ga_mnt_backup_share))
        if ga_mnt_backup_type == "cifs":
            ga_setup_log_writeplain("backupmntusr %s, backupmntdom %s\n" % (ga_mnt_backup_usr, ga_mnt_backup_dom))
ga_setup_log_writeplain("Log vars: logpath %s, logmnt %r\n" % (ga_path_log, ga_mnt_log_))
if ga_mnt_log is True:
    ga_setup_log_writeplain("logmnttype %s, logserver %s, logshare %s\n" 
                            % (ga_mnt_log_type, ga_mnt_log_server, ga_mnt_log_share))
    if ga_mnt_log_type == "cifs":
        ga_setup_log_writeplain("logmntusr %s, logmntdom %s\n" % (ga_mnt_log_usr, ga_mnt_log_dom))
if ga_setup_type == "agent":
    ga_setup_log_writeplain("Agent vars: serverip %s, sqlport %s, sqluser %s"
                         % (ga_sql_server_ip, ga_serversqlport, ga_sql_server_agent_usr))
ga_setup_shelloutput_header("Thank you for providing the setup information\nThe installation will start now")

########################################################################################################################


# functions
def ga_foldercreate(tmppath):
    os.system("mkdir -p %s && chown -R growautomation:growautomation %s %s" % (tmppath, tmppath, ga_setup_log_redirect))


def ga_setup_config_file(opentype, openinput):
    tmpfile = "%s/main/main.conf" % ga_path_root
    tmpfile_open = open(tmpfile, opentype)
    if opentype == "a" or opentype == "w":
        tmpfile_open.write(openinput)
        os.system("chown growautomation:growautomation %s && chmod 440 %s" % (tmpfile, tmpfile))
    elif opentype == "r":
        return tmpfile_open.readlines()
    tmpfile_open.close()
    

def ga_mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
    ga_setup_shelloutput_header("Mounting %s share" % mname)
    ga_setup_log_write("Mounting %s share" % mname)
    if mtype == "cifs":
        mcreds = "username=%s,password=%s,domain=%s" % (muser, mpwd, mdom)
    else:
        mcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write("#Growautomation %s mount\n//%s/%s %s %s %s 0 0\n\n" % (mname, msrv, mshr, mpath, mtype, mcreds))
    ga_fstab.close()
    os.system("mount -a %s" % ga_setup_log_redirect)


def ga_replaceline(file, replace, insert):
    os.system("sed -i 's/" + replace + "/" + insert + "/p' " + file)


def ga_openssl_setup():
    ga_foldercreate("%s/ca/private" % ga_path_root)
    ga_foldercreate("%s/ca/certs" % ga_path_root)
    ga_foldercreate("%s/ca/crl" % ga_path_root)
    os.system("chmod 770 %s/ca/private" % ga_path_root)
    ga_replaceline("%s/ca/openssl.cnf", "= /root/ca", "= %s/ca"
                   ) % (ga_path_root, ga_path_root)
    ga_setup_shelloutput_text("Creating root certificate")
    os.system("openssl genrsa -aes256 -out %s/ca/private/ca.key.pem 4096 && chmod 400 %s/ca/private/ca.key.pe %s"
              % (ga_path_root, ga_path_root, ga_setup_log_redirect))
    os.system("openssl req -config %s/ca/openssl.cnf -key %s/ca/private/ca.key.pem -new -x509 -days 7300 -sha256 "
              "-extensions v3_ca -out %s/ca/certs/ca.cer.pem %s"
              % (ga_path_root, ga_path_root, ga_path_root, ga_setup_log_redirect))


def ga_openssl_server_cert(tmpname):
    ga_setup_shelloutput_text("Generating server certificate")
    os.system("openssl genrsa -aes256 -out %s/ca/private/%s.key.pem 2048" % (ga_path_root, tmpname))
    os.system("eq -config %s/ca/openssl.cnf -key %s/ca/private/%s.key.pem "
              "-new -sha256 -out %s/ca/csr/%s.csr.pem" % (ga_path_root, ga_path_root, tmpname, ga_path_root, tmpname))
    os.system("openssl ca -config %s/ca/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 "
              "-in %s/ca/csr/%s.csr.pem -out %s/ca/certs/%s.cert.pem"
              % (ga_path_root, ga_path_root, tmpname, ga_path_root, tmpname))


def ga_sql_all():
    ga_setup_shelloutput_header("Starting sql setup")
    ga_sql_backup_pwd = ga_setup_pwd_gen(ga_setup_pwd_length)
    ga_setup_shelloutput_text("Creating mysql backup user")
    ga_mysql(dbuser="root", command="CREATE USER 'gabackup'@'localhost' IDENTIFIED BY '%s';"
                                    "GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON *.* TO "
                                    "'gabackup'@'localhost' IDENTIFIED BY '%s';"
                                    "FLUSH PRIVILEGES;" % (ga_sql_backup_pwd, ga_sql_backup_pwd))

    ga_setup_shelloutput_text("Set a secure password and answer all other questions with Y/yes")
    ga_setup_shelloutput_text("Example random password: %s\nMySql will not ask for the password if you start it "
                              "(mysql -u root) locally with sudo/root privileges (set & forget)"
                              % ga_setup_pwd_gen(ga_setup_pwd_length))
    os.system("mysql_secure_installation %s" % ga_setup_log_redirect)

    tmpfile = open("/etc/mysql/conf.d/ga.mysqldump.cnf", 'a')
    tmpfile.write("[mysqldump]\nuser=gabackup\npassword=%s" % ga_sql_backup_pwd)
    tmpfile.close()

    os.system("usermod -a -G growautomation mysql")
    ga_foldercreate("/etc/mysql/ssl")


def ga_sql_server():
    ga_setup_shelloutput_header("Configuring sql as growautomation server")
    os.system("mysql -u root < /tmp/controller/setup/server/ga_db_setup.sql %s" % ga_setup_log_redirect)
    if ga_setup_type == "server":
        os.system("cp /tmp/controller/setup/server/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_setup_log_redirect)
    elif ga_setup_type == "standalone":
        os.system("cp /tmp/controller/setup/standalone/50-server.cnf /etc/mysql/mariadb.conf.d/ %s"
                  % ga_setup_log_redirect)

    ga_setup_shelloutput_text("Creating mysql admin user")
    ga_mysql(dbuser="root", command="CREATE USER 'gadmin'@'%s' IDENTIFIED BY '%s';"
                                    "GRANT ALL ON ga.* TO 'gadmin'@'%s' IDENTIFIED BY '%s';"
                                    "FLUSH PRIVILEGES;"
                                    % ("%", ga_sql_admin_pwd, "%", ga_sql_admin_pwd))

    ga_setup_config_file("a", "[db_growautomation]\nuser=gadmin\npassword=%s" % ga_sql_admin_pwd)

    if ga_setup_type == "server":
        print("Creating mysql server certificate\n")
        ga_openssl_server_cert("mysql")
        os.system("ln -s %s/ca/certs/ca.cer.pem /etc/mysql/ssl/cacert.pem && "
                  "ln -s %s/ca/certs/mysql.cer.pem /etc/mysql/ssl/server-cert.pem && "
                  "ln -s %s/ca/private/mysql.key.pem /etc/mysql/ssl/server-key.pem %s"
                  % (ga_path_root, ga_path_root, ga_path_root, ga_setup_log_redirect))


def ga_sql_agent():
    ga_setup_shelloutput_header("Configuring sql as growautomation agent")
    ga_sql_agent_pwd = ga_setup_pwd_gen(ga_setup_pwd_length)
    os.system("cp /tmp/controller/setup/agent/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_setup_log_redirect)
    ga_setup_shelloutput_text("Configuring mysql master-slave setup")
    ga_setup_shelloutput_text("Replicating server db to agent for the first time")
    os.system("mysqldump -h %s -u %s -p %s ga > /tmp/ga.dbdump.sql && mysql -u root ga < /tmp/ga.dbdump.sql %s"
              % (ga_sql_server_ip, ga_sql_server_agent_usr, ga_sql_server_agent_pwd, ga_setup_log_redirect))
    tmpsearchdepth = 500
    tmpfile = open("/tmp/ga.dbdump.sql", 'r')
    tmplines = tmpfile.readlines()[:tmpsearchdepth]
    for line in tmplines:
        if line.find("Master_Log_File: ") != -1:
            ga_sql_server_repl_file = line.split("Master_Log_File: ")[1].split("\n", 1)[0]
        elif line.find("Master_Log_Pos: ") != -1:
            ga_sql_server_repl_pos = line.split("Master_Log_Pos: ")[1].split("\n", 1)[0]

    tmpreplfilestate = ga_setup_varcheck(ga_sql_server_repl_file, "Info Master_Log_File not  found.")
    tmpreplposstate = ga_setup_varcheck(ga_sql_server_repl_pos, "Info Master_Log_Pos not found.")

    ga_sql_server_agent_id = int(ga_mysql(dbuser=ga_sql_server_agent_usr, dbpwd=ga_sql_server_agent_pwd,
                                          dbserver=ga_sql_server_ip,
                                          command="SELECT id FROM ga.ServerConfigAgents WHERE controller = %s;"
                                                  % ga_config_name)) + 100
    ga_replaceline("/etc/mysql/mariadb.conf.d/50-server.cnf", "server-id              = 1",
                   "server-id = %s" % ga_sql_server_agent_id)
    os.system("systemctl restart mysql")

    ga_setup_shelloutput_text("Creating local mysql controller user (read only)")
    ga_mysql(dbuser="root", command="CREATE USER 'gacon'@'localhost' IDENTIFIED BY '%s';"
                                    "GRANT SELECT ON ga.* TO 'gacon'@'localhost' IDENTIFIED BY '%s';"
                                    "FLUSH PRIVILEGES;"
                                    % (ga_sql_agent_pwd, ga_sql_agent_pwd))

    ga_setup_config_file("a", "[db_local]\nlocaluser=gacon\nlocalpassword=%s\n[server]\nagentuser=%s\nagentpassword=%s"
                              "\nserverip=%s" % (ga_sql_agent_pwd, ga_sql_server_agent_usr, ga_sql_server_agent_pwd,
                                                 ga_sql_server_ip))
    ga_sql_agent_masterslave_command = "CHANGE MASTER TO MASTER_HOST='%s', MASTER_USER='%s', MASTER_PASSWORD='%s', " \
                                       "MASTER_LOG_FILE='%s', MASTER_LOG_POS=%s; START SLAVE; SHOW SLAVE STATUS\G"
    
    if tmpreplfilestate is False or tmpreplposstate is False:
        ga_setup_shelloutput_text("SQL master slave configuration not possible due to missing information.\n"
                                  "Should be found in mysql dump from server (searching in first %s lines).\n"
                                  "Failed command: %s" % (tmpsearchdepth, ga_sql_agent_masterslave_command))
    else:
        ga_mysql(dbuser="root", command=ga_sql_agent_masterslave_command 
                                        % (ga_sql_server_ip, ga_sql_server_repl, ga_sql_server_replpwd,
                                           ga_sql_server_repl_file, ga_sql_server_repl_pos))

    ga_setup_shelloutput_text("Linking mysql certificate")
    os.system("ln -s %s /etc/mysql/ssl/cacert.pem && "
              "ln -s %s /etc/mysql/ssl/server-cert.pem && "
              "ln -s %s /etc/mysql/ssl/server-key.pem %s"
              % (ga_config_server_ca, ga_config_server_cert, ga_config_server_key, ga_setup_log_redirect))


def ga_sql_server_create_agent():
    ga_setup_shelloutput_header("Registering a new growautomation agent to the server")
    ga_sql_create_agent = ga_setup_input("Do you want to register an agent to the ga-server?", True)
    if ga_sql_create_agent is True:
        ga_sql_server_agent_list = ga_mysql(dbuser="gadmin", dbpwd=ga_sql_admin_pwd,
                                            command="SELECT controller FROM ga.ServerConfigAgents WHERE enabled = 1;")
        if len(ga_sql_server_agent_list) > 0:
            ga_setup_shelloutput_text("List of registered agents:\n%s\n" % ga_sql_server_agent_list)
        else:
            ga_setup_shelloutput_text("No agents are registered/enabled yet.\n")

        ga_sql_create_agent_namelen = 0
        while ga_sql_create_agent_namelen > 10:
            if ga_sql_create_agent_namelen > 10:
                ga_setup_shelloutput_text("Agent could not be created due to a too long name.\nMax 10 "
                                          "characters supported.\nProvided: %s" % ga_sql_create_agent_namelen)
            ga_sql_create_agent_name = ga_setup_input("Provide agent name.", "gacon01", poss="max. 10 characters long")
            if ga_sql_create_agent_name in ga_sql_server_agent_list:
                ga_setup_shelloutput_text("Controllername already registered to server. Choose a diffent name")
                ga_sql_create_agent_name = "-----------"
            ga_sql_create_agent_namelen = len(ga_sql_create_agent_name)

        ga_sql_create_agent_pwdlen = 0
        while ga_sql_create_agent_pwdlen > 99 or ga_sql_create_agent_pwdlen < 8:
            if ga_sql_create_agent_pwdlen > 99 or ga_sql_create_agent_pwdlen < 8:
                    ga_setup_shelloutput_text("Input error. Value should be between 8 and 99")
            ga_sql_create_agent_pwd = ga_setup_input("Provide agent password.", ga_setup_pwd_gen(ga_setup_pwd_length),
                                                     poss="between 8 and 99 characters")
            ga_sql_create_agent_pwdlen = len(ga_sql_create_agent_pwd)

        ga_setup_shelloutput_text("Creating mysql controller user")
        ga_sql_create_agent_desclen = 0
        while ga_sql_create_agent_desclen > 50:
            if ga_sql_create_agent_desclen > 50:
                ga_setup_shelloutput_text("Description longer than 50 characters. Try again.")
            ga_sql_create_agent_desc = ga_setup_input("Do you want to add a description to the agent?",
                                                      poss="String up to 50 characters")
            ga_sql_create_agent_desclen = len(ga_sql_create_agent_desc)

        ga_mysql(dbuser="gadmin", dbpwd=ga_sql_admin_pwd,
                 command="CREATE USER '%s'@'%s' IDENTIFIED BY '%s';"
                         "GRANT CREATE, DELETE, INSERT, SELECT, UPDATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';"
                         "FLUSH PRIVILEGES;"
                         "INSERT INTO ga.ServerConfigAgents (author, controller, description) VALUES (%s, %s, %s);"
                         % (ga_sql_create_agent_name, "%", ga_sql_create_agent_pwd, ga_sql_create_agent_name, "%",
                            ga_sql_create_agent_pwd,
                            "gasetup", ga_sql_create_agent_name, ga_sql_create_agent_desc))

        ga_sql_create_replica_usr = ga_sql_create_agent_name + "replica"
        ga_sql_create_replica_pwd = ga_setup_pwd_gen(ga_setup_pwd_length)
        ga_mysql(dbuser="gadmin", dbpwd=ga_sql_admin_pwd,
                 command="CREATE USER '%s'@'%s' IDENTIFIED BY '%s';"
                         "GRANT REPLICATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';"
                         "FLUSH PRIVILEGES;"
                         % (ga_sql_create_replica_usr, "%", ga_sql_create_replica_pwd, ga_sql_create_replica_usr, "%",
                            ga_sql_create_replica_pwd))

        ga_setup_config_file("a", "[db_agent_%s]\nserverip=%s\nagentuser=%s\nagentpassword=%s\nreplicauser=%s"
                                  "\nreplicapassword=%s"
                      % (ga_sql_create_agent_name, ga_sql_server_ip, ga_sql_create_agent_name, ga_sql_create_agent_pwd,
                         ga_sql_create_replica_usr, ga_sql_create_replica_pwd))

        ga_setup_shelloutput_text("Creating mysql agent certificate\n")
        ga_openssl_server_cert(ga_sql_create_agent_name)


def ga_ufw_setup():
    ga_setup_shelloutput_header("Configuring firewall")
    os.system("ufw default deny outgoing && ufw default deny incoming && "
              "ufw allow out to any port 80/tcp && ufw allow out to any port 443/tcp && allow out to any port 22/tcp &&"
              " ufw allow out to any port 53/udp && ufw allow out to any port 123/udp && "
              "ufw allow 22/tcp from 192.168.0.0/16 && ufw allow 22/tcp from 172.16.0.0/12 && "
              "ufw allow 22/tcp from 10.0.0.0/10")
    if ga_setup_type == "server" or ga_setup_type == "agent":
              os.system("ufw allow 3306/tcp from 192.168.0.0/16 && ufw allow 3306/tcp from 172.16.0.0/12 && "
                        "ufw allow 3306/tcp from 10.0.0.0/10 %s" % ga_setup_log_redirect)
    ga_ufw_enable = ga_setup_input("Firewall rules were configured. Do you want to enable them?\n"
                                   "SSH and MySql connections from public ip ranges will be denied!", True)
    if ga_ufw_enable is True:
        os.system("ufw enable %s" % ga_setup_log_redirect)


########################################################################################################################


# install packages
ga_setup_shelloutput_header("Installing software packages")
os.system("apt-get update" + ga_setup_log_redirect)
if ga_setup_linuxupgrade is True:
    os.system("apt-get -y dist-upgrade && apt-get -y upgrade %s" % ga_setup_log_redirect)

os.system("apt-get -y install python3 mariadb-server mariadb-client git %s" % ga_setup_log_redirect)

if ga_setup_type == "agent" or ga_setup_type == "standalone":
    os.system("apt-get -y install python3 python3-pip python3-dev python-smbus git %s" % ga_setup_log_redirect)
    if ga_setup_ca is True:
        os.system("git main --global http.sslCAInfo %s && python3 -m pip main set global.cert %s %s"
                  % (ga_setup_capath, ga_setup_capath, ga_setup_log_redirect))
    ga_setup_shelloutput_text("Installing python packages")
    os.system("python3 -m pip install "
              "mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay "
              "--default-timeout=100 %s" % ga_setup_log_redirect)
else:
    os.system("apt-get -y install openssl")

if (ga_mnt_backup or ga_mnt_log_) is True:
    if ga_mnt_backup_type == "nfs" or ga_mnt_log_type == "nfs":
        os.system("apt-get -y install nfs-common %s" % ga_setup_log_redirect)
    elif ga_mnt_backup_type == "cifs" or ga_mnt_log_type == "cifs":
        os.system("apt-get -y install cifs-utils %s" % ga_setup_log_redirect)

if ga_ufw is True:
    os.system("apt-get -y install ufw %s" % ga_setup_log_redirect)

# folders
# Create folders
ga_setup_shelloutput_header("Setting up directories")
ga_setup_log_write("Setting up directories")
os.system("useradd growautomation %s" % ga_setup_log_redirect)

ga_foldercreate(ga_path_backup)
if ga_versionold is True:
    if ga_versionold_replace_backup is True:
        ga_versionoldbackup = ga_path_backup + "/install"
        os.system("mkdir -p %s && mv %s %s %s"
                  % (ga_versionoldbackup, ga_path_root, ga_versionoldbackup, ga_setup_log_redirect))
        os.system("mv %s %s" % (ga_version_file, ga_versionoldbackup))
    else:
        os.system("mv %s /tmp" % ga_path_root)
    tmpfile = open(ga_version_file, 'w')
    tmpfile.write("gaversion=%s\ngaroot=%s\n" % (ga_version, ga_path_root))
    tmpfile.close()
ga_foldercreate(ga_path_root)
ga_foldercreate(ga_path_log)

if ga_mnt_backup is True:
    ga_mounts("backup", ga_mnt_backup_usr, ga_mnt_backup_pwd, ga_mnt_backup_dom, ga_mnt_backup_server, ga_mnt_backup_share,
              ga_path_backup, ga_mnt_backup_type)
if ga_mnt_log is True:
    ga_mounts("log", ga_mnt_log_usr, ga_mnt_log_pwd, ga_mnt_log_dom, ga_mnt_log_server, ga_mnt_log_share, ga_path_log,
              ga_mnt_log_type)

# code setup
ga_setup_shelloutput_header("Setting up growautomation code")
ga_setup_log_write("Setting up growautomation code")
os.system("cd /tmp && git clone https://github.com/growautomation-at/controller.git %s" % ga_setup_log_redirect)
os.system("PYVER=$(python3 --version | cut -c8-10) && ln -s /etc/growautomation/main "
          "/usr/local/lib/python$PYVER/dist-packages/GA %s" % ga_setup_log_redirect)
if ga_setup_type == "agent" or ga_setup_type == "standalone":
    os.system("cp -r /tmp/controller/code/agent/* %s %s" % (ga_path_root, ga_setup_log_redirect))

if ga_setup_type == "server" or ga_setup_type == "standalone":
    os.system("cp -r /tmp/controller/code/server/* %s %s" % (ga_path_root, ga_setup_log_redirect))

ga_setup_config_file("w", "[main]\nname=%s\ntype=%s" % (ga_config_name, ga_setup_type))

# creating openssl ca
if ga_setup_type == "server":
    ga_openssl_setup()


# db setup
ga_sql_all()

if ga_setup_type == "server" or "standalone":
    ga_sql_admin_pwd = ga_setup_pwd_gen(ga_setup_pwd_length)
    ga_sql_server(ga_path_root, ga_sql_admin_pwd)
    
if ga_setup_type == "server":
    ga_sql_server_create_agent()

elif ga_setup_type == "agent":
    ga_sql_agent()

if ga_ufw is True:
    ga_ufw_setup()

ga_setup_shelloutput_header("Setup finished! Please reboot the system.")
ga_setup_log_write("Setup finished.")
# delete old fstab entries and replace them (ask user)
# systemd timer setup for agentdata and serverbackup
# ga service check for python path /usr/bin/python3 and growautomation root -> change execstart execstop etc
# add [Unit]After=mysqld.service to service if standalone installation
# write setup config to sql server
# add script to add users to db (prompt for pwd and username -> set db privileges)

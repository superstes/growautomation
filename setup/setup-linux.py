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

import os
from datetime import datetime
import getpass
from random import choice as random_choice
from string import ascii_letters as string_ascii_letters
from string import digits as string_digits
from colorama import Fore as colorama_fore


# basic vars
ga_config = {}
ga_config["version"] = "0.2.1.2"
ga_config["setup_version_file"] = "/etc/growautomation.version"
ga_config["setup_log"] = "/var/log/growautomation-setup_%s.log" % datetime.now().strftime("%Y-%m-%d_%H-%M")
ga_config["setup_log_redirect"] = " 2>&1 | tee -a %s" % ga_config["setup_log"]


########################################################################################################################


# shell output
def ga_setup_shelloutput_header(output):
    shellhight, shellwidth = os.popen('stty size', 'r').read().split()
    print("\n")
    print('#' * (int(shellwidth) - 1))
    print("\n" + output + "\n")
    print('#' * (int(shellwidth) - 1))
    print("\n")


def ga_setup_shelloutput_subheader(output):
    shellhight, shellwidth = os.popen('stty size', 'r').read().split()
    print('-' * (int(shellwidth) - 1))
    print(output)
    print('-' * (int(shellwidth) - 1))
    ga_setup_log_write("####################################")
    ga_setup_log_write(output)
    ga_setup_log_write("####################################")


def ga_setup_shelloutput_colors(style):
    if style == "warn":
        return colorama_fore.YELLOW
    elif style == "info":
        return colorama_fore.CYAN
    elif style == "err":
        return colorama_fore.RED
    elif style == "succ":
        return colorama_fore.GREEN
    else:
        return ""


def ga_setup_shelloutput_text(output, style=""):
    styletype = ga_setup_shelloutput_colors(style)
    print(styletype + "%s.\n" % output + colorama_fore.RESET)
    ga_setup_log_write(output)


def ga_setup_log_write(output):
    tmplog = open(ga_config["setup_log"], "a")
    tmplog.write("\n" + output + "\n")
    tmplog.close()


def ga_setup_log_write_plain(output):
    tmplog = open(ga_config["setup_log"], "a")
    tmplog.write(output + "\n")
    tmplog.close()


def ga_setup_pwd_gen(stringlength):
    chars = string_ascii_letters + string_digits + "!#-_"
    return ''.join(random_choice(chars) for i in range(stringlength))


def ga_setup_fstabcheck():
    with open("/etc/fstab", 'r') as readfile:
        stringcount = readfile.read().count("Growautomation")
        if stringcount > 0:
            shellhight, shellwidth = os.popen('stty size', 'r').read().split()
            ga_setup_shelloutput_text("WARNING!\nYou already have one or more remote shares configured.\nIf you want"
                                      " to install new ones you should disable the old ones by editing the "
                                      "'/etc/fstab' file.\nJust add a '#' in front of the old shares or delete "
                                      "those lines to disable them", style="warn")


def ga_setup_input(prompt, default="", poss="", intype="", style=""):
    styletype = ga_setup_shelloutput_colors(style)
    if type(default) == bool:
        while True:
            try:
                return {"true": True, "false": False, "yes": True, "no": False, "y": True, "n": False,
                        "": default}[input(styletype + "\n%s\n(Poss: yes/true/no/false - Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower()]
            except KeyError:
                print(styletype + "WARNING: Invalid input please enter either yes/true/no/false!\n" + colorama_fore.RESET)
    elif type(default) == str:
        if intype == "pass" and default != "":
            getpass.getpass(prompt="\n%s\n(Random: %s)\n > " % (prompt, default)) or "%s" % default
        elif intype == "pass":
            getpass.getpass(prompt="\n%s\n > " % prompt)
        elif intype == "passgen":
            inputnumber = 0
            while inputnumber < 8 or inputnumber > 99:
                if inputnumber < 8 or inputnumber > 99:
                    print("Input error. Value should be between 8 and 99.\n")
                inputstr = str(input("\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default)).lower() or "%s" % default)
                inputnumber = int(inputstr)
            return inputstr
        elif poss != "":
            return str(input(styletype + "\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default) + colorama_fore.RESET).lower() or "%s" % default)
        elif default != "":
            return str(input(styletype + "\n%s\n(Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower() or "%s" % default)
        else:
            return str(input(styletype + "\n%s\n > " % prompt + colorama_fore.RESET).lower())


def ga_mnt_creds(outtype, inputstr=""):
    if outtype == "usr":
        return ga_setup_input("Provide username for share authentication.", inputstr)
    elif outtype == "pwd":
        return ga_setup_input("Provide password for share authentication.", inputstr, intype="pass")
    elif outtype == "dom":
        return ga_setup_input("Provide domain for share authentication.", "workgroup")


# def ga_setup_varcheck(tmpvar, error=""):
#     try:
#         tmpvar
#         return True
#     except NameError:
#         if error != "":
#             ga_setup_shelloutput_text("WARNING! %s" % error)
#         return False


def ga_setup_keycheck(dictkey):
    dict = ga_config
    if dict[dictkey] is None:
        ga_setup_log_write("WARNING! Dict key %s has value of None" % dictkey)
        return False
    elif dictkey in dict:
        return True
    else:
        ga_setup_log_write("WARNING! Dict key not found" % dictkey)
        return False


def ga_mysql_unixsock():
    global ga_config
    sql_sock = "/var/run/mysqld/mysqld.sock"
    if os.path.exists(sql_sock) is False:
        sql_customsock = ga_setup_input("Mysql was unable to find the mysql unix socket file at %s.\nThe path can be found in mysql via "
                                        "the command:\n > show variables like 'socket;'\nProvide the correct path to it.")
        ga_config["sql_sock"] = sql_customsock
        return sql_customsock
    else:
        ga_config["sql_sock"] = sql_sock
        return sql_sock


def ga_mysql(command, dbuser="", dbpwd=""):
    try:
        if ga_config["sql_server_ip"] == "127.0.0.1" and dbuser != "root" or dbuser != "":
            mysql_doit = "user=%s, passwd=%s, unix_socket=%s" % (dbuser, dbpwd, ga_mysql_unixsock())
        elif ga_config["sql_server_ip"] == "127.0.0.1":
            mysql_doit = "unix_socket=%s" % ga_mysql_unixsock()
        else:
            mysql_doit = "host=%s, port=%s, user=%s, passwd=%s" % (ga_config["sql_server_ip"], ga_config["sql_server_port"], dbuser, dbpwd)
        db = mysql.connector.connect(mysql_doit)
        dbcursor = db.cursor()
        dbcursor.execute(command)
        data = dbcursor.fetchall()
        dbcursor.close()
        db.close()
        return data
    except mysql.connector.Error as error:
        ga_setup_shelloutput_text("MySql was unable to perform action '%s'.\nError message:\n%s" % (command, error), style="warn")
        return False


def ga_mysql_conntest(dbuser="", dbpwd=""):
    if dbuser is None or dbpwd is None or ga_config["sql_server_ip"] is None:
        return False
    sqltest = ga_mysql("SELECT * FROM ga.AgentConfig ORDER BY changed DESC LIMIT 10;", dbuser, dbpwd)
    if type(sqltest) == list:
        return True
    else:
        return False


def ga_setup_configparser_mysql(searchfor, user, pwd, agent=""):
    if agent == "":
        command_table = "Server"
        command_agents = ""
    else:
        command_table = "Agent"
        command_agents = " and agent = '%s'" % agent
    if type(searchfor) == list:
        itemdatadict = {}
        for item in searchfor:
            itemdatadict[item] = ga_mysql("SELECT data FROM ga.%sConfig WHERE name = '%s'%s"
                                          % (command_table, item, command_agents), user, pwd)
        return itemdatadict
    elif type(searchfor) == str:
        data = ga_mysql("SELECT data FROM ga.%sConfig WHERE name = '%s'%s"
                        % (command_table, searchfor, command_agents), user, pwd)
        return data


def ga_setup_configparser_file(file, text):
    tmpfile = open(file)
    for line in tmpfile.readlines():
        if line.find(text) != -1:
            return line
    return False


def ga_setup_exit(shell, log):
    ga_setup_log_write("\nExit. %s.\n\n" % log)
    raise SystemExit(colorama_fore.RED + "\n%s!\nYou can find the full setup log at %s.\n\n" + colorama_fore.RESET % (shell, ga_config["setup_log"]))


########################################################################################################################


ga_setup_log_write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# prechecks
ga_setup_shelloutput_header("Installing setup dependencies")

os.system("apt-get -y install python3-pip && python3 -m pip install mysql-connector-python colorama %s" % ga_config["setup_log_redirect"])
import mysql.connector


# check for root privileges
if os.getuid() != 0:
    ga_setup_exit("This script needs to be run with root privileges", "Script not started as root")

else:
    ga_setup_shelloutput_header("Starting Growautomation installation script\n"
                                "The newest versions can be found at: https://git.growautomation.at")
    ga_config["setup_warning"] = ga_setup_input("WARNING!\n\nWe recommend using this installation script on dedicated systems.\n"
                                                "This installation script won't check your already installed programs for compatibility problems.\n"
                                                "If you already use web-/database or other complex software on this system you should back it up before installing this software.\n"
                                                "We assume no liability for problems that may be caused by this installation!\n"
                                                "Accept the risk if you want to continue.", False, style="warn")
    if ga_config["setup_warning"] is False:
        ga_setup_exit("Script cancelled by user\nYou can also install this software manually through the setup "
                      "manual.\nIt can be found at: https://git.growautomation.at/tree/master/manual",
                      "Setupwarning not accepted by user")

ga_setup_shelloutput_header("Checking if growautomation is already installed on the system")

# check if growautomation is already installed
if os.path.exists(ga_config["setup_version_file"]) is True or os.path.exists("/etc/growautomation") is True:
    ga_setup_shelloutput_text("Growautomation version file or default root path found", style="info")

    def ga_config_vars_oldversion_replace():
        global ga_config
        ga_config["setup_old"] = True
        ga_config["setup_old_replace"] = ga_setup_input("Do you want to replace your current growautomation isntallation?", False)
        if ga_config["setup_old_replace"] is True:
            ga_config["setup_old_replace_migrate"] = ga_setup_input("Should we try to keep your old configuration and data?", False)
            if ga_config["setup_old_replace_migrate"] is True:
                ga_config["setup_fresh"] = False
            else:
                ga_config["setup_fresh"] = True
        if ga_config["setup_old_replace"] is True:
            ga_config["setup_old_backup"] = ga_setup_input("Do you want to backup your old growautomation installation?", True)
        else:
            ga_setup_exit("Stopping script. Current installation should not be overwritten",
                          "User chose that currently installed ga should not be overwritten")


    if os.path.exists(ga_config["setup_version_file"]) is True:
        ga_versionfile_line = ga_setup_configparser_file(ga_config["setup_version_file"], "gaversion=")
        if ga_versionfile_line is False:
            if os.path.exists("/etc/growautomation") is True:
                ga_setup_shelloutput_text("Growautomation is currently installed. But its version number could not be found", style="warn")
                ga_config_vars_oldversion_replace()
            else:
                ga_setup_shelloutput_text("No data for previous growautomation installation found. Installing as new", style="warn")
                ga_config["setup_old"] = False
        else:
            print("A version of growautomation is/was already installed on this system!\n\n"
                  "Installed version: " + ga_versionfile_line[11:] +
                  "\nReplace version: %s" % ga_config["version"])
            ga_config_vars_oldversion_replace()
    elif os.path.exists("/etc/growautomation") is True:
        ga_setup_shelloutput_text("Growautomation is currently installed. But its version number could not be found", style="warn")
        ga_config_vars_oldversion_replace()
else:
    ga_setup_shelloutput_text("No previous growautomation installation found", style="info")
    ga_config["setup_old"] = False

if ga_config["setup_old"] is False:
    ga_config["setup_fresh"] = True
    ga_config["setup_old_backup"] = False
    ga_setup_shelloutput_text("Growautomation will be installed completely new", style="succ")
else:
    ga_setup_shelloutput_text("Growautomation will be migrated to the new version", style="succ")

########################################################################################################################

# setup vars
ga_setup_shelloutput_header("Retrieving setup configuration through user input")


def ga_config_var_base():
    global ga_config
    ga_setup_shelloutput_subheader("Checking basic information")

    def ga_config_var_base_name():
        global ga_config
        if ga_config["setup_type"] == "agent":
            ga_config["hostname"] = ga_setup_input("Provide the name of this growautomation agent as configured on the server.", "gacon01")
        elif ga_config["setup_type"] == "server":
            ga_config["hostname"] = "gaserver"
        elif ga_config["setup_type"] == "standalone":
            ga_config["hostname"] = "gacon01"
    if ga_config["setup_fresh"] is False:
        ga_config["path_root"] = ga_setup_configparser_file(ga_config["setup_version_file"], "garoot=")[8:]
        ga_config["hostname"] = ga_setup_configparser_file(ga_config["setup_version_file"], "name=")[6:]
        ga_config["setup_type"] = ga_setup_configparser_file(ga_config["setup_version_file"], "type=")[6:]
        if ga_config["path_root"] is False:
            ga_setup_shelloutput_text("Growautomation rootpath not found in old versionfile", style="warn")
            ga_config["path_root"] = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation")
            if ga_config["setup_old_backup"] is True:
                ga_config["path_old_root"] = ga_setup_input("Please provide the install path of your current installation (for backup).", "/etc/growautomation")
            else:
                ga_config["path_old_root"] = False

        if ga_config["hostname"] is False:
            ga_setup_shelloutput_text("Growautomation hostname not found in old versionfile", style="warn")
            ga_config_var_base_name()

        if ga_config["setup_type"] is False:
            ga_setup_shelloutput_text("Growautomation setuptype not found in old versionfile.\n\n"
                                      "WARNING!\nTo keep your old configuration the setuptype must be the same as before", style="warn")
            ga_config["setup_type"] = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone", "agent/standalone/server")
            if ga_config["setup_old_backup"] is False:
                ga_setup_shelloutput_text("Turning on migration backup option - just in case", style="info")
                ga_config["setup_old_backup"] = True

    if ga_config["setup_fresh"] is True:
        ga_config["setup_type"] = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone", "agent/standalone/server")

        if ga_config["setup_type"] == "agent":
            ga_config["setup_yousure"] = ga_setup_input("WARNING!\nYou should install/update the growautomation server component before the agent because of dependencies.\n"
                                                        "Find more information about the creation of new agents at:\nhttps://git.growautomation.at/tree/master/manual/agent\n\n"
                                                        "Agree if you have already installed/updated the ga server or disagree to stop the installation.", False, style="warn")
            if ga_config["setup_yousure"] is False:
                ga_setup_exit("Stopping script. Server was not installed before agent", "User has not installed the server before the agent")
        ga_config["path_root"] = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation")
        if ga_config["setup_old"] and ga_config["setup_old_backup"] is True:
            ga_config["path_old_root"] = ga_setup_input("Please provide the install path of your current installation (for backup).", "/etc/growautomation")
        else:
            ga_config["path_old_root"] = False
        ga_config_var_base_name()

    if ga_config["setup_type"] == "server" or ga_config["setup_type"] == "standalone":
        ga_config["setup_type_ss"] = True
    else:
        ga_config["setup_type_ss"] = False


def ga_config_var_setup():
    global ga_config
    ga_setup_shelloutput_subheader("Checking setup options")
    ga_config["setup_pwd_length"] = ga_setup_input("This setup will generate random passwords for you.\nPlease define the length of those random passwords!", "12", "8-99", "passgen")

    ga_config["setup_ca"] = ga_setup_input("Need to import internal ca certificate for git/pip? Mainly needed if your firewall uses ssl inspection.", False)

    if ga_config["setup_ca"] is True:
        ga_config["setup_ca_path"] = ga_setup_input("Provide path to the ca file.", "/etc/ssl/certs/internalca.cer")
    else:
        ga_config["setup_ca_path"] = "notprovided"

    ga_config["setup_linuxupgrade"] = ga_setup_input("Want to upgrade your software and distribution before growautomation installation?", True)


def ga_config_var_db():
    global ga_config
    ga_setup_shelloutput_subheader("Checking for database credentials")
    whilecount = 0
    whilestate = False
    if ga_config["setup_type"] == "agent":
        if ga_config["setup_fresh"] is True:
            ga_config["sql_agent_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            while whilestate is False:
                if whilecount > 0:
                    ga_setup_shelloutput_text("SQL connection failed. Please try again", style="warn")
                whilecount += 1
                ga_config["sql_server_ip"] = ga_setup_input("Provide the ip address of the growautomation server.", "192.168.0.201")
                ga_config["sql_server_port"] = ga_setup_input("Provide the mysql port of the growautomation server.", "3306")
                print("The following credentials can be found in the serverfile '$garoot/main/main.conf'\n")
                ga_config["sql_server_agent_usr"] = ga_setup_input("Please provide the user used to connect to the database.", ga_config["hostname"])
                ga_config["sql_server_agent_pwd"] = ga_setup_input("Please provide the password used to connect to the database.", ga_config["sql_agent_pwd"], intype="pass")
                if ga_mysql_conntest(ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"]) is True:
                    whilestate = True
                    ga_setup_shelloutput_text("Server SQL connection verified", style="succ")
                    ga_config["sql_server_repl_usr"] = ga_setup_input("Please provide sql replication user.", ga_config["hostname"] + "replica")
                    ga_config["sql_server_repl_pwd"] = ga_setup_input("Please provide sql replication password.", ga_config["sql_server_agent_pwd"])
        else:
            ga_config["sql_agent_usr"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "localuser=")[11:]
            ga_config["sql_agent_pwd"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "localpassword=")[15:]

            if ga_mysql_conntest(ga_config["sql_agent_usr"], ga_config["sql_agent_pwd"]) is True:
                ga_setup_shelloutput_text("Local SQL connection verified", style="succ")

            while whilestate is False:
                if whilecount > 0:
                    ga_setup_shelloutput_text("You can reset/configure the agent database credentials on the "
                                              "growautomation server. Details can be found in the manual: "
                                              "https://git.growautomation.at/tree/master/manual", style="info")
                ga_config["sql_server_agent_usr"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "agentuser=")[11:]
                ga_config["sql_server_agent_pwd"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "agentpassword=")[15:]
                ga_config["sql_server_ip"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "serverip=")[10:]
                whilestate = ga_mysql_conntest(ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"])

            ga_setup_shelloutput_text("Server SQL connection verified", style="succ")
            # other config will be received via sql query
            return "default"

    elif ga_config["setup_type_ss"] is True:
        ga_config["sql_server_ip"] = "127.0.0.1"
        ga_config["sql_server_port"] = "3306"
        if ga_config["setup_fresh"] is True:
            ga_config["sql_server_admin_usr"] = ga_setup_input("How should the growautomation database admin user be named?", "gadmin")
            ga_config["sql_server_admin_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
        else:
            ga_config["sql_server_admin_usr"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "serveruser=")[10:]
            ga_config["sql_server_admin_pwd"] = ga_setup_configparser_file("%s/main/main.conf" % ga_config["path_root"], "serverpassword=")[10:]
            if ga_mysql_conntest(ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"]) is False:
                while whilestate is False:
                    if whilecount > 0:
                        ga_config["setup_server_admin_reset"] = ga_setup_input("Do you want to reset the database admin via the setup?", False)
                        if ga_config["setup_server_admin_reset"] is True:
                            if ga_mysql_conntest() is False:
                                ga_setup_shelloutput_text("Database admin can't be reset since the database check as root failed.\nThis could happen "
                                                          "if the growautomation database doesn't exist", style="warn")
                                ga_config["sql_server_noaccess_yousure"] = ga_setup_input("Do you want to continue the setup anyway? The problem might maybe get fixed by the setup process.", False)
                                if ga_config["sql_server_noaccess_yousure"] is False:
                                    ga_setup_exit("All database connections failed", "User chose to exit since all database connections failed")
                                ga_config["setup_server_admin_reset"] = False
                                if ga_config["setup_old_backup"] is False:
                                    ga_setup_shelloutput_text("Turning on migration backup option - just in case", style="info")
                                    ga_config["setup_old_backup"] = True
                                return "none"
                            else:
                                ga_setup_shelloutput_text("SQL connection verified", style="succ")
                                return "root"
                    ga_setup_shelloutput_text("SQL connection failed. Please try again.\nThe following credentials can normally be found in the serverfile '$garoot/main/main.conf'", style="warn")
                    ga_config["sql_server_admin_usr"] = ga_setup_input("Provide the name of the growautomation database admin user.", "gadmin")
                    ga_config["sql_server_admin_pwd"] = ga_setup_input("Please provide the password used to connect to the database.", intype="pass")
                    whilestate = ga_mysql_conntest(ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])
                    whilecount += 1

                ga_setup_shelloutput_text("SQL connection verified", style="succ")
                return "default"


def ga_config_var_certs():
    global ga_config
    ga_setup_shelloutput_subheader("Checking certificate information")
    if ga_config["setup_type"] == "agent":
        ga_setup_shelloutput_text("The following certificates can be found in the serverpath '$garoot/ca/certs/'\n", style="info")
        ga_config["sql_ca"] = ga_setup_input("Provide the path to the ca-certificate from your ga-server.", "%s/ssl/ca.cer.pem" % ga_config["path_root"])
        ga_config["sql_cert"] = ga_setup_input("Provide the path to the agent server certificate.", "%s/ssl/%s.cer.pem" % (ga_config["path_root"], ga_config["hostname"]))
        ga_config["sql_key"] = ga_setup_input("Provide the path to the agent server key.", "%s/ssl/%s.key.pem" % (ga_config["path_root"], ga_config["hostname"]))
########################################################################################################################
# Config migration from old installation


if ga_config["setup_fresh"] is False:
    ga_config_var_setup()
    ga_config_var_db()

    ga_setup_shelloutput_subheader("Retrieving existing configuration from database")
    ga_config_list_agent = ["backup", "path_backup", "mnt_backup", "mnt_backup_type", "mnt_backup_server",
                            "mnt_backup_share", "mnt_backup_usr", "mnt_backup_pwd", "mnt_backup_dom", "path_log",
                            "mnt_log", "mnt_shared_creds", "mnt_shared_server", "mnt_shared_type", "mnt_log_type",
                            "mnt_log_server", "mnt_log_share", "mnt_log_usr", "mnt_log_pwd", "mnt_log_dom", "ga_ufw"]
    ga_config_list_server = []
    if ga_config["setup_type"] == "server":
        ga_configdict_sql = ga_setup_configparser_mysql("ga_config_list_server", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])
    elif ga_config["setup_type"] == "standalone":
        ga_configdict_sql_agent = ga_setup_configparser_mysql("ga_config_list_agent", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], ga_config["hostname"])
        ga_configdict_sql_server = ga_setup_configparser_mysql("ga_config_list_server", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], ga_config["hostname"])
        ga_configdict_sql = {**ga_configdict_sql_agent, **ga_configdict_sql_server}
    else:
        ga_configdict_sql = ga_setup_configparser_mysql("ga_config_list_agent", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], ga_config["hostname"])

    ga_config = {**ga_configdict_sql, **ga_config}

########################################################################################################################
# Configuration without migration
if ga_config["setup_fresh"] is True:
    ga_config_var_base()
    ga_config_var_setup()
    ga_config_var_db()

    ga_config["path_backup"] = ga_setup_input("Want to choose a custom backup path?", "/mnt/growautomation/backup/")
    ga_backup = ga_setup_input("Want to enable backup?", True)
    if ga_backup is True:
        ga_config["mnt_backup"] = ga_setup_input("Want to mount remote share as backup destination? Smb and nfs available.", True)
        if ga_config["mnt_backup"] is True:
            ga_setup_fstabcheck()
            ga_config["mnt_backup_type"] = ga_setup_input("Mount nfs or smb/cifs share as backup destination?", "nfs", "nfs/cifs")
            ga_config["mnt_backup_srv"] = ga_setup_input("Provide the server ip.", "192.168.0.201")
            ga_config["mnt_backup_share"] = ga_setup_input("Provide the share name.", "growautomation/backup")
            if ga_config["mnt_backup_type"] == "cifs":
                ga_mnt_backup_tmppwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
                ga_config["mnt_backup_usr"] = ga_mnt_creds("usr", "gabackup")
                ga_config["mnt_backup_pwd"] = ga_mnt_creds("pwd", ga_mnt_backup_tmppwd)
                ga_config["mnt_backup_dom"] = ga_mnt_creds("dom")
            # else:
            #     ga_setup_shelloutput_text("Not mounting remote share for backup!\nCause: No sharetype, "
            #                               "serverip or sharename provided.\n")
    else:
        ga_config["mnt_backup"] = False
        ga_config["mnt_backup_type"] = "no"
    
    ga_config["path_log"] = ga_setup_input("Want to choose a custom log path?", "/var/log/growautomation")
    ga_config["mnt_log"] = ga_setup_input("Want to mount remote share as log destination? Smb and nfs available.", False)
    if ga_config["mnt_log"] is True:
        ga_setup_fstabcheck()
        if ga_config["mnt_backup"] is True:
            ga_config["mnt_samecreds"] = ga_setup_input("Use same server as for remote backup?", True)
            if ga_config["mnt_samecreds"] is True:
                ga_config["mnt_log_type"] = ga_config["mnt_backup_type"]
                ga_config["mnt_log_server"] = ga_config["mnt_backup_srv"]
        else:
            ga_config["mnt_log_type"] = ga_setup_input("Mount nfs or smb/cifs share as log destination?", "nfs", "nfs/cifs")
            ga_config["mnt_log_server"] = ga_setup_input("Provide the server ip.", "192.168.0.201")
        ga_config["mnt_log_share"] = ga_setup_input("Provide the share name.", "growautomation/log")
    
        if ga_config["mnt_log_type"] == "cifs":


            def ga_mnt_log_creds():
                global ga_config
                ga_config["mnt_backup_usr"] = ga_mnt_creds("usr", "galog")
                ga_config["mnt_backup_pwd"] = ga_mnt_creds("pwd", ga_setup_pwd_gen(ga_config["setup_pwd_length"]))
                ga_config["mnt_backup_dom"] = ga_mnt_creds("dom")

            if ga_config["mnt_backup"] is True and ga_config["mnt_backup_type"] == "cifs" and \
                    ga_config["mnt_samecreds"] is True:
                ga_config["mnt_samecreds"] = ga_setup_input("Use same share credentials as for remote backup?", True)
                if ga_config["mnt_samecreds"] is True:
                    ga_config["mnt_log_usr"] = ga_config["mnt_backup_usr"]
                    ga_config["ga_mnt_log_pwd"] = ga_config["mnt_backup_pwd"]
                    ga_config["ga_mnt_log_dom"] = ga_config["mnt_backup_dom"]
                else:
                    ga_mnt_log_creds()
            else:
                ga_mnt_log_creds()
    else:
        ga_config["mnt_log_type"] = "no"  # for nfs/cifs apt installation

########################################################################################################################
# always vars
if ga_config["setup_type"] == "agent":
    ga_config_var_certs()

ga_ufw = ga_setup_input("Do you want to install the linux software firewall (ufw)?\n"
                        "It will be configured for growautomation", True)

########################################################################################################################

ga_setup_shelloutput_subheader("Logging setup information")


def ga_log_write_vars():
    for key, value in ga_config.items():
        if "pwd" in key:
            pass
        else:
            ga_setup_log_write_plain("%s - %s" % (key, value))


ga_log_write_vars()

ga_setup_shelloutput_text("Thank you for providing the setup information\nThe installation will start now")

########################################################################################################################


# functions
def ga_foldercreate(tmppath):
    os.system("mkdir -p %s && chown -R growautomation:growautomation %s %s" % (tmppath, tmppath, ga_config["setup_log_redirect"]))


def ga_setup_config_file(opentype, openinput):
    tmpfile = "%s/main/main.conf" % ga_config["path_root"]
    tmpfile_open = open(tmpfile, opentype)
    if opentype == "a" or opentype == "w":
        tmpfile_open.write(openinput)
        os.system("chown growautomation:growautomation %s && chmod 440 %s" % (tmpfile, tmpfile))
    elif opentype == "r":
        return tmpfile_open.readlines()
    tmpfile_open.close()
    

def ga_mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
    ga_setup_shelloutput_subheader("Mounting %s share" % mname)
    if mtype == "cifs":
        mcreds = "username=%s,password=%s,domain=%s" % (muser, mpwd, mdom)
    else:
        mcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write("#Growautomation %s mount\n//%s/%s %s %s %s 0 0\n\n" % (mname, msrv, mshr, mpath, mtype, mcreds))
    ga_fstab.close()
    os.system("mount -a %s" % ga_config["setup_log_redirect"])


def ga_replaceline(file, replace, insert):
    os.system("sed -i 's/" + replace + "/" + insert + "/p' " + file)


def ga_openssl_setup():
    ga_foldercreate("%s/ca/private" % ga_config["path_root"])
    ga_foldercreate("%s/ca/certs" % ga_config["path_root"])
    ga_foldercreate("%s/ca/crl" % ga_config["path_root"])
    os.system("chmod 770 %s/ca/private" % ga_config["path_root"])
    ga_replaceline("%s/ca/openssl.cnf", "= /root/ca", "= %s/ca") % (ga_config["path_root"], ga_config["path_root"])
    ga_setup_shelloutput_subheader("Creating root certificate")
    os.system("openssl genrsa -aes256 -out %s/ca/private/ca.key.pem 4096 && chmod 400 %s/ca/private/ca.key.pe %s"
              % (ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))
    os.system("openssl req -config %s/ca/openssl.cnf -key %s/ca/private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out %s/ca/certs/ca.cer.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))


def ga_openssl_server_cert(tmpname):
    ga_setup_shelloutput_subheader("Generating server certificate")
    os.system("openssl genrsa -aes256 -out %s/ca/private/%s.key.pem 2048" % (ga_config["path_root"], tmpname))
    os.system("eq -config %s/ca/openssl.cnf -key %s/ca/private/%s.key.pem -new -sha256 -out %s/ca/csr/%s.csr.pem"
              % (ga_config["path_root"], ga_config["path_root"], tmpname, ga_config["path_root"], tmpname))
    os.system("openssl ca -config %s/ca/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 -in %s/ca/csr/%s.csr.pem -out %s/ca/certs/%s.cert.pem"
              % (ga_config["path_root"], ga_config["path_root"], tmpname, ga_config["path_root"], tmpname))


def ga_sql_all():
    ga_setup_shelloutput_header("Starting sql setup")
    ga_sql_backup_pwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
    ga_setup_shelloutput_subheader("Creating mysql backup user")
    ga_mysql("CREATE USER 'gabackup'@'localhost' IDENTIFIED BY '%s';GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, "
             "TRIGGER ON *.* TO 'gabackup'@'localhost' IDENTIFIED BY '%s';FLUSH PRIVILEGES;" % (ga_sql_backup_pwd, ga_sql_backup_pwd))

    ga_setup_shelloutput_text("Set a secure password and answer all other questions with Y/yes")
    ga_setup_shelloutput_text("Example random password: %s\nMySql will not ask for the password if you start it "
                              "(mysql -u root) locally with sudo/root privileges (set & forget)" % ga_setup_pwd_gen(ga_config["setup_pwd_length"]))
    os.system("mysql_secure_installation %s" % ga_config["setup_log_redirect"])

    tmpfile = open("/etc/mysql/conf.d/ga.mysqldump.cnf", 'a')
    tmpfile.write("[mysqldump]\nuser=gabackup\npassword=%s" % ga_sql_backup_pwd)
    tmpfile.close()

    os.system("usermod -a -G growautomation mysql")
    ga_foldercreate("/etc/mysql/ssl")


def ga_sql_server():
    ga_setup_shelloutput_header("Configuring sql as growautomation server")
    os.system("mysql -u root < /tmp/controller/setup/server/ga_db_setup.sql %s" % ga_config["setup_log_redirect"])
    if ga_config["setup_type"] == "server":
        os.system("cp /tmp/controller/setup/server/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])
    elif ga_config["setup_type"] == "standalone":
        os.system("cp /tmp/controller/setup/standalone/50-server.cnf /etc/mysql/mariadb.conf.d/ %s"
                  % ga_config["setup_log_redirect"])

    ga_setup_shelloutput_subheader("Creating mysql admin user")
    ga_mysql("CREATE USER '%s'@'%s' IDENTIFIED BY '%s';GRANT ALL ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';FLUSH PRIVILEGES;"
             % (ga_config["sql_server_admin_usr"], "%", ga_config["sql_server_admin_pwd"], ga_config["sql_server_admin_usr"], "%", ga_config["sql_server_admin_pwd"]))

    ga_setup_config_file("a", "[db_growautomation]\nserveruser=%s\nserverpassword=%s" % (ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"]))

    if ga_config["setup_type"] == "server":
        print("Creating mysql server certificate\n")
        ga_openssl_server_cert("mysql")
        os.system("ln -s %s/ca/certs/ca.cer.pem /etc/mysql/ssl/cacert.pem && ln -s %s/ca/certs/mysql.cer.pem /etc/mysql/ssl/server-cert.pem && "
                  "ln -s %s/ca/private/mysql.key.pem /etc/mysql/ssl/server-key.pem %s"
                  % (ga_config["path_root"], ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))


def ga_sql_agent():
    ga_setup_shelloutput_header("Configuring sql as growautomation agent")
    ga_config["sql_agent_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
    os.system("cp /tmp/controller/setup/agent/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])
    ga_setup_shelloutput_subheader("Configuring mysql master-slave setup")
    ga_setup_shelloutput_text("Replicating server db to agent for the first time", style="info")
    os.system("mysqldump -h %s --port %s -u %s -p %s ga > /tmp/ga.dbdump.sql && mysql -u root ga < /tmp/ga.dbdump.sql "
              "%s" % (ga_config["sql_server_ip"], ga_config["sql_server_port"], ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"], ga_config["setup_log_redirect"]))
    tmpsearchdepth = 500
    tmpfile = open("/tmp/ga.dbdump.sql", 'r')
    tmplines = tmpfile.readlines()[:tmpsearchdepth]
    for line in tmplines:
        if line.find("Master_Log_File: ") != -1:
            ga_config["sql_server_repl_file"] = line.split("Master_Log_File: ")[1].split("\n", 1)[0]
        elif line.find("Master_Log_Pos: ") != -1:
            ga_config["sql_server_repl_pos"] = line.split("Master_Log_Pos: ")[1].split("\n", 1)[0]

    ga_sql_server_agent_id = int(ga_mysql("SELECT id FROM ga.ServerConfigAgents WHERE controller = %s;"
                                          % ga_config["hostname"], ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"]) + 100)
    ga_replaceline("/etc/mysql/mariadb.conf.d/50-server.cnf", "server-id              = 1", "server-id = %s" % ga_sql_server_agent_id)
    os.system("systemctl restart mysql")

    ga_setup_shelloutput_subheader("Creating local mysql controller user (read only)")
    ga_mysql("CREATE USER 'gacon'@'localhost' IDENTIFIED BY '%s';GRANT SELECT ON ga.* TO 'gacon'@'localhost' "
             "IDENTIFIED BY '%s';FLUSH PRIVILEGES;" % (ga_config["sql_agent_pwd"], ga_config["sql_agent_pwd"]))

    ga_setup_config_file("a", "[db_local]\nlocaluser=gacon\nlocalpassword=%s\n[server]\nagentuser=%s\nagentpassword=%s\nserverip=%s"
                         % (ga_config["sql_agent_pwd"], ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"], ga_config["sql_server_ip"]))
    
    if ga_setup_keycheck(ga_config["sql_server_repl_file"]) is False or ga_setup_keycheck(ga_config["sql_server_repl_pos"]) is False:
        ga_setup_shelloutput_text("SQL master slave configuration not possible due to missing information.\nShould be found in mysql dump from server "
                                  "(searching in first %s lines).\nNot found: 'Master_Log_File:'/'Master_Log_Pos:'" % tmpsearchdepth, style="warn")
    else:
        ga_mysql("CHANGE MASTER TO MASTER_HOST='%s', MASTER_USER='%s', MASTER_PASSWORD='%s', MASTER_LOG_FILE='%s', MASTER_LOG_POS=%s; START SLAVE; SHOW SLAVE STATUS;"
                 % (ga_config["sql_server_ip"], ga_config["sql_server_repl_usr"], ga_config["sql_server_repl_pwd"], ga_config["sql_server_repl_file"], ga_config["sql_server_repl_pos"]))
        # \G

    ga_setup_shelloutput_subheader("Linking mysql certificate")
    os.system("ln -s %s /etc/mysql/ssl/cacert.pem && ln -s %s /etc/mysql/ssl/server-cert.pem && ln -s %s /etc/mysql/ssl/server-key.pem %s"
              % (ga_config["sql_ca"], ga_config["sql_cert"], ga_config["sql_key"], ga_config["setup_log_redirect"]))


def ga_sql_server_create_agent():
    ga_setup_shelloutput_header("Registering a new growautomation agent to the server")
    create_agent = ga_setup_input("Do you want to register an agent to the ga-server?", True)
    if create_agent is True:
        server_agent_list = ga_mysql("SELECT controller FROM ga.ServerConfigAgents WHERE enabled = 1;", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])
        if len(server_agent_list) > 0:
            ga_setup_shelloutput_text("List of registered agents:\n%s\n" % server_agent_list, style="info")
        else:
            ga_setup_shelloutput_text("No agents are registered/enabled yet.\n", style="info")

        create_agent_namelen = 0
        while create_agent_namelen > 10:
            if create_agent_namelen > 10:
                ga_setup_shelloutput_text("Agent could not be created due to a too long name.\nMax 10 characters supported.\nProvided: %s" % create_agent_namelen, style="warn")
            create_agent_name = ga_setup_input("Provide agent name.", "gacon01", poss="max. 10 characters long")
            if create_agent_name in server_agent_list:
                ga_setup_shelloutput_text("Controllername already registered to server. Choose a diffent name", style="warn")
                create_agent_name = "-----------"
            create_agent_namelen = len(create_agent_name)

        create_agent_pwdlen = 0
        while create_agent_pwdlen > 99 or create_agent_pwdlen < 8:
            if create_agent_pwdlen > 99 or create_agent_pwdlen < 8:
                ga_setup_shelloutput_text("Input error. Value should be between 8 and 99", style="warn")
            create_agent_pwd = ga_setup_input("Provide agent password.", ga_setup_pwd_gen(ga_config["setup_pwd_length"]), poss="between 8 and 99 characters")
            create_agent_pwdlen = len(create_agent_pwd)

        ga_setup_shelloutput_subheader("Creating mysql controller user")
        create_agent_desclen = 0
        while create_agent_desclen > 50:
            if create_agent_desclen > 50:
                ga_setup_shelloutput_text("Description longer than 50 characters. Try again.", style="warn")
            create_agent_desc = ga_setup_input("Do you want to add a description to the agent?", poss="String up to 50 characters")
            create_agent_desclen = len(create_agent_desc)

        ga_mysql("CREATE USER '%s'@'%s' IDENTIFIED BY '%s';GRANT CREATE, DELETE, INSERT, SELECT, UPDATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';FLUSH "
                 "PRIVILEGES;INSERT INTO ga.ServerConfigAgents (author, controller, description) VALUES (%s, %s, %s);"
                 % (create_agent_name, "%", create_agent_pwd, create_agent_name, "%", create_agent_pwd, "gasetup", create_agent_name, create_agent_desc),
                 ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])

        create_replica_usr = create_agent_name + "replica"
        create_replica_pwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
        ga_mysql("CREATE USER '%s'@'%s' IDENTIFIED BY '%s';GRANT REPLICATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';FLUSH PRIVILEGES;"
                 % (create_replica_usr, "%", create_replica_pwd,  create_replica_usr, "%", create_replica_pwd), ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])

        ga_setup_config_file("a", "[db_agent_%s]\nserverip=%s\nagentuser=%s\nagentpassword=%s\nreplicauser=%s\nreplicapassword=%s"
                             % (create_agent_name, ga_config["sql_server_ip"], create_agent_name, create_agent_pwd, create_replica_usr, create_replica_pwd))

        ga_setup_shelloutput_subheader("Creating mysql agent certificate\n")
        ga_openssl_server_cert(create_agent_name)


def ga_ufw_setup():
    ga_setup_shelloutput_subheader("Configuring firewall")
    os.system("ufw default deny outgoing && ufw default deny incoming && ufw allow out to any port 80/tcp && ufw allow out to any port 443/tcp && "
              "ufw allow out to any port 22/tcp && ufw allow out to any port 53/udp && ufw allow out to any port 123/udp && "
              "ufw allow 22/tcp from 192.168.0.0/16 && ufw allow 22/tcp from 172.16.0.0/12 && ufw allow 22/tcp from 10.0.0.0/10")
    if ga_config["setup_type"] == "server" or ga_config["setup_type"] == "agent":
        os.system("ufw allow 3306/tcp from 192.168.0.0/16 && ufw allow 3306/tcp from 172.16.0.0/12 && ufw allow 3306/tcp from 10.0.0.0/10 %s" % ga_config["setup_log_redirect"])
    ga_ufw_enable = ga_setup_input("Firewall rules were configured. Do you want to enable them?\nSSH and MySql connections from public ip ranges will be denied!", True)
    if ga_ufw_enable is True:
        os.system("ufw enable %s" % ga_config["setup_log_redirect"])


########################################################################################################################


# install packages
ga_setup_shelloutput_header("Installing software packages")
os.system("apt-get update" + ga_config["setup_log_redirect"])
if ga_config["setup_linuxupgrade"] is True:
    os.system("apt-get -y dist-upgrade && apt-get -y upgrade %s" % ga_config["setup_log_redirect"])

os.system("apt-get -y install python3 mariadb-server mariadb-client git %s" % ga_config["setup_log_redirect"])

if ga_config["setup_type"] == "agent" or ga_config["setup_type"] == "standalone":
    os.system("apt-get -y install python3 python3-pip python3-dev python-smbus git %s" % ga_config["setup_log_redirect"])
    if ga_config["setup_ca"] is True:
        os.system("git main --global http.sslCAInfo %s && python3 -m pip main set global.cert %s %s" % (ga_config["setup_ca_path"], ga_config["setup_ca_path"], ga_config["setup_log_redirect"]))
    ga_setup_shelloutput_subheader("Installing python packages")
    os.system("python3 -m pip install mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay --default-timeout=100 %s" % ga_config["setup_log_redirect"])
else:
    os.system("apt-get -y install openssl")

if (ga_config["mnt_backup"] or ga_config["mnt_log"]) is True:
    if ga_config["mnt_backup_type"] == "nfs" or ga_config["mnt_log_type"] == "nfs":
        os.system("apt-get -y install nfs-common %s" % ga_config["setup_log_redirect"])
    elif ga_config["mnt_backup_type"] == "cifs" or ga_config["mnt_log_type"] == "cifs":
        os.system("apt-get -y install cifs-utils %s" % ga_config["setup_log_redirect"])

if ga_ufw is True:
    os.system("apt-get -y install ufw %s" % ga_config["setup_log_redirect"])

# folders
# Create folders
ga_setup_shelloutput_header("Setting up directories")
os.system("useradd growautomation %s" % ga_config["setup_log_redirect"])

ga_foldercreate(ga_config["path_backup"])

def ga_oldversion_rootcheck():
    if ga_config["path_old_root"] is False:
        return ga_config["path_root"]
    else:
        return ga_config["path_old_root"]


def ga_oldversion_cleanconfig():
    os.system("mv %s /tmp" % ga_oldversion_rootcheck())
    ga_mysql("DROP DATABASE ga;")


def ga_oldversion_backup():
    global ga_config
    ga_setup_shelloutput_subheader("Backing up old growautomation root directory and database")
    oldbackup = ga_config["path_backup"] + "/install"
    os.system("mkdir -p %s && mv %s %s %s" % (oldbackup, ga_oldversion_rootcheck(), oldbackup, ga_config["setup_log_redirect"]))
    os.system("mv %s %s" % (ga_config["setup_version_file"], oldbackup))
    os.system("mysqldump ga > %s/ga.dbdump.sql %s" % (oldbackup, ga_config["setup_log_redirect"]))
    os.listdir(oldbackup)
    if os.path.exists(oldbackup + "/ga.dbdump.sql") is False or \
            os.path.exists(oldbackup + "/growautomation/") is False:
        ga_setup_shelloutput_text("Success of backup couldn't be verified. Please check it yourself to be sure that it was successfully created. (Strg+Z "
                                  "to get to Shell -> 'fg' to get back)\nBackuppath: %s" % oldbackup, style="warn")
        ga_config["setup_old_backup_failed_yousure"] = ga_setup_input("Please verify that you want to continue the setup", False)
    else:
        ga_config["setup_old_backup_failed_yousure"] = True
    ga_oldversion_cleanconfig()


if ga_config["setup_old"] is True and ga_config["setup_old_backup"] is True:
    ga_oldversion_backup()
elif ga_config["setup_old"] is True:
    ga_oldversion_cleanconfig()


def ga_versionfile_write():
    tmpfile = open(ga_config["setup_version_file"], 'w')
    tmpfile.write("version=%s\nroot=%s\nname=%s\ntype=%s\n" % (ga_config["version"], ga_config["path_root"], ga_config["hostname"], ga_config["setup_type"]))
    tmpfile.close()


ga_versionfile_write()
ga_foldercreate(ga_config["path_root"])
ga_foldercreate(ga_config["path_log"])

if ga_config["mnt_backup"] is True or ga_config["mnt_log"] is True:
    ga_setup_shelloutput_header("Mounting shares")
    if ga_config["mnt_backup"] is True:
        ga_mounts("backup", ga_config["mnt_backup_usr"], ga_config["mnt_backup_pwd"], ga_config["mnt_backup_dom"], ga_config["mnt_backup_srv"],
                  ga_config["mnt_backup_share"], ga_config["path_backup"], ga_config["mnt_backup_type"])
    if ga_config["mnt_log"] is True:
        ga_mounts("log", ga_config["mnt_log_usr"], ga_config["ga_mnt_log_pwd"], ga_config["ga_mnt_log_dom"], ga_config["mnt_log_server"], ga_config["mnt_log_share"],
                  ga_config["path_log"], ga_config["mnt_log_type"])

# code setup
ga_setup_shelloutput_header("Setting up growautomation code")
ga_setup_log_write("Setting up growautomation code")
os.system("cd /tmp && git clone https://github.com/growautomation-at/controller.git %s" % ga_config["setup_log_redirect"])
os.system("PYVER=$(python3 --version | cut -c8-10) && ln -s /etc/growautomation/main /usr/local/lib/python$PYVER/dist-packages/GA %s" % ga_config["setup_log_redirect"])
if ga_config["setup_type"] == "agent" or ga_config["setup_type"] == "standalone":
    os.system("cp -r /tmp/controller/code/agent/* %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

if ga_config["setup_type_ss"] is True:
    os.system("cp -r /tmp/controller/code/server/* %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

ga_setup_config_file("w", "[main]\nname=%s\ntype=%s" % (ga_config["hostname"], ga_config["setup_type"]))

# creating openssl ca
if ga_config["setup_type"] == "server":
    ga_openssl_setup()


# db setup
ga_sql_all()

if ga_config["setup_type_ss"] is True:
    ga_sql_server()
    
if ga_config["setup_type"] == "server":
    ga_sql_server_create_agent()

elif ga_config["setup_type"] == "agent":
    ga_sql_agent()

if ga_ufw is True:
    ga_ufw_setup()

ga_setup_shelloutput_header("Writing configuration to database")


def ga_mysql_write_config():
    newdict = {}
    for key, value in ga_config.items():
        if "setup_" in key or "sql_server_agent_pwd" in key or "sql_agent_pwd" in key or "sql_agent_usr" in key or "sql_server_admin_pwd" in key:
            pass
        else:
            newdict[key] = value
    if ga_config["setup_type_ss"] is True:
        dbuser = ga_config["sql_server_admin_usr"]
        dbpwd = ga_config["sql_server_admin_pwd"]
        table = "Server"
    else:
        dbuser = ga_config["sql_server_agent_usr"]
        dbpwd = ga_config["sql_server_agent_pwd"]
        table = "Agent"
    for key, value in newdict.items():
        if ga_config["setup_type"] == "agent":
            ga_mysql("INSERT INTO ga.%sConfig (author, agent, name, data) VALUES (%s, %s, %s, %s);" % (table, "gasetup", ga_config["hostname"], key, value), dbuser, dbpwd)
        elif ga_config["setup_type_ss"] is True:
            ga_mysql("INSERT INTO ga.%sConfig (author, name, data) VALUES (%s, %s, %s);" % (table, "gasetup", key, value), dbuser, dbpwd)


ga_mysql_write_config()
ga_log_write_vars()

ga_setup_shelloutput_header("Setup finished! Please reboot the system")
ga_setup_log_write("Setup finished.")
# delete old fstab entries and replace them (ask user)
# systemd timer setup for agentdata and serverbackup
# ga service check for python path /usr/bin/python3 and growautomation root -> change execstart execstop etc
# add [Unit]After=mysqld.service to service if standalone installation
# write setup config to sql server
# add script to add users to db (prompt for pwd and username -> set db privileges)
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

# ga_version 0.3

########################################################################################################################

from os import popen as os_popen
from os import path as os_path
from os import system as os_system
from os import getuid as os_getuid
from os import listdir as os_listdir
from datetime import datetime
from getpass import getpass
from random import choice as random_choice
from string import ascii_letters as string_ascii_letters
from string import digits as string_digits
from sys import version_info as sys_version_info
from sys import argv as sys_argv
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe

# basic vars
ga_config = {}
ga_config_server = {}
ga_config["version"] = "0.3"
ga_config["setup_version_file"] = "/etc/growautomation.version"
ga_config["setup_log_path"] = "/var/log/growautomation/"
ga_config["setup_log"] = "%ssetup_%s.log" % (ga_config["setup_log_path"], datetime.now().strftime("%Y-%m-%d_%H-%M"))
ga_config["setup_log_redirect"] = " 2>&1 | tee -a %s" % ga_config["setup_log"]

try:
    if sys_argv[1] == "debug":
        debug = True
except IndexError:
    debug = False

########################################################################################################################


# shell output
def ga_setup_shelloutput_header(output, symbol, line=False):
    shellhight, shellwidth = os_popen('stty size', 'r').read().split()
    if line:
        print(symbol * (int(shellwidth) - 1))
    else:
        print("\n%s\n%s\n%s\n" % (symbol * (int(shellwidth) - 1), output, symbol * (int(shellwidth) - 1)))
        ga_setup_log_write("\n%s\n%s\n%s\n" % (symbol * 36, output, symbol * 36))


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


def ga_setup_shelloutput_text(output, style="", point=True):
    styletype = ga_setup_shelloutput_colors(style)
    if point:
        print(styletype + "%s.\n" % output + colorama_fore.RESET)
    else:
        print(styletype + "%s\n" % output + colorama_fore.RESET)
    ga_setup_log_write(output)


def ga_setup_log_write(output, special=False):
    if os_path.exists(ga_config["setup_log_path"]) is False:
        os_system("mkdir -p %s %s" % (ga_config["setup_log_path"], ga_config["setup_log_redirect"]))
    tmplog = open(ga_config["setup_log"], "a")
    if special is True:
        tmplog.write(output)
    else:
        tmplog.write("\n" + output + "\n")
    tmplog.close()


def ga_log_write_vars():
    ga_setup_log_write("Setup vars:")

    def write(thatdict):
        for key, value in sorted(thatdict.items()):
            if "pwd" in key:
                pass
            else:
                ga_setup_log_write("%s - %s, " % (key, value), True)
    write(ga_config)
    write(ga_config_server)


def ga_setup_pwd_gen(stringlength):
    chars = string_ascii_letters + string_digits + "!#-_"
    return ''.join(random_choice(chars) for i in range(stringlength))


def ga_setup_string_check(string, maxlength=10, minlength=2):
    char_blacklist = "!$§?^´`µ{}()><|\\*ÄÖÜüöä@,"
    if type(string) != str:
        ga_setup_shelloutput_text("Input error. Expected string, got %s" % type(string), style="warn")
        return False
    elif len(string) > maxlength or len(string) < minlength:
        ga_setup_shelloutput_text("Input error. Input must be between %s and %s characters long" % (minlength, maxlength), style="warn")
        return False
    elif any((char in char_blacklist) for char in string):
        ga_setup_shelloutput_text("Input error. Input must not include the following characters: %s" % char_blacklist, style="warn")
        return False
    else:
        return True


def ga_setup_fstabcheck():
    with open("/etc/fstab", 'r') as readfile:
        stringcount = readfile.read().count("Growautomation")
        if stringcount > 0:
            ga_setup_shelloutput_text("WARNING!\nYou already have one or more remote shares configured.\nIf you want"
                                      " to install new ones you should disable the old ones by editing the "
                                      "'/etc/fstab' file.\nJust add a '#' in front of the old shares or delete "
                                      "those lines to disable them", style="warn")


def ga_setup_input(prompt, default="", poss="", intype="", style="", posstype="str", max_value=20, min_value=2, neg=False):
    styletype = ga_setup_shelloutput_colors(style)

    if neg and adv is False:
        print("\n%s\nConfig: %s\n" % (prompt, default))
        return default

    def ga_setup_input_posscheck():
        while True:
            try:
                if posstype == "str":
                    usrinput = str(input(styletype + "\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default) + colorama_fore.RESET).lower() or default)
                elif posstype == "int":
                    usrinput = int(input(styletype + "\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default) + colorama_fore.RESET).lower() or default)
                if type(poss) == list:
                    if usrinput in poss:
                        break
                elif type(poss) == str:
                    if usrinput == poss:
                        break
            except KeyError:
                ga_setup_shelloutput_text("Input error. Choose one of the following: %s\n" % poss, style="warn")
        return usrinput

    whilecount = 0
    if type(default) == bool:
        while True:
            try:
                return {"true": True, "false": False, "yes": True, "no": False, "y": True, "n": False, "f": False, "t": True,
                        "": default}[input(styletype + "\n%s\n(Poss: yes/true/no/false - Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower()]
            except KeyError:
                ga_setup_shelloutput_text("WARNING: Invalid input please enter either yes/true/no/false!\n", style="warn", point=False)
    elif type(default) == str:
        if intype == "pass" and default != "":
            getpass(prompt="\n%s\n(Random: %s)\n > " % (prompt, default)) or "%s" % default
        elif intype == "pass":
            getpass(prompt="\n%s\n > " % prompt)
        elif intype == "passgen":
            usrinput = 0
            while usrinput < 8 or usrinput > 99:
                if (usrinput < 8 or usrinput > 99) and whilecount > 0:
                    ga_setup_shelloutput_text("Input error. Value should be between 8 and 99.\n", style="warn")
                whilecount += 1
                usrinput = int(input("\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default)).lower() or "%s" % default)
            return usrinput
        elif intype == "free":
            while True:
                if poss != "":
                    usrinput = ga_setup_input_posscheck()
                elif default == "":
                    usrinput = input(styletype + "\n%s\n > " % prompt + colorama_fore.RESET).lower() or default
                else:
                    usrinput = input(styletype + "\n%s\n(Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower() or default
                if ga_setup_string_check(usrinput, maxlength=max_value, minlength=min_value):
                    return usrinput

        elif poss != "":
            return ga_setup_input_posscheck()
        elif default != "":
            return str(input(styletype + "\n%s\n(Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower() or "%s" % default)
        else:
            return str(input(styletype + "\n%s\n > " % prompt + colorama_fore.RESET).lower())
    elif type(default) == int:
        min_value, max_value = 1, 10000
        usrinput = 0
        while usrinput < int(min_value) or usrinput > int(max_value):
            if (usrinput < int(min_value) or usrinput > int(max_value)) and whilecount > 0:
                ga_setup_shelloutput_text("Input error. Value should be between 1 and 1209600.\n", style="warn")
            whilecount += 1
            usrinput = int(input("\n%s\n(Default: %s)\n > " % (prompt, default)).lower() or "%s" % default)
        return usrinput
    else:
        raise KeyError


def ga_mnt_creds(outtype, inputstr=""):
    if outtype == "usr":
        return ga_setup_input("Provide username for share authentication.", inputstr)
    elif outtype == "pwd":
        return ga_setup_input("Provide password for share authentication.", inputstr, intype="pass")
    elif outtype == "dom":
        return ga_setup_input("Provide domain for share authentication.", "workgroup")


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


class ga_mysql(object):
    def __init__(self, dbinput, user="", pwd="", query=False, basic=None):
        self.input = dbinput
        self.user = user
        self.pwd = pwd
        self.query = query
        self.basic = basic
        self.start()

    def start(self):
        if debug:
            print(type(self.input), self.input)
        if type(self.input) == str:
            output = self.execute(self.input)
            if debug:
                print(type(output), output)
            return output
        elif type(self.input) == list:
            output_list = []
            anyfalse = True
            for command in self.input:
                if debug:
                    print(type(command), command)
                output = self.execute(command)
                output_list.append(output)
                if debug:
                    print(type(output), output)
                if output is False:
                    anyfalse = False
            if anyfalse is False:
                return False
            return output_list

    def unixsock(self):
        global ga_config
        sql_sock = "/var/run/mysqld/mysqld.sock"
        if os_path.exists(sql_sock) is False:
            output, error = subprocess_popen(["systemctl status mysql.service | grep 'Active:'"], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
            outputstr = output.decode("ascii")
            if outputstr.find("Active: inactive") != -1:
                os_system("systemctl start mysql.service %s" % ga_config["setup_log_redirect"])
            if os_path.exists(sql_sock) is False:
                sql_customsock = ga_setup_input("Mysql was unable to find the mysql unix socket file at %s.\nThe path can be found in mysql via "
                                                "the command:\n > show variables like 'socket;'\nProvide the correct path to it.")
                ga_config["sql_sock"] = sql_customsock
                return sql_customsock
        else:
            ga_config["sql_sock"] = sql_sock
            return sql_sock

    def execute(self, command):
        if self.user == "":
            self.user = "root"
        if self.basic is not None:
            if self.user == "root":
                connection = mysql.connector.connect(unix_socket=self.unixsock(), user=self.user)
            else:
                connection = mysql.connector.connect(unix_socket=self.unixsock(), user=self.user, passwd=self.pwd)
        elif ga_config["sql_server_ip"] == "127.0.0.1":
            connection = mysql.connector.connect(host=ga_config["sql_server_ip"], port=ga_config["sql_server_port"], unix_socket=self.unixsock(), user=self.user, passwd=self.pwd)
        else:
            connection = mysql.connector.connect(host=ga_config["sql_server_ip"], port=ga_config["sql_server_port"], user=self.user, passwd=self.pwd)
        try:
            cursor = connection.cursor(buffered=True)
            cursor.execute(command)
            if self.query is True:
                data = cursor.fetchall()
                if cursor.rowcount < 1:
                    data = False
                    ga_setup_log_write("MySql did not receive any data.\nCommand: '%s'" % command)
            else:
                connection.commit()
            cursor.close()
            connection.close()
            if self.query is True:
                return data
            else:
                return True
        except (mysql.connector.Error, mysql.connector.errors.ProgrammingError) as error:
            connection.rollback()
            ga_setup_log_write("MySql was unable to perform action:\n'%s'\nError message:\n%s" % (command, error))
            ga_setup_shelloutput_text("MySql was unable to perform action '%s'.\nError message:\n%s" % (command, error), style="warn")
            return False

    def find(self, findstr):
        data = str(self.execute(self.input))
        return data.find(findstr)


def ga_mysql_conntest(dbuser="", dbpwd="", check_ga_exists=False, local=False, check_system=False, write=False):
    if (dbuser == "" or dbuser == "root") and ga_config["sql_server_ip"] == "127.0.0.1":
        if check_ga_exists is True:
            sqltest = ga_mysql("SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;", query=True, basic=True).start()
        else:
            sqltest = ga_mysql("SELECT * FROM mysql.help_category LIMIT 10;", query=True, basic=True).start()
    elif dbpwd == "":
        ga_setup_shelloutput_text("SQL connection failed. No password provided and not root.", style="warn")
        ga_setup_log_write("Sql connection test failed!\nNo password provided and not root.\nServer: %s, user: %s" % (ga_config["sql_server_ip"], dbuser))
        return False
    elif local and check_system:
        sqltest = ga_mysql("SELECT * FROM mysql.help_category LIMIT 10;", dbuser, dbpwd, query=True, basic=True).start()
    elif local:
        if write:
            sqltest = ga_mysql("INSERT INTO ga.Data (agent,data,device) VALUES ('setup','conntest','none');", dbuser, dbpwd, basic=True).start()
        else:
            sqltest = ga_mysql("SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;", dbuser, dbpwd, query=True, basic=True).start()
    else:
        sqltest = ga_mysql("SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;", dbuser, dbpwd, query=True).start()
    if type(sqltest) == list:
        ga_setup_shelloutput_text("SQL connection verified", style="succ")
        return True
    elif type(sqltest) == bool and sqltest:
        ga_setup_shelloutput_text("SQL connection verified", style="succ")
        return sqltest
    else:
        ga_setup_shelloutput_text("SQL connection failed", style="warn")
        ga_setup_log_write("Sql connection test failed:\nServer: %s, user: %s\nSql output: %s" % (ga_config["sql_server_ip"], dbuser, sqltest))
        return False


class ga_setup_configparser_mysql(object):
    def __init__(self, search, user, pwd, hostname):
        self.search = search
        self.user = user
        self.pwd = pwd
        self.hostname = hostname

    def __repr__(self):
        if type(self.search) == list:
            itemdatadict = {}
            for item in self.search:
                itemdatadict[item] = ga_mysql(self.command(item), self.user, self.pwd, True)
            return itemdatadict
        elif type(self.search) == str:
            data = ga_mysql(self.command(self.search), self.user, self.pwd, True)
            return data
    
    def command(self, setting):
        return "SELECT data FROM ga.Setting WHERE belonging = '%s' and setting = '%s';" % (self.hostname, setting)


def ga_setup_configparser_file(file, text):
    tmpfile = open(file, 'r')
    for line in tmpfile.readlines():
        if line.find(text) != -1:
            try:
                split = line.split("=")[1].strip()
                return split
            except (IndexError, ValueError):
                return False
    return False


def ga_setup_exit(shell, log):
    ga_log_write_vars()
    ga_setup_log_write("\nExit. %s.\n\n" % log)
    raise SystemExit(ga_setup_shelloutput_colors("err") + "\n%s!\nYou can find the full setup log at %s.\n\n" % (shell, ga_config["setup_log"]) + colorama_fore.RESET)


########################################################################################################################


ga_setup_log_write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# prechecks
ga_setup_shelloutput_header("Installing setup dependencies", "#")

os_system("apt-get -y install python3-pip && python3 -m pip install mysql-connector-python colorama %s" % ga_config["setup_log_redirect"])
import mysql.connector
from colorama import Fore as colorama_fore


# check for root privileges
if os_getuid() != 0:
    ga_setup_exit("This script needs to be run with root privileges", "Script not started as root")

else:
    ga_setup_shelloutput_header("Starting Growautomation installation script\n"
                                "The newest versions can be found at: https://git.growautomation.at", "#")
    ga_config["setup_warning_accept"] = ga_setup_input("WARNING!\n\nWe recommend using this installation script on dedicated systems.\n"
                                                       "This installation script won't check your already installed programs for compatibility problems.\n"
                                                       "If you already use web-/database or other complex software on this system you should back it up before installing this software.\n"
                                                       "We assume no liability for problems that may be caused by this installation!\n\n"
                                                       "Accept the risk if you want to continue.", False, style="warn")
    if ga_config["setup_warning_accept"] is False:
        ga_setup_exit("Script cancelled by user\nYou can also install this software manually through the setup "
                      "manual.\nIt can be found at: https://git.growautomation.at/tree/master/manual",
                      "Setupwarning not accepted by user")

ga_setup_shelloutput_header("Checking if growautomation is already installed on the system", "#")

# check if growautomation is already installed

ga_config["setup_old_version_file"] = os_path.exists(ga_config["setup_version_file"])
if ga_config["setup_old_version_file"] is True:
    ga_setup_shelloutput_text("Growautomation version file exists", style="info")
    ga_config["setup_old_version"] = ga_setup_configparser_file(ga_config["setup_version_file"], "version=")
else:
    ga_setup_shelloutput_text("No growautomation version file found", style="info")
ga_config["setup_old_root"] = os_path.exists("/etc/growautomation")
if ga_config["setup_old_root"] is True:
    ga_setup_shelloutput_text("Growautomation default root path exists", style="info")
else:
    ga_setup_shelloutput_text("No growautomation default root path exists", style="info")
if ga_mysql("SHOW DATABASES;", query=True, basic=True).find("ga") != -1:
    ga_config["setup_old_db"] = True
    ga_setup_shelloutput_text("Growautomation database exists", style="info")
else:
    ga_config["setup_old_db"] = False
    ga_setup_shelloutput_text("No growautomation database found", style="info")

if ga_config["setup_old_version_file"] is True or ga_config["setup_old_root"] is True or ga_config["setup_old_db"] is True:
    def ga_config_vars_oldversion_replace():
        global ga_config
        ga_config["setup_old"] = True
        ga_config["setup_old_replace"] = ga_setup_input("Do you want to replace your current growautomation installation?", False, style="warn")
        if ga_config["setup_old_replace"] is True:
            ga_config["setup_old_replace_migrate"] = ga_setup_input("Should we try to keep your old configuration and data?", False, style="warn")
            if ga_config["setup_old_replace_migrate"] is True:
                ga_config["setup_fresh"] = False
            else:
                ga_config["setup_fresh"] = True
        if ga_config["setup_old_replace"] is True:
            ga_config["setup_old_backup"] = ga_setup_input("Do you want to backup your old growautomation installation?", True)
        else:
            ga_setup_exit("Stopping script. Current installation should not be overwritten",
                          "User chose that currently installed ga should not be overwritten")
    if ga_config["setup_old_version_file"] is True:
        if ga_config["setup_old_version"] is None:
            if ga_config["setup_old_root"] is True:
                ga_setup_shelloutput_text("Growautomation is currently installed. But its version number could not be found", style="warn")
                ga_config_vars_oldversion_replace()
            elif ga_config["setup_old_db"] is True:
                ga_config_vars_oldversion_replace()
            else:
                ga_setup_shelloutput_text("Error verifying existing growautomation installation. Installing as new", style="warn")
                ga_config["setup_old"] = False
        else:
            ga_setup_shelloutput_text("A version of growautomation is/was already installed on this system!\n\n"
                                      "Installed version: %s\nReplace version: %s" % (ga_config["setup_old_version"], ga_config["version"]))
            ga_config_vars_oldversion_replace()
    elif ga_config["setup_old_root"] is True:
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
    if ga_config["setup_fresh"] is True:
        ga_setup_shelloutput_text("The configuration and data will be overwritten", style="warn")
    else:
        ga_setup_shelloutput_text("The configuration and data will be migrated", style="succ")

########################################################################################################################

# setup vars
ga_setup_shelloutput_header("Retrieving setup configuration through user input", "#")

adv = ga_setup_input("Do you want to have advanced options in this setup?", False)


def ga_config_var_base():
    global ga_config
    ga_setup_shelloutput_header("Checking basic information", "-")

    def ga_config_var_base_name():
        global ga_config
        if ga_config["setuptype"] == "agent":
            ga_config["hostname"] = ga_setup_input("Provide the name of this growautomation agent as configured on the server.", "gacon01")
        elif ga_config["setuptype"] == "server":
            ga_config["hostname"] = "gaserver"
        elif ga_config["setuptype"] == "standalone":
            ga_config["hostname"] = "gacon01"

    if ga_config["setup_fresh"] is False:
        ga_config["path_root"] = ga_setup_configparser_file(ga_config["setup_version_file"], "path_root=")
        ga_config["hostname"] = ga_setup_configparser_file(ga_config["setup_version_file"], "hostname=")
        ga_config["setuptype"] = ga_setup_configparser_file(ga_config["setup_version_file"], "setuptype=")
        ga_config["log_level"] = ga_setup_configparser_file(ga_config["setup_version_file"], "log_level=")
        if ga_config["path_root"] is False:
            ga_setup_shelloutput_text("Growautomation rootpath not found in old versionfile", style="warn")
            ga_config["path_root"] = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation")
            if ga_config["setup_old_backup"] is True:
                ga_config["path_old_root"] = ga_setup_input("Please provide the install path of your current installation. (for backup)", "/etc/growautomation")
            else:
                ga_config["path_old_root"] = False

        if ga_config["hostname"] is False:
            ga_setup_shelloutput_text("Growautomation hostname not found in old versionfile", style="warn")
            ga_config_var_base_name()

        if ga_config["setuptype"] is False:
            ga_setup_shelloutput_text("Growautomation setuptype not found in old versionfile.\n\n"
                                      "WARNING!\nTo keep your old configuration the setuptype must be the same as before", style="warn")
            ga_config["setuptype"] = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone", "agent/standalone/server")
            if ga_config["setup_old_backup"] is False:
                ga_setup_shelloutput_text("Turning on migration backup option - just in case", style="info")
                ga_config["setup_old_backup"] = True

    if ga_config["setup_fresh"] is True:
        ga_config["setuptype"] = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone", ["agent", "standalone", "server"])
        if ga_config["setuptype"] == "agent":
            ga_config["setup_yousure"] = ga_setup_input("WARNING!\nYou should install/update the growautomation server component before the agent because of dependencies.\n"
                                                        "Find more information about the creation of new agents at:\nhttps://git.growautomation.at/tree/master/manual/agent\n\n"
                                                        "Agree if you have already installed/updated the ga server or disagree to stop the installation.", False, style="warn")
            if ga_config["setup_yousure"] is False:
                ga_setup_exit("Stopping script. Server was not installed before agent", "User has not installed the server before the agent")
        ga_config["path_root"] = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation", neg=True)
        if ga_config["setup_old"] and ga_config["setup_old_backup"] is True:
            ga_config["path_old_root"] = ga_setup_input("Please provide the install path of your current installation (for backup).", "/etc/growautomation")
        else:
            ga_config["path_old_root"] = False
        ga_config["log_level"] = ga_setup_input("Want to change the log level?", "1", ["0", "1", "2", "3", "4", "5"], neg=True)
        ga_config_var_base_name()

    if ga_config["setuptype"] == "server" or ga_config["setuptype"] == "standalone":
        ga_config["setup_type_ss"] = True
    else:
        ga_config["setup_type_ss"] = False

    if ga_config["setuptype"] == "agent" or ga_config["setuptype"] == "standalone":
        ga_config["setup_type_as"] = True
    else:
        ga_config["setup_type_as"] = False


def ga_config_var_setup():
    global ga_config
    ga_setup_shelloutput_header("Checking setup options", "-")
    ga_config["setup_pwd_length"] = int(ga_setup_input("This setup will generate random passwords for you.\nPlease define the length of those random passwords!", "12", "8-99", "passgen", neg=True))

    ga_config["setup_ca"] = ga_setup_input("Need to import internal ca certificate for git/pip? Mainly needed if your firewall uses ssl inspection.", False, neg=True)

    if ga_config["setup_ca"] is True:
        ga_config["setup_ca_path"] = ga_setup_input("Provide path to the ca file.", "/etc/ssl/certs/internalca.cer")
    else:
        ga_config["setup_ca_path"] = "notprovided"

    ga_config["setup_linuxupgrade"] = ga_setup_input("Want to upgrade your existing software packages before growautomation installation?", True, neg=True)


def ga_config_var_db():
    global ga_config
    ga_setup_shelloutput_header("Checking for database credentials", "-")
    whilecount = 0
    if ga_config["setuptype"] == "agent":
        if ga_config["setup_fresh"] is True:
            ga_config["sql_agent_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            ga_config["sql_local_user"] = "agent"
            ga_config["sql_local_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            while True:
                whilecount += 1
                ga_config["sql_server_ip"] = ga_setup_input("Provide the ip address of the growautomation server.", "192.168.0.201")
                ga_config["sql_server_port"] = ga_setup_input("Provide the mysql port of the growautomation server.", "3306")
                ga_setup_shelloutput_text("The following credentials can be found in the serverfile '$garoot/core/core.conf'")
                ga_config["sql_agent_user"] = ga_setup_input("Please provide the user used to connect to the database.", ga_config["hostname"])
                ga_config["sql_agent_pwd"] = ga_setup_input("Please provide the password used to connect to the database.", ga_config["sql_agent_pwd"], intype="pass")
                if ga_mysql_conntest(ga_config["sql_agent_user"], ga_config["sql_agent_pwd"]) is True:
                    ga_config["sql_server_repl_user"] = ga_setup_input("Please provide sql replication user.", ga_config["hostname"] + "replica")
                    ga_config["sql_server_repl_pwd"] = ga_setup_input("Please provide sql replication password.", ga_config["sql_agent_pwd"])
                    break
        else:
            ga_config["sql_local_user"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_local_user=")
            if ga_config["sql_local_user"] is False:
                ga_config["sql_local_user"] = "agent"
            ga_config["sql_local_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_local_pwd=")
            if ga_config["sql_local_pwd"] is False:
                ga_config["sql_local_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            ga_config["sql_agent_user"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_agent_user=")
            ga_config["sql_agent_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_agent_pwd=")

            while True:
                if whilecount > 0:
                    ga_setup_shelloutput_text("You can reset/configure the agent database credentials on the "
                                              "growautomation server. Details can be found in the manual: "
                                              "https://git.growautomation.at/tree/master/manual", style="info")
                ga_config["sql_agent_user"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_agent_user=")
                ga_config["sql_agent_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_agent_pwd=")
                ga_config["sql_server_ip"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_server_ip=")
                if ga_mysql_conntest(ga_config["sql_agent_user"], ga_config["sql_agent_pwd"]) is True:
                    break
            return True

    else:
        ga_config["sql_server_ip"] = "127.0.0.1"
        ga_config["sql_server_port"] = "3306"
        if ga_config["setup_fresh"] is True:
            ga_config["sql_admin_user"] = ga_setup_input("How should the growautomation database admin user be named?", "gadmin", neg=True)
            ga_config["sql_admin_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            if ga_mysql_conntest() is False:
                ga_setup_shelloutput_text("Unable to connect to local mysql server with root privileges", style="err")
        else:
            ga_config["sql_admin_user"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_admin_user=")
            ga_config["sql_admin_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_admin_pwd=")
            while True:
                if whilecount > 0:
                    ga_setup_shelloutput_text("Please try again.\nThe following credentials can normally be found in the serverfile '$garoot/core/core.conf'", style="warn")
                if whilecount > 1:
                    ga_config["setup_sql_admin_reset"] = ga_setup_input("Do you want to reset the database admin via the setup?", False)
                    if ga_config["setup_sql_admin_reset"] is True:
                        if ga_mysql_conntest() is False:
                            ga_setup_shelloutput_text("Database admin can't be reset since the database check as root failed.\nThis could happen "
                                                      "if the growautomation database doesn't exist", style="warn")
                            ga_config["setup_sql_noaccess_proceed"] = ga_setup_input("Do you want to continue the setup anyway? The problem might maybe get fixed by the setup process.", False)
                            if ga_config["setup_sql_noaccess_proceed"] is False:
                                ga_setup_exit("All database connections failed", "User chose to exit since all database connections failed")
                            ga_config["setup_sql_admin_reset"] = False
                            if ga_config["setup_old_backup"] is False:
                                ga_setup_shelloutput_text("Turning on migration backup option - just in case", style="info")
                                ga_config["setup_old_backup"] = True
                            return "none"
                        else:
                            return "root"

                    ga_config["sql_admin_user"] = ga_setup_input("Provide the name of the growautomation database admin user.", "gadmin")
                    ga_config["sql_admin_pwd"] = ga_setup_input("Please provide the password used to connect to the database.", intype="pass")
                    if ga_mysql_conntest(ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], local=True) is True:
                        break
                    whilecount += 1

            return True


def ga_config_var_certs():
    global ga_config
    ga_setup_shelloutput_header("Checking certificate information", "-")
    if ga_config["setuptype"] == "agent":
        ga_setup_shelloutput_text("The following certificates can be found in the serverpath '$garoot/ca/certs/'\n", style="info")
        ga_config["sql_ca"] = ga_setup_input("Provide the path to the ca-certificate from your ga-server.", "%s/ssl/ca.cer.pem" % ga_config["path_root"])
        ga_config["sql_cert"] = ga_setup_input("Provide the path to the agent server certificate.", "%s/ssl/%s.cer.pem" % (ga_config["path_root"], ga_config["hostname"]))
        ga_config["sql_key"] = ga_setup_input("Provide the path to the agent server key.", "%s/ssl/%s.key.pem" % (ga_config["path_root"], ga_config["hostname"]))


########################################################################################################################
# Basic config
ga_config_var_base()
ga_config_var_setup()
ga_config_var_db()


########################################################################################################################
# Config migration from old installation


if ga_config["setup_fresh"] is False:
    ga_setup_shelloutput_header("Retrieving existing configuration from database", "-")
    ga_config_list_agent = ["backup", "path_backup", "mnt_backup", "mnt_backup_type", "mnt_backup_server",
                            "mnt_backup_share", "mnt_backup_usr", "mnt_backup_pwd", "mnt_backup_dom", "path_log",
                            "mnt_log", "mnt_shared_creds", "mnt_shared_server", "mnt_shared_type", "mnt_log_type",
                            "mnt_log_server", "mnt_log_share", "mnt_log_usr", "mnt_log_pwd", "mnt_log_dom"]
    ga_config_list_server = []
    if ga_config["setuptype"] == "server":
        ga_configdict_sql = ga_setup_configparser_mysql("ga_config_list_server", ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], ga_config["hostname"])
    elif ga_config["setuptype"] == "standalone":
        ga_configdict_sql_agent = ga_setup_configparser_mysql("ga_config_list_agent", ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], ga_config["hostname"])
        ga_configdict_sql_server = ga_setup_configparser_mysql("ga_config_list_server", ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], ga_config["hostname"])
        ga_configdict_sql = {**ga_configdict_sql_agent, **ga_configdict_sql_server}
    else:
        ga_configdict_sql = ga_setup_configparser_mysql("ga_config_list_agent", ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], ga_config["hostname"])

    ga_config = {**ga_configdict_sql, **ga_config}

########################################################################################################################
# Configuration without migration
if ga_config["setup_fresh"] is True:
    ga_setup_shelloutput_header("Checking directory information", "-")

    ga_config["path_backup"] = ga_setup_input("Want to choose a custom backup path?", "/mnt/growautomation/backup/", neg=True)
    ga_config["backup"] = ga_setup_input("Want to enable backup?", True, neg=True)
    if ga_config["backup"] is True:
        ga_config["mnt_backup"] = ga_setup_input("Want to mount remote share as backup destination? Smb and nfs available.", False, neg=True)
        if ga_config["mnt_backup"] is True:
            ga_setup_fstabcheck()
            ga_config["mnt_backup_type"] = ga_setup_input("Mount nfs or smb/cifs share as backup destination?", "nfs", ["nfs", "cifs"])
            ga_config["mnt_backup_srv"] = ga_setup_input("Provide the server ip.", "192.168.0.201")
            ga_config["mnt_backup_share"] = ga_setup_input("Provide the share name.", "growautomation/backup")
            if ga_config["mnt_backup_type"] == "cifs":
                ga_mnt_backup_tmppwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
                ga_config["mnt_backup_user"] = ga_mnt_creds("usr", "gabackup")
                ga_config["mnt_backup_pwd"] = ga_mnt_creds("pwd", ga_mnt_backup_tmppwd)
                ga_config["mnt_backup_dom"] = ga_mnt_creds("dom")
            # else:
            #     ga_setup_shelloutput_text("Not mounting remote share for backup!\nCause: No sharetype, "
            #                               "serverip or sharename provided.\n")
    else:
        ga_config["mnt_backup"] = False
        ga_config["mnt_backup_type"] = "False"
    
    ga_config["path_log"] = ga_setup_input("Want to choose a custom log path?", "/var/log/growautomation", neg=True)
    ga_config["mnt_log"] = ga_setup_input("Want to mount remote share as log destination? Smb and nfs available.", False, neg=True)
    if ga_config["mnt_log"] is True:
        ga_setup_fstabcheck()
        if ga_config["mnt_backup"] is True:
            ga_config["mnt_samecreds"] = ga_setup_input("Use same server as for remote backup?", True)
            if ga_config["mnt_samecreds"] is True:
                ga_config["mnt_log_type"] = ga_config["mnt_backup_type"]
                ga_config["mnt_log_server"] = ga_config["mnt_backup_srv"]
        else:
            ga_config["mnt_log_type"] = ga_setup_input("Mount nfs or smb/cifs share as log destination?", "nfs", ["nfs", "cifs"])
            ga_config["mnt_log_server"] = ga_setup_input("Provide the server ip.", "192.168.0.201")
        ga_config["mnt_log_share"] = ga_setup_input("Provide the share name.", "growautomation/log")
    
        if ga_config["mnt_log_type"] == "cifs":

            def ga_mnt_log_creds():
                global ga_config
                ga_config["mnt_backup_user"] = ga_mnt_creds("usr", "galog")
                ga_config["mnt_backup_pwd"] = ga_mnt_creds("pwd", ga_setup_pwd_gen(ga_config["setup_pwd_length"]))
                ga_config["mnt_backup_dom"] = ga_mnt_creds("dom")

            if ga_config["mnt_backup"] is True and ga_config["mnt_backup_type"] == "cifs" and \
                    ga_config["mnt_samecreds"] is True:
                ga_config["mnt_samecreds"] = ga_setup_input("Use same share credentials as for remote backup?", True)
                if ga_config["mnt_samecreds"] is True:
                    ga_config["mnt_log_user"] = ga_config["mnt_backup_user"]
                    ga_config["ga_mnt_log_pwd"] = ga_config["mnt_backup_pwd"]
                    ga_config["ga_mnt_log_dom"] = ga_config["mnt_backup_dom"]
                else:
                    ga_mnt_log_creds()
            else:
                ga_mnt_log_creds()
    else:
        ga_config["mnt_log_type"] = "False"  # for nfs/cifs apt installation

########################################################################################################################
# always vars
if ga_config["setuptype"] == "agent":
    ga_config_var_certs()

########################################################################################################################

ga_setup_shelloutput_header("Logging setup information", "-")

ga_log_write_vars()

ga_setup_shelloutput_text("Thank you for providing the setup information.\nThe installation will start now")

########################################################################################################################


# functions
def ga_foldercreate(path):
    if os_path.exists(path) is False:
        os_system("mkdir -p %s && chown -R growautomation:growautomation %s %s" % (path, path, ga_config["setup_log_redirect"]))


def ga_setup_config_file(opentype, openinput, openfile=""):
    if openfile == "":
        file = "%s/core/core.conf" % ga_config["path_root"]
    else:
        file = openfile
    file_open = open(file, opentype)
    if opentype == "a" or opentype == "w":
        file_open.write(openinput)
        os_system("chown growautomation:growautomation %s && chmod 440 %s %s" % (file, file, ga_config["setup_log_redirect"]))
    elif opentype == "r":
        return file_open.readlines()
    file_open.close()
    

def ga_mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
    ga_setup_shelloutput_header("Mounting %s share" % mname, "-")
    if mtype == "cifs":
        mcreds = "username=%s,password=%s,domain=%s" % (muser, mpwd, mdom)
    else:
        mcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write("#Growautomation %s mount\n//%s/%s %s %s %s 0 0\n\n" % (mname, msrv, mshr, mpath, mtype, mcreds))
    ga_fstab.close()
    os_system("mount -a %s" % ga_config["setup_log_redirect"])


def ga_replaceline(file, replace, insert):
    os_system("sed -i 's/%s/%s/p' %s %s" % (replace, insert, file, ga_config["setup_log_redirect"]))


def ga_openssl_setup():
    ga_foldercreate("%s/ca/private" % ga_config["path_root"])
    ga_foldercreate("%s/ca/certs" % ga_config["path_root"])
    ga_foldercreate("%s/ca/crl" % ga_config["path_root"])
    os_system("chmod 770 %s/ca/private %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))
    ga_replaceline("%s/ca/openssl.cnf", "= /root/ca", "= %s/ca") % (ga_config["path_root"], ga_config["path_root"])
    ga_setup_shelloutput_header("Creating root certificate", "-")
    os_system("openssl genrsa -aes256 -out %s/ca/private/ca.key.pem 4096 && chmod 400 %s/ca/private/ca.key.pe %s"
              % (ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))
    os_system("openssl req -config %s/ca/openssl.cnf -key %s/ca/private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out %s/ca/certs/ca.cer.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))


def ga_openssl_server_cert(certname):
    ga_setup_shelloutput_header("Generating server certificate", "-")
    os_system("openssl genrsa -aes256 -out %s/ca/private/%s.key.pem 2048 %s" % (ga_config["path_root"], certname, ga_config["setup_log_redirect"]))
    os_system("eq -config %s/ca/openssl.cnf -key %s/ca/private/%s.key.pem -new -sha256 -out %s/ca/csr/%s.csr.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], certname, ga_config["path_root"], certname, ga_config["setup_log_redirect"]))
    os_system("openssl ca -config %s/ca/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 -in %s/ca/csr/%s.csr.pem -out %s/ca/certs/%s.cert.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], certname, ga_config["path_root"], certname, ga_config["setup_log_redirect"]))


def ga_sql_all():
    ga_setup_shelloutput_header("Starting sql setup", "#")
    ga_sql_backup_pwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
    ga_setup_shelloutput_text("Creating mysql backup user")
    ga_mysql(["DROP USER 'gabackup'@'localhost';", "CREATE USER 'gabackup'@'localhost' IDENTIFIED BY '%s';" % ga_sql_backup_pwd,
              "GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON *.* TO 'gabackup'@'localhost' IDENTIFIED BY '%s';" % ga_sql_backup_pwd, "FLUSH PRIVILEGES;"], basic=True)
    ga_mysql_conntest("gabackup", ga_sql_backup_pwd, local=True, check_system=True)
    ga_setup_shelloutput_header("Setting up mysql db", "-")
    ga_setup_shelloutput_text("Set a secure password and answer all other questions with Y/yes", style="info")
    ga_setup_shelloutput_text("Example random password: %s" % ga_setup_pwd_gen(ga_config["setup_pwd_length"]), style="info", point=False)
    ga_setup_shelloutput_text("\nMySql will not ask for the password if you start it locally (mysql -u root) with sudo/root privileges (set & forget)", style="info")
    os_system("mysql_secure_installation %s" % ga_config["setup_log_redirect"])

    ga_setup_config_file("w", "[mysqldump]\nuser=gabackup\npassword=%s\n" % ga_sql_backup_pwd, "/etc/mysql/conf.d/ga.mysqldump.cnf")

    os_system("usermod -a -G growautomation mysql %s" % ga_config["setup_log_redirect"])
    ga_foldercreate("/etc/mysql/ssl")


def ga_sql_server():
    ga_setup_shelloutput_header("Configuring sql as growautomation server", "#")
    os_system("mysql -u root < /tmp/controller/setup/server/ga_db_setup.sql %s" % ga_config["setup_log_redirect"])
    if ga_config["setuptype"] == "server":
        os_system("cp /tmp/controller/setup/server/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])
    elif ga_config["setuptype"] == "standalone":
        os_system("cp /tmp/controller/setup/standalone/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])

    ga_setup_shelloutput_text("Creating mysql admin user")
    ga_mysql(["DROP USER '%s'@'%s';" % (ga_config["sql_admin_user"], "%"), "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (ga_config["sql_admin_user"], "%", ga_config["sql_admin_pwd"]),
              "GRANT ALL ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (ga_config["sql_admin_user"], "%", ga_config["sql_admin_pwd"]), "FLUSH PRIVILEGES;"])
    ga_mysql_conntest(ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], local=True, write=True)
    ga_setup_config_file("a", "\n[db_growautomation]\nsql_admin_user=%s\nsql_admin_pwd=%s\n" % (ga_config["sql_admin_user"], ga_config["sql_admin_pwd"]))

    if ga_config["setuptype"] == "server":
        ga_setup_shelloutput_text("Creating mysql server certificate")
        ga_openssl_server_cert("mysql")
        os_system("ln -s %s/ca/certs/ca.cer.pem /etc/mysql/ssl/cacert.pem && ln -s %s/ca/certs/mysql.cer.pem /etc/mysql/ssl/server-cert.pem && "
                  "ln -s %s/ca/private/mysql.key.pem /etc/mysql/ssl/server-key.pem %s"
                  % (ga_config["path_root"], ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))


def ga_sql_agent():
    ga_setup_shelloutput_header("Configuring sql as growautomation agent", "#")
    os_system("cp /tmp/controller/setup/agent/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])
    ga_setup_shelloutput_text("Configuring mysql master-slave setup")
    ga_setup_shelloutput_text("Replicating server db to agent for the first time", style="info")
    os_system("mysqldump -h %s --port %s -u %s -p %s ga > /tmp/ga.dbdump.sql && mysql -u root ga < /tmp/ga.dbdump.sql "
              "%s" % (ga_config["sql_server_ip"], ga_config["sql_server_port"], ga_config["sql_agent_user"], ga_config["sql_agent_pwd"], ga_config["setup_log_redirect"]))
    tmpsearchdepth = 500
    tmpfile = open("/tmp/ga.dbdump.sql", 'r')
    tmplines = tmpfile.readlines()[:tmpsearchdepth]
    for line in tmplines:
        if line.find("Master_Log_File: ") != -1:
            ga_config["sql_server_repl_file"] = line.split("Master_Log_File: ")[1].split("\n", 1)[0]
        elif line.find("Master_Log_Pos: ") != -1:
            ga_config["sql_server_repl_pos"] = line.split("Master_Log_Pos: ")[1].split("\n", 1)[0]

    ga_sql_server_agent_id = ga_mysql("SELECT data FROM ga.Setting WHERE belonging = '%s' AND setting = 'id';" % ga_config["hostname"], ga_config["sql_agent_user"],
                                      ga_config["sql_agent_pwd"], query=True)
    ga_replaceline("/etc/mysql/mariadb.conf.d/50-server.cnf", "server-id              = 1", "server-id = %s" % (int(ga_sql_server_agent_id) + 100))
    os_system("systemctl restart mysql %s" % ga_config["setup_log_redirect"])

    ga_setup_shelloutput_header("Creating local mysql controller user (read only)", "-")
    ga_mysql(["DROP USER '%s'@'localhost';" % ga_config["sql_local_user"], "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (ga_config["sql_local_user"], ga_config["sql_local_pwd"]),
              "GRANT SELECT ON ga.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (ga_config["sql_local_user"], ga_config["sql_local_pwd"]), "FLUSH PRIVILEGES;"], basic=True)
    ga_mysql_conntest(ga_config["sql_local_user"], ga_config["sql_local_pwd"], local=True)
    ga_setup_config_file("a", "[db_local]\nsql_local_user=%s\nsql_local_pwd=%s\n[server]\nsql_agent_user=%s\nsql_agent_pwd=%s\nsql_server_ip=%s\nsql_server_port=%s"
                         % (ga_config["sql_local_user"], ga_config["sql_agent_pwd"], ga_config["sql_agent_user"], ga_config["sql_agent_pwd"], ga_config["sql_server_ip"], ga_config["sql_server_port"]))
    
    if ga_setup_keycheck(ga_config["sql_server_repl_file"]) is False or ga_setup_keycheck(ga_config["sql_server_repl_pos"]) is False:
        ga_setup_shelloutput_text("SQL master slave configuration not possible due to missing information.\nShould be found in mysql dump from server "
                                  "(searching in first %s lines).\nNot found: 'Master_Log_File:'/'Master_Log_Pos:'" % tmpsearchdepth, style="warn")
    else:
        ga_mysql(["CHANGE MASTER TO MASTER_HOST='%s', MASTER_USER='%s', MASTER_PASSWORD='%s', MASTER_LOG_FILE='%s', MASTER_LOG_POS=%s;"
                  % (ga_config["sql_server_ip"], ga_config["sql_server_repl_user"], ga_config["sql_server_repl_pwd"], ga_config["sql_server_repl_file"],
                     ga_config["sql_server_repl_pos"]), " START SLAVE;", " SHOW SLAVE STATUS;"])
        # \G

    ga_setup_shelloutput_header("Linking mysql certificate", "-")
    os_system("ln -s %s /etc/mysql/ssl/cacert.pem && ln -s %s /etc/mysql/ssl/server-cert.pem && ln -s %s /etc/mysql/ssl/server-key.pem %s"
              % (ga_config["sql_ca"], ga_config["sql_cert"], ga_config["sql_key"], ga_config["setup_log_redirect"]))


def ga_sql_server_create_agent():
    ga_setup_shelloutput_header("Registering a new growautomation agent to the server", "#")
    create_agent = ga_setup_input("Do you want to register an agent to the ga-server?", True)
    if create_agent is True:
        server_agent_list = ga_mysql("SELECT name FROM ga.Object WHERE type = 'agent';", ga_config["sql_admin_user"], ga_config["sql_admin_pwd"], query=True)
        if len(server_agent_list) > 0:
            ga_setup_shelloutput_text("List of registered agents:\n%s\n" % server_agent_list, style="info")
        else:
            ga_setup_shelloutput_text("No agents are registered.\n", style="info")

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

        ga_setup_shelloutput_header("Creating mysql controller user", "-")
        create_agent_desclen = 0
        while create_agent_desclen > 50:
            if create_agent_desclen > 50:
                ga_setup_shelloutput_text("Description longer than 50 characters. Try again.", style="warn")
            create_agent_desc = ga_setup_input("Do you want to add a description to the agent?", poss="String up to 50 characters")
            create_agent_desclen = len(create_agent_desc)

        ga_mysql(["DROP USER '%s'@'%s';" % (create_agent_name, "%"), "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (create_agent_name, "%", create_agent_pwd),
                  "GRANT CREATE, DELETE, INSERT, SELECT, UPDATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (create_agent_name, "%", create_agent_pwd),
                  "FLUSH PRIVILEGES;", "INSERT INTO ga.Agent (author, controller, description) VALUES (%s, %s, %s);"
                  % ("gasetup", create_agent_name, create_agent_desc)], ga_config["sql_admin_user"], ga_config["sql_admin_pwd"])

        create_replica_usr = create_agent_name + "replica"
        create_replica_pwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
        ga_mysql(["DROP USER '%s'@'%s';" % (create_replica_usr, "%"), "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (create_replica_usr, "%", create_replica_pwd),
                  "GRANT REPLICATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (create_replica_usr, "%", create_replica_pwd),
                  "FLUSH PRIVILEGES;"], ga_config["sql_admin_user"], ga_config["sql_admin_pwd"])

        ga_setup_config_file("a", "[db_agent_%s]\nsql_server_ip=%s\nsql_server_port=%s\nsql_agent_user=%s\nsql_agent_pwd=%s\nsql_replica_user=%s\nsql_replica_pwd=%s"
                             % (create_agent_name, ga_config["sql_server_ip"], ga_config["sql_server_port"], create_agent_name, create_agent_pwd, create_replica_usr, create_replica_pwd))

        ga_setup_shelloutput_header("Creating mysql agent certificate\n", "-")
        ga_openssl_server_cert(create_agent_name)


########################################################################################################################


# install packages
def ga_setup_apt():
    ga_setup_shelloutput_header("Installing software packages", "#")
    os_system("apt-get update" + ga_config["setup_log_redirect"])
    if ga_config["setup_linuxupgrade"] is True:
        os_system("apt-get -y dist-upgrade && apt-get -y upgrade %s && apt -y autoremove" % ga_config["setup_log_redirect"])

    os_system("apt-get -y install python3 mariadb-server mariadb-client git %s" % ga_config["setup_log_redirect"])

    if ga_config["setup_type_as"] is True:
        os_system("apt-get -y install python3 python3-pip python3-dev python-smbus git %s" % ga_config["setup_log_redirect"])
    else:
        os_system("apt-get -y install openssl %s" % ga_config["setup_log_redirect"])

    if (ga_config["mnt_backup"] or ga_config["mnt_log"]) is True:
        if ga_config["mnt_backup_type"] == "nfs" or ga_config["mnt_log_type"] == "nfs":
            os_system("apt-get -y install nfs-common %s" % ga_config["setup_log_redirect"])
        elif ga_config["mnt_backup_type"] == "cifs" or ga_config["mnt_log_type"] == "cifs":
            os_system("apt-get -y install cifs-utils %s" % ga_config["setup_log_redirect"])


def ga_setup_pip():
    if ga_config["setup_ca"] is True:
        os_system("git core --global http.sslCAInfo %s && python3 -m pip core set global.cert %s %s" % (ga_config["setup_ca_path"], ga_config["setup_ca_path"], ga_config["setup_log_redirect"]))
    ga_setup_shelloutput_header("Installing python packages", "-")
    os_system("python3 -m pip install mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay --default-timeout=100 %s" % ga_config["setup_log_redirect"])


ga_setup_apt()
if ga_config["setup_type_as"] is True:
    ga_setup_pip()


# folders
# Create folders
def ga_infra_oldversion_rootcheck():
    if ga_config["path_old_root"] is False:
        return ga_config["path_root"]
    else:
        return ga_config["path_old_root"]


def ga_infra_oldversion_cleanconfig():
    movedir = "/tmp/ga_setup_%s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"))
    os_system("mkdir -p %s" % movedir)
    os_system("mv %s %s %s" % (ga_infra_oldversion_rootcheck(), movedir, ga_config["setup_log_redirect"]))
    os_system("mysqldump -u root ga > /tmp/ga.dbdump_%s.sql %s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"), ga_config["setup_log_redirect"]))
    ga_mysql("DROP DATABASE ga;", basic=True)
    ga_setup_shelloutput_text("Removed old ga database")


def ga_infra_oldversion_backup():
    global ga_config
    ga_setup_shelloutput_header("Backing up old growautomation root directory and database", "-")
    oldbackup = ga_config["path_backup"] + "install_%s" % datetime.now().strftime("%Y-%m-%d_%H-%M")
    os_system("mkdir -p %s && cp -r %s %s %s" % (oldbackup, ga_infra_oldversion_rootcheck(), oldbackup, ga_config["setup_log_redirect"]))
    os_system("mv %s %s %s" % (ga_config["setup_version_file"], oldbackup, ga_config["setup_log_redirect"]))
    os_system("mysqldump -u root ga > %s/ga.dbdump.sql %s" % (oldbackup, ga_config["setup_log_redirect"]))
    ga_setup_shelloutput_text("Backupfolder: %s\n%s\nRoot backupfolder:\n%s" % (oldbackup, os_listdir(oldbackup), os_listdir(oldbackup + "/growautomation")), style="info")
    if os_path.exists(oldbackup + "/ga.dbdump.sql") is False or \
            os_path.exists(oldbackup + "/growautomation/") is False:
        ga_setup_shelloutput_text("Success of backup couldn't be verified. Please check it yourself to be sure that it was successfully created. (Strg+Z "
                                  "to get to Shell -> 'fg' to get back)\nBackuppath: %s" % oldbackup, style="warn")
        ga_config["setup_old_backup_failed_yousure"] = ga_setup_input("Please verify that you want to continue the setup", False)
    else:
        ga_config["setup_old_backup_failed_yousure"] = True
    ga_infra_oldversion_cleanconfig()


def ga_setup_infra_mounts():
    if ga_config["mnt_backup"] is True or ga_config["mnt_log"] is True:
        ga_setup_shelloutput_header("Mounting shares", "#")
        if ga_config["mnt_backup"] is True:
            ga_mounts("backup", ga_config["mnt_backup_user"], ga_config["mnt_backup_pwd"], ga_config["mnt_backup_dom"], ga_config["mnt_backup_srv"],
                      ga_config["mnt_backup_share"], ga_config["path_backup"], ga_config["mnt_backup_type"])
        if ga_config["mnt_log"] is True:
            ga_mounts("log", ga_config["mnt_log_user"], ga_config["ga_mnt_log_pwd"], ga_config["ga_mnt_log_dom"], ga_config["mnt_log_server"], ga_config["mnt_log_share"],
                      ga_config["path_log"], ga_config["mnt_log_type"])


def ga_setup_infra():
    ga_setup_shelloutput_header("Setting up directories", "#")
    os_system("useradd growautomation %s" % ga_config["setup_log_redirect"])

    ga_foldercreate(ga_config["path_backup"])

    if ga_config["setup_old"] is True and ga_config["setup_old_backup"] is True:
        ga_infra_oldversion_backup()
    elif ga_config["setup_old"] is True:
        ga_infra_oldversion_cleanconfig()

    ga_setup_config_file("w", "version=%s\npath_root=%s\nhostname=%s\nsetuptype=%s\n"
                         % (ga_config["version"], ga_config["path_root"], ga_config["hostname"], ga_config["setuptype"]), ga_config["setup_version_file"])
    os_system("chmod 664 %s && chown growautomation:growautomation %s %s" % (ga_config["setup_version_file"], ga_config["setup_version_file"], ga_config["setup_log_redirect"]))
    ga_foldercreate(ga_config["path_root"])
    ga_foldercreate(ga_config["path_log"])
    ga_setup_infra_mounts()


# code setup
def ga_setup_infra_code():
    ga_setup_shelloutput_header("Setting up growautomation code", "#")
    if os_path.exists("/tmp/controller") is True:
        os_system("mv /tmp/controller /tmp/controller_%s %s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"), ga_config["setup_log_redirect"]))

    os_system("cd /tmp && git clone https://github.com/growautomation-at/controller.git %s" % ga_config["setup_log_redirect"])

    if ga_config["setup_type_as"] is True:
        os_system("cp -r /tmp/controller/code/agent/* %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    if ga_config["setup_type_ss"] is True:
        os_system("cp -r /tmp/controller/code/server/* %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    os_system("cp /tmp/controller/setup/setup-linux.py %s/core %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    os_system("find %s -type f -iname '*.py' -exec chmod 754 {} \\; %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))
    os_system("chown -R growautomation:growautomation %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    ga_pyvers = "%s.%s" % (sys_version_info.major, sys_version_info.minor)
    ga_pyvers_modpath = "/usr/local/lib/python%s/dist-packages/ga" % ga_pyvers
    if os_path.exists(ga_pyvers_modpath) is False:
        os_system("ln -s %s %s %s" % (ga_config["path_root"], ga_pyvers_modpath, ga_config["setup_log_redirect"]))

    os_system("ln -s %s %s/backup && ln -s %s %s/log %s" % (ga_config["path_backup"], ga_config["path_root"], ga_config["path_log"], ga_config["path_root"], ga_config["setup_log_redirect"]))

    ga_setup_config_file("w", "[core]\nhostname=%s\nsetuptype=%s\npath_root=%s\nlog_level=%s" % (ga_config["hostname"], ga_config["setuptype"], ga_config["path_root"], ga_config["log_level"]))

    service_path = "%s/service/systemd/growautomation.service" % ga_config["path_root"]
    ga_replaceline(service_path, "ExecStart=", "ExecStart=\/usr\/bin\/python3 %s" % service_path.replace("/", "\/"))
    os_system("systemctl link %s %s" % (service_path, ga_config["setup_log_redirect"]))
    os_system("systemctl enable growautomation.service %s" % ga_config["setup_log_redirect"])
    ga_setup_shelloutput_text("Linked and enabled growautomation service", style="info")

ga_setup_infra()
ga_setup_infra_code()

# creating openssl ca
if ga_config["setuptype"] == "server":
    ga_openssl_setup()

# db setup
ga_sql_all()

if ga_config["setup_type_ss"] is True:
    ga_sql_server()

if ga_config["setuptype"] == "server":
    ga_sql_server_create_agent()

elif ga_config["setuptype"] == "agent":
    ga_sql_agent()

########################################################################################################################
# create devicetypes and devices


class GetObject:
    def __init__(self):
        self.object_dict = {}
        self.setting_dict = {}
        self.group_dict = {}
        self.add_core()

    def add_core(self):
        ga_setup_shelloutput_header("Basic device setup", "#")
        ga_setup_shelloutput_text("Please refer to the documentation if you are new to growautomation.\nLink: https://docs.growautomation.at", point=False)
        core_object_dict = {}
        core_object_dict["check"] = "NULL"
        self.setting_dict["check"] = {"range": 10, "function": "parrot.py"}
        self.setting_dict["backup"] = {"timer": 86400, "function": "backup.py"}
        core_object_dict["backup"] = "NULL"
        self.object_dict["core"] = core_object_dict
        self.get_devicetype()

    def get_devicetype(self):
        dt_object_dict = {}
        ga_setup_shelloutput_header("Devicetypes", "-")
        while_devicetype = ga_setup_input("Do you want to add devicetypes?\n"
                                          "Info: must be created for every sensor/action/downlink hardware model; they provide per model configuration", True)
        while_count = 0
        while while_devicetype:
            ga_setup_shelloutput_header("", symbol="-", line=True)
            setting_dict = {}
            if while_count > 0:
                name = ga_setup_input("Provide a unique name - at max 20 characters long.\nAlready existing:\n%s" % list(dt_object_dict.keys()), default="AirHumidity", intype="free")
            else:
                name = ga_setup_input("Provide a unique name - at max 20 characters long.", default="AirHumidity", intype="free")
            dt_object_dict[name] = ga_setup_input("Provide a type.", default="sensor", poss=["sensor", "action", "downlink"], intype="free")
            setting_dict["function"] = ga_setup_input("Which function should be started for the devicetype?\n"
                                                      "Info: just provide the name of the file; they must be placed in the ga %s folder" % dt_object_dict[name],
                                                      default="%s.py" % name, intype="free", max_value=50)
            setting_dict["function_arg"] = ga_setup_input("Provide system arguments to pass to you function -> if you need it.\n"
                                                          "Info: pe. if one function can provide data to multiple devicetypes", intype="free", min_value=0, max_value=75)
            if dt_object_dict[name] == "action":
                setting_dict["boomerang"] = ga_setup_input("Will this type need to reverse itself?\nInfo: pe. opener that needs to open/close", False)
                if setting_dict["boomerang"]:
                    setting_dict["boomerang_type"] = ga_setup_input("How will the reverse be initiated?", default="threshold", poss=["threshold", "time"], intype="free")
                    if setting_dict["boomerang_type"] == "time":
                        setting_dict["boomerang_time"] = ga_setup_input("Provide the time after the action will be reversed.", default=1200, max_value=1209600, min_value=10)
                    reverse_function = ga_setup_input("Does reversing need an other function?", False)
                    if reverse_function:
                        setting_dict["boomerang_function"] = ga_setup_input("Provide the name of the function.", intype="free", max_value=50)
                        setting_dict["function_arg"] = ga_setup_input("Provide system arguments to pass to the reverse function -> if you need it.", intype="free", min_value=0, max_value=75)
            elif dt_object_dict[name] == "sensor":
                setting_dict["timer"] = ga_setup_input("Provide the interval to run the function in seconds.", default=600, max_value=1209600, min_value=10)
                setting_dict["unit"] = ga_setup_input("Provide the unit for the sensor input.", "°C", intype="free")
                setting_dict["threshold_max"] = ga_setup_input("Provide a maximum threshold value for the sensor.\n"
                                                               "Info: if this value is exceeded the linked action(s) will be started", default=26, max_value=1000000, min_value=1)
                setting_dict["threshold_optimal"] = ga_setup_input("Provide a optimal threshold value for the sensor.\n"
                                                                   "Info: if this value is reached the linked action(s) will be reversed", default=20, max_value=1000000, min_value=1)

                setting_dict["time_check"] = ga_setup_input("How often should the threshold be checked? Interval in seconds.", 3600, max_value=1209600, min_value=60)
            self.setting_dict[name] = setting_dict
            while_count += 1
            while_devicetype = ga_setup_input("Want to add another devicetype?", True, style="info")
        if while_count > 0:
            self.object_dict["devicetype"] = dt_object_dict
            self.create_device()
        else:
            return

    def create_device(self):
        d_object_dict = {}

        def to_create(to_ask, info):
            create = ga_setup_input("Do you want to add a %s\nInfo: %s" % (to_ask, info), True)
            create_dict = {}
            while create:
                ga_setup_shelloutput_header("", symbol="-", line=True)
                setting_dict = {}
                dt_list = [name for value in d_object_dict.values() if dict(value).keys() == to_ask for name in dict(value).values()]
                name = ga_setup_input("Provide a unique name - at max 20 characters long.", default="%s01" % dt_list[0], intype="free")
                create_dict[name] = ga_setup_input("Provide its devicetype.", default=dt_list[0], poss=dt_list, intype="free")
                if to_ask != "downlink":
                    dl_list = [name for key, value in d_object_dict.items() if key == "downlink" for name in dict(value).keys()]
                    if len(dl_list) > 0:
                        setting_dict["connection"] = ga_setup_input("How is the device connected to the growautomation agent?\n"
                                                                    "'downlink' => pe. analog to serial converter, 'direct' => gpio pin", default="direct", poss=["downlink", "direct"], intype="free")
                    else:
                        setting_dict["connection"] = ga_setup_input("How is the device connected to the growautomation agent?\nInfo: 'downlink' => pe. analog to serial converter, 'direct' => "
                                                                    "gpio pin", default="direct", poss=["downlink", "direct"], intype="free", neg=True)
                    if setting_dict["connection"] == "downlink":
                        setting_dict["downlink"] = ga_setup_input("Provide the name of the downlink to which the device is connected to.\n"
                                                                  "Info: the downlink must also be added as device", poss=dl_list, intype="free")
                setting_dict["port"] = ga_setup_input("Provide the portnumber to which the device is/will be connected.", default=2, intype="free")
                self.setting_dict[name] = setting_dict
                create = ga_setup_input("Want to add another %s?" % to_ask, True, style="info")
            d_object_dict[to_ask] = create_dict

        def check_type(name):
            if len([x for key, value in self.object_dict.items() if key == "devicetype" for x in dict(value).values() if x == name]) > 0:
                return True
            else:
                return False

        if check_type("downlink"):
            ga_setup_shelloutput_header("Downlinks", "-")
            to_create("downlink", "if devices are not connected directly to the gpio pins you will probably need this one\n"
                                  "Check the documentation for more informations: https://docs.growautomation.at")
        if check_type("sensor"):
            ga_setup_shelloutput_header("Sensors", "-")
            to_create("sensor", "any kind of device that provides data to growautomation")
        if check_type("action"):
            ga_setup_shelloutput_header("Actions", "-")
            to_create("action", "any kind of device that should react if the linked thresholds are exceeded")
        self.object_dict["device"] = d_object_dict
        self.create_group()

    def create_group(self):
        def to_create(to_ask, info, info_member):
            create_count, create_dict = 0, {}
            create = ga_setup_input("Do you want to add a %s?\nInfo: %s" % (to_ask, info), True)
            while create:
                ga_setup_shelloutput_header("", symbol="-", line=True)
                member_list = []
                member_count, add_member = 0, True
                while add_member:
                    if member_count == 0:
                        info = "\nInfo: %s" % info_member
                    else:
                        info = ""
                    if to_ask == "sector":
                        posslist = [name for key, value in self.object_dict.items() if key == "device" for nested in dict(value).values() for name in dict(nested).keys()]
                    elif to_ask == "link":
                        posslist = [name for key, value in self.object_dict.items() if key == "devicetype" for name in dict(value).keys()]
                    member_list.append(ga_setup_input("Provide a name for member %s%s." % (member_count + 1, info), poss=list(set(posslist) - set(member_list)), default=posslist[0], intype="free"))
                    member_count += 1
                    if member_count > 1:
                        add_member = ga_setup_input("Want to add another member?", True, style="info")
                create_dict[create_count] = member_list
                create_count += 1
                create = ga_setup_input("Want to add another %s?" % to_ask, True, style="info")
            return create_dict

        ga_setup_shelloutput_header("Sectors", "-")
        self.group_dict["sector"] = to_create("sector", "links objects which are in the same area", "must match one device")
        ga_setup_shelloutput_header("Devicetype links", "-")
        self.group_dict["link"] = to_create("link", "links action- and sensortypes\npe. earth humidity sensor with water pump", "must match one devicetype")
        self.write_config()

    def write_config(self):
        ga_setup_shelloutput_header("Writing configuration to database", "-")

        def insert(command):
            if ga_config["setuptype"] == "agent":
                return ga_mysql(command, ga_config["sql_agent_user"], ga_config["sql_agent_pwd"])
            else:
                return ga_mysql(command, basic=True)

        ga_setup_shelloutput_text("Writing object configuration")
        insert("INSERT INTO ga.ObjectReference (author,name) VALUES ('setup','%s');" % ga_config("hostname"))
        [insert("INSERT INTO ga.Category (author,name) VALUES ('setup','%s')" % key) for key in self.object_dict.keys()]
        object_count = 0
        for object_type, packed_values in self.object_dict.items():
            def unpack_values(values, parent="NULL"):
                count = 0
                for object_name, object_class in sorted(values.items()):
                    if object_class != "NULL":
                        insert("INSERT IGNORE INTO ga.ObjectReference (author,name) VALUES ('setup','%s');" % object_class)
                        object_class = "'%s'" % object_class
                    if parent != "NULL":
                        parent = "'%s'" % parent
                    insert("INSERT INTO ga.Object (author,name,parent,class,type) VALUES ('setup','%s',%s,%s,'%s');" % (object_name, parent, object_class, object_type))
                    count += 1
                return count
            if object_type == "device":
                for subtype, packed_subvalues in packed_values.items():
                    object_count += unpack_values(packed_subvalues, ga_config("hostname"))
            else:
                object_count += unpack_values(packed_values)
        ga_setup_shelloutput_text("%s objects were added" % object_count, style="info")

        ga_setup_shelloutput_text("Writing object settings")
        setting_count = 0
        for object_name, packed_values in self.setting_dict.items():
            for setting, data in sorted(packed_values.items()):
                insert("INSERT INTO ga.Setting (author,belonging,setting,data) VALUES ('setup','%s','%s','%s');" % (object_name, setting, data))
                setting_count += 1
        ga_setup_shelloutput_text("%s object settings were added" % setting_count, style="info")

        ga_setup_shelloutput_text("Writing group configuration")
        group_count, member_count = 0, 0
        for group_type, packed_values in self.group_dict.items():
            for group_id, group_member_list in packed_values.items():
                insert("INSERT INTO ga.Category (author,name) VALUES ('setup','%s')" % group_type)
                insert("INSERT INTO ga.Grp (author,type) VALUES ('setup','%s');" % group_type)
                sql_gid = insert("SELECT id FROM ga.Grp WHERE author = 'setup' AND type = '%s' ORDER BY changed DESC LIMIT 1;" % group_type)
                for member in sorted(group_member_list):
                    insert("INSERT INTO ga.Grouping (author,gid,member) VALUES ('setup','%s','%s');" % (sql_gid, member))
                    member_count += 1
                group_count += 1
        ga_setup_shelloutput_text("%s groups with a total of %s members were added" % (group_count, member_count), style="info")

    def get_object_list(self, subtract=None, cat=None, subcat=None):
        if cat is not None:
            if cat == "device":
                subcat = True
            if subcat is not None:
                if subcat:
                    object_list = [name for key, value in self.object_dict.items() if key == cat for name in dict(value).values()]
                else:
                    object_list = [name for key, value in self.object_dict.items() if key == cat for subkey, name in dict(value).items() if subkey == subcat]
            else:
                object_list = [name for key, value in self.object_dict.items() if key == cat for name in dict(value).keys()]
        else:
            object_list = [name for value in self.object_dict.values() for name in dict(value).keys()]
        if subtract is not None:
            return list(set(object_list) - set(subtract))
        else:
            return object_list


GetObject()

########################################################################################################################
# post setup tasks

# defining default values
ga_config["backup_time"] = "2000"
ga_config["backup_log"] = False
ga_config["install_timestamp"] = datetime.now().strftime("%Y-%m-%d_%H-%M")


def ga_mysql_write_config(thatdict):
    insertdict = {}
    for key, value in thatdict.items():
        if "setup_" in key or "pwd" in key:
            pass
        else:
            insertdict[key] = value

    for key, value in sorted(insertdict.items()):
        if type(value) == bool:
            if value is True:
                value = 1
            else:
                value = 0
        if ga_config["setuptype"] == "agent":
            command = "INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('%s', '%s', '%s', '%s');" % ("gasetup", ga_config["hostname"], key, value)
            ga_mysql(command, ga_config["sql_agent_user"], ga_config["sql_agent_pwd"])
        else:
            ga_mysql("INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('%s', '%s', '%s', '%s');" % ("gasetup", ga_config["hostname"], key, value), basic=True)
    ga_setup_shelloutput_text("Wrote %s settings to database table ga.Setting ()" % len(insertdict), style="succ", point=False)


ga_setup_shelloutput_header("Writing configuration to database", "#")
ga_log_write_vars()
writedict = {**ga_config_server, **ga_config}
ga_mysql_write_config(writedict)

ga_setup_shelloutput_header("Starting growautomation service", "#")
os_system("systemctl start growautomation.service %s" % ga_config["setup_log_redirect"])

ga_setup_shelloutput_header("Setup finished! Please reboot the system", "#")
ga_setup_log_write("Setup finished.")

# check path inputs for ending / and remove it
# delete old fstab entries and replace them (ask user)
# systemd systemd setup for agentdata and serverbackup
# ga service check for python path /usr/bin/python3 and growautomation root -> change execstart execstop etc
# ga_config["backup"] should do something.. but what?
# simple setup -> preconfigure most settings
# advanced setup -> like now
# dont repeat output if wrong input -> only warning
# oldconf
#    db functions for oldconfig checken -> less to do?
#    should certs be renewed?
#    tell user that type cant be changed without replace option (done already?)
#    adv setup value overwrite x5 or so (manually)
# keepconfig -> doesnt get setup_type / doesnt start basic vars function
# mysql bug workaround MySql was unable to perform action 'CREATE USER
# check all string inputs with ga_setup_string_check (reference in input function if poss/default is str?)
# replaceline error if not found ?

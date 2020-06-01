#!/usr/bin/python3.8
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
#     E-Mail: contact@growautomation.at
#     Web: https://git.growautomation.at

# ga_version 0.4

########################################################################################################################

from os import getuid as os_getuid
from os import path as os_path
from os import system as os_system
from os import listdir as os_listdir
from datetime import datetime
from random import choice as random_choice
from string import ascii_letters as string_ascii_letters
from string import digits as string_digits
from sys import version_info as sys_version_info
from sys import argv as sys_argv
from sys import exc_info as sys_exc_info
import signal

# setup vars
ga_config = {}
ga_config_server = {}
ga_config['version'] = '0.4'
ga_config['python_min_version'] = '3.8'
ga_config['python_version'] = "%s.%s" % (sys_version_info.major, sys_version_info.minor)
ga_config['setup_version_file'] = '/etc/growautomation.version'
ga_config['setup_log_path'] = '/var/log/growautomation'
ga_config['setup_log'] = "%s/setup_%s.log" % (ga_config['setup_log_path'], datetime.now().strftime("%Y-%m-%d_%H-%M"))
ga_config['setup_log_redirect'] = " 2>&1 | tee -a %s" % ga_config['setup_log']

if float(ga_config['python_version']) < float(ga_config['python_min_version']):
    raise SystemExit("Your current python version isn't supported!\nYou have '%s' and need '%s'" % (ga_config['python_version'], ga_config['python_min_version']))
os_system("/usr/bin/python%s -m pip install wheel mysql-connector-python colorama" % ga_config['python_version'])

from colorama import Fore as colorama_fore

try:
    from ..code.agent.core.owl import DoSql
    from ..code.agent.core.ant import ShellInput
    from ..code.agent.core.ant import ShellOutput
    from ..code.agent.core.smallant import VarHandler
    from ..code.agent.core.smallant import process
    from ..code.agent.maintenance.config_interface import setup as object_setup
except (ImportError, ModuleNotFoundError):
    from owl import DoSql
    from ant import ShellInput
    from ant import ShellOutput
    from smallant import VarHandler
    from smallant import process
    from config_interface import setup as object_setup


def setup_stop(error_msg=None, shell=None, log=None, ignore_log=False):
    if error_msg is not None and shell is None:
        shell = ("An error occurred:\n\n%s" % error_msg)
        shell_logfile = ''
    else:
        shell_logfile = "\nPath to the full setup log: %s\n\n" % ga_config['setup_log']
    if ignore_log:
        setup_log_write_vars()
        setup_log_write("\nExit. %s.\n\n" % log)
    if debug: VarHandler().stop()
    raise SystemExit(colorama_fore.RED + "\n%s%s" % (shell, shell_logfile) + colorama_fore.RESET)


try:
    if sys_argv[1] == 'debug':
        ShellOutput('Starting setup in debug mode.')
        VarHandler(name='debug', data=1).set()
        debug = True
except IndexError:
    debug = False


if os_getuid() != 0:
    setup_stop(shell='This script needs to be run with root privileges', log='Script not started as root', ignore_log=True)


def setup_signal(signum=None, stack=None):
    try:
        raise RuntimeError("Received signal %s |last error: \"%s - %s\"" % (signum,  sys_exc_info()[0].__name__, sys_exc_info()[1]))
    except AttributeError:
        raise RuntimeError("Received signal %s" % signum)


signal.signal(signal.SIGTERM, setup_signal)
signal.signal(signal.SIGINT, setup_signal)

########################################################################################################################

try:
    def setup_input(prompt, default='', poss='', intype='', style='', posstype='', max_value=20, min_value=2, neg=False, lower=True, petty=False):
        if petty is True and setup_advanced is False:
            print("\n%s\nConfig: %s\n" % (prompt, default))
            return default
        return ShellInput(prompt, default=default, poss=poss, intype=intype, style=style, posstype=posstype,
                          max_value=max_value, min_value=min_value, neg=neg, lower=lower).get()


    def setup_log_write(output, special=False):
        if os_path.exists(ga_config['setup_log_path']) is False:
            os_system("mkdir -p %s %s" % (ga_config['setup_log_path'], ga_config['setup_log_redirect']))
        with open(ga_config['setup_log'], 'a') as logfile:
            if special is True:
                logfile.write(output)
            else:
                logfile.write("\n%s\n" % output)


    def setup_log_write_vars():
        setup_log_write('Setup vars:')

        def write(thatdict):
            for key, value in sorted(thatdict.items()):
                if 'pwd' in key:
                    pass
                else:
                    setup_log_write("%s - %s, " % (key, value), True)
        write(ga_config)
        write(ga_config_server)


    def setup_pwd_gen(stringlength):
        chars = string_ascii_letters + string_digits + '!#-_'
        return ''.join(random_choice(chars) for i in range(stringlength))


    def setup_fstabcheck():
        with open('/etc/fstab', 'r') as readfile:
            stringcount = readfile.read().count('Growautomation')
            if stringcount > 0:
                ShellOutput(output="WARNING!\nYou already have one or more remote shares configured.\nIf you want"
                            " to install new ones you should disable the old ones by editing the "
                            "'/etc/fstab' file.\nJust add a '#' in front of the old shares or delete "
                            "those lines to disable them", style="warn")


    def setup_mnt_creds(outtype, inputstr=''):
        if outtype == 'usr':
            return setup_input(prompt='Provide username for share authentication.', default=inputstr)
        elif outtype == 'pwd':
            return setup_input(prompt='Provide password for share authentication.', default=inputstr, intype='pass')
        elif outtype == 'dom':
            return setup_input(prompt='Provide domain for share authentication.', default='workgroup')


    def setup_keycheck(dictkey):
        dict = ga_config
        if dict[dictkey] is None:
            setup_log_write("WARNING! Dict key %s has value of None" % dictkey)
            return False
        elif dictkey in dict:
            return True
        else:
            setup_log_write('WARNING! Dict key not found' % dictkey)
            return False


    def setup_mysql_conntest(dbuser='', dbpwd='', check_ga_exists=False, local=False, check_system=False, write=False):
        ShellOutput('Testing sql connection.', style='info')
        if process('apt-cache policy mariadb-server | grep Installed').find('none') != -1:
            ShellOutput('MariaDB not installed.', style='warn')
            return False
        if dbuser == '': dbuser = 'root'
        if dbuser == 'root' and ga_config['sql_server_ip'] == '127.0.0.1':
            if check_ga_exists is True:
                sqltest = DoSql(command='SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;', user='root', exit=False, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
            else:
                sqltest = DoSql(command='SELECT * FROM mysql.help_category LIMIT 10;', user='root', exit=False, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
        elif dbpwd == '':
            ShellOutput(output='SQL connection failed. No password provided and not root.', style='warn')
            setup_log_write("Sql connection test failed!\nNo password provided and not root.\nServer: %s, user: %s" % (ga_config['sql_server_ip'], dbuser))
            return False
        elif local and check_system:
            sqltest = DoSql(command='SELECT * FROM mysql.help_category LIMIT 10;', user=dbuser, pwd=dbpwd, exit=False, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
        elif local:
            if write:
                sqltest = DoSql(command="INSERT INTO ga.Data (agent,data,device) VALUES ('setup','conntest','%s');" % ga_config['hostname'], user=dbuser, pwd=dbpwd, write=True, exit=False,
                                hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
            else:
                sqltest = DoSql(command='SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;', user=dbuser, pwd=dbpwd, exit=False, hostname=ga_config['hostname'],
                                setuptype=ga_config['setuptype']).start()
        else:
            sqltest = DoSql(command='SELECT * FROM ga.Setting ORDER BY changed DESC LIMIT 10;', user=dbuser, pwd=dbpwd, exit=False, hostname=ga_config['hostname'],
                            setuptype=ga_config['setuptype']).start()
        if type(sqltest) == list:
            ShellOutput(output='SQL connection verified', style='succ')
            return True
        elif type(sqltest) == bool and sqltest:
            ShellOutput(output='SQL connection verified', style='succ')
            return sqltest
        else:
            ShellOutput(output="SQL connection to %s failed for user %s" % (ga_config['sql_server_ip'], dbuser), style='warn')
            setup_log_write("Sql connection test failed:\nServer: %s, user: %s\nSql output: %s" % (ga_config['sql_server_ip'], dbuser, sqltest))
            return False


    def setup_config_mysql(search, user, pwd, hostname):
        def command(setting):
            return "SELECT data FROM ga.Setting WHERE belonging = '%s' and setting = '%s';" % (hostname, setting)

        if type(search) == list:
            itemdatadict = {}
            for item in search:
                itemdatadict[item] = DoSql(command=command(item), user=user, pwd=pwd, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
            return itemdatadict
        elif type(search) == str:
            data = DoSql(command=command(search), user=user, pwd=pwd, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
            return data


    def setup_config_file(file=None, text=None, typ='r'):
        if file is None:
            file = "%s/core/core.conf" % ga_config['path_root']
        current_path = os_path.dirname(os_path.realpath(__file__))
        if os_path.exists("%s/%s" % (current_path, 'core.conf')) is False and file.find('core.conf') != -1:
            os_system("ln -s %s %s" % (file, current_path))
        with open(file, typ) as config_file:
            if typ != 'r':
                if typ == 'w': output = "%s\n" % text
                else: output = "\n%s\n" % text
                config_file.write(output)
                os_system("chown growautomation:growautomation %s && chmod 440 %s %s" % (file, file, ga_config['setup_log_redirect']))
                return True
            else:
                for line in config_file.readlines():
                    if line.find(text) != -1:
                        try:
                            value = line.split('=')[1].strip()
                            return value
                        except (IndexError, ValueError):
                            return False
                return False


    ########################################################################################################################

    setup_log_write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    ShellOutput(font='head', output="Starting Growautomation installation script\n"
                "The newest versions can be found at: https://git.growautomation.at", symbol='#')
    ga_config['setup_warning_accept'] = setup_input(prompt="WARNING!\n\nWe recommend using this installation script on dedicated systems.\n"
                                                    "This installation script won't check your already installed programs for compatibility problems.\n"
                                                    "If you already use web-/database or other complex software on this system you should back it up before installing this software.\n"
                                                    "We assume no liability for problems that may be caused by this installation!\n\n"
                                                    "Accept the risk if you want to continue.", default=False, style='warn')
    if ga_config['setup_warning_accept'] is False:
        setup_stop(shell="Script cancelled by user\nYou can also install this software manually through the setup "
                         "manual.\nIt can be found at: https://git.growautomation.at/tree/master/manual",
                         log='Setupwarning not accepted by user')

    if os_path.exists("/usr/bin/python%s" % ga_config['python_version']):
        ga_config['python_path'] = "/usr/bin/python%s" % ga_config['python_version']
    elif os_path.exists("/usr/local/bin/python%s" % ga_config['python_version']):
        os_system("ln -s /usr/local/bin/python%s /usr/bin/ %s" % (ga_config['python_version'], ga_config['setup_log_redirect']))
        ga_config['python_path'] = "/usr/bin/python%s" % ga_config['python_version']
    else:
        ga_config['python_path'] = setup_input(prompt="Please provide the path to your python%s binary!\n"
                                                      "Info: wasn't found in '/usr/bin/' or '/usr/local/bin'" % ga_config['python_version'],
                                               default="/usr/sbin/python%s" % ga_config['python_version'], intype='free')

    ShellOutput(font='head', output='Checking if growautomation is already installed on the system', symbol='#')

    # check if growautomation is already installed

    ga_config['setup_old_version_file'] = os_path.exists(ga_config['setup_version_file'])
    if ga_config['setup_old_version_file'] is True:
        ShellOutput(output='Growautomation version file exists', style='info')
        ga_config['setup_old_version'] = setup_config_file(file=ga_config['setup_version_file'], text='version=')
    else:
        ShellOutput(output='No growautomation version file found', style='info')
    ga_config['setup_old_root'] = os_path.exists('/etc/growautomation')
    if ga_config['setup_old_root'] is True:
        ShellOutput(output='Growautomation default root path exists', style='info')
    else:
        ShellOutput(output="Growautomation default root path doesn't exist", style='info')
    if DoSql(command='SHOW DATABASES;', user='root').find('ga') != -1:
        ga_config['setup_old_db'] = True
        ShellOutput(output='Growautomation database exists', style='info')
    else:
        ga_config['setup_old_db'] = False
        ShellOutput(output='No growautomation database found', style='info')

    if ga_config['setup_old_version_file'] is True or ga_config['setup_old_root'] is True or ga_config['setup_old_db'] is True:
        def ga_config_vars_oldversion_replace():
            global ga_config
            ga_config['setup_old'] = True
            ga_config['setup_old_replace'] = setup_input(prompt='Do you want to replace your current growautomation installation?', default=False, style='warn')
            if ga_config['setup_old_replace'] is True:
                ga_config['setup_old_replace_migrate'] = setup_input(prompt='Should we try to keep your old configuration and data?', default=False, style='warn')
                if ga_config['setup_old_replace_migrate'] is True:
                    ga_config['setup_fresh'] = False
                else:
                    ga_config['setup_fresh'] = True
            if ga_config['setup_old_replace'] is True:
                ga_config['setup_old_backup'] = setup_input(prompt='Do you want to backup your old growautomation installation?', default=True)
            else:
                setup_stop(shell='Stopping script. Current installation should not be overwritten',
                           log='User chose that currently installed ga should not be overwritten')
        if ga_config['setup_old_version_file'] is True:
            if ga_config['setup_old_version'] is None:
                if ga_config['setup_old_root'] is True:
                    ga_config_vars_oldversion_replace()
                elif ga_config['setup_old_db'] is True:
                    ga_config_vars_oldversion_replace()
                else:
                    ShellOutput(output='Error verifying existing growautomation installation. Installing as new', style='warn')
                    ga_config['setup_old'] = False
            else:
                ShellOutput(output="A version of growautomation is/was already installed on this system!\n\n"
                            "Installed version: %s\nReplace version: %s" % (ga_config['setup_old_version'], ga_config['version']))
                ga_config_vars_oldversion_replace()
        else: ga_config_vars_oldversion_replace()
    else:
        ShellOutput(output='No previous growautomation installation found', style='info')
        ga_config['setup_old'] = False

    if ga_config['setup_old'] is False:
        ga_config['setup_fresh'] = True
        ga_config['setup_old_backup'] = False
        ShellOutput(output='Growautomation will be installed completely new', style='succ')
    else:
        ShellOutput(output='Growautomation will be migrated to the new version', style='succ')
        if ga_config['setup_fresh'] is True:
            ShellOutput(output='The configuration and data will be overwritten', style='warn')
        else:
            ShellOutput(output='The configuration and data will be migrated', style='succ')

    ########################################################################################################################

    ShellOutput(font='head', output='Retrieving setup configuration through user input', symbol='#')
    setup_advanced = setup_input(prompt='Do you want to have advanced options in this setup?', default=False)


    def ga_config_var_base():
        global ga_config
        ShellOutput(font='head', output='Checking basic information', symbol='-')

        def ga_config_var_base_name():
            global ga_config
            if ga_config['setuptype'] == 'agent':
                ga_config['hostname'] = setup_input(prompt='Provide the name of this growautomation agent as configured on the server.', default='gacon01')
            elif ga_config['setuptype'] == 'server':
                ga_config['hostname'] = 'gaserver'
            elif ga_config['setuptype'] == 'standalone':
                ga_config['hostname'] = 'gacon01'

        if ga_config['setup_fresh'] is False:
            ga_config['path_root'] = setup_config_file(file=ga_config['setup_version_file'], text='path_root=')
            ga_config['hostname'] = setup_config_file(file=ga_config['setup_version_file'], text='hostname=')
            ga_config['setuptype'] = setup_config_file(file=ga_config['setup_version_file'], text='setuptype=')
            ga_config['log_level'] = setup_config_file(file=ga_config['setup_version_file'], text='log_level=')
            if ga_config['path_root'] is False:
                ShellOutput(output='Growautomation rootpath not found in old versionfile', style='warn')
                ga_config['path_root'] = setup_input(prompt='Want to choose a custom install path?', default='/etc/growautomation')
                if ga_config['setup_old_backup'] is True:
                    ga_config['path_old_root'] = setup_input(prompt="Please provide the install path of your current installation. (for backup)", default='/etc/growautomation')
                else:
                    ga_config['path_old_root'] = False

            if ga_config['hostname'] is False:
                ShellOutput(output='Growautomation hostname not found in old versionfile', style='warn')
                ga_config_var_base_name()

            if ga_config['setuptype'] is False:
                ShellOutput(output="Growautomation setuptype not found in old versionfile.\n\n"
                            "WARNING!\nTo keep your old configuration the setuptype must be the same as before", style='warn')
                ga_config['setuptype'] = setup_input(prompt="Setup as growautomation standalone, agent or server?\n"
                                                            "Agent and Server setup is disabled for now. It will become available after further testing!",
                                                     poss='standalone', default='standalone', petty=True)  # ['agent', 'standalone', 'server']
                if ga_config['setup_old_backup'] is False:
                    ShellOutput(output='Turning on migration backup option - just in case', style='info')
                    ga_config['setup_old_backup'] = True

        if ga_config['setup_fresh'] is True:
            ga_config['setuptype'] = setup_input(prompt="Setup as growautomation standalone, agent or server?\n"
                                                        "Agent and Server setup is disabled for now. It will become available after further testing!",
                                                 poss='standalone', default='standalone', petty=True)  # ['agent', 'standalone', 'server']
            if ga_config['setuptype'] == 'agent':
                ga_config['setup_yousure'] = setup_input(prompt="WARNING!\nYou should install/update the growautomation server component before the agent because of dependencies.\n"
                                                         "Find more information about the creation of new agents at:\nhttps://git.growautomation.at/tree/master/manual/agent\n\n"
                                                         "Agree if you have already installed/updated the ga server or disagree to stop the installation.", default=False, style='warn')
                if ga_config['setup_yousure'] is False:
                    setup_stop(shell='Stopping script. Server was not installed before agent',
                               log='User has not installed the server before the agent')
            ga_config['path_root'] = setup_input(prompt='Want to choose a custom install path?', default='/etc/growautomation', petty=True)
            if ga_config['setup_old'] and ga_config['setup_old_backup'] is True:
                ga_config['path_old_root'] = setup_input(prompt="Please provide the install path of your current installation (for backup).", default='/etc/growautomation')
            else:
                ga_config['path_old_root'] = False
            ga_config['log_level'] = setup_input(prompt='Want to change the log level?', default='1', poss=['0', '1', '2', '3', '4', '5'], petty=True)
            ga_config_var_base_name()

        if ga_config['setuptype'] == 'server' or ga_config['setuptype'] == 'standalone':
            ga_config['setup_type_ss'] = True
        else:
            ga_config['setup_type_ss'] = False

        if ga_config['setuptype'] == 'agent' or ga_config['setuptype'] == 'standalone':
            ga_config['setup_type_as'] = True
        else:
            ga_config['setup_type_as'] = False


    def ga_config_var_setup():
        global ga_config
        ShellOutput(font='head', output='Checking setup options', symbol='-')
        ga_config['setup_pwd_length'] = int(setup_input(prompt="This setup will generate random passwords for you.\nPlease define the length of those random passwords!", default=12, min_value=8,
                                                        max_value=50, intype='passgen', petty=True))

        ga_config['setup_ca'] = setup_input(prompt='Need to import internal ca certificate for git/pip? Mainly needed if your firewall uses ssl inspection.', default=False, petty=True)

        if ga_config['setup_ca'] is True:
            ga_config['setup_ca_path'] = setup_input(prompt='Provide path to the ca file.', default='/etc/ssl/certs/internalca.cer')
        else:
            ga_config['setup_ca_path'] = 'notprovided'

        ga_config['setup_linuxupgrade'] = setup_input(prompt='Want to upgrade your existing software packages before growautomation installation?', default=True, petty=True)


    def ga_config_var_db():
        global ga_config
        ShellOutput(font='head', output='Checking for database credentials', symbol='-')
        whilecount = 0
        if ga_config['setuptype'] == 'agent':
            if ga_config['setup_fresh'] is True:
                ga_config['sql_agent_pwd'] = setup_pwd_gen(ga_config['setup_pwd_length'])
                ga_config['sql_local_user'] = 'agent'
                ga_config['sql_local_pwd'] = setup_pwd_gen(ga_config['setup_pwd_length'])
                while True:
                    whilecount += 1
                    ga_config['sql_server_ip'] = setup_input(prompt='Provide the ip address of the growautomation server.', default='192.168.0.201')
                    ga_config['sql_server_port'] = setup_input(prompt='Provide the mysql port of the growautomation server.', default='3306')
                    ShellOutput(output="The following credentials can be found in the serverfile '$garoot/core/core.conf'")
                    ga_config['sql_agent_user'] = setup_input(prompt='Please provide the user used to connect to the database.', default=ga_config['hostname'])
                    ga_config['sql_agent_pwd'] = setup_input(prompt='Please provide the password used to connect to the database.', default=ga_config['sql_agent_pwd'], intype='pass')
                    if setup_mysql_conntest(ga_config['sql_agent_user'], ga_config['sql_agent_pwd']) is True:
                        ga_config['sql_server_repl_user'] = setup_input(prompt='Please provide sql replication user.', default=ga_config['hostname'] + 'replica')
                        ga_config['sql_server_repl_pwd'] = setup_input(prompt='Please provide sql replication password.', default=ga_config['sql_agent_pwd'])
                        break
            else:
                ga_config['sql_local_user'] = setup_config_file(text='sql_local_user=')
                if ga_config['sql_local_user'] is False:
                    ga_config['sql_local_user'] = 'agent'
                ga_config['sql_local_pwd'] = setup_config_file(text='sql_local_pwd=')
                if ga_config['sql_local_pwd'] is False:
                    ga_config['sql_local_pwd'] = setup_pwd_gen(ga_config['setup_pwd_length'])
                ga_config['sql_agent_user'] = setup_config_file(text='sql_agent_user=')
                ga_config['sql_agent_pwd'] = setup_config_file(text='sql_agent_pwd=')

                while True:
                    if whilecount > 0:
                        ShellOutput(output='You can reset/configure the agent database credentials on the growautomation server. '
                                           'Details can be found in the manual: https://git.growautomation.at/tree/master/manual', style='info')
                    ga_config['sql_agent_user'] = setup_config_file(text='sql_agent_user=')
                    ga_config['sql_agent_pwd'] = setup_config_file(text='sql_agent_pwd=')
                    ga_config['sql_server_ip'] = setup_config_file(text='sql_server_ip=')
                    if setup_mysql_conntest(ga_config['sql_agent_user'], ga_config['sql_agent_pwd']) is True:
                        break
                return True

        else:
            ga_config['sql_server_ip'] = '127.0.0.1'
            ga_config['sql_server_port'] = '3306'
            if ga_config['setup_fresh'] is True:
                ga_config['sql_admin_user'] = setup_input(prompt='How should the growautomation database admin user be named?', default='gadmin', petty=True)
                ga_config['sql_admin_pwd'] = setup_pwd_gen(ga_config['setup_pwd_length'])
                if setup_mysql_conntest() is False:
                    ShellOutput(output='Unable to connect to local mysql server with root privileges', style='err')
            else:
                ga_config['sql_admin_user'] = setup_config_file(text='sql_admin_user=')
                ga_config['sql_admin_pwd'] = setup_config_file(text='sql_admin_pwd=')
                while True:
                    if whilecount > 0:
                        ShellOutput(output="Please try again.\nThe following credentials can normally be found in the serverfile '$garoot/core/core.conf'", style='warn')
                    if whilecount > 1:
                        ga_config['setup_sql_admin_reset'] = setup_input(prompt='Do you want to reset the database admin via the setup?', default=False)
                        if ga_config['setup_sql_admin_reset'] is True:
                            if setup_mysql_conntest() is False:
                                ShellOutput(output="Database admin can't be reset since the database check as root failed.\nThis could happen "
                                            "if the growautomation database doesn't exist", style='warn')
                                ga_config['setup_sql_noaccess_proceed'] = setup_input(prompt='Do you want to continue the setup anyway? The problem might maybe get fixed by the setup process.', default=False)
                                if ga_config['setup_sql_noaccess_proceed'] is False:
                                    setup_stop(shell='All database connections failed',
                                               log='User chose to exit since all database connections failed')
                                ga_config['setup_sql_admin_reset'] = False
                                if ga_config['setup_old_backup'] is False:
                                    ShellOutput(output='Turning on migration backup option - just in case', style='info')
                                    ga_config['setup_old_backup'] = True
                                return 'none'
                            else:
                                return 'root'

                        ga_config['sql_admin_user'] = setup_input(prompt='Provide the name of the growautomation database admin user.', default='gadmin')
                        ga_config['sql_admin_pwd'] = setup_input(prompt='Please provide the password used to connect to the database.', intype='pass')
                        if setup_mysql_conntest(ga_config['sql_admin_user'], ga_config['sql_admin_pwd'], local=True) is True:
                            break
                        whilecount += 1

                return True


    def ga_config_var_certs():
        global ga_config
        ShellOutput(font='head', output='Checking certificate information', symbol='-')
        if ga_config['setuptype'] == 'agent':
            ShellOutput(output="The following certificates can be found in the serverpath '$garoot/ca/certs/'\n", style='info')
            ga_config['sql_ca'] = setup_input(prompt='Provide the path to the ca-certificate from your ga-server.', default="%s/ssl/ca.cer.pem" % ga_config['path_root'])
            ga_config['sql_cert'] = setup_input(prompt='Provide the path to the agent server certificate.', default="%s/ssl/%s.cer.pem" % (ga_config['path_root'], ga_config['hostname']))
            ga_config['sql_key'] = setup_input(prompt='Provide the path to the agent server key.', default="%s/ssl/%s.key.pem" % (ga_config['path_root'], ga_config['hostname']))


    ########################################################################################################################
    # Basic config
    ga_config_var_base()
    ga_config_var_setup()
    ga_config_var_db()

    ########################################################################################################################
    # Config migration from old installation

    if ga_config['setup_fresh'] is False:
        ShellOutput(font='head', output='Retrieving existing configuration from database', symbol='-')
        ga_config_list_agent = ['backup', 'path_backup', 'mnt_backup', 'mnt_backup_type', 'mnt_backup_server',
                                'mnt_backup_share', 'mnt_backup_usr', 'mnt_backup_pwd', 'mnt_backup_dom', 'path_log',
                                'mnt_log', 'mnt_shared_creds', 'mnt_shared_server', 'mnt_shared_type', 'mnt_log_type',
                                'mnt_log_server', 'mnt_log_share', 'mnt_log_usr', 'mnt_log_pwd', 'mnt_log_dom']
        ga_config_list_server = []
        if ga_config['setuptype'] == 'server':
            ga_configdict_sql = setup_config_mysql('ga_config_list_server', ga_config['sql_admin_user'], ga_config['sql_admin_pwd'], ga_config['hostname'])
        elif ga_config['setuptype'] == 'standalone':
            ga_configdict_sql_agent = setup_config_mysql('ga_config_list_agent', ga_config['sql_admin_user'], ga_config['sql_admin_pwd'], ga_config['hostname'])
            ga_configdict_sql_server = setup_config_mysql('ga_config_list_server', ga_config['sql_admin_user'], ga_config['sql_admin_pwd'], ga_config['hostname'])
            ga_configdict_sql = {**ga_configdict_sql_agent, **ga_configdict_sql_server}
        else:
            ga_configdict_sql = setup_config_mysql('ga_config_list_agent', ga_config['sql_admin_user'], ga_config['sql_admin_pwd'], ga_config['hostname'])

        ga_config = {**ga_configdict_sql, **ga_config}

    ########################################################################################################################
    # Configuration without migration
    if ga_config['setup_fresh'] is True:
        ShellOutput(font='head', output='Checking directory information', symbol='-')

        ga_config['backup'] = setup_input(prompt='Want to enable backup?', default=True, petty=True)
        if ga_config['backup'] is True:
            ga_config['path_backup'] = setup_input(prompt='Want to choose a custom backup path?', default='/var/backups/growautomation')
        else:
            ga_config['path_backup'] = '/var/backups/growautomation'
        if ga_config['backup'] is True:
            ga_config['mnt_backup'] = setup_input(prompt='Want to mount remote share as backup destination? Smb and nfs available.', default=False, petty=True)
            if ga_config['mnt_backup'] is True:
                setup_fstabcheck()
                ga_config['mnt_backup_type'] = setup_input(prompt='Mount nfs or smb/cifs share as backup destination?', default='nfs', poss=['nfs', 'cifs'])
                ga_config['mnt_backup_srv'] = setup_input(prompt='Provide the server ip.', default='192.168.0.201')
                ga_config['mnt_backup_share'] = setup_input(prompt='Provide the share name.', default='growautomation/backup')
                if ga_config['mnt_backup_type'] == 'cifs':
                    ga_mnt_backup_tmppwd = setup_pwd_gen(ga_config['setup_pwd_length'])
                    ga_config['mnt_backup_user'] = setup_mnt_creds('usr', 'gabackup')
                    ga_config['mnt_backup_pwd'] = setup_mnt_creds('pwd', ga_mnt_backup_tmppwd)
                    ga_config['mnt_backup_dom'] = setup_mnt_creds('dom')
                # else:
                #     ShellOutput(output="Not mounting remote share for backup!\nCause: No sharetype, "
                #                               "serverip or sharename provided.\n")
        else:
            ga_config['mnt_backup'] = False
            ga_config['mnt_backup_type'] = 'False'

        ga_config['path_log'] = setup_input(prompt='Want to choose a custom log path?', default='/var/log/growautomation', petty=True)
        ga_config['mnt_log'] = setup_input(prompt='Want to mount remote share as log destination? Smb and nfs available.', default=False, petty=True)
        if ga_config['mnt_log'] is True:
            setup_fstabcheck()
            if ga_config['mnt_backup'] is True:
                ga_config['mnt_samecreds'] = setup_input(prompt='Use same server as for remote backup?', default=True)
                if ga_config['mnt_samecreds'] is True:
                    ga_config['mnt_log_type'] = ga_config['mnt_backup_type']
                    ga_config['mnt_log_server'] = ga_config['mnt_backup_srv']
            else:
                ga_config['mnt_log_type'] = setup_input(prompt='Mount nfs or smb/cifs share as log destination?', default='nfs', poss=['nfs', 'cifs'])
                ga_config['mnt_log_server'] = setup_input(prompt='Provide the server ip.', default='192.168.0.201')
            ga_config['mnt_log_share'] = setup_input(prompt='Provide the share name.', default='growautomation/log')

            if ga_config['mnt_log_type'] == 'cifs':

                def ga_mnt_log_creds():
                    global ga_config
                    ga_config['mnt_backup_user'] = setup_mnt_creds('usr', 'galog')
                    ga_config['mnt_backup_pwd'] = setup_mnt_creds('pwd', setup_pwd_gen(ga_config['setup_pwd_length']))
                    ga_config['mnt_backup_dom'] = setup_mnt_creds('dom')

                if ga_config['mnt_backup'] is True and ga_config['mnt_backup_type'] == 'cifs' and \
                        ga_config['mnt_samecreds'] is True:
                    ga_config['mnt_samecreds'] = setup_input(prompt='Use same share credentials as for remote backup?', default=True)
                    if ga_config['mnt_samecreds'] is True:
                        ga_config['mnt_log_user'] = ga_config['mnt_backup_user']
                        ga_config['ga_mnt_log_pwd'] = ga_config['mnt_backup_pwd']
                        ga_config['ga_mnt_log_dom'] = ga_config['mnt_backup_dom']
                    else:
                        ga_mnt_log_creds()
                else:
                    ga_mnt_log_creds()
        else:
            ga_config['mnt_log_type'] = 'False'  # for nfs/cifs apt installation

    ########################################################################################################################

    if ga_config['setuptype'] == 'agent':
        ga_config_var_certs()

    ########################################################################################################################

    ShellOutput(font='head', output='Logging setup information', symbol='-')

    setup_log_write_vars()

    ShellOutput(output="Thank you for providing the setup information.\nThe installation will start now")

    ########################################################################################################################


    def ga_foldercreate(path):
        if os_path.exists(path) is False:
            os_system("mkdir -p %s & chown -R growautomation:growautomation %s %s" % (path, path, ga_config['setup_log_redirect']))


    def ga_mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
        # need to test smb and nfs mount and correct it
        ShellOutput(font='head', output="Mounting %s share" % mname, symbol='-')
        if mtype == 'cifs':
            mcreds = "username=%s,password=%s,domain=%s" % (muser, mpwd, mdom)
        else:
            mcreds = 'auto'
        ga_fstab = open('/etc/fstab', 'a')
        if mtype == 'smb':
            ga_fstab.write("#Growautomation %s mount\n%s:/%s %s cifs %s 0 0\n\n" % (mname, msrv, mshr, mpath, mcreds))
        elif mtype == 'nfs':
            ga_fstab.write("#Growautomation %s mount\n%s:/%s %s nfs rw,relatime,user 0 0\n\n" % (mname, msrv, mshr, mpath))
        ga_fstab.close()
        os_system("mount -a %s" % ga_config['setup_log_redirect'])


    def ga_replaceline(file, replace, insert):
        os_system("sed -i 's^%s^%s^g' %s %s" % (replace, insert, file, ga_config['setup_log_redirect']))


    def ga_openssl_setup():
        ga_foldercreate("%s/ca/private" % ga_config['path_root'])
        ga_foldercreate("%s/ca/certs" % ga_config['path_root'])
        ga_foldercreate("%s/ca/crl" % ga_config['path_root'])
        os_system("chmod 770 %s/ca/private %s" % (ga_config['path_root'], ga_config['setup_log_redirect']))
        ga_replaceline("%s/ca/openssl.cnf", '= /root/ca', "= %s/ca") % (ga_config['path_root'], ga_config['path_root'])
        ShellOutput(font='head', output='Creating root certificate', symbol='-')
        os_system("openssl genrsa -aes256 -out %s/ca/private/ca.key.pem 4096 && chmod 400 %s/ca/private/ca.key.pe %s"
                  % (ga_config['path_root'], ga_config['path_root'], ga_config['setup_log_redirect']))
        os_system("openssl req -config %s/ca/openssl.cnf -key %s/ca/private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out %s/ca/certs/ca.cer.pem %s"
                  % (ga_config['path_root'], ga_config['path_root'], ga_config['path_root'], ga_config['setup_log_redirect']))


    def ga_openssl_server_cert(certname):
        ShellOutput(font='head', output='Generating server certificate', symbol='-')
        os_system("openssl genrsa -aes256 -out %s/ca/private/%s.key.pem 2048 %s" % (ga_config['path_root'], certname, ga_config['setup_log_redirect']))
        os_system("eq -config %s/ca/openssl.cnf -key %s/ca/private/%s.key.pem -new -sha256 -out %s/ca/csr/%s.csr.pem %s"
                  % (ga_config['path_root'], ga_config['path_root'], certname, ga_config['path_root'], certname, ga_config['setup_log_redirect']))
        os_system("openssl ca -config %s/ca/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 -in %s/ca/csr/%s.csr.pem -out %s/ca/certs/%s.cert.pem %s"
                  % (ga_config['path_root'], ga_config['path_root'], certname, ga_config['path_root'], certname, ga_config['setup_log_redirect']))


    def ga_sql_all():
        ShellOutput(font='head', output='Starting sql setup', symbol='#')
        ga_sql_backup_pwd = setup_pwd_gen(ga_config['setup_pwd_length'])
        ShellOutput(output='Creating mysql backup user')
        DoSql(command=["DROP USER 'gabackup'@'localhost';", "CREATE USER 'gabackup'@'localhost' IDENTIFIED BY '%s';" % ga_sql_backup_pwd,
                       "GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON *.* TO 'gabackup'@'localhost' IDENTIFIED BY '%s';" % ga_sql_backup_pwd, 'FLUSH PRIVILEGES;'],
              user='root', write=True, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
        setup_mysql_conntest('gabackup', ga_sql_backup_pwd, local=True, check_system=True)
        ShellOutput(font='head', output='Setting up mysql db', symbol='-')
        ShellOutput(output='Set a secure password and answer all other questions with Y/yes', style='info')
        ShellOutput(output="Example random password: %s" % setup_pwd_gen(ga_config['setup_pwd_length']), style='info')
        ShellOutput(output="\nMySql will not ask for the password if you start it locally (mysql -u root) with sudo/root privileges (set & forget)", style='info')
        os_system("mysql_secure_installation %s" % ga_config['setup_log_redirect'])

        setup_config_file(typ='w', text="[mysqldump]\nuser=gabackup\npassword=%s" % ga_sql_backup_pwd, file='/etc/mysql/conf.d/ga.mysqldump.cnf')

        os_system("usermod -a -G growautomation mysql %s" % ga_config['setup_log_redirect'])
        ga_foldercreate('/etc/mysql/ssl')


    def ga_sql_server():
        ShellOutput(font='head', output='Configuring sql as growautomation server', symbol='#')
        os_system("mysql -u root < /tmp/controller/setup/server/ga_db_setup.sql %s" % ga_config['setup_log_redirect'])
        ShellOutput('Imported sql database', style='info')
        if ga_config['setuptype'] == 'server':
            os_system("cp /tmp/controller/setup/server/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config['setup_log_redirect'])
        elif ga_config['setuptype'] == 'standalone':
            os_system("cp /tmp/controller/setup/standalone/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config['setup_log_redirect'])

        ShellOutput(output='Creating mysql admin user')
        DoSql(command=["DROP USER '%s'@'%s';" % (ga_config['sql_admin_user'], "%"), "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (ga_config['sql_admin_user'], "%", ga_config['sql_admin_pwd']),
                       "GRANT ALL ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (ga_config['sql_admin_user'], "%", ga_config['sql_admin_pwd']), 'FLUSH PRIVILEGES;'], user='root', write=True,
              hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
        setup_mysql_conntest(ga_config['sql_admin_user'], ga_config['sql_admin_pwd'], local=True, write=True)
        setup_config_file(typ='a', text="[db_server]\nsql_admin_user=%s\nsql_admin_pwd=%s"
                                        % (ga_config['sql_admin_user'], ga_config['sql_admin_pwd']))
        ShellOutput('Wrote admin credentials to config', style='info')

        if ga_config['setuptype'] == 'server':
            ShellOutput(output='Creating mysql server certificate')
            ga_openssl_server_cert('mysql')
            os_system("ln -s %s/ca/certs/ca.cer.pem /etc/mysql/ssl/cacert.pem && ln -s %s/ca/certs/mysql.cer.pem /etc/mysql/ssl/server-cert.pem && "
                      "ln -s %s/ca/private/mysql.key.pem /etc/mysql/ssl/server-key.pem %s"
                      % (ga_config['path_root'], ga_config['path_root'], ga_config['path_root'], ga_config['setup_log_redirect']))


    def ga_sql_agent():
        ShellOutput(font='head', output='Configuring sql as growautomation agent', symbol='#')
        os_system("cp /tmp/controller/setup/agent/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config['setup_log_redirect'])
        ShellOutput(output='Configuring mysql master-slave setup')
        ShellOutput(output='Replicating server db to agent for the first time', style='info')
        os_system("mysqldump -h %s --port %s -u %s -p %s ga > /tmp/ga.dbdump.sql && mysql -u root ga < /tmp/ga.dbdump.sql "
                  "%s" % (ga_config['sql_server_ip'], ga_config['sql_server_port'], ga_config['sql_agent_user'], ga_config['sql_agent_pwd'], ga_config['setup_log_redirect']))
        tmpsearchdepth = 500
        tmpfile = open('/tmp/ga.dbdump.sql', 'r')
        tmplines = tmpfile.readlines()[:tmpsearchdepth]
        for line in tmplines:
            if line.find('Master_Log_File: ') != -1:
                ga_config['sql_server_repl_file'] = line.split('Master_Log_File: ')[1].split("\n", 1)[0]
            elif line.find('Master_Log_Pos: ') != -1:
                ga_config['sql_server_repl_pos'] = line.split('Master_Log_Pos: ')[1].split("\n", 1)[0]

        ga_sql_server_agent_id = DoSql(command="SELECT data FROM ga.Setting WHERE belonging = '%s' AND setting = 'id';" % ga_config['hostname'],
                                       user=ga_config['sql_agent_user'], pwd=ga_config['sql_agent_pwd'], hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
        ga_replaceline('/etc/mysql/mariadb.conf.d/50-server.cnf', 'server-id              = 1', "server-id = %s" % (int(ga_sql_server_agent_id) + 100))
        process("systemctl restart mysql %s" % ga_config['setup_log_redirect'])

        ShellOutput(font='head', output="Creating local mysql controller user (read only)", symbol='-')
        DoSql(command=["DROP USER '%s'@'localhost';" % ga_config['sql_local_user'], "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (ga_config['sql_local_user'], ga_config['sql_local_pwd']),
                       "GRANT SELECT ON ga.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (ga_config['sql_local_user'], ga_config['sql_local_pwd']), 'FLUSH PRIVILEGES;'], user='root',
              write=True, hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
        setup_mysql_conntest(ga_config['sql_local_user'], ga_config['sql_local_pwd'], local=True)
        setup_config_file(typ='a', text="[db_local]\nsql_local_user=%s\nsql_local_pwd=%s\n[db_server]\nsql_agent_user=%s"
                                        "\nsql_agent_pwd=%s\nsql_server_ip=%s\nsql_server_port=%s"
                          % (ga_config['sql_local_user'], ga_config['sql_agent_pwd'], ga_config['sql_agent_user'],
                             ga_config['sql_agent_pwd'], ga_config['sql_server_ip'], ga_config['sql_server_port']))

        if setup_keycheck(ga_config['sql_server_repl_file']) is False or setup_keycheck(ga_config['sql_server_repl_pos']) is False:
            ShellOutput(output="SQL master slave configuration not possible due to missing information.\nShould be found in mysql dump from server "
                        "(searching in first %s lines).\nNot found: 'Master_Log_File:'/'Master_Log_Pos:'" % tmpsearchdepth, style='warn')
        else:
            DoSql(command=["CHANGE MASTER TO MASTER_HOST='%s', MASTER_USER='%s', MASTER_PASSWORD='%s', MASTER_LOG_FILE='%s', MASTER_LOG_POS=%s;"
                           % (ga_config['sql_server_ip'], ga_config['sql_server_repl_user'], ga_config['sql_server_repl_pwd'], ga_config['sql_server_repl_file'],
                              ga_config['sql_server_repl_pos']), ' START SLAVE;', ' SHOW SLAVE STATUS;'], user='root', write=True,
                  hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()

        ShellOutput(font='head', output='Linking mysql certificate', symbol='-')
        os_system("ln -s %s /etc/mysql/ssl/cacert.pem && ln -s %s /etc/mysql/ssl/server-cert.pem && ln -s %s /etc/mysql/ssl/server-key.pem %s"
                  % (ga_config['sql_ca'], ga_config['sql_cert'], ga_config['sql_key'], ga_config['setup_log_redirect']))


    def ga_sql_server_create_agent():
        ShellOutput(font='head', output='Registering a new growautomation agent to the server', symbol='#')
        create_agent = setup_input(prompt='Do you want to register an agent to the ga-server?', default=True)
        if create_agent is True:
            server_agent_list = DoSql(command="SELECT name FROM ga.Object WHERE type = 'agent';", user=ga_config['sql_admin_user'], pwd=ga_config['sql_admin_pwd'],
                                      hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
            if len(server_agent_list) > 0:
                ShellOutput(output="List of registered agents:\n%s\n" % server_agent_list, style='info')
            else:
                ShellOutput(output="No agents are registered.\n", style='info')

            create_agent_namelen = 0
            while create_agent_namelen > 10:
                if create_agent_namelen > 10:
                    ShellOutput(output="Agent could not be created due to a too long name.\nMax 10 characters supported.\nProvided: %s" % create_agent_namelen, style='warn')
                create_agent_name = setup_input(prompt='Provide agent name.', default='gacon01', poss='max. 10 characters long')
                if create_agent_name in server_agent_list:
                    ShellOutput(output='Controllername already registered to server. Choose a diffent name', style='warn')
                    create_agent_name = '-----------'
                create_agent_namelen = len(create_agent_name)

            create_agent_pwdlen = 0
            while create_agent_pwdlen > 99 or create_agent_pwdlen < 8:
                if create_agent_pwdlen > 99 or create_agent_pwdlen < 8:
                    ShellOutput(output='Input error. Value should be between 8 and 99', style='warn')
                create_agent_pwd = setup_input(prompt='Provide agent password.', default=setup_pwd_gen(ga_config['setup_pwd_length']), poss='between 8 and 99 characters')
                create_agent_pwdlen = len(create_agent_pwd)

            ShellOutput(font='head', output='Creating mysql controller user', symbol='-')
            create_agent_desclen = 0
            while create_agent_desclen > 50:
                if create_agent_desclen > 50:
                    ShellOutput(output='Description longer than 50 characters. Try again.', style='warn')
                create_agent_desc = setup_input(prompt='Do you want to add a description to the agent?', poss='String up to 50 characters')
                create_agent_desclen = len(create_agent_desc)

            DoSql(command=["DROP USER '%s'@'%s';" % (create_agent_name, "%"), "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (create_agent_name, "%", create_agent_pwd),
                           "GRANT CREATE, DELETE, INSERT, SELECT, UPDATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (create_agent_name, "%", create_agent_pwd),
                           'FLUSH PRIVILEGES;', "INSERT INTO ga.Agent (author, controller, description) VALUES (%s, %s, %s);"
                           % ('gasetup', create_agent_name, create_agent_desc)], user=ga_config['sql_admin_user'], pwd=ga_config['sql_admin_pwd'], write=True,
                  hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()

            create_replica_usr = create_agent_name + 'replica'
            create_replica_pwd = setup_pwd_gen(ga_config['setup_pwd_length'])
            DoSql(command=["DROP USER '%s'@'%s';" % (create_replica_usr, "%"), "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (create_replica_usr, "%", create_replica_pwd),
                           "GRANT REPLICATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (create_replica_usr, "%", create_replica_pwd),
                           'FLUSH PRIVILEGES;'], user=ga_config['sql_admin_user'], pwd=ga_config['sql_admin_pwd'], write=True,
                  hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()

            setup_config_file(typ='a', text="[db_agent_%s]\nsql_server_ip=%s\nsql_server_port=%s\nsql_agent_user=%s"
                                            "\nsql_agent_pwd=%s\nsql_replica_user=%s\nsql_replica_pwd=%s"
                              % (create_agent_name, ga_config['sql_server_ip'], ga_config['sql_server_port'], create_agent_name, create_agent_pwd, create_replica_usr, create_replica_pwd))

            ShellOutput(font='head', output="Creating mysql agent certificate\n", symbol='-')
            ga_openssl_server_cert(create_agent_name)


    ########################################################################################################################


    def setup_apt():
        ShellOutput(font='head', output='Installing software packages', symbol='#')
        os_system('apt-get update' + ga_config['setup_log_redirect'])
        if ga_config['setup_linuxupgrade'] is True:
            os_system("apt-get -y dist-upgrade && apt-get -y upgrade %s && apt -y autoremove" % ga_config['setup_log_redirect'])
            os_system("%s -m pip install --upgrade pip setuptools" % ga_config['python_path'])

        os_system("apt-get -y install mariadb-server mariadb-client git libsystemd-dev %s" % ga_config['setup_log_redirect'])

        if ga_config['setup_type_as'] is not True:
            os_system("apt-get -y install openssl %s" % ga_config['setup_log_redirect'])

        if (ga_config['mnt_backup'] or ga_config['mnt_log']) is True:
            if ga_config['mnt_backup_type'] == 'nfs' or ga_config['mnt_log_type'] == 'nfs':
                os_system("apt-get -y install nfs-common %s" % ga_config['setup_log_redirect'])
            elif ga_config['mnt_backup_type'] == 'cifs' or ga_config['mnt_log_type'] == 'cifs':
                os_system("apt-get -y install cifs-utils %s" % ga_config['setup_log_redirect'])


    def setup_pip():
        if ga_config['setup_ca'] is True:
            os_system("%s -m pip config set global.cert %s %s" % (ga_config['python_path'], ga_config['setup_ca_path'], ga_config['setup_log_redirect']))
            os_system("git config --global http.sslVerify true && git config --global http.sslCAInfo %s %s" % (ga_config['setup_ca_path'], ga_config['setup_log_redirect']))
        ShellOutput(font='head', output='Installing python packages', symbol='-')
        os_system("%s -m pip install systemd mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay smbus2 --default-timeout=100 %s"
                  % (ga_config['python_path'], ga_config['setup_log_redirect']))


    setup_apt()
    if ga_config['setup_type_as'] is True:
        setup_pip()


    def infra_oldversion_cleanconfig():
        movedir = "/tmp/setup_%s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"))
        os_system("mkdir -p %s" % movedir)
        oldversion_root_path = ga_config['path_root'] if ga_config['path_old_root'] is False else ga_config['path_old_root']
        if os_path.exists(oldversion_root_path):
            os_system("mv %s %s %s" % (oldversion_root_path, movedir, ga_config['setup_log_redirect']))
        if ga_config['setup_old_db'] is True:
            os_system("mysqldump -u root ga > /tmp/ga.dbdump_%s.sql %s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"),
                                                                           ga_config['setup_log_redirect']))
            DoSql(command='DROP DATABASE ga;', write=True, user='root', hostname=ga_config['hostname'],
                  setuptype=ga_config['setuptype']).start()
        ShellOutput(output='Removed old ga database')


    def infra_oldversion_backup():
        global ga_config
        ShellOutput(font='head', output='Backing up old growautomation root directory and database', symbol='-')
        oldbackup = ga_config['path_backup'] + "install_%s" % datetime.now().strftime("%Y-%m-%d_%H-%M")
        oldversion_root_path = ga_config['path_root'] if ga_config['path_old_root'] is False else ga_config['path_old_root']
        os_system("mkdir -p %s && cp -r %s %s %s" % (oldbackup, oldversion_root_path, oldbackup,
                                                     ga_config['setup_log_redirect']))
        os_system("mv %s %s %s" % (ga_config['setup_version_file'], oldbackup, ga_config['setup_log_redirect']))
        if ga_config['setup_old_db'] is True:
            os_system("mysqldump -u root ga > %s/ga.dbdump.sql %s" % (oldbackup, ga_config['setup_log_redirect']))
        ShellOutput(output="Backupfolder: %s\n%s\nRoot backupfolder:\n%s" % (oldbackup, os_listdir(oldbackup),
                                                                             os_listdir(oldbackup + '/growautomation')), style='info')
        if os_path.exists(oldbackup + '/ga.dbdump.sql') is False or \
                os_path.exists(oldbackup + '/growautomation/') is False:
            ShellOutput(output="Success of backup couldn't be verified. Please check it yourself to be sure that "
                               "it was successfully created. (Strg+Z "
                        "to get to Shell -> 'fg' to get back)\nBackuppath: %s" % oldbackup, style='warn')
            ga_config['setup_old_backup_failed_yousure'] = setup_input(prompt='Please verify that you want to continue the setup',
                                                                       default=False)
        else:
            ga_config['setup_old_backup_failed_yousure'] = True
        infra_oldversion_cleanconfig()


    def setup_infra_mount():
        if ga_config['mnt_backup'] is True or ga_config['mnt_log'] is True:
            ShellOutput(font='head', output='Mounting shares', symbol='-')
            if ga_config['mnt_backup'] is True:
                ga_mounts('backup', ga_config['mnt_backup_user'], ga_config['mnt_backup_pwd'], ga_config['mnt_backup_dom'],
                          ga_config['mnt_backup_srv'],
                          ga_config['mnt_backup_share'], ga_config['path_backup'], ga_config['mnt_backup_type'])
                ShellOutput(output='Added backup mount', style='succ')
            if ga_config['mnt_log'] is True:
                ga_mounts('log', ga_config['mnt_log_user'], ga_config['ga_mnt_log_pwd'], ga_config['ga_mnt_log_dom'],
                          ga_config['mnt_log_server'], ga_config['mnt_log_share'],
                          ga_config['path_log'], ga_config['mnt_log_type'])
                ShellOutput(output='Added log mount', style='succ')


    def setup_infra_dir():
        ShellOutput(font='head', output='Setting up directories', symbol='-')
        process("id -u growautomation || useradd growautomation & usermod -a -G gpio growautomation %s" % ga_config['setup_log_redirect'])
        ga_foldercreate(ga_config['path_backup'])

        if ga_config['setup_old'] is True and ga_config['setup_old_backup'] is True:
            infra_oldversion_backup()
        elif ga_config['setup_old'] is True:
            infra_oldversion_cleanconfig()

        setup_config_file(typ='w', text="version=%s\npath_root=%s\nhostname=%s\nsetuptype=%s"
                          % (ga_config['version'], ga_config['path_root'], ga_config['hostname'], ga_config['setuptype']),
                          file=ga_config['setup_version_file'])
        os_system("chmod 664 %s && chown growautomation:growautomation %s %s" % (ga_config['setup_version_file'],
                                                                                 ga_config['setup_version_file'],
                                                                                 ga_config['setup_log_redirect']))
        ga_foldercreate(ga_config['path_root'])
        ga_foldercreate(ga_config['path_log'])
        ShellOutput(output='Created directories', style='succ')
        setup_infra_mount()


    def setup_infra():
        ShellOutput(font='head', output='Setting up growautomation code', symbol='#')
        setup_infra_dir()
        ShellOutput(font='head', output='Setting up code', symbol='-')
        if process('systemctl status growautomation.service').find('not found') == -1:
            process("systemctl stop growautomation.service %s" % ga_config['setup_log_redirect'])
        # if os_path.exists('/tmp/controller') is True:
        #     os_system("mv /tmp/controller /tmp/controller_%s %s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"),
        #     ga_config['setup_log_redirect']))
        # os_system("cd /tmp && git clone https://github.com/growautomation-at/controller.git %s" % ga_config['setup_log_redirect'])

        if ga_config['setup_type_as'] is True:
            os_system("cp -r /tmp/controller/code/agent/* %s %s" % (ga_config['path_root'], ga_config['setup_log_redirect']))

        if ga_config['setup_type_ss'] is True:
            os_system("cp -r /tmp/controller/code/server/* %s %s" % (ga_config['path_root'], ga_config['setup_log_redirect']))

        os_system("cp /tmp/controller/setup/setup_linux.py %s/core %s" % (ga_config['path_root'], ga_config['setup_log_redirect']))

        os_system("find %s -type f -iname '*.py' -exec chmod 754 {} \\; %s" % (ga_config['path_root'], ga_config['setup_log_redirect']))
        os_system("chown -R growautomation:growautomation %s %s" % (ga_config['path_root'], ga_config['setup_log_redirect']))

        os_system("ln -s %s %s/backup && ln -s %s %s/log %s" % (ga_config['path_backup'], ga_config['path_root'],
                                                                ga_config['path_log'], ga_config['path_root'],
                                                                ga_config['setup_log_redirect']))

        setup_config_file(typ='w', text="[core]\nhostname=%s\nsetuptype=%s\npath_root=%s\nlog_level=%s"
                                        % (ga_config['hostname'], ga_config['setuptype'], ga_config['path_root'],
                                           ga_config['log_level']))

        service_system_path, service_py_path = "%s/service/systemd/growautomation.service" % ga_config['path_root'], \
                                               "%s/service/" % ga_config['path_root']
        if os_path.exists('/etc/systemd/system/growautomation.service'):
            os_system("mv /etc/systemd/system/growautomation.service /tmp %s" % ga_config['setup_log_redirect'])
        if ga_config['path_root'] != '/etc/growautomation':
            ga_replaceline(service_system_path, "Environment=\"PYTHONPATH=/etc/growautomation\"",
                           "Environment=\"PYTHONPATH=%s\"" % ga_config['path_root'] % (ga_config['python_path'], service_py_path))
            if ga_config['python_path'] != '/usr/bin/python3.8':
                ga_replaceline(service_system_path, "ExecStart=%s /etc/growautomation/service/service.py",
                               "ExecStart=%s %s/service.py" % (ga_config['python_path'], service_py_path))
                ga_replaceline(service_system_path, "ExecStartPre=%s /etc/growautomation/service/earlybird.py",
                               "ExecStartPre=%s %s/earlybird.py" % (ga_config['python_path'], service_py_path))
        process("systemctl link %s %s" % (service_system_path, ga_config['setup_log_redirect']))
        process("systemctl enable growautomation.service %s" % ga_config['setup_log_redirect'])
        process("systemctl daemon-reload %s" % ga_config['setup_log_redirect'])
        ShellOutput(output='Linked and enabled growautomation service', style='succ')

    setup_infra()

    # creating openssl ca
    if ga_config['setuptype'] == 'server':
        ga_openssl_setup()

    ga_sql_all()

    if ga_config['setup_type_ss'] is True:
        ga_sql_server()

    if ga_config['setuptype'] == 'server':
        ga_sql_server_create_agent()

    elif ga_config['setuptype'] == 'agent':
        ga_sql_agent()

    ########################################################################################################################

    ShellOutput(font='head', output='Basic device setup', symbol='#')
    ShellOutput(output="Please refer to the documentation if you are new to growautomation.\nLink: https://docs.growautomation.at")
    object_setup(setup_dict=ga_config)

    ########################################################################################################################
    # post setup tasks

    # default settings
    ga_config['backup_log'] = False
    ga_config['install_timestamp'] = datetime.now().strftime("%Y-%m-%d_%H-%M")


    def setup_mysql_write_config(thatdict):
        insertdict = {}
        for key, value in thatdict.items():
            if 'setup_' in key or 'pwd' in key:
                pass
            else:
                insertdict[key] = value

        for key, value in sorted(insertdict.items()):
            if type(value) == bool:
                if value is True:
                    value = 1
                else:
                    value = 0
            if ga_config['setuptype'] == 'agent':
                command = "INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('%s', '%s', '%s', '%s');" \
                          % ('setup', ga_config['hostname'], key, value)
                DoSql(command=command, user=ga_config['sql_agent_user'], pwd=ga_config['sql_agent_pwd'], write=True,
                      hostname=ga_config['hostname'], setuptype=ga_config['setuptype']).start()
            else:
                DoSql(command="INSERT INTO ga.Setting (author, belonging, setting, data) VALUES ('%s', '%s', '%s', '%s');"
                              % ('setup', ga_config['hostname'], key, value), user='root', write=True, hostname=ga_config['hostname'],
                      setuptype=ga_config['setuptype']).start()
        ShellOutput(output="Wrote %s setup settings to database" % len(insertdict), style='succ')


    ShellOutput(font='head', output='Writing configuration to database', symbol='#')
    setup_log_write_vars()
    writedict = {**ga_config_server, **ga_config}
    setup_mysql_write_config(writedict)

    ShellOutput(font='head', output='Starting growautomation service', symbol='#')
    process("chown -R growautomation:growautomation %s & chown -R growautomation:growautomation %s"
            % (ga_config['path_log'], ga_config['path_backup']))
    process("systemctl start growautomation.service %s" % ga_config['setup_log_redirect'])
    if process('systemctl status growautomation.service | grep Active:').find('running') != -1:
        ShellOutput('Service started', style='succ')
    else:
        ShellOutput('Service not running', style='warn')
    VarHandler().stop()
    ShellOutput(font='head', output='Setup finished! Please reboot the system', symbol='#')
    setup_log_write('Setup finished.')
except:
    try:
        setup_stop(error_msg="%s: %s" % (sys_exc_info()[0].__name__, sys_exc_info()[1]))
    except AttributeError:
        setup_stop()

# check path inputs for ending / and remove it
# delete old fstab entries and replace them (ask user)
# systemd systemd setup for agentdata and serverbackup
# ga service check for python path /usr/bin/python3.8 and growautomation root -> change execstart execstop etc
# ga_config['backup'] should do something.. but what?
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
# check all string inputs with setup_string_check (reference in input function if poss/default is str?)
# replaceline error if not found ?
# if setup-ca -> add ca to root-certs /usr/local/share/ca-certificates + update-ca-certificates before installing packages

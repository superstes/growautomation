#!/usr/bin/python3.9
# This file is part of GrowAutomation
#     Copyright (C) 2021  René Pascal Rath
#
#     GrowAutomation is free software: you can redistribute it and/or modify
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
#     Web: https://github.com/superstes/growautomation

# ga_version 1.0

# this script starts the ansible-playbook that updates the GrowAutomation components to the newer version

from re import match as regex_match
from os import listdir
from subprocess import run as subprocess_run
from time import sleep
from systemd import journal
from datetime import datetime


class Update:
    PROCESS_TIMEOUT = 3600
    CMD_PRE_SLEEP = 2
    NONE_RESULTS = ['', 'None', None, ' ']
    UPDATE_PACKAGES = [
        'ansible', 'git',
    ]

    def __init__(self):
        self.config = {}
        self.ansible_repo = f"/tmp/ga/update/ansible/{datetime.now().strftime('%Y-%m-%d_%H-%M')}"

    def start(self):
        if self._execute():
            journal.send("Update succeeded! Exiting.")

        else:
            journal.send("Update failed! Exiting.")

    def _execute(self):
        self._process(
            cmd=f"apt install -y {' '.join([pkg for pkg in self.UPDATE_PACKAGES])}",
            msg='Installing update dependencies',
        )

        # building config
        apache_tmp_folder = [_dir for _dir in listdir('/tmp') if regex_match('systemd-private-.*-apache2.service.*', _dir) is not None][0]
        config_file = f"/tmp/{apache_tmp_folder}/tmp/ga_update.conf"

        with open(config_file, 'r') as file:
            for line in file.readlines():
                _key, _value = line.split('=')
                key = _key.strip()
                value = _value.replace('\n', '').strip()
                self.config[key] = value

        results = []

        # preparing update script
        if self.config['ga_update_path_repo'] in self.NONE_RESULTS:
            if self.config['ga_update_method'] != 'offline':
                results.append(self._process(
                    cmd=f"git clone https://github.com/superstes/growautomation.git --single-branch {self.ansible_repo}",
                    msg='Downloading git repository',
                ))
                self.config['ga_update_path_repo'] = self.ansible_repo

            else:
                journal.send("ERROR: No valid repository provided and update-mode is offline. Can't continue!")
                return False

        else:
            self.ansible_repo = self.config['ga_update_path_repo']

        # NOTE: we do this since it could lead to incompatibility problems in the future if we use the newest version of the update-script
        target_version = self.config['ga_update_release'] if self.config['ga_update_type'] != 'commit' else self.config['ga_update_commit']
        results.append(self._process(
            cmd=f"cd {self.ansible_repo} && git reset --hard {target_version}",
            msg='Getting correct script-version',
        ))

        vars_string = [f"--extra-vars '{key}={value}' " for key, value in self.config.items()]
        path_ansible = f"{self.ansible_repo}/setup"

        results.append(self._process(
            cmd=f"cd {path_ansible} && ansible-galaxy collection install -r requirements.yml",
            msg="Installing update-script requirements (ansible)")
        )

        results.append(self._process(
            cmd=f"cd {path_ansible} && ansible-playbook update.yml {vars_string}",
            msg="Starting ansible-playbook to update GrowAutomation!")
        )

        return all(results)

    def _process(self, cmd: str, msg: str) -> bool:
        journal.send(msg)
        sleep(self.CMD_PRE_SLEEP)

        proc = subprocess_run(cmd, shell=True, timeout=self.PROCESS_TIMEOUT)

        if proc.returncode != 0:
            journal.send(f"Subprocess for command '{cmd}' returned an error!")
            return False

        return True


if __name__ == '__main__':
    Update().start()

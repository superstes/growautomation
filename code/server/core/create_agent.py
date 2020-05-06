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

#ga_version0.2

# checking for registered agent in the server db
# registering new agent (next free nr.)
# creating db user for agent since it will be needed in the agent setup
# option to create backup and or log shares
    # option to create a linux user for shares

# def ga_openssl_server_cert(tmpname):
#     os.system("openssl genrsa -aes256 -out %s/ca/private/%s.key.pem 2048" % (ga_rootpath, tmpname))
#     os.system("eq -config %s/ca/openssl.cnf -key %s/ca/private/%s.key.pem "
#               "-new -sha256 -out %s/ca/csr/%s.csr.pem" % (ga_rootpath, ga_rootpath, tmpname, ga_rootpath, tmpname))
#     os.system("openssl ca -config %s/ca/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 "
#               "-in %s/ca/csr/%s.csr.pem -out %s/ca/certs/%s.cert.pem"
#               % (ga_rootpath, ga_rootpath, tmpname, ga_rootpath, tmpname))
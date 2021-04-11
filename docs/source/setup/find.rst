.. _setup-find:

===========
Find device
===========

Description
***********

How to find a raspberry on the network.


Scanning
********

If the raspberry pi is connected to the same network as your computer you can just use a network scan tool.

1. Find local network range

  * **Windows**: (*not really needed -> the tool will normally pre-fill it for you*)

    1. Open commandline:

      Windows-Key+R => powershell => enter

    2. Get ip

      .. code-block:: none

        > ipconfig

        Ethernet adapter Ethernet:

        Connection-specific DNS Suffix  . : random.lan
        IPv4 Address. . . . . . . . . . . : 192.168.1.10
        Subnet Mask . . . . . . . . . . . : 255.255.255.0
        Default Gateway . . . . . . . . . : 192.168.1.254

  * **Linux**:

    1. Open terminal

      Ctrl+Alt+T

    2. Get ip

      .. code-block:: bash

        $ ip a

        7: eth0: <BROADCAST,MULTICAST,UP> mtu 1500 group default qlen 1
        inet 192.168.1.10/24 brd 192.168.1.255 scope global dynamic

2. Scan the network for an open ssh port (*you must have added the empty ssh file on the boot partition*)

  * **Windows**:

    `PortScan <https://www.heise.de/download/product/portscan-70308>`_

  * **Linux**:

    * Get the network address (*in a /24 network it always is the .0*) of you subnet (*192.168.1.X/24*)
    * You can also just put your data in a subnet calculator like `this one from heise <https://www.heise.de/netze/tools/netzwerkrechner/>`_
    * You need this for the scan as seen here:

      .. code-block:: bash

        $ sudo nmap -sS -p 22 192.168.1.0/24



.. warning::
   Documentation is not yet finished.
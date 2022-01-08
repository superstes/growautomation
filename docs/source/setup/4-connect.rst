.. _setup-connect:

.. include:: ../includes/tip_links.rst

==========
4. Connect
==========

.. _setup-connect-ssh:

SSH
***

How to connect to a raspberry via ssh.

Windows
=======

If you have Windows 10 or higher => you can use the native PowerShell SSH-Client to connect.

For earlier versions you will need to download a tool like `Putty <https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe>`_.



Linux
=====

Every linux distribution I know has a SSH-Client pre-installed - therefore you just need to open a terminal to use it.


----

Physical
********

Description
===========

Options how to connect your GrowAutomation setup to power and a network (*for your access*).


DISCLAIMER
==========

All the links for mentioned products are from amazon.

This is mainly because of convenience.

You **WILL GET** those products for a **better price somewhere else**.


.. _setup-connect-power:

Power
=====

**How to power it?**

This is a basic question and we came up with the following options for the answer:

* With a **power cord**

  This might or might not be an option for you. But it certainly would be the easiest way.

  You would have to buy an `outdoor power cable <https://www.amazon.de/Underground-Metres-Electric-Outdoor-Installation/dp/B08VHGQFHF>`_
  and some `electrical tubing <https://www.amazon.de/40775-Unitec-Flexible-Tube/dp/B002ZD800C>`_
  to bury it.

* With **sunlight**

  This one is trickier.

  You would have to buy a whole photovoltaic system with:

  * `a solar panel <https://www.amazon.de/gp/product/B07RZBVTGR>`_,
  * `a charge controller <https://www.amazon.de/gp/product/B07RZBVTGR>`_,
  * `a battery <https://www.amazon.de/gp/product/B08TRHGKZX>`_ and
  * if AC power is needed `a power inverter <https://www.amazon.de/Bapdas-300-1000-inverter-voltage-converter/dp/B06XJD7CHL>`_


----

.. _setup-connect-network:

Network
=======

The future **server-agent setup** will make wireless connections for agents easier.

Since the web user-interface will be run on the server and the agent just needs to communicate its data to the server.


WLAN
----

If you have an existing WIFI network you could just connect the raspberry to it.

This can be easy or hard. It depends on your environment.

Extend
^^^^^^

When your GrowAutomation setup is placed outside your house/apartment (*like in the garden*) it might be necessary to **extend the signal range** of your WIFI.

This can be done using a wlan repeater.

There are many types of wlan-repeaters. You should always buy/use the ones with **external antennas**. This is a good indication for their functionality.

We had good experiences with these ones:

  * `TPLink RE200 <https://www.amazon.de/RE450-TP-Link-RE200-WLAN-RepeateR/dp/B010RXXY48>`_
  * `TPLink TL-WA860RE <https://www.amazon.de/dp/B00K11UHVA/ref=emc_b_5_i>`_

LAN
===

The easiest and hardest way => *just* bury a network cable and connect the raspberry directly to your existing network.

This will be much work but it will work like a charm and won't make any problems.

SIM/LTE
=======

We have planned that the GrowAutomation setup should be able to work with a sim card. It should be accessible via dyn-dns over the mobile network.

But this is currently **not yet possible**!

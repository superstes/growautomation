.. _setup-raspberry:

.. include:: ../includes/tip_links.rst
.. include:: ../includes/warn_in_progress.rst

============
2. Raspberry
============

Description
***********

Here you can find some information on how to set-up your raspberry.

----

.. _setup-raspberry-ssd:

SSD
***

How to use an external usb ssd as system storage.


Reasons
=======

* A SSD is faster than a sd-card
* Has more read-write cycles

  * it will therefore not die as fast as a sd-card

* It is currently even cheaper


Needed
======

* SSD
* USB chassis
* SD card (*needed temporarily if it is an older model*)
* Raspberry Pi 2 or higher => 4 would be recommended
* Power supply with `recommended amperage <https://www.raspberrypi.org/documentation/hardware/raspberrypi/power/README.md>`_ (*since the usb device will suck relatively much power*)
* Active cooling => per example a raspi chassis with a build-in 5V fan (*since the power throughput will heat the board*)

Notes
=====

* You must not connect the external ssd via usb 3.x (*blue one*) since it might draw too much current and keep the device from booting at all
* If you have a raspberry pi 4 => try it without the sd card first; it might just work

HowTo
=====

Raspberry Pi 4
______________

* Download `raspi imager <https://www.raspberrypi.org/software/>`_
* Flash RaspberryPi OS on the usb-ssd (*lite version is recommended but has no graphical user interface*)
* Un- and re-plug both so they get automatically mounted on your computer

  * Add an empty 'ssh' file on each of the boot partitions as seen `in this tutorial <https://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh/enabling-ssh>`_
  * If you are using windows make sure you `enable it to show common file extensions <https://support.microsoft.com/en-us/windows/common-file-name-extensions-in-windows-da4a4430-8e76-89c5-59f7-1cdbbc75cb01>`_

* Find the device in the network and connect to it via ssh per powershell (*windows*) or bash (*linux*) (*default password is 'raspberry'*)

  .. code-block:: bash

      $ ssh pi@IP-ADDRESS

Older models
____________

* Download `raspi imager <https://www.raspberrypi.org/software/>`_
* Flash RaspberryPi OS on the sd card and usb-ssd (*lite version is recommended but has no graphical user interface*)
* Un- and re-plug both so they get automatically mounted on your computer

  * Add an empty 'ssh' file on each of the boot partitions as seen `in this tutorial <https://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh/enabling-ssh>`_
  * If you are using windows make sure you `enable it to show common file extensions <https://support.microsoft.com/en-us/windows/common-file-name-extensions-in-windows-da4a4430-8e76-89c5-59f7-1cdbbc75cb01>`_

* Plug in the sd card and start the raspberry
* Find the device in the network and connect to it via ssh per powershell (*windows*) or bash (*linux*) (*default password is 'raspberry'*)

  .. code-block:: bash

      $ ssh pi@IP-ADDRESS

* Now we will set-up the usb device to be bootable as described `in this raspi doc <https://www.raspberrypi.org/documentation/hardware/raspberrypi/bootmodes/msd.md>`_

  1. If you have an older board you might want to install all updates

    .. code-block:: bash

        $ sudo apt-get update && apt-get full-upgrade --yes
        $ sudo reboot
        # wait to reboot and re-connect
        $ sudo raspi-config

  2. Select Advanced Options
  3. Bootloader version

    * choose latest and confirm choice

  4. Select Boot Order

    * Select USB

  5. Exit the menu via 'finish' (*or Ctrl+D*)

    .. code-block:: bash

        $ sudo reboot

  6. The raspi will now boot to the usb-ssd

  7. Re-connect to the raspi and re-do the steps 2 to 5

  8. Disconnect the sd-card and you are done with this!

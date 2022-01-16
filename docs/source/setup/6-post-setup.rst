.. _setup-post-setup:

.. |users| image:: ../_static/img/setup/post-setup/users.png
   :class: ga-img-center ga-img-border
.. |script_end| image:: ../_static/img/setup/post-setup/script_end.png
   :class: ga-img-center ga-img-border

.. include:: ../includes/tip_links.rst

=============
6. Post-Setup
=============

Description
***********

Here we will go through the tasks you need to perform :ref:`after the installation <setup-setup>` per **script or image**.


Basic tasks
***********

1. You will have to connect to the device using ssh!

  Look into the :ref:`find <setup-find>` and :ref:`connect guide <setup-connect>` on how to do that.

  If you have used the installation image the password to connect should be: **Gr0w21736!**

2. Get information to access the controller

2.1. If you have used the **installation image**:

  * you should run the password randomization script:

    .. code-block:: bash

      sudo bash /var/lib/ga/setup/randomize_pwds.sh

  * you need to retrieve your passwords:

    .. code-block:: bash

      sudo cat /etc/.ga_setup
      # after that you should remove the password file
      sudo rm /etc/.ga_setup

2.2. If you have run the **setup script**:

  * The setup script should have displayed the URL and passwords for you to access the controller!

    |script_end|

3. Login into the web user-interface using the retrieved password:

  Open the URL https://${IP} - in which '${IP}' is the address you found using the :ref:`find guide <setup-find>`

4. You can now manage the users using the 'System - Users' site. (*change passwords and so on*)

  |users|

5. Now you can configure your devices and start using the GrowAutomation software!

  More information to the configuration can be found :ref:`here <config-device>`.

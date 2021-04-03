.. _basic-bugs:

.. |system_export| image:: ../_static/img/basic/bugs/system_export.png
   :class: ga-img-basic ga-img-border

====
Bugs
====

**When you encounter errors** you can check out our :ref:`troubleshooting guide <basic-troubleshoot>`.

If you could not resolve your problem by troubleshooting you can submit a bug ticket per email.

-----

Support
*******

The GrowAutomation software is an open source project.

Since we have limited time we cannot operate a basic technical support.

Therefore a community portal will be created to build a knowledge-base: `Community (not yet online) <https://community.growautomation.eu/>`_

**If you want to support our efforts** => consider `becoming a patreon <https://www.patreon.com/growautomation/>`_

-----

Bug hunting
***********

Before continuing => you need to know what's the source of the error. As described in the :ref:`troubleshooting guide <basic-troubleshoot>`.

Basic
=====

Note the following in the ticket email:

- What action did you perform as the error occurred? (*if any*)
- Export the current config and attach it to the email:

  |system_export|

Core
====

Please prepare the following:

- Set your log-level to 6 or above like described in the :ref:`troubleshooting guide <basic-troubleshoot>`
- Try to re-create the error
- Copy the following logs each in a separate text file:

  - core log
  - growautomation service log
  - growautomation service journal log
  - device logs (*if device-logging is enabled and devices are affected*)

- Send a `ticket <mailto:bugs@growautomation.eu>`_

Web
===

- Try to re-create the error
- Copy the following logs each in a separate text file:

  - web log
  - apache-webserver service log
  - apache-webserver service journal log

- Send a `ticket <mailto:bugs@growautomation.eu>`_
.. _workflow-input:

.. include:: ../includes/tip_links.rst

=====
Input
=====

Description
***********

Inputs are used to **gather sensor data**.

The data collection is done in a **time interval** :ref:`as configured <config-device-input>`.

This data inserted and stored in the database.

It can be :ref:`analyzed <config-dashboard>` or be used for decition making in :ref:`output-conditions <config-condition>`.

Types
*****

There are basically two types of sensors:

* Analogue sensors

  * can only be connected via :ref:`analogue-to-digital converters <device-connection>`, since the raspberry pi has no support for reading those directly

* Digital sensors

  * can be directly connected to the raspberry pi gpio pins

Of course there is the possibility that you would want to add another source to pull data from. This can be done by using a :ref:`custom script <config-script>`.

This way you can also implement new, not natively supported, sensors or connectors on your own.

.. _workflow-output:

======
Output
======

Description
***********

The output workflow is used to start actions when some condition is met.

Actions
*******

Actions can be anything you can script. Per example:

* starting a water pump
* opening a windows
* starting an air heater

The sky is the limit.

You can add custom, not natively supported, actors by using a :ref:`custom script <config-script>`.

Reverse
=======

Actors can also be **reversable**.

That can be handy per example for:

* a water pump that must be started and stopped
* a windows that must be opened and closed

Types
^^^^^

There are multiple ways an actor can be reversed:

* **time**

  * a timer is started after the initial execution of the actor after which the reversing process is done
  * this can be useful for:

    * a water pump

* **condition**

  * after the initial execution the actor's state is set to 'active'
  * the actor's reverse condition will be checked in an interval
  * if the reverse condition is met => it will be reversed
  * this can be useful for:

    * an air heater which will only stop if the air temperature is suitable
    * open a windows when the temperature is too high, close it when it gets too cold

Conditions
**********

You can configure complex condition that must be matched before an action is executed or reversed.

A condition **must be linked** at least with an **output device** or an **output model**.

The matching rules are connected to the condition via **condition links**.

It can also be **linked to areas**. This will filter the output devices, that would be started, to the ones that are a member of this area.

Matches
=======

A condition match is a single rule to match.

It can only be True or False.

As an example:

* Time average must be higher

  * Check input device 'air temperature'
  * Get the datapoints from the last hour
  * Calculate the average value from them
  * This value must be higher than X

* Maximum of last 15 readings must be lower

  * Check input device 'earth humidity'
  * Get the last 15 datapoints
  * Get the minimal value
  * This value must be lower than Y

You can find more details to this :ref:`here <config-condition-match>`.

Links
=====

A condition link connects either:

* two condition matches
* a condition match with a nested condition
* two nested conditions

It defines how the results of condition matches are 'added up'.

You can find more details to this :ref:`here <config-condition-link>`.

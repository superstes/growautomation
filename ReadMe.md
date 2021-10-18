<br>
<p align="center">
  <img src="https://www.growautomation.eu/img/svg/ga02c.svg" width="65%"/>
</p>
<br><br>

The goal is to automate activities related to the cultivation of plants.

And thus to minimize the associated repetitive tasks and optimize the process.

It's simple! And should remain so if you have little time for it.

----

## But what can it do?

### It provides:
* Simplified use of a <b>raspberry pi</b>
* A '<a href="https://docs.growautomation.eu/en/latest/workflow/input.html">input</a> => 
  <a href="https://docs.growautomation.eu/en/latest/workflow/output.html#conditions">condition</a> => 
  <a href="https://docs.growautomation.eu/en/latest/workflow/output.html#actions">output</a>' 
  <b>framework</b>
* Easy interaction through a <a href="https://demo.growautomation.eu"><b>web interface</b></a>
* Independence
  * The software-system has no need for external resources like cloud-services nor internet access
* A customizable <b>dashboard-system</b>


### It empowers you to:
* <b>Add</b> your <b>custom devices and actions</b>
* <b>Visually monitor</b> your sensor <b>data</b> via dashboards
* Use the web-ui to <b>easily troubleshoot</b> your hardware setup


### It can help you:
* Getting started with your own automation system
* Prevent <a href="https://docs.growautomation.eu/en/latest/basic/troubleshoot.html">common mistakes</a> with your <a href="https://docs.growautomation.eu/en/latest/device/input.html">hardware</a> and <a href="https://docs.growautomation.eu/en/latest/setup/wiring.html">wiring</a>
* Optimizing your growing environment
* Having a great time growing

----

## Documentation
<img src="https://readthedocs.org/projects/growautomation/badge/?version=latest&style=plastic"/>
<a href="https://docs.growautomation.eu">docs.growautomation.eu</a>

----

## Contact
<a href="mailto:contact@growautomation.eu">contact@growautomation.eu</a>

### Found bugs?
Just open a github issue!

### Support
Want to support the project?

<a href="https://www.patreon.com/growautomation">Become a patron</a>

----

## Version
__The code is currently not in a stable state !__

First 'stable' release coming <strong>SOON</strong>! :D

Version: 0.9

=> <a href="https://demo.growautomation.at/">DEMO</a> at its current state _(bugs included.. (; )_

### Work in progress
- testing and fixing input-condition-output workflow
- writing ansible-script to set-up the application


### History
- v0.9 _(2021-09)_
  - action-button in webUI
  - saving of action states to db (_keeping track of active actors_)
  - added basic dark-mode
- v0.8 _(2021-03 - 2021-04)_
  - updated condition workflow
  - created basic <a href="https://docs.growautomation.eu">documentation</a>
  - scripting setup using ansible
- v0.7 _(2020-12 - 2021-03)_
  - created basic _(django)_ web interface => <a href="https://demo.growautomation.at/">DEMO</a>
    - functionality:
      - config management
      - system management _(systemd / logs)_
      - help users test and debug their setup
      - customizable statistics/graphs
  - updated core to use django mysql schema

- v0.6 _(2020-11 - 2020-12)_
  - object-oriented config management
  
- v0.3 - v0.5 _(2020-02 - 2020-10)_
  - optimized code via implementing classes
  - created a systemd service to run the core
  
- v0.1 - v0.2 _(2019-05 - 2020-01)_
  - creating basic code structure _(functional programming)_

- v0.0 _(2018-� - 2019-04)_
  - dark age _(connected scripts)_

### Planned features
- installation per pre-configured image for easy setup
- documenting clean hardware setup _(easy wiring via patchpanel)_
- implementing more input _(sensors)_, output _(actors)_ and connection devices for native support _(air speed sensor/window opener actor/analog to digital converter)_
- builtin notification tasks
  - *get notified if the temperature is not optimal for growing*
- creating how-to videos on <a href="https://www.youtube.com/channel/UCLJyDlo3Z6eP_X2Pw0-Z8Pw">YouTube</a>
- improving webUI by using AJAX, optimizing workflow and so on
- integration of a scale so that the harvest can be logged
- off-grid installation => dyndns and hardware-guide
- actors in dashboard elements => when was an action taken; when was it reversed

### Maybe future features
- agent/server installation
  - server should be able to run as vm or on dedicated hardware
  - cloud-hosted server component
- create plans for 3d printable parts
- plant monitoring via nfc-tags => <a href="https://www.youtube.com/watch?v=13X_MqCHwgE">idea source</a>

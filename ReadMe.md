# Growautomation
We want to make an easy solution for anybody to automate everything around growing plants. <br />
Making it easier and optimizing the process.

And provide code samples to the diy community.

## Contact information
If you..
- want to contribute to this project
- have found bugs
- miss information of how to use it

<br> contact us at contact@growautomation.at

## Version information

__The code is currently not in a stable state !__

Version: 0.5

### Currently active
- updating action-handling
  - testing action-profile handling
  - updating and testing action-master module
- updating the installation script

### New features
- version 0.5
    - added action-profiles for complexer condition matching
    - split-up some core modules for better overview
- version 0.4
    - written basic [manual](https://github.com/growautomation-at/controller/blob/master/manual/agent/manual.md)
    - sensor data collection working
    - designed and tested easy and clean way to wire sensors to controller
      - connect vcc, gnd and data lines to a network patchpanel
      - splitting connection via network hub (not switch!!)
      - maximum 6 sensors per patchpanel port
      <br> <img src="https://github.com/growautomation-at/controller/blob/master/manual/hardware/cable-management.png" float="middle" border="4" alt="cable management topology">
- version 0.3
    - [setup notes](https://github.com/growautomation-at/controller/blob/master/setup/setup_notes.txt) if you wish to manually setup the growautomation core
    - service to dynamically start sensor data-collection and action-checks in threads
    - rewriting the whole core modules to support dynamic configuration
    - configuration interface to add and remove DeviceTypes/Devices easily
    - device sectors for limit actions to a physical area
    - linking of sensor and action devicetypes for easy action management

### On hold 
- documenting clean and easy wiring [as displayed here](https://github.com/growautomation-at/controller/blob/master/manual/hardware/cable-management.png) _(how-to video)_

### Optimizations
- optimizing database queries and adding indices
- splitting up grown-up modules
  - cleaner implementation of the config-interface (_split into muliple modules etc._)
- rework shell-input class

### Future features
- web interface for user interactions
- agent/server installation
  - documenting server installation on intel nuc and as vm
  - give users the option to use the official growautomation-server
    - to view data of their agents
    - to manage their agents and agent-actions
    - they only need to install the agent and give it network access
- creating a troubleshooing script to gather error logs
- add support for more sensors/actions
  - implementation of an air speed sensor
  - implementation of 3d-printable window openers (with dc motors)
  - checking clean solutions to implement analog sensors on the raspberry pi (p.e. ADS1115)
  
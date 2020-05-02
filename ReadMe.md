# Growautomation
We want to make an easy solution for anybody to automate everything around growing plants. <br />
Making it easier and optimizing the process.

And provide code samples to the diy community.

__The code is currently not in a stable state !__

Version: 0.4

## Currently active projects
- writing installation manual
- updating the installation script

## New features
- version 0.3
    - service to dynamically start sensor data-collection and action-checks in threads
    - rewriting the whole core modules to support dynamic configuration
    - configuration interface to add and remove DeviceTypes/Devices easily
    - device sectors for limit actions to a physical area
    - linking of sensor and action devicetypes for easy action management

## On hold projects
- designing a clean plug&play alternative for connecting sensors
    - example: <br /> <img src="https://github.com/growautomation-at/controller/blob/master/images/cable-topology.jpg" float="middle" width="50%" height="50%" border="4" alt="cable topology example">
- documenting server installation on intel nuc

## Future projects
- creating a troubleshooing script to gather error logs
- implement server/agent cofiguration
- webserver for observation and manual actions
- implementation of an air speed sensor
- implementation of 3d-printable window openers (with dc motors)
- checking clean solutions to implement analog sensors on the raspberry pi (p.e. ADS1115)
- testing a standalone solution with higher quality hardware (_gpio alternatives [?]_)
  
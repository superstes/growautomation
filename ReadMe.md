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

Version: 0.4

### Currently active
- updating action-handling
  - implementing complexer condition matching for actions
  - updating and testing action-master module
- updating the installation script

### New features
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
- documenting server installation on intel nuc

### Future features
- creating a troubleshooing script to gather error logs
- implement server/agent cofiguration
- webserver for observation and manual actions
- implementation of an air speed sensor
- implementation of 3d-printable window openers (with dc motors)
- checking clean solutions to implement analog sensors on the raspberry pi (p.e. ADS1115)
- testing a standalone solution with higher quality hardware (_gpio alternatives [?]_)
  
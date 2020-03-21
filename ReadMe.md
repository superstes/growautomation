# Growautomation
We want to make an easy solution for anybody to automate everything around growing plants. <br />
Making it easier and optimizing the process.

And provide code samples to the diy community.

__The code is currently not in a stable state !__

Version: 0.2.5

## Currently active projects
- rewriting the whole core modules to support dynamic configuration (_v0.3_)
- modules to add and remove DeviceTypes/Devices easily
- writing installation manual
- finishing the installation script
- creating a troubleshooing script to gather error logs

## On hold projects
- designing a clean plug&play alternative for connecting sensors
    - example: <br /> <img src="https://github.com/growautomation-at/controller/blob/master/images/cable-topology.jpg" float="middle" width="50%" height="50%" border="4" alt="cable topology example">
- documenting server installation on intel nuc
- implementing actionblocks and actiontypes
    - to provide custom linking of sensors and actions
        - being able to add new sensormodels and actions without changing the main code
    - to provide a simplified configuration for users
    - example: <br /> <img src="https://github.com/growautomation-at/controller/blob/master/images/actionblocks.jpg" float="middle" width="50%" height="50%" border="4" alt="actionblock example">

## Future projects
- webserver for observation and manual actions
- implementation of an air speed sensor
- implementation of 3d-printable window openers (with dc motors)
- checking clean solutions to implement analog sensors on the raspberry pi (p.e. ADS1115)
- testing a standalone solution with higher quality hardware (_gpio alternatives [?]_)
# Growautomation
We want to make an easy solution for anybody to automate everything around growing plants. <br />
Making it easier and optimizing the process.

And provide code samples to the diy community.

__The code is currently not in a stable state !__

Version: 0.2.1

## Currently active projects
- centralizing the configuration
    - plaintext config file for users -> mainconfig should format it as needed
    - create config format checker
- writing installation manual / scripting installation
    - implementing the main config changes into the setup script
- designing a clean plug&play alternative for connecting sensors
    - example: <br /> <img src="https://github.com/growautomation-at/controller/blob/master/images/cable-topology.jpg" float="middle" width="75%" height="75%" border="4" alt="cable topology example">

## On hold projects
- implementing actionblocks and actiontypes
    - to provide custom linking of sensors and actions
        - being able to add new sensormodels and actions without changing the main code
    - to provide a simplified configuration for users
    - example: <br /> <img src="https://github.com/growautomation-at/controller/blob/master/images/actionblocks.jpg" float="middle" width="50%" height="50%" border="4" alt="actionblock example">

## Planned projects
- webserver for observation and manual actions
- implementation of an air speed sensor
- implementation of 3d-printable window openers (with dc motors)
- troubleshooing script to gather error logs
- checking clean solutions to implement analog sensors on the raspberry pi (p.e. ADS1115)
- testing a standalone solution with higher quality hardware

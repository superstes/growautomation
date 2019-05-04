# GA standalone controller
Growautomation controller - based on a raspberry pi


## Setup types:

### centralized setup
  - rpi processess sensor data and hosts the database and webserver
  - for small setups
  - database/rpi should be backed up
  - rpi must be connected via network for website and other remote management options
  
### decentralized setup
  - rpi only processess sensor data
  - seperate operating systems host the database and webserver
  - controller and webserver are easily exchangeable
  - setup could scale up from standalone to multiple (rpi-) controllers
  - database should be backed up
  - different segments need to be interconnected via network

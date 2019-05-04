# GA standalone controller
Growautomation controller - based on a raspberry pi


## Setup types:

### centralized setup
  - rpi processess sensor data and hosts the database and webserver
  - for small setups
  - database/rpi should be backed up
  
### decentralized setup
  - rpi only processess sensor data
  - seperate operating systems host the database and webserver
  - controller and webserver are easily exchangeable
  - setup could scale up from standalone to multiple controllers
  - database should be backed up

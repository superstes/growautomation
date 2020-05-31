# Growautomation functionality manual

Written for growautomation version 0.4 <br>
Manual is not finished yet. <br>
<br>

## Basic Workflow
<img src="https://github.com/growautomation-at/controller/blob/master/manual/agent/basic_workflow.jpg" float="middle" border="4" alt="cable management topology"> <br>
<br>

### Pulling sensor data


### Perform actions



## Configuration

### Objects
Objects are used to link settings, other objects or groups. <br>
The following object types are relevant to use growautomation: <br>
* devicetypes
* devices
* agents

#### Devicetypes
Devicetypes are logical groupings of actions, sensors or downlinks. <br>
These types provide setting-inheritence for their child-devices. <br>

#### Devices
Devices are actual physical connected devices. <br>
All devices must be linked to a devicetype from which they will inherit their basic settings. <br>
<br>
Some sensors return more than one type of data. <i>(p.e. Adafruit DHT22)</i> <br>
In this case two devices must be created for each physical sensor. <i>(since every devicetype supports only one type of data)</i> <br>

#### Agents
Will be relevant after the server-agent installation-type gets available. <br>
All growautomation agents are added so their settings can be linked to them. <br>
<br>

### Groups
The following types of groups currently exist:
* sectors
* sectorgroups
* links

#### Sectors
This sort of group links devices into physical areas. <i>(p.e. bed in greenhouse)</i> <br>
Actions will be limited to the sectors they belong to. <br>
Also if a sensor threshold reaches its limit in one sector, the actions will only be started in the affected sector. <br>

#### Sectorgroups
Groups sectors into bigger areas. <i>(p.e. greenhouse)</i> <br>

#### Links
Links sensor- and action-devicetypes. <br>
If the threshold limit of a sensor-devicetype is reached their linked actions will be started. <br>

### Settings
* Each setting must be linked to an existing object.
* There is a set of settings that are needed to be processed via the growautomation core modules.
* Most settings will <b>inherit</b> their configuration from devicetype to child-devices. <br>
If the child-device has a specific configuration for this setting -> this overrides the devicetype config. <br>

#### General settings
* enabled <i>(devicetype/device)</i> <br>
Defines if the object will be processed or ignored by the core modules. <br>
If a devicetype is disabled, none of its child-devices will be processed. <br>
<br>
Options: <br>
  * 1 <br>
  Enables object. <br>
  * 0 <br>
  Disables object.<br>

#### Sensor settings
* connection <i>(devicetype/device)</i> <br>
Sets the way of how the controller can communicate to the sensor device. <br>
<br>
Options: <br>
  * direct <br>
  The device is directly connected to the raspberry gpio pins <br>
  * downlink <br>
  The device is connected through a downlink device <i>(p.e. an analog to digital converter)</i> <br>
  * specific <i>(devicetype only)</i> <br>
  Deactivates the connection-type inheritence to its child-devices. <br>
  It must be configured for each device on its own.<br>

* function <i>(devicetype)</i> <br>
Defines which function will be started to pull the sensor data. <br>
The path to the growautomation sensor-folder will prepended -> so only the filename needs to be provided. <br>
P.e. function = dht22.py, executed = '/etc/growautomation/sensor/dht22.py'<br>

* function_arg <i>(devicetype, optional)</i> <br>
You can define an argument to pass to the function-to-start. <br>
It will be passed as system argument #3 <i>(sys.argv[3])</i><br>

* threshold_max <i>(devicetype)</i> <br>
If this threshold limit is passed, it will trigger actions. <br>

* threshold_optimal <i>(devicetype)</i> <br>
If an action is set to reverse itself after the sensor threshold reached an optimal status -> this setting will be checked. <br>

* timer <i>(devicetype/device)</i> <br>
Interval in which to run the sensor function to pull its data. <br>

* timer_check <i>(devicetype)</i> <br>
Interval in which to run the check if linked actions should be executed. <br>

* unit <i>(devicetype)</i> <br>
Sets the unit of data received by the sensors from this type. <br>

* downlink <i>(device)</i> <br>
If the connection of the device was set to 'downlink' -> an existing downlink-device must be linked to it. <br>

#### Action settings
* connection <i>(devicetype/device)</i> <br>
Sets the way of how the controller can communicate to the sensor device. <br>
<br>
Options: <br>
  * direct <br>
  The device is directly connected to the raspberry gpio pins <br>
  * downlink <br>
  The device is connected through a downlink device <i>(p.e. an analog to digital converter)</i> <br>
  * specific <i>(devicetype only)</i> <br>
  Deactivates the connection-type inheritence to its child-devices. <br>
  It must be configured for each device on its own. <br>

* function <i>(devicetype)</i> <br>
Defines which function will be started to pull the sensor data. <br>
The path to the growautomation sensor-folder will prepended -> so only the filename needs to be provided. <br>
P.e. function = pump.py, executed = '/etc/growautomation/action/pump.py' <br>

* function_arg <i>(devicetype, optional)</i> <br>
You can define an argument to pass to the function-to-start. <br>
It will be passed as system argument #3 <i>(sys.argv[3])</i> <br>

* boomerang <i>(devicetype)</i> <br>
Defines if the action must be actively reversed. <br>
<br>
Options: <br>
  * 1 <br>
  Yes. <br>
  * 0 <br>
  No. <br>

* boomerang_type <i>(devicetype)</i> <br>
Indicates how it is decided when the action will be carried out. <br>
<br>
Options: <br>
  * time <br>
  The reverse-action will be started after the given time. <br>
  * threshold <br>
  The reverse-action will be started after the optimal threshold of the sensor is reached. <br>

* boomerang_time <i>(devicetype, optional)</i> <br>
If 'boomerang_type' is set to 'time' -> the time in seconds is defined.<br>

* boomerang_function <i>(devicetype, optional)</i> <br>
Defines if a different function must be started to reverse the action. <i>(compared to the default action function)</i><br>

* boomerang_function_arg <i>(devicetype, optional)</i> <br>
You can define an argument to pass to the function-to-start. <br>
It will be passed as system argument #3 <i>(sys.argv[3])</i> <br>

* downlink <i>(device)</i> <br>
If the connection of the device was set to 'downlink' -> an existing downlink-device must be linked to it. <br>

#### Downlink settings
* portcount <i>(devicetype)</i> <br>
The count of ports provided by each downlink of this type. <br>

* output_per_port <i>(devicetype)</i> <br>
Only relevant if sensors are connected via this type of downlink. <br>
Defines if the downlink function can output data per port. <br>
<br>
Options: <br>
  * 1 <br>
  The downlink function will output data per port <i>(outputs single string of data)</i> <br>
  * 0 <br>
  The downlink function will output the data of all ports at once. <br>
  The output must be a data-dict that must look like this:<br>
  {sensor1name: data1, sensor2name: data2} <br>

* function <i>(devicetype)</i> <br>
Defines which function will be started to pull the sensor data. <br>
The path to the growautomation sensor-folder will prepended -> so only the filename needs to be provided. <br>
P.e. function = ads1115.py, executed = '/etc/growautomation/downlink/ads1115.py' <br>

* function_arg <i>(devicetype, optional)</i> <br>
You can define an argument to pass to the function-to-start. <br>
It will be passed as system argument #3 <i>(sys.argv[3])</i> <br>


## Detailed Workflow

### Service

### Sensor master

### Action master


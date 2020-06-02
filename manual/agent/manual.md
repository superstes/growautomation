# Growautomation functionality manual

Written for growautomation version 0.4 <br>
<br>

## Basic Workflow
<img src="https://github.com/growautomation-at/controller/blob/master/manual/agent/basic_workflow.jpg" float="middle" border="4" alt="cable management topology"> <br>
<br>

### Pulling sensor data
Basic workflow:
1. The service will run a sensor timer for each sensor-devicetype there is.
2. This timer will start the sensor-master with the devicetype as argument.
3. Some filtering on base of the object settings will happen <i>(p.e. if the sensor-devicetype and -device is enabled)</i>
4. All sensor-data will be pulled via starting the configured sensor-function.
5. The data will be written to the database.
6. Return to timer-loop.

### Performing actions
The action-handling is still work-in-progress. <br>
<br>
Basically it will look like this:
1. The service will run a action-check timer for each action-profile there is.
2. This action-check then will inspect every condition in the action-profile. <br>
If not every condition applies -> skip 3.
3. Starts the action-function as configured for the devicetype. <br>
3.1. If the action needs to be reversed - the action-master will handle it.
4. Return to timer-loop. 

---

## Custom devices
You can find templates for all types of devices in their associated directories.

### Custom sensors

#### Input
The input received from the sensor-master will look like this: <br>
<ul>
  <li>
    "{device: port}" "None" "custom_argument"
    <ol>
      <li>
        dictionary with device and gpio port in it
      </li>
      <li>
        left blank for sensors
      </li>
      <li>
         custom function argument as configured for the sensor-devicetype
      </li>
    </ol>
  </li>
</ul>

#### Output
The output from a sensor-function must be a single string output via print(). <br>
The function may not output any other data.

### Custom downlinks

#### Output per port

##### Input
The input for this type of downlink will look like this: <br>
<ul>
  <li>
    "{device: port}" "{setting1: data1, setting2: data2}" "custom_argument"
    <ol>
      <li>
        dictionary with device and downlink port in it
      </li>
      <li>
        dictionary with all settings for the current downlink device in it
      </li>
      <li>
         custom function argument as configured for the sensor-devicetype
      </li>
    </ol>
  </li>
</ul>

##### Output
If the downlink if only used to start actions - there is no need to output anything to the growautomation core. <br><br>
The output for this type of downlink must be a single string output via print(). <br>
The function may not output any other data.

#### Output for all ports at once
In this example - the downlink will have a count of two ports.

##### Input
The input for this type of downlink will look like this: <br>
<ul>
  <li>
    "{device1: port1, device2: port2}" "{setting1: data1, setting2: data2}" "custom_argument"
    <ol>
      <li>
        dictionary with devices and downlink ports in it
      </li>
      <li>
        dictionary with all settings for the current downlink device in it
      </li>
      <li>
         custom function argument as configured for the sensor-devicetype
      </li>
    </ol>
  </li>
</ul>

##### Output
This type of downlink must output its data in the form of a dictionary. <br>
It must be formatted like this: <br>
* {device1: data1, device2: data2}

The output-dictionary **must have** all devices from the input-dictionary in it! <br>
If no data was received for either of the devices -> its data must be set to one of the following values:
* '' <br>
  empty string <i>(two single quotes)</i>
* None <br>
  None-type
* 'error' <br>
  This error message will be filtered via the sensor-master

---

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

---

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

---

### Settings
* Each setting must be linked to an existing object.
* There is a set of settings that are needed to be processed via the growautomation core modules.
* Most settings will <b>inherit</b> their configuration from devicetype to child-devices. <br>
If the child-device has a specific configuration for this setting -> this overwrites the devicetype config. <br>

#### General settings
<ul>
  <li>
    enabled <i>(devicetype/device)</i> <br>
    Defines if the object will be processed or ignored by the core modules. <br>
    If a devicetype is disabled, none of its child-devices will be processed. <br>
    <br>
    Options:
    <ul>
      <li>
        1 <br>
        Enables object.
      </li>
      <li>
        0 <br>
        Disables object.
      </li>
    </ul>
  </li>
</ul>

#### Sensor settings
<ul>
  <li>
    connection <i>(devicetype/device)</i> <br>
    Sets the way of how the controller can communicate to the sensor device. <br>
    <br>
    Options:
    <ul>
      <li>
        direct <br>
        The device is directly connected to the raspberry gpio pins
      </li>
      <li>
        downlink <br>
        The device is connected through a downlink device <i>(p.e. an analog to digital converter)</i>
      </li>
      <li>
        specific <i>(devicetype only)</i> <br>
        Deactivates the connection-type inheritence to its child-devices. <br>
        It must be configured for each device on its own.
      </li>
    </ul>
  </li>
</ul>

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
* function <i>(devicetype)</i> <br>
Defines which function will be started to pull the sensor data. <br>
The path to the growautomation sensor-folder will prepended -> so only the filename needs to be provided. <br>
P.e. function = pump.py, executed = '/etc/growautomation/action/pump.py' <br>

* function_arg <i>(devicetype, optional)</i> <br>
You can define an argument to pass to the function-to-start. <br>
It will be passed as system argument #3 <i>(sys.argv[3])</i> <br>

<ul>
  <li>
    connection <i>(devicetype/device)</i> <br>
    Sets the way of how the controller can communicate to the sensor device. <br>
    <br>
    Options:
    <ul>
      <li>
        direct <br>
        The device is directly connected to the raspberry gpio pins
      </li>
      <li>
        downlink <br>
        The device is connected through a downlink device <i>(p.e. an analog to digital converter)</i>
      </li>
      <li>
        specific <i>(devicetype only)</i> <br>
        Deactivates the connection-type inheritence to its child-devices. <br>
        It must be configured for each device on its own.
      </li>
    </ul>
  </li>
  <li>
    boomerang <i>(devicetype)</i> <br>
    Defines if the action must be actively reversed. <br>
    <br>
    Options:
    <ul>
      <li>
        1 <br>
        Yes.
      </li>
      <li>
        0 <br>
        No.
      </li>
    </ul>
  </li>
  <li>
    boomerang_type <i>(devicetype)</i> <br>
    Indicates how it is decided when the action will be carried out. <br>
    <br>
    Options:
    <ul>
      <li>
        time <br>
        The reverse-action will be started after the given time.
      </li>
      <li>
        threshold <br>
        The reverse-action will be started after the optimal threshold of the sensor is reached.
      </li>
    </ul>
  </li>
</ul>

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

<ul>
  <li>
    output_per_port <i>(devicetype)</i> <br>
    Only relevant if sensors are connected via this type of downlink. <br>
    Defines if the downlink function can output data per port. <br>
    <br>
    Options:
    <ul>
      <li>
        1 <br>
        The downlink function will output data per port <i>(outputs single string of data)</i>
      </li>
      <li>
        0 <br>
        The downlink function will output the data of all ports at once. <br>
        The output must be a data-dict that must look like this:<br>
        {sensor1name: data1, sensor2name: data2}
      </li>
    </ul>
  </li>
</ul>

* function <i>(devicetype)</i> <br>
Defines which function will be started to pull the sensor data. <br>
The path to the growautomation sensor-folder will prepended -> so only the filename needs to be provided. <br>
P.e. function = ads1115.py, executed = '/etc/growautomation/downlink/ads1115.py' <br>

* function_arg <i>(devicetype, optional)</i> <br>
You can define an argument to pass to the function-to-start. <br>
It will be passed as system argument #3 <i>(sys.argv[3])</i> <br>

---

## Growautomation Core

<table>
<tr><th>Name</th><th>Description</th></tr>
<tr><td>core/ant.py</td><td>Diverse shared functions/classes (extended use)</td></tr>
<tr><td>core/backup.py</td><td>Backups the database and root-path on timer</td></tr>
<tr><td>core/config.py</td><td>Config parser</td></tr>
<tr><td>core/hamster.py</td><td>For agent-server installation - will cache data to write to database if it isn't reachable</td></tr>
<tr><td>core/owl.py</td><td>Handles sql connections</td></tr>
<tr><td>core/parrot.py</td><td>Action-Master - checks if action should be started, starts actions</td></tr>
<tr><td>core/sensor_data_check.py</td><td>For usage in sensor functions - compares current data output to older ones</td></tr>
<tr><td>core/smallant.py</td><td>Diverse shared functions/classes (basic use)</td></tr>
<tr><td>core/smallconfig.py</td><td>Config parser for config file</td></tr>
<tr><td>core/snake.py</td><td>Sensor-Master - starts sensor functions to pull data, writes data to database</td></tr>
<tr><td>maintenance/config_interface.py</td><td>Commandline interface to interact with growautomation configuration</td></tr>
<tr><td>maintenance/update.sh</td><td>Will update all growautomation modules to the newest version found on github</td></tr>
<tr><td>service/systemd/growautomation.service</td><td>Systemd service file</td></tr>
<tr><td>service/earlybird.py</td><td>Checks system for dependencies before service start</td></tr>
<tr><td>service/threader.py</td><td>Runs timed threads</td></tr>
<tr><td>service/service.py</td><td>Service to handle timed threads</td></tr>
<tr><td>service/worker.py</td><td>Decides which module to start for a thread</td></tr>
</table>

---

## Database overview
Here you can see an overview over the tables used: <br> <br>
<img src="https://github.com/growautomation-at/controller/blob/master/manual/agent/database-plan.jpg" float="middle" border="4" alt="cable management topology"> <br>
<br>

## Detailed Workflow

### Service


---

### Sensor master


---

### Action master


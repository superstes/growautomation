_ga_version0.2.2

## Installation options:
1. Install a raspberry from scratch<br>
1.1. Install via script <br>
1.2. Install manually
2. Install a preconfigured raspberry pi image <br>
Download coming soon

### Install via script
+ cd /tmp && wget https://github.com/growautomation-at/controller/blob/master/setup/setup-linux.py
+ python3 setup-linux.py
+ follow the setup instructions
+ if you encounter an error you can get support in the [community](https://community.growautomation.at) (coming soon)
+ if you want to add your own sensortypes follow the [custom sensor ](https://git.growautomation.at/blob/master/manual/agent/install-custom-sensor.md) documentation

### Install manually
+ apt-get -y install python3 python3-pip git
+ python3 -m pip install mysql-connector-python + python3 -m pip install mysql-connector-python --default-timeout=100
+ you may need to install other python3 modules for your needed sensors<br>
 you can find information to some sensors in the [sensor guide](https://git.growautomation.at/blob/master/manual/hardware/sensors.md)
+ cd /tmp && git clone https://github.com/growautomation-at/controller.git && mkdir /etc/growautomation.at && cp -r /tmp/controller/code/agent/* /etc/growautomation
+ cp /tmp/controller/setup/agent/ga@* /etc/systemd/system/ && systemctl daemon-reload
+ PYVER=$(python3 --version | cut -c8-10) && ln -s /etc/growautomation/config /usr/local/lib/python$PYVER/dist-packages/GA
+ all sensors must be added like shown in the [custom sensor ](https://git.growautomation.at/blob/master/manual/agent/install-custom-sensor.md) documentation
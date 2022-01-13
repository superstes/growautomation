<br>
<p align="center">
  <img src="https://raw.githubusercontent.com/superstes/growautomation/dev/docs/source/_static/img/ga02c.svg" width="50%"/>
</p>
<br><br>

## Installation

There are basically two ways of installing the GrowAutomation software:

----

### Image

To install the pre-configured raspberry image you need to:

* Download the image: <a href="https://drive.google.com/file/d/1MIoagaB4rKUwSbUtUW5E5ZUCCDU3k30S/view?usp=sharing">Google Drive</a>
* Download and install the <a href="https://www.raspberrypi.com/software/">Raspberry Pi Imager</a> software on your computer (_or any other tool to flash images on a sd card_)
* Flash the image on a sd card or <a href="https://docs.growautomation.eu/en/latest/setup/2-raspberry.html#ssd">ssd</a>
* Look into the <a href="https://docs.growautomation.eu/en/latest/setup/6-post-setup.html">post-setup guide</a> for further ToDos.


----

### Setup script

This setup option allows you to modify/configure a lot of custom settings that are pre-set in the image installation!

#### Base setup

First you need to go through the basic setup process as described <a href="https://docs.growautomation.eu/en/latest/setup/2-raspberry.html">here</a>

#### Software setup

For now: the device will need internet access for the setup-process to work.

We might create an offline-setup guide in the future.

Run the following command on your raspberry:

```bash
curl -s https://raw.githubusercontent.com/superstes/growautomation/dev/setup/setup.sh | sudo bash
```

ELSE: if you want to modify the release or run the script on a remote host, you will have to do it this way:
```bash
wget https://raw.githubusercontent.com/superstes/growautomation/dev/setup/setup.sh -O /tmp/setup.sh
sudo bash /tmp/setup.sh TARGET-RELEASE(default=latest) DESTINATION-HOST(default=localhost)
```

This script will prepare your system to run the Ansible setup tasks/script.

It will ask you to modify the configuration before continuing as seen here:

```bash
###################################################################################
##################################### WARNING #####################################
###################################################################################
This is the last time you can modify the config before the installation is started.
  You could:
  -> send this window to the background (Ctrl+Z)
  -> make your modifications
  -> and bring it back to the foreground (fg).

###################################### INFO #######################################
The following config files exist:
  main: /tmp/ga_2022-01-13/setup/vars/main.yml
  remote hosts: (optional)
    - /tmp/ga_2022-01-13/setup/inventories/hosts.yml
    - /tmp/ga_2022-01-13/setup/inventories/host_vars/${HOSTNAME}.yml

Do you want to continue? (yes/NO)
```

Just put it in the background, change what you want and bring the setup back to the foreground.

Type 'yes' and press enter to start the setup tasks.

After that it will ask you for a 'BECOME password' => you need to **provide the password for a user with root privileges** on the target system! (_Default = 'raspberry'_)

##### Post install

* Look into the <a href="https://docs.growautomation.eu/en/latest/setup/6-post-setup.html">post-setup guide</a> for further ToDos.

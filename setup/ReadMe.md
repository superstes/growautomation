<br>
<p align="center">
  <img src="https://www.growautomation.eu/img/svg/ga02c.svg" width="50%"/>
</p>
<br><br>

## Installation

There are basically two ways of installing the GrowAutomation software:

### Setup script

#### Base setup

First you need to go through the basic setup process as described <a href="https://docs.growautomation.eu/en/latest/setup/raspberry.html">here</a>

#### Software setup

The device will need internet access since the setup will download the code for you.

You can just copy the 'setup.sh' file to the target system and run it:

```bash
$ sudo bash setup.sh
```

This script will prepare your system to run the Ansible setup tasks.

It will ask you to modify the configuration before continuing as seen here:

```bash
###################################################################################
##################################### WARNING #####################################
###################################################################################
This is the last time you can modify the config before the installation is started.
  You could:
  -> send this window to the background (Ctrl+Z)
  -> make your modifications and
  -> bring it back to the foreground (fg).

###################################### INFO #######################################
The following config files exist:
  main: /tmp/ga_2021-04-11/setup/vars/main.yml
  remote hosts (if needed):
    - /tmp/ga_2021-04-11/setup/inventories/hosts.yml
    - /tmp/ga_2021-04-11/setup/inventories/host_vars/$HOSTNAME.yml

Do you want to continue? (yes/any=no)
```

Just put it in the background, change what you want and bring the setup back to the foreground.

Type 'yes' and press enter to start the setup tasks.

##### Post install

If you haven't set custom passwords -> you can find the randomly generated ones like this:

```bash
cat /etc/.ga_setup
# rm /etc/.ga_setup  # to delete the file
```

**You should delete this file** after you saved your passwords safely!

Now you can access the web-interface and configure your devices.

More information to the configuration can be found <a href="https://docs.growautomation.eu/en/latest/index.html">here</a>.

### Image

**Currently not available**!

Will be provided for later versions.

You just need to flash the image on the sd-card or ssd for the raspberry and plug it in.

GrowAutomation is pre-installed.

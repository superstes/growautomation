_ga_version0.2.1_

# Basic raspberry pi setup on sd card

## What to buy: 
+ Raspberry Pi
  + [Rasperry Pi 3b Amazon](https://www.amazon.de/Raspberry-Model-Mainboard-MicroSD-Speicherkartenslot/dp/B00LPESRUK/)
+ SSD 2,5" 30GB+
  + [WD Green SSD 120GB](https://www.amazon.de/Green-interne-Festplatte-Lesegeschwindigkeit-Solid/dp/B076XWDN6V/)
+ RPI heat sinks and cooling fan<br>
  When using an usb-ssd you should consider cooling your rpi with a fan since it consumes more power than normally.<br>
  The most heat will be produced in the area where power supply is plugged into the rpi.
  + [Raspberry Pi Heatsink with Fan](https://www.amazon.de/GeeekPi-Raspberry-L%C3%BCfter-Aluminium-K%C3%BChlk%C3%B6rper/dp/B07JGNF5F8/)
+ A usb to sata chassis for 2,5" disks
  + [Inatec chassis](https://www.amazon.de/Inateck-festplatten-Werkzeuglose-Installation-Tool-free/dp/B00IJNDBM4/)
  

## Installation options:
1. Install a raspberry from scratch<br>
1.1. Install via script <br>
1.2. Install manually
2. Install a preconfigured raspberry pi image <br>
Download coming soon

### Install a raspberry from scratch
1. Format ssd to have one partition
2. Download latest [raspbian](https://www.raspberrypi.org/downloads/raspbian/)
3. Write .img file to ssd with a tool like<br> 
Windows: [Win32DiskImager](https://sourceforge.net/projects/win32diskimager/)  or [Rufus](https://rufus.ie/)<br>
Linux: "dd bs=4M if=/PATH/TO/raspbian.img of=/dev/SDCARD_DEVID conv=fsync"
4. Unplug the ssd
5. Replug the ssd to your computer
6. Go to the new "boot" partition
7. Create empty "ssh" file on it
8. Edit config.txt file with a text editor<br>
Windows: [Notepad++](https://notepad-plus-plus.org/)
9. Add "Enable USB Bootprogram_usb_boot_mode=1" as last line in the file
10. Connect the ssd, ethernet and power to the rpi
11. Find it on the local network with a tool like<br>
 Windows: [portscan](https://www.heise.de/download/product/portscan-70308)<br>
 Linux: [nmap](https://nmap.org/)
12. Connect to it via ssh with an application like<br>
 Windows: 7-10<1809 [putty](https://www.putty.org/), W10>1809 [openssh](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)<br>
 Linux: [openssh](https://www.openssh.com/)
13. Change the administrative password with the command "sudo passwd pi".
14. You are good to go!

### Growautomation setup
See [raspberry pi ga installation](https://git.growautomation.at/blob/master/manual/agent/install-ga.md)
_ga_version0.2.1_

# Basic raspberry pi setup on sd card

## What to buy: 
+ Raspberry Pi
  + [Rasperry Pi 3b Amazon](https://www.amazon.de/Raspberry-Model-Mainboard-MicroSD-Speicherkartenslot/dp/B00LPESRUK/)
+ SD Card with 8GB+
  + [Intenso SD Card 16GB](https://www.amazon.de/Intenso-Micro-Speicherkarte-SD-Adapter-schwarz/dp/B008RDCCR6/)
+ RPI heat sinks and cooling fan (if used in hot climate)
  + [Raspberry Pi Heatsink with Fan](https://www.amazon.de/GeeekPi-Raspberry-L%C3%BCfter-Aluminium-K%C3%BChlk%C3%B6rper/dp/B07JGNF5F8/)


## Installation options:
1. Install a raspberry from scratch<br>
1.1. Install via script <br>
1.2. Install manually
2. Install a preconfigured raspberry pi image <br>
Download coming soon

### Install a raspberry from scratch
1. Format sd card so you have one partition
2. Download latest [raspbian](https://www.raspberrypi.org/downloads/raspbian/)
3. Write .img file to sd card with a tool like<br> 
Windows: [Win32DiskImager](https://sourceforge.net/projects/win32diskimager/)  or [Rufus](https://rufus.ie/)<br>
Linux: "dd bs=4M if=/PATH/TO/raspbian.img of=/dev/SDCARD_DEVID conv=fsync"
4. Unplug the sd
5. Replug the sd to your computer
6. Go to the new "boot" partition
7. Create empty "ssh" file on it
8. Connect the sd, ethernet and power to the rpi
9. Find it on the local network with a tool like<br>
 Windows: [portscan](https://www.heise.de/download/product/portscan-70308)<br>
 Linux: [nmap](https://nmap.org/)
10. Connect to it via ssh with an application like<br>
 Windows: 7-10<1809 [putty](https://www.putty.org/), W10>1809 [openssh](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)<br>
 Linux: [openssh](https://www.openssh.com/)
11. Change the administrative password with the command "sudo passwd pi".
12. Run the following command(s) to extend the lifetime of your sd card: <br>
sudo dphys-swapfile swapoff && sudo dphys-swapfile uninstall && sudo update-rc.d dphys-swapfile remove
12. You are good to go!

### Growautomation setup
See [raspberry pi ga installation](https://git.growautomation.at/blob/master/manual/agent/install-ga.md)
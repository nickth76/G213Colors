# G213Colors
An application to change the key colors on a Logitech G213 Prodigy Gaming Keyboard and G203 Mouse.

Slightly modified to run on Ubuntu 20.04.
 
It is using [JeroenED](https://github.com/JeroenED)'s [G213Colors-gui](https://github.com/JeroenED/G213Colors) which is based on [SebiTimeWaster](https://github.com/SebiTimeWaster)'s [G213Colors](https://github.com/SebiTimeWaster/G213Colors)

## Supported devices

* G213 keyboard
* G203 mouse

## Screenshots
![g213-colors-static](https://raw.githubusercontent.com/nickth76/G213Colors/master/Preview/Screenshot%20from%202021-02-24%2020-54-34.png)
![g213-colors-breathe](https://raw.githubusercontent.com/nickth76/G213Colors/master/Preview/Screenshot%20from%202021-02-24%2020-55-01.png)
![g213-colors-segments](https://raw.githubusercontent.com/nickth76/G213Colors/master/Preview/Screenshot%20from%202021-02-24%2020-44-48.png)
![g213-colors-app](https://raw.githubusercontent.com/nickth76/G213Colors/master/Preview/Screenshot%20from%202021-02-24%2020-45-33.png)

## What it does
G213Colors lets you set the color(s) and certain effects of the illuminated keys on a G213 keyboard and G203 mouse under Ubuntu Linux.

The "Wave" color effect that is available with the Logitech software could not be replicated since it is completely generated in the software by updating the colors every x ms (In contrast to the other effects which run on the keyboard itself). You could generate this effect with a script, but since G213Colors has to detach the kernel driver from one of the G213's interfaces to send data out the multimedia keys would most likely stop working. Unfortunately this is a side effect of the linux driver structure.

## Installation
First clone the repository
`git clone https://github.com/nickth76/G213Colors.git` 

then run `INSTALL.sh`

It should do the rest automatically. In the end you can find the app , in the apps menu, named as G213 Colors.

### Restoring previous state
After rebooting your pc you can restore the pre-reboot state by running the app with the parameter `-t`

```Bash
sudo g213colors-gui -t
```
You can also do this automatically at reboot by enabling the systemd service.

```Bash
sudo systemctl enable g213colors.service
```

# G213Colors
A application to change the key colors on a Logitech G213 Prodigy Gaming Keyboard and G203 Mouse.

Slightly modified to run on Ubuntu 20.04.
 
It is using [JeroenED](https://github.com/JeroenED)'s [G213Colors-gui](https://github.com/JeroenED/G213Colors) which is based on [SebiTimeWaster](https://github.com/SebiTimeWaster)'s [G213Colors](https://github.com/SebiTimeWaster/G213Colors)

## Supported devices

* G213 keyboard
* G203 mouse

## Screenshots
![g213-colors-static](https://user-images.githubusercontent.com/15942848/30737264-4bab741c-9f86-11e7-893b-3ec0398c85b9.png)
![g213-colors-cycle](https://user-images.githubusercontent.com/15942848/30737260-49058a04-9f86-11e7-9682-94fd42b98881.png)
![g213-colors-breathe](https://user-images.githubusercontent.com/15942848/30737256-45c8ca18-9f86-11e7-9fbc-ff9caa317e14.png)
![g213-colors-segments](https://user-images.githubusercontent.com/15942848/30737263-4b84ca42-9f86-11e7-83e7-dd84e464b601.png)

## What it does
G213Colors lets you set the color(s) and certain effects of the illuminated keys on a G213 keyboard and G203 mouse under Ubuntu Linux.

The "Wave" color effect that is available with the Logitech software could not be replicated since it is completely generated in the software by updating the colors every x ms (In contrast to the other effects which run on the keyboard itself). You could generate this effect with a script, but since G213Colors has to detach the kernel driver from one of the G213's interfaces to send data out the multimedia keys would most likely stop working. Unfortunately this is a side effect of the linux driver structure.

## Installation
First clone the repository
`git clone .........` 

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
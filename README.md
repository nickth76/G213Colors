# G213Colors & G203Colors Control

An application to manage the illuminated key colors and effects on Logitech G213 Prodigy Gaming Keyboards and G203 Prodigy Gaming Mice on Linux.

This project is based on the work of [JeroenED's G213Colors-gui](https://github.com/JeroenED/G213Colors-gui) and [SebiTimeWaster's G213Colors](https://github.com/SebiTimeWaster/G213Colors), updated and enhanced for modern Linux distributions.

## Features

* Control static colors, breathing effects, and cycle effects.
* G213: Control individual keyboard segments.
* GUI for easy color selection and effect management.
* Settings are saved per user.
* System service to apply a default color scheme at system startup (for G213).
* **New:** Option to automatically apply a user's last saved settings for each device when they log into their desktop session.

## Supported Devices

* Logitech G213 Prodigy Gaming Keyboard
* Logitech G203 Prodigy Gaming Mouse

## Installation

The installation script automates the setup process, including installing dependencies, setting USB device permissions, and installing the application files.

1.  **Clone the repository:**
    ```
    git clone [https://github.com/githubuser/G213Colors.git](https://github.com/githubuser/G213Colors.git)
    cd G213Colors
    ```

2.  **Run the installation script with sudo:**
    ```sudo ./INSTALL.sh```
    The script will guide you through the necessary steps. After installation, you should find "G213 Colors" in your application menu.

    **Note:** If your Logitech devices were connected during installation, you might need to unplug and replug them, or reboot your computer, for the USB device permissions (udev rules) to take full effect.

## How it Works

There are two main ways color settings are applied:

### 1. GUI Application (User-Specific Settings & Login Autostart)

* Launch "G213 Colors" from your application menu. **It does not require `sudo` to run.**
* Select your device (G213 or G203) and configure your desired colors and effects.
* When you apply settings by clicking "Set G213", "Set G203", or "Set all Products", they are saved to your user's personal configuration directory (`~/.config/G213Colors/<DEVICE_NAME>.conf`, e.g., `G213.conf`). These settings are specific to your user account.

* **Applying Your Settings on Login:**
    * The GUI now includes checkboxes at the bottom: "Apply user settings on login: [ ] G213 [ ] G203".
    * If you check these boxes, your last saved configuration for the selected device(s) will be automatically applied when you log into your desktop session.
    * This works by creating a small startup file in your user's autostart directory (`~/.config/autostart/`).
    * This ensures your preferred colors are restored after the system's initial default (if any) is applied at boot.

### 2. System Startup Settings (System-wide Default via Service)

* The `INSTALL.sh` script sets up a systemd service (`g213colors.service`) that runs early during system startup.
* This service automatically applies a default color scheme to the **Logitech G213 keyboard**, setting it to a standard white color. This configuration is stored in `/etc/G213Colors.conf`.
* Currently, the G203 mouse does not have a color set by this system service at startup; its color will be its hardware default, or what its onboard memory retained, until you log in and your user-specific autostart (if enabled) applies your preference.

**Order of Application:**
1.  On system boot, `g213colors.service` sets the G213 to the system default (e.g., white).
2.  When you log into your desktop, if you've enabled "Apply user settings on login" via the GUI, your saved preferences for G213/G203 will be applied, overriding the system default for your session.

**Customizing System-Wide Startup Colors:**
If you wish to change the *system-wide default startup color* that the service applies (currently G213 white):
1.  You will need to edit the `/etc/G213Colors.conf` file with root privileges (e.g., `sudo nano /etc/G213Colors.conf`).
2.  The file format requires the first line to be `PRODUCT=<DEVICE_NAME>` (e.g., `PRODUCT=G213`) followed by the raw hex command string for the device on the next line.
    *(A future enhancement may allow setting this system default more easily via the GUI.)*

You can enable the system service to start on boot (this should be done automatically by `INSTALL.sh`) with:
```sudo systemctl enable g213colors.service```

You can also manually trigger the application of the system default settings by running:

```sudo /usr/bin/g213colors-gui -t```

## Screenshots 

![Application in Apps menu](https://raw.githubusercontent.com/nickth76/G213Colors/refs/heads/master/screenshots/screenshot-3.png)
![Main GUI](https://raw.githubusercontent.com/nickth76/G213Colors/refs/heads/master/screenshots/screenshot-1.png)
![Color picker](https://raw.githubusercontent.com/nickth76/G213Colors/refs/heads/master/screenshots/screenshot-2.png)

## Limitations
The "Wave" color effect available in official Logitech software on other platforms is not replicated here. This effect is typically software-generated by rapidly updating colors, which would conflict with how this tool interacts with the device (by detaching the kernel driver for direct USB control, which can affect multimedia keys if done continuously). The effects provided (static, breathe, cycle) run directly on the device hardware.

## Uninstallation
To remove the application and its system-wide components:
1. Navigate to the cloned repository directory.
2. Run the following command:
```sudo make uninstall```

This will remove the application files, the system-wide configuration file (/etc/G213Colors.conf), the systemd service unit, and the udev rule.

**Note on User Files:** The uninstallation command does not remove your personal configuration files (in ~/.config/G213Colors/) or any autostart entries you created via the GUI (in ~/.config/autostart/). You can remove these manually if desired, or simply uncheck the "Apply user settings on login" boxes in the GUI before uninstalling.
